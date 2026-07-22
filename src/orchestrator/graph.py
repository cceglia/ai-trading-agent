from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from src.analysis.candle_cache import (
    load_cached_analysis,
    save_analysis,
    should_run_analysis,
)
from src.data.snapshot_builder import SnapshotBuilder
from src.decision.models import DecisionOutput, MarketContextSummary, ReviewVerdict

logger = logging.getLogger(__name__)

MAX_REVIEW_ATTEMPTS = 2


class AgentState(TypedDict):
    """State for the trading graph."""

    symbol: str
    market_data: dict[str, Any]
    current_positions: list[dict[str, Any]]
    current_pending_orders: list[dict[str, Any]]
    account_info: dict[str, Any] | None
    structure_analysis: dict[str, Any] | None
    calendar_events: list[dict[str, Any]] | None
    market_context: MarketContextSummary | None
    decision: DecisionOutput | None
    review: ReviewVerdict | None
    review_feedback: str | None
    review_attempts: int
    errors: list[str]
    final_output: dict[str, Any] | None


class TradingGraph:
    """LangGraph orchestrator for trading analysis."""

    def __init__(
        self,
        data_provider: Any,
        structure_analyzer: Any,
        calendar_provider: Any,
        synthesizer: Any,
        decider: Any,
        reviewer: Any,
    ) -> None:
        """Initialize trading graph with dependencies.

        Args:
            data_provider: DataSource implementation
            structure_analyzer: StructureAnalyzer implementation
            calendar_provider: CalendarProvider implementation
            synthesizer: SynthesizerAgent
            decider: DeciderAgent
            reviewer: ReviewerAgent
        """
        self.data_provider = data_provider
        self.structure_analyzer = structure_analyzer
        self.calendar_provider = calendar_provider
        self.synthesizer = synthesizer
        self.decider = decider
        self.reviewer = reviewer
        self._snapshot_builder = SnapshotBuilder()

        self.graph = self._build_graph()

    def _build_graph(self) -> CompiledStateGraph[AgentState, None, Any, Any]:
        """Build the LangGraph StateGraph."""
        graph = StateGraph(AgentState)

        graph.add_node("fetch_data", self._fetch_data)
        graph.add_node("analyze_structure", self._analyze_structure)
        graph.add_node("evaluate_calendar", self._evaluate_calendar)
        graph.add_node("synthesize_context", self._synthesize_context)
        graph.add_node("decide", self._decide)
        graph.add_node("review", self._review)

        graph.set_entry_point("fetch_data")

        graph.add_edge("fetch_data", "analyze_structure")
        graph.add_edge("analyze_structure", "evaluate_calendar")
        graph.add_edge("evaluate_calendar", "synthesize_context")
        graph.add_edge("synthesize_context", "decide")
        graph.add_edge("decide", "review")

        graph.add_conditional_edges(
            "review",
            self._review_to_decide,
            {
                "retry": "decide",
                "end": END,
            },
        )

        return graph.compile()

    def _fetch_data(self, state: AgentState) -> dict[str, Any]:
        """Fetch market data from MT5."""
        logger.info("Fetching data for %s", state["symbol"])

        symbol = state["symbol"]

        try:
            current_positions = self.data_provider.get_positions(symbol)
            current_pending_orders = self.data_provider.get_pending_orders(symbol)
            account_info = self.data_provider.get_symbol_price(symbol)

            return {
                "current_positions": current_positions,
                "current_pending_orders": current_pending_orders,
                "account_info": account_info,
            }
        except Exception as e:
            logger.error("Failed to fetch data: %s", e)
            return {
                "errors": state.get("errors", []) + [f"Data fetch failed: {e}"],
            }

    def _analyze_structure(self, state: AgentState) -> dict[str, Any]:
        """Analyze market structure with candle-aligned caching."""
        logger.info("Analyzing structure for %s", state["symbol"])
        symbol = state["symbol"]
        now_utc = datetime.now(UTC)

        try:
            snapshots = {}
            cached_results = {}

            for timeframe in ["D1", "H4", "H1"]:
                if timeframe == "H1":
                    # H1 always runs fresh
                    pass
                elif not should_run_analysis(timeframe, symbol, now_utc):
                    # Cache is valid for this candle period
                    cached = load_cached_analysis(timeframe, symbol, now_utc)
                    if cached is not None:
                        cached_results[timeframe] = cached
                        continue

                csv_data = self.data_provider.get_candles(symbol, timeframe, 100)
                try:
                    snapshots[timeframe] = self._snapshot_builder.build(csv_data, symbol, timeframe)
                except (ValueError, Exception) as e:
                    logger.warning("Snapshot build failed for %s %s: %s", symbol, timeframe, e)
                    snapshots[timeframe] = csv_data

            if snapshots:
                fresh_result = self.structure_analyzer.analyze(snapshots)
            else:
                fresh_result = {}

            result: dict[str, Any] = {}
            for timeframe in ["D1", "H4", "H1"]:
                if timeframe in cached_results:
                    result[timeframe] = cached_results[timeframe]
            if fresh_result and isinstance(fresh_result, dict):
                for tf, val in fresh_result.items():
                    result[tf] = val
            for timeframe in ["D1", "H4", "H1"]:
                if timeframe not in result and timeframe in snapshots:
                    result[timeframe] = snapshots[timeframe]

            for timeframe in ("D1", "H4"):
                if timeframe in snapshots and timeframe in result:
                    save_analysis(timeframe, symbol, now_utc, result[timeframe])

            return {"structure_analysis": result}
        except Exception as e:
            logger.error("Structure analysis failed: %s", e)
            return {
                "errors": state.get("errors", []) + [f"Structure analysis failed: {e}"],
            }

    def _evaluate_calendar(self, state: AgentState) -> dict[str, Any]:
        """Evaluate calendar events."""
        logger.info("Evaluating calendar for %s", state["symbol"])

        try:
            events = self.calendar_provider.fetch_events()
            return {"calendar_events": events}
        except Exception as e:
            logger.error("Calendar evaluation failed: %s", e)
            return {
                "errors": state.get("errors", []) + [f"Calendar evaluation failed: {e}"],
                "calendar_events": [],
            }

    def _synthesize_context(self, state: AgentState) -> dict[str, Any]:
        """Synthesize market context."""
        logger.info("Synthesizing context for %s", state["symbol"])

        try:
            context = self.synthesizer.synthesize(
                structure_analysis=state.get("structure_analysis", {}),
                calendar_events=state.get("calendar_events", []),
                symbol=state["symbol"],
            )
            return {"market_context": context}
        except Exception as e:
            logger.error("Context synthesis failed: %s", e)
            return {
                "errors": state.get("errors", []) + [f"Context synthesis failed: {e}"],
            }

    def _decide(self, state: AgentState) -> dict[str, Any]:
        """Make trading decision."""
        logger.info("Making decision for %s", state["symbol"])

        try:
            context = state.get("market_context")
            if not context:
                return {
                    "errors": state.get("errors", []) + ["No market context available"],
                }

            feedback = state.get("review_feedback")
            attempts = state.get("review_attempts", 0) + 1

            decision = self.decider.decide(
                context=context,
                positions=state.get("current_positions", []),
                pending_orders=state.get("current_pending_orders", []),
                feedback=feedback if attempts > 1 else None,
            )
            return {"decision": decision, "review_attempts": attempts}
        except Exception as e:
            logger.error("Decision failed: %s", e)
            return {
                "errors": state.get("errors", []) + [f"Decision failed: {e}"],
            }

    def _review(self, state: AgentState) -> dict[str, Any]:
        """Review the decision."""
        logger.info("Reviewing decision for %s", state["symbol"])

        try:
            decision = state.get("decision")
            context = state.get("market_context")
            calendar_events = state.get("calendar_events", [])

            if not decision or not context:
                return {
                    "review": ReviewVerdict(
                        approved=False,
                        reasoning="Missing decision or context for review",
                        concerns=["Incomplete data for review"],
                    ),
                }

            verdict = self.reviewer.review(
                decision=decision,
                context=context,
                calendar_events=calendar_events,
            )

            feedback = None
            if not verdict.approved:
                feedback = f"Concerns: {verdict.concerns}\n"
                feedback += f"Suggestions: {verdict.suggested_improvements}"

            return {"review": verdict, "review_feedback": feedback}
        except Exception as e:
            logger.error("Review failed: %s", e)
            return {
                "review": ReviewVerdict(
                    approved=False,
                    reasoning=f"Review failed: {e}",
                    concerns=[str(e)],
                ),
            }

    def _review_to_decide(self, state: AgentState) -> str:
        """Conditional edge from review to decide or end."""
        review = state.get("review")
        attempts = state.get("review_attempts", 0)

        if review and review.approved:
            return "end"
        elif attempts < MAX_REVIEW_ATTEMPTS:
            return "retry"
        else:
            return "end"

    def run(self, symbol: str) -> dict[str, Any]:
        """Run the trading graph for a symbol.

        Args:
            symbol: Trading symbol to analyze

        Returns:
            Final analysis result
        """
        logger.info("Starting analysis for %s", symbol)

        initial_state = AgentState(
            symbol=symbol,
            market_data={},
            current_positions=[],
            current_pending_orders=[],
            account_info=None,
            structure_analysis=None,
            calendar_events=None,
            market_context=None,
            decision=None,
            review=None,
            review_feedback=None,
            review_attempts=0,
            errors=[],
            final_output=None,
        )

        result: dict[str, Any] = self.graph.invoke(initial_state)
        logger.info("Analysis complete for %s", symbol)
        return result
