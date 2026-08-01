from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from config.settings import Settings
from src.analysis.candle_cache import (
    load_cached_analysis,
    save_analysis,
    should_run_analysis,
)
from src.analysis.market_structure_engine.config import get_profile
from src.analysis.market_structure_engine.errors import (
    InvalidTradeDirectionError,
    StructureSchemaError,
)
from src.analysis.market_structure_engine.execution_policy import (
    PolicySettings,
    evaluate_execution_policy,
)
from src.analysis.market_structure_engine.grading import grade_setup
from src.analysis.market_structure_engine.models import (
    DecisionAction,
    DeterministicSetupState,
    ExecutionPolicyState,
    ExecutionStatus,
    FinalDecisionState,
    ReviewStatus,
    RiskPolicyState,
    SetupGrade,
)
from src.analysis.market_structure_engine.risk_policy import build_risk_policy
from src.data.snapshot_builder import SnapshotBuilder
from src.decision.cost_tracker import CostLimitExceeded
from src.decision.enforcement import DeterministicEnforcementGate
from src.decision.models import DecisionOutput, MarketContextSummary, ReviewVerdict
from src.decision.output_assembler import FinalOutputAssembler
from src.decision.synthesizer_cache import (
    load_cached_synthesis,
    save_synthesis,
    should_run_synthesis,
)
from src.output.ohlc_cache import load_ohlc_cache, save_ohlc_cache
from src.output.ohlc_extractor import extract_ohlc_from_csv
from src.output.result_models import AnalysisResult, OHLCBar

logger = logging.getLogger(__name__)

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
    if events is not None and not isinstance(events, dict):
        logger.warning("Unexpected type for 'events' in timeframe data: %s", type(events).__name__)
        events = {}
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
    if levels is not None and not isinstance(levels, dict):
        logger.warning("Unexpected type for 'levels' in timeframe data: %s", type(levels).__name__)
        levels = {}
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
    if liquidity is not None and not isinstance(liquidity, dict):
        logger.warning(
            "Unexpected type for 'liquidity' in timeframe data: %s",
            type(liquidity).__name__,
        )
        liquidity = {}
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
    """State for the trading graph.

    Fields are grouped by their provenance within the pipeline:

    * **Market data** — positions, orders, prices, calendar events.
    * **Structure analysis** — per-timeframe engine output.
    * **Deterministic pipeline** — graded setup, risk policy, execution policy.
    * **LLM agents** — synthesised context, decision, review.
    * **Enforcement & output** — final decision state, assembled result.
    """

    # ── Market data ───────────────────────────────────────────────────
    broker_now: datetime | None
    calendar_events: list[dict[str, Any]] | None
    current_pending_orders: list[dict[str, Any]]
    current_positions: list[dict[str, Any]]
    symbol: str
    symbol_price: dict[str, Any] | None

    # ── Structure analysis (engine output) ────────────────────────────
    structure_analysis: dict[str, Any] | None

    # ── LLM agents (interpretive) ─────────────────────────────────────
    market_context: MarketContextSummary | None
    decision: DecisionOutput | None
    review: ReviewVerdict | None

    # ── Review loop ───────────────────────────────────────────────────
    review_attempts: int
    review_feedback: str | None

    # ── Deterministic pipeline (authoritative) ────────────────────────
    deterministic_setup: DeterministicSetupState | None
    risk_policy: RiskPolicyState | None
    execution_policy: ExecutionPolicyState | None

    # ── Enforcement & output ──────────────────────────────────────────
    final_decision: FinalDecisionState | None
    analysis_result: AnalysisResult | None

    # ── Error tracking ────────────────────────────────────────────────
    errors: list[str]
    fatal_error: str | None
    final_output: dict[str, Any] | None


def _has_high_impact_calendar_event(calendar_events: list[dict[str, Any]] | None) -> bool:
    """Check if any calendar event has a high impact level."""
    if not calendar_events:
        return False
    for event in calendar_events:
        impact = event.get("impact", "")
        if isinstance(impact, str) and impact.upper() == "HIGH":
            return True
    return False


def _deterministic_order_type(state: AgentState) -> str | None:
    """Return the canonical order type for LLM context, never an LLM value."""
    setup = state.get("deterministic_setup")
    return setup.entry_type.value if setup is not None and setup.entry_type is not None else None


class TradingGraph:
    """LangGraph orchestrator for trading analysis with multi-timeframe pipeline.

    The pipeline flow (per symbol):

    ``fetch_data`` → ``analyze_structure`` → ``evaluate_calendar`` →
    ``synthesize_context`` → ``grade_setup`` → ``build_risk_policy`` →
    ``evaluate_execution_policy`` → ``early_execution_routing`` →
    (``decide`` | deterministic NO_TRADE) → ``pre_review_decision_validation`` →
    ``review`` → (retry to ``decide`` | ``final_enforcement``) →
    ``assemble_output`` → END
    """

    def __init__(
        self,
        data_provider: Any,
        structure_analyzer: Any,
        calendar_provider: Any,
        synthesizer: Any,
        decider: Any,
        reviewer: Any,
        max_review_attempts: int | None = None,
    ) -> None:
        """Initialize trading graph with dependencies.

        Args:
            data_provider: DataSource implementation
            structure_analyzer: StructureAnalyzer implementation
            calendar_provider: CalendarProvider implementation
            synthesizer: SynthesizerAgent
            decider: DeciderAgent
            reviewer: ReviewerAgent
            max_review_attempts: Maximum review retry attempts (default from Settings)
        """
        self.data_provider = data_provider
        self.structure_analyzer = structure_analyzer
        self.calendar_provider = calendar_provider
        self.synthesizer = synthesizer
        self.decider = decider
        self.reviewer = reviewer
        self.max_review_attempts = (
            max_review_attempts
            if max_review_attempts is not None
            else Settings().max_review_attempts
        )
        self._settings = Settings()
        self._snapshot_builder = SnapshotBuilder()
        self._enforcement_gate = DeterministicEnforcementGate()
        self._output_assembler = FinalOutputAssembler()

        self.graph = self._build_graph()

    # ==================================================================
    # Graph construction
    # ==================================================================

    def _build_graph(self) -> CompiledStateGraph[AgentState, None, Any, Any]:
        """Build the LangGraph StateGraph with the multi-timeframe pipeline."""
        graph = StateGraph(AgentState)

        # ── Data pipeline ─────────────────────────────────────────────
        graph.add_node("fetch_data", self._fetch_data)
        graph.add_node("analyze_structure", self._analyze_structure)
        graph.add_node("evaluate_calendar", self._evaluate_calendar)

        # ── LLM agents ────────────────────────────────────────────────
        graph.add_node("synthesize_context", self._synthesize_context)
        graph.add_node("decide", self._decide)
        graph.add_node("review", self._review)

        # ── Deterministic pipeline ────────────────────────────────────
        graph.add_node("grade_setup", self._grade_setup)
        graph.add_node("build_risk_policy", self._build_risk_policy)
        graph.add_node("evaluate_execution_policy", self._evaluate_execution_policy)
        graph.add_node("early_execution_routing", self._early_execution_routing)

        # ── Validation & enforcement ──────────────────────────────────
        graph.add_node("pre_review_decision_validation", self._pre_review_decision_validation)
        graph.add_node("final_enforcement", self._final_enforcement)
        graph.add_node("assemble_output", self._assemble_output)

        # ── Entry point ───────────────────────────────────────────────
        graph.set_entry_point("fetch_data")

        # ── Sequential data pipeline ──────────────────────────────────
        graph.add_edge("fetch_data", "analyze_structure")
        graph.add_edge("analyze_structure", "evaluate_calendar")
        graph.add_edge("evaluate_calendar", "synthesize_context")

        # ── Deterministic pipeline (after LLM synthesis) ──────────────
        graph.add_edge("synthesize_context", "grade_setup")
        graph.add_edge("grade_setup", "build_risk_policy")
        graph.add_edge("build_risk_policy", "evaluate_execution_policy")
        graph.add_edge("evaluate_execution_policy", "early_execution_routing")

        # ── Early execution routing ───────────────────────────────────
        # NON_EXECUTABLE / BLOCKED_BY_DATA_QUALITY → skip LLM
        # All other statuses → proceed to LLM decide
        graph.add_conditional_edges(
            "early_execution_routing",
            self._early_execution_router,
            {
                "deterministic_continue": "pre_review_decision_validation",
                "llm_decide": "decide",
            },
        )

        # ── Decide → pre-review validation → review ──────────────────
        graph.add_edge("decide", "pre_review_decision_validation")
        graph.add_edge("pre_review_decision_validation", "review")

        # ── Review routing ────────────────────────────────────────────
        # approved / NOT_REQUIRED / max attempts → enforcement
        # rejected with attempts remaining → retry decide
        graph.add_conditional_edges(
            "review",
            self._review_router,
            {
                "continue_enforcement": "final_enforcement",
                "retry_decide": "decide",
            },
        )

        # ── Final enforcement → output → END ──────────────────────────
        graph.add_edge("final_enforcement", "assemble_output")
        graph.add_edge("assemble_output", END)

        return graph.compile()

    # ==================================================================
    # Data-pipeline nodes
    # ==================================================================

    def _fetch_data(self, state: AgentState) -> dict[str, Any]:
        """Fetch market data from MT5."""
        logger.info("Fetching data for %s", state["symbol"])

        if state.get("fatal_error"):
            return {}

        symbol = state["symbol"]

        try:
            current_positions = self.data_provider.get_positions(symbol)
            current_pending_orders = self.data_provider.get_pending_orders(symbol)
            symbol_price_data = self.data_provider.get_symbol_price(symbol)

            return {
                "current_positions": current_positions,
                "current_pending_orders": current_pending_orders,
                "symbol_price": symbol_price_data,
            }
        except CostLimitExceeded:
            raise
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
        except CostLimitExceeded:
            raise
        except Exception as e:
            msg = f"Structure analysis failed: cannot get broker time: {e}"
            logger.error(msg)
            return {"fatal_error": msg}

        supported_tfs = ("D1", "H4", "H1")

        try:
            # --- Try loading from cache first ---
            # All three timeframes must be cached to use the cache, because
            # the multi-timeframe engine needs all three snapshots and we
            # avoid partial re-runs. If any one timeframe is missing we
            # re-fetch everything.
            cached: dict[str, Any] = {}
            all_cached = True
            for timeframe in supported_tfs:
                if should_run_analysis(timeframe, symbol, broker_now):
                    # should_run_analysis returns True when cache is MISSING
                    all_cached = False
                    break
                cached_tf = load_cached_analysis(timeframe, symbol, broker_now)
                if cached_tf is None:
                    all_cached = False
                    break
                logger.info("Loaded %s analysis from cache for %s", timeframe, symbol)
                cached[timeframe] = cached_tf

            if all_cached:
                logger.info("Using cached analysis for %s (D1/H4/H1 all present)", symbol)
                mtf_result = load_cached_analysis("MTF", symbol, broker_now)
                if mtf_result is None:
                    logger.info("MTF cache missing for %s — falling back to fresh fetch", symbol)
                    all_cached = False  # fall through to fresh-fetch path
                else:
                    logger.info("Loaded MTF analysis from cache for %s", symbol)
                    # Wrap cached per-timeframe data under 'timeframes' key
                    result: dict[str, Any] = {"timeframes": cached}
                    result["_full_multi_timeframe"] = mtf_result
                    result["confluence"] = mtf_result.get("confluence", {})

                    # Load OHLC bars from dedicated cache for each timeframe
                    ohlc_bars_cache: dict[str, list[OHLCBar]] = {}
                    for tf in supported_tfs:
                        cached_bars = load_ohlc_cache(tf, symbol, broker_now)
                        if cached_bars is not None:
                            ohlc_bars_cache[tf] = cached_bars
                    if ohlc_bars_cache:
                        result["_ohlc_bars"] = ohlc_bars_cache

                    return {"structure_analysis": result, "broker_now": broker_now}

            # --- Cache miss: fetch all three timeframes fresh ---
            logger.info("Cache miss for %s — fetching fresh data", symbol)
            snapshots: dict[str, Any] = {}
            ohlc_bars_all: dict[str, list[OHLCBar]] = {}
            for timeframe in supported_tfs:
                bar_count = get_profile(timeframe).preferred_bars
                logger.info("Fetching %s candles for %s from broker", timeframe, symbol)
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
                    # Save OHLC bars to dedicated cache after successful snapshot build
                    try:
                        ohlc_bars = extract_ohlc_from_csv(csv_data)
                        save_ohlc_cache(timeframe, symbol, broker_now, ohlc_bars)
                        ohlc_bars_all[timeframe] = ohlc_bars
                    except Exception as e:
                        logger.warning(
                            "Failed to cache OHLC bars for %s %s: %s",
                            symbol,
                            timeframe,
                            e,
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
            logger.info("Running structure analysis for %s (D1/H4/H1)", symbol)
            analysis_result = self.structure_analyzer.analyze(snapshots)

            # --- Build the legacy per-timeframe result dict ---
            result = {}
            if isinstance(analysis_result, dict):
                # Nest per-timeframe data under a 'timeframes' key so that
                # downstream nodes (e.g. _grade_setup) can validate the schema.
                timeframes_dict: dict[str, Any] = {}
                for tf in supported_tfs:
                    if tf in analysis_result.get("timeframes", {}):
                        timeframes_dict[tf] = analysis_result["timeframes"][tf]
                if timeframes_dict:
                    result["timeframes"] = timeframes_dict

            # Stash the full multi-timeframe result + top-level confluence
            if isinstance(analysis_result, dict):
                result["_full_multi_timeframe"] = analysis_result
                result["confluence"] = analysis_result.get("confluence", {})

            # --- Write per-timeframe cache files (non-critical) ---
            timeframes_in_result = result.get("timeframes", {})
            for timeframe in ("D1", "H4", "H1"):
                if timeframe in snapshots and timeframe in timeframes_in_result:
                    try:
                        tf_data = timeframes_in_result[timeframe]
                        save_analysis(timeframe, symbol, broker_now, tf_data)
                    except Exception:
                        logger.warning(
                            "Failed to cache %s analysis for %s",
                            timeframe,
                            symbol,
                        )

            # --- Save full MTF result for correct confluence on cache-hit ---
            if isinstance(analysis_result, dict):
                try:
                    save_analysis("MTF", symbol, broker_now, analysis_result)
                except Exception:
                    logger.warning("Failed to cache MTF analysis for %s", symbol)

            # Stash OHLC bars accumulated during the fresh-fetch loop
            if ohlc_bars_all:
                result["_ohlc_bars"] = ohlc_bars_all

            return {"structure_analysis": result, "broker_now": broker_now}
        except CostLimitExceeded:
            raise
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
        except CostLimitExceeded:
            raise
        except Exception as e:
            msg = f"Calendar evaluation failed: {e}"
            logger.error(msg)
            return {"fatal_error": msg, "calendar_events": []}

    # ==================================================================
    # LLM-agent nodes
    # ==================================================================

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

            # --- Check synthesizer cache before calling LLM ---
            # Reuse broker_now from state (set by _analyze_structure) to avoid
            # a redundant get_broker_time() call.
            broker_now = state.get("broker_now")
            if broker_now is None:
                broker_now = self.data_provider.get_broker_time()
            symbol = state["symbol"]

            if not should_run_synthesis(symbol, broker_now):
                cached = load_cached_synthesis(symbol, broker_now)
                if cached is not None:
                    logger.info("Using cached synthesis for %s", symbol)
                    # Stamp the canonical price on cached summaries too
                    if cached.current_price is None and current_price is not None:
                        cached.current_price = current_price
                        cached.current_price_time = current_price_time
                    return {"market_context": cached}

            # --- Cache miss (or disabled): call LLM ---
            context = self.synthesizer.synthesize(
                structure_analysis=compact_structure,
                calendar_events=state.get("calendar_events", []),
                symbol=symbol,
                current_price=current_price,
                current_price_time=current_price_time,
            )

            # If the LLM-returned summary omits the canonical price, stamp
            # it post-hoc so downstream nodes always have a price anchor.
            if context.current_price is None and current_price is not None:
                context.current_price = current_price
                context.current_price_time = current_price_time

            # Write cache (best-effort, non-fatal)
            save_synthesis(symbol, broker_now, context)

            return {"market_context": context}
        except CostLimitExceeded:
            raise
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
            attempts = state.get("review_attempts", 0)

            decision = self.decider.decide(
                context=context,
                positions=state.get("current_positions", []),
                pending_orders=state.get("current_pending_orders", []),
                feedback=feedback if attempts > 0 else None,
                current_price=context.current_price,
                order_type=_deterministic_order_type(state),
            )
            return {"decision": decision, "review_attempts": attempts}
        except CostLimitExceeded:
            raise
        except Exception as e:
            msg = f"Decision failed: {e}"
            logger.error(msg)
            return {"fatal_error": msg}

    def _review(self, state: AgentState) -> dict[str, Any]:
        """Review the decision.

        If a review is already present in state (set by the deterministic
        early-exit path), skip calling the LLM reviewer and pass through.
        """
        logger.info("Reviewing decision for %s", state["symbol"])

        if state.get("fatal_error"):
            return {}

        # ── Deterministic early exit: review already populated ─────────
        if state.get("review") is not None:
            logger.info("Review already present — skipping LLM review")
            return {
                "review_attempts": state.get("review_attempts", 0) + 1,
            }

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
                order_type=_deterministic_order_type(state),
            )

            feedback = None
            if not verdict.approved:
                feedback = f"Concerns: {verdict.concerns}\n"
                feedback += f"Suggestions: {verdict.suggested_improvements}"

            return {
                "review": verdict,
                "review_feedback": feedback,
                "review_attempts": state.get("review_attempts", 0) + 1,
            }
        except CostLimitExceeded:
            raise
        except Exception as e:
            msg = f"Review failed: {e}"
            logger.error(msg)
            return {"fatal_error": msg}

    # ==================================================================
    # Deterministic pipeline nodes
    # ==================================================================

    def _grade_setup(self, state: AgentState) -> dict[str, Any]:
        """Grade the setup using the deterministic grading engine.

        Extracts D1/H4/H1 analysis contexts from the structure analysis
        and runs the grading algorithm that determines setup grade,
        lifecycle status, geometry status, and trade direction.

        Raises ``StructureSchemaError`` (caught below → fatal error) when
        the structure analysis is missing or has an empty ``timeframes``
        mapping.
        """
        logger.info("Grading setup for %s", state["symbol"])

        if state.get("fatal_error"):
            return {}

        structure = state.get("structure_analysis") or {}

        try:
            # ── Schema validation ──────────────────────────────────────
            timeframes = structure.get("timeframes")

            if not isinstance(timeframes, dict) or not timeframes:
                raise StructureSchemaError(
                    "Structure analysis must contain a non-empty 'timeframes' mapping"
                )

            d1_engine = timeframes.get("D1", {})
            h4_engine = timeframes.get("H4", {})
            h1_engine = timeframes.get("H1", {})

            # Each timeframe's engine output contains an ``analysis_context``
            # dict that the grading engine expects.
            d1_context = d1_engine.get("analysis_context", d1_engine)
            h4_context = h4_engine.get("analysis_context", h4_engine)
            h1_context = h1_engine.get("analysis_context", h1_engine)

            # Entry planning needs the same canonical price exposed to the
            # decision layer. Keep it outside the LLM output and inject it
            # into the deterministic H1 setup context only.
            canonical_price = None
            market_context = state.get("market_context")
            if market_context is not None and isinstance(market_context.current_price, int | float):
                canonical_price = market_context.current_price
            if canonical_price is None:
                price = state.get("symbol_price") or {}
                bid = price.get("bid")
                ask = price.get("ask")
                if isinstance(bid, int | float) and isinstance(ask, int | float):
                    canonical_price = (bid + ask) / 2
                elif isinstance(bid, int | float):
                    canonical_price = bid
                elif isinstance(ask, int | float):
                    canonical_price = ask
            if canonical_price is not None:
                h1_context = dict(h1_context)
                h1_setup = dict(h1_context.get("setup_context") or h1_context)
                h1_setup["current_price"] = canonical_price
                if "setup_context" in h1_context:
                    h1_context["setup_context"] = h1_setup
                else:
                    h1_context = h1_setup

            setup = grade_setup(
                h1_context=h1_context,
                h4_context=h4_context,
                d1_context=d1_context,
            )
            logger.info(
                "Setup graded: classification=%s grade=%s direction=%s",
                setup.setup_classification_status.value,
                setup.setup_grade.value if setup.setup_grade else "None",
                setup.trade_direction.value,
            )
            return {"deterministic_setup": setup}
        except InvalidTradeDirectionError as exc:
            # Defensive catch: if InvalidTradeDirectionError escapes from
            # entry_calculator unexpectedly (it should be caught internally),
            # treat it as an invariant violation → fatal.
            logger.error(
                "Unexpected invalid trade direction for %s: %s",
                state["symbol"],
                exc,
            )
            return {
                "fatal_error": str(exc),
                "fatal_error_code": "INTERNAL_INVALID_TRADE_DIRECTION",
            }
        except StructureSchemaError as exc:
            logger.exception("Invalid structure-analysis schema for %s", state["symbol"])
            return {
                "fatal_error": str(exc),
                "fatal_error_code": "INVALID_STRUCTURE_SCHEMA",
            }
        except Exception as e:
            msg = f"Setup grading failed: {e}"
            logger.error(msg)
            return {"fatal_error": msg}

    def _build_risk_policy(self, state: AgentState) -> dict[str, Any]:
        """Build the risk policy from the deterministic setup grade.

        Maps the setup grade to its grade-specific risk multiplier and
        minimum reward-to-risk threshold.
        """
        logger.info("Building risk policy for %s", state["symbol"])

        if state.get("fatal_error"):
            return {}

        setup = state.get("deterministic_setup")
        if not setup:
            return {"fatal_error": "No deterministic setup available — cannot build risk policy"}

        # Use a default base risk percentage when none is configured.
        # This can be moved to Settings in a future iteration.
        base_risk_percentage: float = 1.0

        try:
            risk = build_risk_policy(
                setup_grade=setup.setup_grade or SetupGrade.AA,
                base_risk_percentage=base_risk_percentage,
                estimated_reward_risk=setup.estimated_reward_risk,
            )
            logger.info(
                "Risk policy: multiplier=%s min_rr=%s final_risk=%.2f%%",
                risk.grade_risk_multiplier,
                risk.minimum_reward_risk,
                risk.final_risk_percentage,
            )
            return {"risk_policy": risk}
        except Exception as e:
            msg = f"Risk policy build failed: {e}"
            logger.error(msg)
            return {"fatal_error": msg}

    def _evaluate_execution_policy(self, state: AgentState) -> dict[str, Any]:
        """Evaluate execution policy and detect blockers.

        Consumes the classified setup and risk policy, applies execution
        rules (policy, calendar, risk/reward, trigger, data quality,
        geometry), and populates the execution policy state with any
        active blockers.
        """
        logger.info("Evaluating execution policy for %s", state["symbol"])

        if state.get("fatal_error"):
            return {}

        setup = state.get("deterministic_setup")
        risk = state.get("risk_policy")

        if not setup or not risk:
            return {
                "fatal_error": ("Missing setup or risk policy — cannot evaluate execution policy")
            }

        has_high_impact = _has_high_impact_calendar_event(state.get("calendar_events", []))

        try:
            policy = evaluate_execution_policy(
                setup=setup,
                risk_policy=risk,
                has_high_impact_event=has_high_impact,
                execution_mode=self._settings.execution_mode,
                settings=PolicySettings(
                    countertrend_enabled=self._settings.enable_countertrend,
                ),
            )
            logger.info(
                "Execution policy: status=%s blockers=%d",
                policy.pre_review_execution_status.value,
                len(policy.execution_blockers),
            )
            return {"execution_policy": policy}
        except Exception as e:
            msg = f"Execution policy evaluation failed: {e}"
            logger.error(msg)
            return {"fatal_error": msg}

    # ==================================================================
    # Routing & validation nodes
    # ==================================================================

    def _early_execution_routing(self, state: AgentState) -> dict[str, Any]:
        """Deterministic early execution routing.

        When the execution policy status is NON_EXECUTABLE or
        BLOCKED_BY_DATA_QUALITY, create a deterministic
        DecisionOutput(NO_TRADE) and ReviewVerdict(NOT_REQUIRED)
        so the LLM agents are bypassed entirely.

        For all other statuses, return empty (the LLM decide node
        handles the decision).
        """
        if state.get("fatal_error"):
            return {}

        execution_policy = state.get("execution_policy")
        if not execution_policy:
            return {"fatal_error": "No execution policy available for routing"}

        status = execution_policy.pre_review_execution_status

        if status in (ExecutionStatus.NON_EXECUTABLE, ExecutionStatus.BLOCKED_BY_DATA_QUALITY):
            logger.info(
                "Early execution routing: %s — creating deterministic NO_TRADE",
                status.value,
            )
            decision = DecisionOutput(
                symbol=state["symbol"],
                action=DecisionAction.NO_TRADE,
                reasoning=f"Early-exit: execution status is {status.value}",
            )
            review = ReviewVerdict(
                status=ReviewStatus.NOT_REQUIRED,
                reasoning="Deterministic early exit — review not required",
                concerns=(),
                suggested_improvements=None,
            )
            return {
                "decision": decision,
                "review": review,
            }

        return {}

    def _early_execution_router(self, state: AgentState) -> str:
        """Route after early execution routing.

        Returns:
            - ``"deterministic_continue"`` when execution status is
              NON_EXECUTABLE or BLOCKED_BY_DATA_QUALITY (bypass LLM).
            - ``"llm_decide"`` for all other statuses (proceed to LLM).
        """
        execution_policy = state.get("execution_policy")
        if not execution_policy:
            return "deterministic_continue"

        status = execution_policy.pre_review_execution_status
        if status in (ExecutionStatus.NON_EXECUTABLE, ExecutionStatus.BLOCKED_BY_DATA_QUALITY):
            return "deterministic_continue"
        return "llm_decide"

    def _pre_review_decision_validation(self, state: AgentState) -> dict[str, Any]:
        """Validate the decision before it reaches the reviewer.

        Ensures the decision is present and the symbol matches.
        Logs a warning if the decision action is NO_TRADE with no
        deterministic early-exit reason — this is advisory only.
        """
        logger.info("Pre-review validation for %s", state["symbol"])

        if state.get("fatal_error"):
            return {}

        decision = state.get("decision")
        if not decision:
            return {"fatal_error": "No decision present for pre-review validation"}

        if decision.symbol != state["symbol"]:
            logger.warning(
                "Decision symbol %s does not match state symbol %s",
                decision.symbol,
                state["symbol"],
            )

        return {}

    def _review_router(self, state: AgentState) -> str:
        """Route after the review node.

        - ``"continue_enforcement"`` when review is approved / NOT_REQUIRED
          / max attempts exceeded / fatal error.
        - ``"retry_decide"`` when review is rejected/REVISION_REQUIRED and
          attempts remain.
        """
        if state.get("fatal_error"):
            return "continue_enforcement"

        review = state.get("review")
        attempts = state.get("review_attempts", 0)

        # Deterministic early exit — review not required
        if review is not None and review.status == ReviewStatus.NOT_REQUIRED:
            return "continue_enforcement"

        # Approved → proceed to enforcement
        if review is not None and review.approved:
            return "continue_enforcement"

        # Rejected/REVISION_REQUIRED with attempts remaining → retry
        if attempts <= self.max_review_attempts:
            return "retry_decide"

        # Max attempts exceeded → proceed to enforcement with current result
        return "continue_enforcement"

    # ==================================================================
    # Enforcement & output nodes
    # ==================================================================

    def _final_enforcement(self, state: AgentState) -> dict[str, Any]:
        """Run the deterministic enforcement gate.

        The gate verifies that every executable action satisfies
        deterministic invariants before it reaches the output stage.
        """
        logger.info("Running enforcement gate for %s", state["symbol"])

        if state.get("fatal_error"):
            return {}

        setup = state.get("deterministic_setup")
        policy = state.get("execution_policy")
        risk = state.get("risk_policy")
        decision = state.get("decision")
        review = state.get("review")

        # If any required state is missing, this is a fatal error.
        # The enforcement gate requires all five inputs.
        missing: list[str] = []
        if setup is None:
            missing.append("deterministic_setup")
        if policy is None:
            missing.append("execution_policy")
        if risk is None:
            missing.append("risk_policy")
        if decision is None:
            missing.append("decision")
        if review is None:
            missing.append("review")

        if missing:
            # If everything is missing due to a fatal_error earlier in
            # the pipeline, create a minimal fallback state.
            if state.get("fatal_error"):
                return {}

            msg = f"Enforcement gate missing required state: {', '.join(missing)}"
            logger.error(msg)
            return {"fatal_error": msg}

        # At this point all five required states have been validated as
        # present (the check above returned early if any were missing).
        # Assert so mypy is satisfied about the types.
        assert setup is not None and policy is not None and risk is not None
        assert decision is not None and review is not None

        try:
            final_state = self._enforcement_gate.enforce(
                setup=setup,
                policy=policy,
                risk=risk,
                decision=decision,
                review=review,
                settings=self._settings,
            )
            logger.info(
                "Enforcement: final_action=%s execution_status=%s violations=%d",
                final_state.final_action.value,
                final_state.final_execution_status.value,
                len(final_state.enforcement_violations),
            )
            return {"final_decision": final_state}
        except Exception as e:
            msg = f"Enforcement gate failed: {e}"
            logger.error(msg)
            return {"fatal_error": msg}

    def _assemble_output(self, state: AgentState) -> dict[str, Any]:
        """Assemble the final AnalysisResult from all pipeline states."""
        logger.info("Assembling output for %s", state["symbol"])

        # Collect all required pipeline states
        setup = state.get("deterministic_setup")
        policy = state.get("execution_policy")
        risk = state.get("risk_policy")
        decision = state.get("decision")
        review = state.get("review")
        enforcement = state.get("final_decision")

        if not enforcement:
            # If enforcement was never reached (e.g. fatal_error earlier),
            # we cannot produce a meaningful result.
            fatal = state.get("fatal_error", "Unknown error")
            logger.error(
                "Cannot assemble output for %s: no final decision (fatal: %s)",
                state["symbol"],
                fatal,
            )
            return {
                "final_output": {
                    "symbol": state["symbol"],
                    "status": "error",
                    "fatal_error": fatal,
                }
            }

        # Use stub models when deterministic pipeline states are missing
        # (e.g. when fatal_error occurred before grading). The assembler
        # tolerates None for optional fields on these models.
        if setup is None:
            setup = DeterministicSetupState()
        if policy is None:
            policy = ExecutionPolicyState()
        if risk is None:
            risk = RiskPolicyState()
        if decision is None:
            decision = DecisionOutput(
                symbol=state["symbol"],
                action=DecisionAction.NO_TRADE,
                reasoning="Pipeline error — no decision available",
            )
        if review is None:
            review = ReviewVerdict(
                status=ReviewStatus.REVIEW_UNAVAILABLE,
                reasoning="Pipeline error — no review available",
            )

        try:
            result = self._output_assembler.assemble(
                setup=setup,
                policy=policy,
                risk=risk,
                decision=decision,
                review=review,
                enforcement=enforcement,
            )

            # Override metadata fields
            result.symbol = state["symbol"]
            result.run_id = f"{state['symbol']}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            now = datetime.now()
            result.started_at = now
            result.completed_at = now
            result.status = "error" if state.get("fatal_error") else result.status

            # Carry forward errors
            errors = state.get("errors", [])
            if errors:
                result.errors = errors
            if state.get("fatal_error"):
                result.fatal_error = state["fatal_error"]

            return {
                "analysis_result": result,
                "final_output": result.model_dump(mode="json"),
            }
        except Exception as e:
            msg = f"Output assembly failed: {e}"
            logger.error(msg)
            return {"fatal_error": msg}

    # ==================================================================
    # Public API
    # ==================================================================

    def run(self, symbol: str) -> dict[str, Any]:
        """Run the trading graph for a symbol.

        Args:
            symbol: Trading symbol to analyze

        Returns:
            Final analysis result
        """
        logger.info("Starting analysis for %s", symbol)

        initial_state = AgentState(
            # Market data
            broker_now=None,
            calendar_events=None,
            current_pending_orders=[],
            current_positions=[],
            symbol=symbol,
            symbol_price=None,
            # Structure analysis
            structure_analysis=None,
            # LLM agents
            market_context=None,
            decision=None,
            review=None,
            # Review loop
            review_attempts=0,
            review_feedback=None,
            # Deterministic pipeline
            deterministic_setup=None,
            risk_policy=None,
            execution_policy=None,
            # Enforcement & output
            final_decision=None,
            analysis_result=None,
            # Error tracking
            errors=[],
            fatal_error=None,
            final_output=None,
        )

        result: dict[str, Any] = self.graph.invoke(initial_state)

        # Log cumulative LLM cost if a cost tracker is available on any agent
        if hasattr(self.synthesizer, "cost_tracker") and self.synthesizer.cost_tracker is not None:
            ct = self.synthesizer.cost_tracker
            if ct.call_count > 0:
                logger.info(
                    "Total LLM cost for %s: $%.4f across %d calls",
                    symbol,
                    ct.total_cost,
                    ct.call_count,
                )

        logger.info("Analysis complete for %s", symbol)
        return result
