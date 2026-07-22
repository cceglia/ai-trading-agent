"""Trading AI Agent - CLI Entry Point."""

import argparse
import logging
import sys

from config.settings import Settings
from src.logging_config import setup_logging

logger = logging.getLogger(__name__)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Trading AI Agent")
    parser.add_argument("symbol", help="Trading symbol (e.g., EURUSD)")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    parser.add_argument("--server-url", help="MCP server URL")
    parser.add_argument("--model", default="gpt-4o", help="LLM model")
    parser.add_argument(
        "--base-url", help="OpenAI-compatible base URL (e.g., http://localhost:11434/v1)"
    )

    args = parser.parse_args()

    setup_logging(args.log_level)

    settings = Settings()
    if args.server_url:
        settings.mcp_server_url = args.server_url
    if args.model:
        settings.openai_model = args.model
    if args.base_url:
        settings.openai_base_url = args.base_url

    logger.info("Starting Trading AI Agent for %s", args.symbol)

    try:
        from src.analysis.structure_analyzer import MarketStructureEngine
        from src.calendar.forexfactory import ForexFactoryCalendar
        from src.data.mt5_data_provider import Mt5DataProvider
        from src.decision.agents import DeciderAgent, ReviewerAgent, SynthesizerAgent
        from src.orchestrator.graph import TradingGraph

        data_provider = Mt5DataProvider(settings.mcp_server_url)
        structure_analyzer = MarketStructureEngine()
        calendar_provider = ForexFactoryCalendar()

        # Convert empty strings to None (agents expect str | None)
        api_key = settings.openai_api_key or None
        base_url = settings.openai_base_url or None

        synthesizer = SynthesizerAgent(
            model=settings.openai_model,
            api_key=api_key,
            base_url=base_url,
        )
        decider = DeciderAgent(
            model=settings.openai_model,
            api_key=api_key,
            base_url=base_url,
        )
        reviewer = ReviewerAgent(
            model=settings.openai_model,
            api_key=api_key,
            base_url=base_url,
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
        print(f"\nAnalysis complete for {args.symbol}")
        if result.get("final_output"):
            print(f"Result: {result['final_output']}")

    except Exception as e:
        logger.error("Analysis failed: %s", e)
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
