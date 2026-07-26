"""Trading AI Agent - CLI Entry Point."""

import argparse
import logging
import sys

from config.settings import Settings
from src.decision.cost_tracker import CostTracker
from src.logging_config import setup_logging

logger = logging.getLogger(__name__)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Trading AI Agent")
    parser.add_argument("symbol", help="Trading symbol (e.g., EURUSD)")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    parser.add_argument("--model", default=None, help="LLM model")
    parser.add_argument(
        "--base-url", help="OpenAI-compatible base URL (e.g., http://localhost:11434/v1)"
    )

    args = parser.parse_args()

    setup_logging(args.log_level)

    settings = Settings()
    if args.model:
        settings.openai_model = args.model
    if args.base_url:
        settings.openai_base_url = args.base_url

    logger.info("Starting Trading AI Agent for %s", args.symbol)

    try:
        from src.analysis.structure_analyzer import MarketStructureEngine
        from src.calendar.forexfactory import ForexFactoryCalendar
        from src.data.terminal_data_provider import TerminalDataProvider
        from src.decision.agents import DeciderAgent, ReviewerAgent, SynthesizerAgent
        from src.orchestrator.graph import TradingGraph

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
        result = graph.run(args.symbol)

        logger.info("Analysis complete for %s", args.symbol)

        # Check for fatal errors first — stop and notify
        fatal_error = result.get("fatal_error")
        if fatal_error:
            print(f"\n❌ FATAL ERROR: {fatal_error}")
            print("The pipeline was stopped. Fix the error and try again.")
            sys.exit(1)

        errors = result.get("errors") or []
        if errors:
            print(f"\n⚠️  Warnings/Errors ({len(errors)}):")
            for err in errors:
                print(f"    • {err}")

        print(f"\n{'=' * 60}")
        print(f"  ANALYSIS REPORT — {args.symbol}")
        print(f"{'=' * 60}")

        decision = result.get("decision")
        if decision:
            action = (
                getattr(decision, "action", decision.get("action", "N/A"))
                if isinstance(decision, dict)
                else getattr(decision, "action", "N/A")
            )
            reasoning = (
                getattr(decision, "reasoning", decision.get("reasoning", "N/A"))
                if isinstance(decision, dict)
                else getattr(decision, "reasoning", "N/A")
            )
            print(f"\n  Decision       : {action}")
            print(f"  Reasoning      : {reasoning}")
            entry_price = (
                getattr(decision, "entry_price", decision.get("entry_price"))
                if isinstance(decision, dict)
                else getattr(decision, "entry_price", None)
            )
            stop_loss = (
                getattr(decision, "stop_loss", decision.get("stop_loss"))
                if isinstance(decision, dict)
                else getattr(decision, "stop_loss", None)
            )
            take_profit = (
                getattr(decision, "take_profit", decision.get("take_profit"))
                if isinstance(decision, dict)
                else getattr(decision, "take_profit", None)
            )
            rr = (
                getattr(decision, "risk_reward_ratio", decision.get("risk_reward_ratio"))
                if isinstance(decision, dict)
                else getattr(decision, "risk_reward_ratio", None)
            )
            auth = (
                getattr(decision, "entry_authorized", decision.get("entry_authorized", False))
                if isinstance(decision, dict)
                else getattr(decision, "entry_authorized", False)
            )
            if entry_price:
                print(f"  Entry Price    : {entry_price}")
            if stop_loss:
                print(f"  Stop Loss      : {stop_loss}")
            if take_profit:
                print(f"  Take Profit    : {take_profit}")
            if rr:
                print(f"  Risk/Reward    : {rr}")
            print(f"  Entry Authorized: {auth}")

        context = result.get("market_context")
        if context:
            bias = (
                getattr(context, "bias", context.get("bias", "N/A"))
                if isinstance(context, dict)
                else getattr(context, "bias", "N/A")
            )
            confidence = (
                getattr(context, "confidence", context.get("confidence", 0))
                if isinstance(context, dict)
                else getattr(context, "confidence", 0)
            )
            reasoning = (
                getattr(context, "reasoning", context.get("reasoning", "N/A"))
                if isinstance(context, dict)
                else getattr(context, "reasoning", "N/A")
            )
            print(f"\n  Market Bias    : {bias}")
            print(f"  Confidence     : {confidence}%")
            print(f"  Reasoning      : {reasoning}")
            key_levels = (
                getattr(context, "key_levels", context.get("key_levels"))
                if isinstance(context, dict)
                else getattr(context, "key_levels", None)
            ) or []
            if key_levels:
                print(f"  Key Levels     : {', '.join(key_levels)}")
            events = (
                getattr(context, "structural_events", context.get("structural_events"))
                if isinstance(context, dict)
                else getattr(context, "structural_events", None)
            ) or []
            if events:
                print(f"  Structure Events: {', '.join(events)}")

        review = result.get("review")
        if review:
            approved = (
                getattr(review, "approved", review.get("approved"))
                if isinstance(review, dict)
                else getattr(review, "approved", False)
            )
            reasoning = (
                getattr(review, "reasoning", review.get("reasoning", "N/A"))
                if isinstance(review, dict)
                else getattr(review, "reasoning", "N/A")
            )
            print(f"\n  Review         : {'✅ APPROVED' if approved else '❌ REJECTED'}")
            print(f"  Review Reason  : {reasoning}")
            concerns = (
                getattr(review, "concerns", review.get("concerns"))
                if isinstance(review, dict)
                else getattr(review, "concerns", None)
            ) or []
            if concerns:
                print(f"  Concerns       : {'; '.join(str(c) for c in concerns)}")
            suggestions = (
                getattr(review, "suggested_improvements", review.get("suggested_improvements"))
                if isinstance(review, dict)
                else getattr(review, "suggested_improvements", None)
            )
            if suggestions:
                print(f"  Suggestions    : {suggestions}")

        print(f"\n{'=' * 60}\n")

    except Exception as e:
        logger.error("Analysis failed: %s", e)
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
