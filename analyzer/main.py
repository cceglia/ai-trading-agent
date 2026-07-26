"""Trading AI Agent - CLI Entry Point."""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Any

from config.settings import Settings
from src.decision.cost_tracker import CostTracker
from src.logging_config import setup_logging

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
    review = result.get("review")

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

    approved = False
    if review is not None:
        if isinstance(review, dict):
            approved = bool(review.get("approved", False))
        else:
            approved = bool(getattr(review, "approved", False))

    review_mark = " ✅" if approved else ""
    print(f"\n  {symbol}")
    print(f"    Bias       : {bias_str}")
    print(f"    Confidence : {confidence_val}%")
    print(f"    Action     : {action_str}{review_mark}")

    # Show key decision details when available
    entry_price = _get_decision_field(decision, "entry_price")
    stop_loss = _get_decision_field(decision, "stop_loss")
    take_profit = _get_decision_field(decision, "take_profit")
    rr = _get_decision_field(decision, "risk_reward_ratio")
    if entry_price:
        print(f"    Entry      : {entry_price}")
    if stop_loss:
        print(f"    Stop Loss  : {stop_loss}")
    if take_profit:
        print(f"    Take Profit: {take_profit}")
    if rr:
        print(f"    R/R        : {rr}")

    # Show reasoning snippets
    ctx_reasoning = _format_field(context, "reasoning") if context else None
    if ctx_reasoning and ctx_reasoning != "N/A":
        # Truncate long reasoning to first 120 chars
        short = ctx_reasoning[:120] + "…" if len(ctx_reasoning) > 120 else ctx_reasoning
        print(f"    Reasoning  : {short}")


def _build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(description="Trading AI Agent")
    parser.add_argument("symbols", nargs="+", help="Trading symbol(s) (e.g., XAUUSD EURUSD)")
    parser.add_argument("--output-dir", default=None, help="Output dir for JSON results")
    parser.add_argument("--model", default=None, help="LLM model")
    parser.add_argument(
        "--base-url", help="OpenAI-compatible base URL (e.g., http://localhost:11434/v1)"
    )
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    return parser


def main() -> None:
    """Main entry point.

    Accepts one or more trading symbols, runs the analysis pipeline for each,
    and prints a compact summary to stdout. When ``--output-dir`` is provided,
    also writes full JSON results to disk via :class:`ResultWriter`.
    """
    parser = _build_parser()
    args = parser.parse_args()

    setup_logging(args.log_level)

    settings = Settings()
    if args.model:
        settings.openai_model = args.model
    if args.base_url:
        settings.openai_base_url = args.base_url

    logger.info("Starting Trading AI Agent for symbols: %s", ", ".join(args.symbols))

    try:
        from src.analysis.structure_analyzer import MarketStructureEngine
        from src.calendar.forexfactory import ForexFactoryCalendar
        from src.data.terminal_data_provider import TerminalDataProvider
        from src.decision.agents import DeciderAgent, ReviewerAgent, SynthesizerAgent
        from src.orchestrator.graph import TradingGraph
        from src.output.result_writer import ResultWriter

        cost_tracker = CostTracker(pricing=settings.model_pricing)

        data_provider = TerminalDataProvider(
            server_url=settings.terminal_server_url,
            api_key=settings.terminal_api_key,
        )
        structure_analyzer = MarketStructureEngine()
        calendar_provider = ForexFactoryCalendar()

        # Convert empty strings to None (agents expect str | None)
        api_key = settings.openai_api_key or None
        base_url = settings.openai_base_url or None
        reasoning_effort = settings.openai_reasoning_effort or None

        synthesizer = SynthesizerAgent(
            model=settings.openai_model,
            api_key=api_key,
            base_url=base_url,
            reasoning_effort=reasoning_effort,
            cost_tracker=cost_tracker,
        )
        decider = DeciderAgent(
            model=settings.openai_model,
            api_key=api_key,
            base_url=base_url,
            reasoning_effort=reasoning_effort,
            cost_tracker=cost_tracker,
        )
        reviewer = ReviewerAgent(
            model=settings.openai_model,
            api_key=api_key,
            base_url=base_url,
            reasoning_effort=reasoning_effort,
            cost_tracker=cost_tracker,
        )

        graph = TradingGraph(
            data_provider=data_provider,
            structure_analyzer=structure_analyzer,
            calendar_provider=calendar_provider,
            synthesizer=synthesizer,
            decider=decider,
            reviewer=reviewer,
        )

        writer = ResultWriter(args.output_dir) if args.output_dir else None
        results: list[tuple[str, str, dict[str, Any]]] = []

        for symbol in args.symbols:
            try:
                logger.info("Running analysis for %s", symbol)
                result = graph.run(symbol)

                if writer:
                    broker_now = result.get("broker_now")
                    if broker_now is None:
                        logger.warning(
                            "No broker_now in result for %s — using current time",
                            symbol,
                        )
                        from datetime import datetime

                        broker_now = datetime.now()

                    structure = result.get("structure_analysis") or {}
                    ohlc = structure.get("_ohlc_bars") or {}
                    writer.write(symbol, result, ohlc, broker_now)

                results.append((symbol, "success", result))
                logger.info("Analysis complete for %s", symbol)

            except Exception as e:
                logger.error("Failed for %s: %s", symbol, e)
                results.append((symbol, "error", {"fatal_error": str(e)}))
                continue

        # ── Print compact summary ──────────────────────────────────────
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

    except Exception as e:
        logger.error("Analysis failed: %s", e)
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
