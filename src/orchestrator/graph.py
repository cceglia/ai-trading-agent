from __future__ import annotations

import logging
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from src.analysis.candle_cache import (
    save_analysis,
)
from src.analysis.market_structure_engine.config import get_profile
from src.data.snapshot_builder import SnapshotBuilder
from src.decision.models import DecisionOutput, MarketContextSummary, ReviewVerdict

logger = logging.getLogger(__name__)

MAX_REVIEW_ATTEMPTS = 2

# Keys within a per-timeframe engine output that contain massive lists
# unsuitable for LLM prompts. These are stripped during summarization.
_LARGE_STRUCTURE_KEYS = frozenset(
    {
        "swings",
        "calculation_metadata",
        "engine",
    }
)


def _summarize_timeframe(tf_data: dict[str, Any]) -> dict[str, Any]:
    """Extract compact analytical fields from a single timeframe engine output.

    The full engine output contains massive lists (swings, events, levels,
    liquidity pools) that can exceed LLM context windows when serialized.
    This function keeps only the compact summary fields the LLM needs.
    """
    summary: dict[str, Any] = {}

    # Source audit (small — bar count, closure status)
    if "source_audit" in tf_data:
        summary["source_audit"] = tf_data["source_audit"]

    # Technical context (latest indicator values only — small)
    if "technical_context" in tf_data:
        summary["technical_context"] = tf_data["technical_context"]

    # Candles (latest candle analysis — small)
    if "candles" in tf_data:
        summary["candles"] = tf_data["candles"]

    # Market structure (classification strings — small)
    if "market_structure" in tf_data:
        summary["market_structure"] = tf_data["market_structure"]

    # Scoring (bias, confidence — small)
    if "scoring" in tf_data:
        summary["scoring"] = tf_data["scoring"]

    # Events — keep only latest_material_event and latest_primary_event,
    # drop the full event lists (primary_events, internal_events, failed_breakouts)
    events = tf_data.get("events", {})
    if isinstance(events, dict):
        compact_events: dict[str, Any] = {}
        for key in ("latest_material_event", "latest_primary_event", "failed_bos_count"):
            if key in events:
                compact_events[key] = events[key]
        if compact_events:
            summary["events"] = compact_events

    # Levels — keep only nearest support/resistance summary fields,
    # drop the full supports/resistances lists
    levels = tf_data.get("levels", {})
    if isinstance(levels, dict):
        compact_levels: dict[str, Any] = {}
        for key in (
            "nearest_support",
            "nearest_resistance",
            "nearest_support_distance_atr",
            "nearest_resistance_distance_atr",
        ):
            if key in levels:
                compact_levels[key] = levels[key]
        if compact_levels:
            summary["levels"] = compact_levels

    # Liquidity — keep only summary fields, drop pools/events lists
    liquidity = tf_data.get("liquidity", {})
    if isinstance(liquidity, dict):
        compact_liquidity: dict[str, Any] = {}
        for key in ("nearest_buy_side", "nearest_sell_side", "dominant_draw", "latest_event"):
            if key in liquidity:
                compact_liquidity[key] = liquidity[key]
        if compact_liquidity:
            summary["liquidity"] = compact_liquidity

    # Analysis context (the structured decision-oriented summary)
    if "analysis_context" in tf_data:
        summary["analysis_context"] = tf_data["analysis_context"]

    # Timeframe metadata
    if "timeframe" in tf_data:
        summary["timeframe"] = tf_data["timeframe"]
    if "timeframe_role" in tf_data:
        summary["timeframe_role"] = tf_data["timeframe_role"]

    return summary


def _select_canonical_current_price(
    timeframes: dict[str, dict[str, Any]],
) -> tuple[float | None, str | None]:
    """Select the canonical current price across timeframes.

    The canonical current price is the close of the most-recently closed
    bar across the available timeframes. For each timeframe we read:

    - ``source_audit.latest_closed_candle_time`` — the timestamp of the
      latest closed bar (used to rank freshness).
    - ``technical_context.close`` — that bar's close price (the value we
      return).

    Iteration order is ``("H1", "H4", "D1")`` and the comparison uses a
    strict ``>`` on the timestamp, so the *first* timeframe encountered
    with the current maximum timestamp keeps precedence. Because H1 is
    iterated first, H1 wins ties, then H4, then D1 — i.e. the most
    granular timeframe wins when timestamps are equal. Timeframes missing
    either the timestamp or the close are skipped.

    Args:
        timeframes: Mapping of timeframe name to its (compact or full)
            engine-output dict. Only the two keys above are read, so the
            compact summary produced by ``_summarize_structure_analysis``
            works identically to the raw engine output.

    Returns:
        ``(selected_close, selected_ts)`` or ``(None, None)`` when no
        timeframe provides both a timestamp and a close.
    """
    selected_close: float | None = None
    selected_ts: str | None = None

    for tf_name in ("H1", "H4", "D1"):
        tf = timeframes.get(tf_name)
        if not isinstance(tf, dict):
            continue
        source_audit = tf.get("source_audit")
        if not isinstance(source_audit, dict):
            continue
        ts = source_audit.get("latest_closed_candle_time")
        technical_context = tf.get("technical_context")
        if not isinstance(technical_context, dict):
            continue
        close = technical_context.get("close")

        if ts is None or close is None:
            continue

        # Strict ``>`` keeps the first-seen max (H1 wins ties because it
        # is iterated first).
        if selected_ts is None or ts > selected_ts:
            selected_ts = ts
            selected_close = close

    if selected_close is None or selected_ts is None:
        return (None, None)
    return (selected_close, selected_ts)


def _summarize_structure_analysis(
    structure_analysis: dict[str, Any],
) -> dict[str, Any]:
    """Build a compact version of structure analysis suitable for LLM prompts.

    The full engine output for D1+H4+H1 exceeds ~537K characters. This
    function extracts only the compact analytical fields and drops the
    massive raw data lists (swings, full event/level/liquidity lists).
    """
    summary: dict[str, Any] = {}

    # Confluence verdict (top-level, always small)
    if "confluence" in structure_analysis:
        summary["confluence"] = structure_analysis["confluence"]
    elif "timeframes" in structure_analysis:
        # Extract confluence from the first timeframe's decision context
        for tf_name in ("D1", "H4", "H1"):
            tf_data = structure_analysis.get(tf_name, {})
            if "confluence" in tf_data:
                summary["confluence"] = tf_data["confluence"]

    # Summarize each timeframe
    timeframes: dict[str, Any] = {}
    for tf_name in ("D1", "H4", "H1"):
        # Prefer the engine's multi-timeframe output structure
        tf_data = structure_analysis.get("timeframes", {}).get(tf_name) or structure_analysis.get(
            tf_name
        )
        if isinstance(tf_data, dict) and tf_data.get("market_structure"):
            timeframes[tf_name] = _summarize_timeframe(tf_data)

    if timeframes:
        summary["timeframes"] = timeframes
    else:
        # Fallback: include the raw dict but strip known-large keys
        raw = dict(structure_analysis)
        for key in list(raw):
            if isinstance(raw.get(key), dict):
                for large_key in _LARGE_STRUCTURE_KEYS:
                    raw[key].pop(large_key, None)
        summary["_fallback"] = raw

    return summary


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
    fatal_error: str | None
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

        if state.get("fatal_error"):
            return {}

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
            msg = f"Data fetch failed: {e}"
            logger.error(msg)
            return {"fatal_error": msg}

    def _analyze_structure(self, state: AgentState) -> dict[str, Any]:
        """Analyze market structure with candle-aligned caching.

        The multi-timeframe engine requires all three snapshots (D1, H4, H1)
        to run. Therefore we either return a complete cached result, or we
        fetch all three timeframes fresh — partial caching is not possible.
        """
        logger.info("Analyzing structure for %s", state["symbol"])

        if state.get("fatal_error"):
            return {}

        symbol = state["symbol"]

        try:
            broker_now = self.data_provider.get_broker_time()
        except Exception as e:
            msg = f"Structure analysis failed: cannot get broker time: {e}"
            logger.error(msg)
            return {"fatal_error": msg}

        supported_tfs = ("D1", "H4", "H1")

        try:
            # H1 is now cached alongside D1 and H4. The per-timeframe cache
            # files are written for all three timeframes. The decision engine
            # always gets fresh data for all 3 TFs.

            # --- Fetch all three timeframes fresh ---
            snapshots: dict[str, Any] = {}
            for timeframe in supported_tfs:
                bar_count = get_profile(timeframe).preferred_bars
                csv_data = self.data_provider.get_candles(
                    symbol,
                    timeframe,
                    bar_count,
                    broker_now=broker_now,
                )
                try:
                    snapshots[timeframe] = self._snapshot_builder.build(
                        csv_data,
                        symbol,
                        timeframe,
                        broker_now=broker_now,
                    )
                except Exception as e:
                    logger.warning(
                        "Snapshot build failed for %s %s: %s",
                        symbol,
                        timeframe,
                        e,
                    )
                    snapshots[timeframe] = csv_data

            # --- Run the multi-timeframe engine ---
            analysis_result = self.structure_analyzer.analyze(snapshots)

            # --- Build the legacy per-timeframe result dict ---
            result: dict[str, Any] = {}
            if isinstance(analysis_result, dict):
                for tf in supported_tfs:
                    if tf in analysis_result.get("timeframes", {}):
                        result[tf] = analysis_result["timeframes"][tf]

            # Also stash the full multi-timeframe result
            if isinstance(analysis_result, dict):
                result["_full_multi_timeframe"] = analysis_result

            # --- Write per-timeframe cache files (non-critical) ---
            for timeframe in ("D1", "H4", "H1"):
                if timeframe in snapshots and timeframe in result:
                    try:
                        save_analysis(timeframe, symbol, broker_now, result[timeframe])
                    except Exception:
                        logger.warning(
                            "Failed to cache %s analysis for %s",
                            timeframe,
                            symbol,
                        )

            return {"structure_analysis": result}
        except Exception as e:
            msg = f"Structure analysis failed: {e}"
            logger.error(msg)
            return {"fatal_error": msg}

    def _evaluate_calendar(self, state: AgentState) -> dict[str, Any]:
        """Evaluate calendar events."""
        logger.info("Evaluating calendar for %s", state["symbol"])

        if state.get("fatal_error"):
            return {}

        try:
            events = self.calendar_provider.fetch_events()
            return {"calendar_events": events}
        except Exception as e:
            msg = f"Calendar evaluation failed: {e}"
            logger.error(msg)
            return {"fatal_error": msg, "calendar_events": []}

    def _synthesize_context(self, state: AgentState) -> dict[str, Any]:
        """Synthesize market context."""
        logger.info("Synthesizing context for %s", state["symbol"])

        if state.get("fatal_error"):
            return {}

        try:
            raw_structure: dict[str, Any] = state.get("structure_analysis") or {}
            compact_structure = _summarize_structure_analysis(raw_structure)

            # Log size reduction for observability
            raw_size = len(str(raw_structure))
            compact_size = len(str(compact_structure))
            reduction = (1 - compact_size / raw_size) * 100 if raw_size else 0
            logger.info(
                "Structure analysis compacted: %d chars -> %d chars (%.0f%% reduction)",
                raw_size,
                compact_size,
                reduction,
            )

            # Canonical current price: close of the most-recently closed
            # bar across the available timeframes (H1 > H4 > D1 tie-break).
            current_price, current_price_time = _select_canonical_current_price(
                compact_structure.get("timeframes", {}) or {}
            )

            context = self.synthesizer.synthesize(
                structure_analysis=compact_structure,
                calendar_events=state.get("calendar_events", []),
                symbol=state["symbol"],
                current_price=current_price,
                current_price_time=current_price_time,
            )

            # If the LLM-returned summary omits the canonical price, stamp
            # it post-hoc so downstream nodes always have a price anchor.
            if context.current_price is None and current_price is not None:
                context.current_price = current_price
                context.current_price_time = current_price_time

            return {"market_context": context}
        except Exception as e:
            msg = f"Context synthesis failed: {e}"
            logger.error(msg)
            return {"fatal_error": msg}

    def _decide(self, state: AgentState) -> dict[str, Any]:
        """Make trading decision."""
        logger.info("Making decision for %s", state["symbol"])

        if state.get("fatal_error"):
            return {}

        try:
            context = state.get("market_context")
            if not context:
                return {"fatal_error": "No market context available — cannot decide"}

            feedback = state.get("review_feedback")
            attempts = state.get("review_attempts", 0) + 1

            decision = self.decider.decide(
                context=context,
                positions=state.get("current_positions", []),
                pending_orders=state.get("current_pending_orders", []),
                feedback=feedback if attempts > 1 else None,
                current_price=context.current_price,
            )
            return {"decision": decision, "review_attempts": attempts}
        except Exception as e:
            msg = f"Decision failed: {e}"
            logger.error(msg)
            return {"fatal_error": msg}

    def _review(self, state: AgentState) -> dict[str, Any]:
        """Review the decision."""
        logger.info("Reviewing decision for %s", state["symbol"])

        if state.get("fatal_error"):
            return {}

        try:
            decision = state.get("decision")
            context = state.get("market_context")
            calendar_events = state.get("calendar_events", [])

            if not decision or not context:
                return {"fatal_error": "Missing decision or context for review — cannot review"}

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
            msg = f"Review failed: {e}"
            logger.error(msg)
            return {"fatal_error": msg}

    def _review_to_decide(self, state: AgentState) -> str:
        """Conditional edge from review to decide or end."""
        if state.get("fatal_error"):
            return "end"
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
            fatal_error=None,
            final_output=None,
        )

        result: dict[str, Any] = self.graph.invoke(initial_state)
        logger.info("Analysis complete for %s", symbol)
        return result
