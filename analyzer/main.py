"""Trading AI Agent - CLI Entry Point."""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime
from typing import Any

from pydantic import BaseModel

from config.settings import Settings
from src.analysis.structure_analyzer import MarketStructureEngine
from src.calendar.forexfactory import ForexFactoryCalendar
from src.data.terminal_data_provider import TerminalDataProvider
from src.decision.agents import SynthesizerAgent
from src.decision.cost_tracker import CostLimitExceeded, CostTracker
from src.decision.llm_client import create_llm_client
from src.decision.llm_config import ProviderKind, resolve_model_identity
from src.logging_config import setup_logging
from src.notification.telegram_sender import send_trade_notification
from src.orchestrator.graph import TradingGraph
from src.output.result_writer import ResultWriter

logger = logging.getLogger(__name__)


def _format_field(
    obj: object,
    attr: str,
    default: str = "N/A",
) -> str:
    """Safely extract an attribute or dict key from an unknown object.

    Handles both pydantic model instances and plain dicts.
    """
    if isinstance(obj, dict):
        return str(obj.get(attr, default))
    return str(getattr(obj, attr, default))


def _format_field_int(
    obj: object,
    attr: str,
    default: int = 0,
) -> int:
    """Safely extract an integer attribute or dict key."""
    if isinstance(obj, dict):
        val = obj.get(attr, default)
    else:
        val = getattr(obj, attr, default)
    if val is None:
        return default
    return int(val)


def _get_decision_field(
    decision: object,
    field: str,
    default: str | None = None,
) -> str | None:
    """Get a decision field that may be None (e.g. entry_price)."""
    if decision is None:
        return default
    if isinstance(decision, dict):
        val = decision.get(field, default)
    else:
        val = getattr(decision, field, default)
    return val


def _print_symbol_summary(symbol: str, result: dict[str, Any]) -> None:
    """Print a compact analysis summary for one symbol to stdout."""
    decision = result.get("decision")
    context = result.get("market_context")
    analysis_result = result.get("analysis_result")
    final_output = result.get("final_output")

    fatal_error = result.get("fatal_error")
    errors = result.get("errors") or []

    if fatal_error:
        print(f"\n  ❌ {symbol}: FATAL — {fatal_error}")
        return

    if errors:
        print(f"\n  ⚠️  {symbol} — Warnings/Errors ({len(errors)}):")
        for err in errors:
            print(f"       • {err}")

    bias_str = _format_field(context, "bias") if context else "N/A"
    confidence_val = _format_field_int(context, "confidence") if context else 0
    action_str = _format_field(decision, "action") if decision else "N/A"

    print(f"\n  {symbol}")
    print(f"    Bias       : {bias_str}")
    print(f"    Confidence : {confidence_val}%")
    print(f"    Action     : {action_str}")

    # Show price fields from analysis_result (deterministic engine).
    # DecisionOutput no longer carries entry_price / stop_loss / take_profit;
    # they are on the SLTPOverlay sub-model within the AnalysisResult.
    if analysis_result is not None:
        sl_tp = analysis_result.sl_tp_overlay if hasattr(analysis_result, "sl_tp_overlay") else None
        if sl_tp is not None:
            entry_price = sl_tp.entry_price
            stop_loss = sl_tp.stop_loss
            take_profit = sl_tp.take_profit
        else:
            entry_price = stop_loss = take_profit = None
        rr = _format_field(analysis_result, "estimated_reward_risk") if analysis_result else None
    elif final_output is not None:
        # Fallback to model_dump(mode="json") dict when AnalysisResult is
        # not available (e.g. with serialised results from disk).
        sl_tp = final_output.get("sl_tp_overlay") or {}
        entry_price = sl_tp.get("entry_price")
        stop_loss = sl_tp.get("stop_loss")
        take_profit = sl_tp.get("take_profit")
        rr = final_output.get("estimated_reward_risk")
    else:
        entry_price = stop_loss = take_profit = rr = None

    if entry_price:
        print(f"    Entry      : {entry_price}")
    if stop_loss:
        print(f"    Stop Loss  : {stop_loss}")
    if take_profit:
        print(f"    Take Profit: {take_profit}")
    if rr and rr != "N/A":
        print(f"    R/R        : {rr}")

    # Show reasoning snippets
    ctx_reasoning = _format_field(context, "reasoning") if context else None
    if ctx_reasoning and ctx_reasoning != "N/A":
        short = ctx_reasoning[:120] + "…" if len(ctx_reasoning) > 120 else ctx_reasoning
        print(f"    Reasoning  : {short}")


def _build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(description="Trading AI Agent")
    parser.add_argument("symbols", nargs="+", help="Trading symbol(s) (e.g., XAUUSD EURUSD)")
    parser.add_argument("--model", default=None, help="LLM model")
    parser.add_argument(
        "--base-url", help="OpenAI-compatible base URL (e.g., http://localhost:11434/v1)"
    )
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    parser.add_argument(
        "--telegram",
        action="store_true",
        help="Send Telegram notifications for approved trade setups",
    )
    return parser


def _parse_and_configure_settings(args: argparse.Namespace) -> Settings:
    """Parse CLI args into a configured Settings instance.

    Applies CLI overrides (model, base_url) and warns about missing
    Telegram credentials when ``--telegram`` is set.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Configured Settings instance.
    """
    settings = Settings()
    if args.model:
        settings.openai_model = args.model
    if args.base_url:
        settings.openai_base_url = args.base_url

    if args.telegram and (not settings.telegram_bot_token or not settings.telegram_chat_id):
        logger.warning(
            "--telegram flag set but TRADING_TELEGRAM_BOT_TOKEN or "
            "TRADING_TELEGRAM_CHAT_ID is empty"
        )

    return settings


def _create_agents(
    settings: Settings,
    cost_tracker: CostTracker,
) -> Any:
    """Create the single LLM presentation agent used in the pipeline.

    Args:
        settings: Application settings.
        cost_tracker: Cost tracker instance.

    Returns:
        SynthesizerAgent instance.
    """
    api_key = settings.openai_api_key or ""
    base_url = settings.openai_base_url or None
    model = settings.openai_model
    reasoning_effort = settings.openai_reasoning_effort or None

    primary_provider = ProviderKind(settings.primary_llm_provider)

    client_kwargs: dict[str, Any] = {
        "api_key": api_key,
        "base_url": base_url,
        "model": model,
        "reasoning_effort": reasoning_effort,
        "default_temperature": settings.openai_temperature,
        "instructor_mode": settings.openai_instructor_mode,
        "timeout": settings.openai_timeout,
    }

    # Resolve model identity for logging and diagnostics.
    model_identity = resolve_model_identity(model, primary_provider)
    logger.info(
        "Resolved model identity: provider=%s family=%s version=%s status=%s",
        model_identity.provider.value,
        model_identity.model_family,
        model_identity.model_version or "N/A",
        model_identity.resolution_status.value,
    )

    primary_client = create_llm_client(provider=primary_provider, **client_kwargs)
    return SynthesizerAgent(
        llm_client=primary_client,
        cost_tracker=cost_tracker,
    )


def _initialize_pipeline(
    settings: Settings,
    cost_tracker: CostTracker,
) -> Any:
    """Create the full analysis pipeline (data providers, agents, graph).

    Args:
        settings: Application settings.
        cost_tracker: Cost tracker instance.

    Returns:
        Tuple of (compiled TradingGraph, ResultWriter).
    """
    data_provider = TerminalDataProvider(
        server_url=settings.terminal_server_url,
        api_key=settings.terminal_api_key,
    )
    structure_analyzer = MarketStructureEngine()
    calendar_provider = ForexFactoryCalendar()

    synthesizer = _create_agents(settings, cost_tracker)

    graph = TradingGraph(
        data_provider=data_provider,
        structure_analyzer=structure_analyzer,
        calendar_provider=calendar_provider,
        synthesizer=synthesizer,
    )

    writer = ResultWriter(settings.analysis_cache_dir)
    return graph, writer


def _write_result(
    symbol: str,
    result: dict[str, Any],
    writer: Any,
) -> None:
    """Write analysis result to disk via the ResultWriter.

    Falls back to ``datetime.now()`` when ``broker_now`` is missing
    from the result dict.

    Args:
        symbol: Trading symbol.
        result: Analysis result dict.
        writer: ResultWriter instance, or ``None`` to skip writing.
    """
    if writer is None:
        return

    broker_now = result.get("broker_now")
    if broker_now is None:
        logger.warning(
            "No broker_now in result for %s — using current time",
            symbol,
        )
        broker_now = datetime.now()

    structure = result.get("structure_analysis") or {}
    ohlc = structure.get("_ohlc_bars") or {}
    writer.write(symbol, result, ohlc, broker_now)


def _model_or_dict(value: Any) -> dict[str, Any]:
    """Normalize a pydantic model, plain dict, or ``None`` into a dict.

    Analysis result steps can carry either a pydantic model (e.g. a decision
    or review) or an already-serialized dict.  This helper makes both forms
    usable by the notification layer, which expects plain dictionaries.
    """
    if isinstance(value, BaseModel):
        return value.model_dump()
    if isinstance(value, dict):
        return value
    return {}


def _send_telegram_notification(
    symbol: str,
    result: dict[str, Any],
    settings: Settings,
) -> None:
    """Send a Telegram notification for an approved trade setup.

    Only sends when the decision is ``buy_setup`` or ``sell_setup`` and the
    deterministic validation status is ``VALID``.

    Args:
        symbol: Trading symbol.
        result: Analysis result dict.
        settings: Application settings (for Telegram credentials).
    """
    decision = _model_or_dict(result.get("decision"))
    context = _model_or_dict(result.get("market_context", result.get("context")))
    if result.get("validation_status") == "VALID" and decision.get("action") in (
        "buy_setup",
        "sell_setup",
    ):
        send_trade_notification(
            symbol=symbol,
            decision=decision,
            context=context,
            web_ui_base_url=settings.web_ui_base_url,
            bot_token=settings.telegram_bot_token,
            chat_id=settings.telegram_chat_id,
            result=result,
        )


def _run_single_symbol(
    graph: Any,
    symbol: str,
    settings: Settings,
    writer: Any,
    telegram_enabled: bool,
) -> tuple[str, str, dict[str, Any]]:
    """Run the full analysis pipeline for a single symbol.

    Args:
        graph: Compiled TradingGraph instance.
        symbol: Trading symbol to analyse.
        settings: Application settings.
        writer: Optional ResultWriter for persisting results.
        telegram_enabled: Whether ``--telegram`` was set on CLI.

    Returns:
        Tuple of ``(symbol, status, data)`` where status is ``"success"``
        or ``"error"``.
    """
    try:
        logger.info("Running analysis for %s", symbol)
        result = graph.run(symbol)

        _write_result(symbol, result, writer)

        if telegram_enabled:
            _send_telegram_notification(symbol, result, settings)

        logger.info("Analysis complete for %s", symbol)
        return symbol, "success", result

    except CostLimitExceeded:
        raise
    except Exception as e:
        logger.error("Failed for %s: %s", symbol, e)
        return symbol, "error", {"fatal_error": str(e)}


def _print_summary(results: list[tuple[str, str, dict[str, Any]]]) -> None:
    """Print the formatted analysis summary for all symbols.

    Args:
        results: List of ``(symbol, status, data)`` tuples.
    """
    print(f"\n{'=' * 60}")
    print(f"  ANALYSIS SUMMARY — {len(results)} symbol(s)")
    print(f"{'=' * 60}")

    for symbol, status, data in results:
        if status == "error":
            err_msg = data.get("fatal_error", "Unknown error")
            print(f"\n  ❌ {symbol}: FAILED — {err_msg}")
            continue

        _print_symbol_summary(symbol, data)

    print(f"\n{'=' * 60}\n")


def _run_pipeline(
    settings: Settings,
    symbols: list[str],
    telegram_enabled: bool,
) -> None:
    """Run the full analysis pipeline for all symbols.

    Args:
        settings: Application settings.
        symbols: Trading symbols to analyse.
        telegram_enabled: Whether ``--telegram`` was set on CLI.
    """
    cost_tracker = CostTracker(pricing=settings.model_pricing)
    cost_tracker.set_limit(settings.cost_per_symbol_limit)
    graph, writer = _initialize_pipeline(settings, cost_tracker)

    results: list[tuple[str, str, dict[str, Any]]] = []
    for symbol in symbols:
        cost_tracker.reset()
        cost_tracker.set_symbol(symbol)
        result = _run_single_symbol(graph, symbol, settings, writer, telegram_enabled)
        results.append(result)

    _print_summary(results)


def main() -> None:
    """Main entry point.

    Parses CLI arguments, initialises the analysis pipeline, runs
    analysis for each requested symbol, and prints a compact summary.
    """
    args = _build_parser().parse_args()
    setup_logging(args.log_level)
    settings = _parse_and_configure_settings(args)

    logger.info("Starting Trading AI Agent for symbols: %s", ", ".join(args.symbols))

    try:
        _run_pipeline(settings, args.symbols, args.telegram)
    except Exception as e:
        logger.error("Analysis failed: %s", e)
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
