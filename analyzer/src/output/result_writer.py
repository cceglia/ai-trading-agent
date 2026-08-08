from __future__ import annotations

import json
import logging
import os
import tempfile
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from src.output.result_models import (
    AnalysisEnvelope,
    AnalysisResult,
    DeterministicFacts,
    EntryPlan,
    OHLCBar,
    OHLCData,
    PolicyFacts,
    RRInfo,
    SynthesisBlock,
    SynthesisStatusV2,
)

logger = logging.getLogger(__name__)

# Public history in the v2 facts contract is bounded (NFR-003).
_EVENT_LIMIT = 50


class ResultWriterContractError(Exception):
    """Raised when ResultWriter receives an invalid or incomplete result."""


def _compact_timeframe_facts(tf_data: dict[str, Any]) -> dict[str, Any]:
    """Extract compact, bounded facts for a single timeframe engine output.

    The raw engine output contains large lists (swings, full event/level/
    liquidity lists); only the small analytical fields and bounded history
    are persisted so the v2 contract stays compact (NFR-003).
    """
    summary: dict[str, Any] = {}

    for key in (
        "source_audit",
        "technical_context",
        "candles",
        "market_structure",
        "scoring",
        "timeframe",
        "timeframe_role",
        "analysis_context",
    ):
        if key in tf_data:
            summary[key] = tf_data[key]

    events = tf_data.get("events")
    if isinstance(events, dict):
        compact_events: dict[str, Any] = {}
        for key in (
            "latest_material_event",
            "latest_primary_event",
            "latest_internal_event",
            "failed_bos_count",
        ):
            if key in events:
                compact_events[key] = events[key]
        for key in ("event_history", "failed_breakouts"):
            value = events.get(key)
            if isinstance(value, list):
                compact_events[key] = value[-_EVENT_LIMIT:]
        if compact_events:
            summary["events"] = compact_events

    levels = tf_data.get("levels")
    if isinstance(levels, dict):
        compact_levels: dict[str, Any] = {}
        for key in (
            "nearest_support",
            "nearest_resistance",
            "nearest_support_distance_atr",
            "nearest_resistance_distance_atr",
            "nearest_eligible_support",
            "nearest_eligible_resistance",
            "invalidation_blocker",
        ):
            if key in levels:
                compact_levels[key] = levels[key]
        if compact_levels:
            summary["levels"] = compact_levels

    liquidity = tf_data.get("liquidity")
    if isinstance(liquidity, dict):
        compact_liquidity: dict[str, Any] = {}
        for key in (
            "current_state",
            "latest_event",
            "nearest_buy_side",
            "nearest_sell_side",
            "dominant_draw",
        ):
            if key in liquidity:
                compact_liquidity[key] = liquidity[key]
        history = liquidity.get("event_history")
        if isinstance(history, list):
            compact_liquidity["event_history"] = history[-_EVENT_LIMIT:]
        if compact_liquidity:
            summary["liquidity"] = compact_liquidity

    return summary


def _resolve_action(action: str | None) -> str:
    """Map a stored action to the canonical v2 decision action (DEC-002).

    ``wait_for_setup`` is removed from the canonical domain and collapses to
    ``no_trade``; any other non-canonical value is a contract error.
    """
    if action is None or action == "no_trade":
        return "no_trade"
    if action == "wait_for_setup":
        return "no_trade"
    if action in ("buy_setup", "sell_setup"):
        return action
    raise ResultWriterContractError(f"decision action {action!r} is not a canonical v2 action")


class ResultWriter:
    """Writes schema-v2 analysis envelopes to JSON files in the data tree."""

    def __init__(self, base_dir: str | Path | None = None) -> None:
        if base_dir is None:
            from config.settings import Settings

            base_dir = Settings().resolved_analysis_cache_dir
        self.base_dir = Path(base_dir)

    def write(
        self,
        symbol: str,
        result: dict[str, Any],
        ohlc: dict[str, list[OHLCBar]],
        broker_now: datetime,
    ) -> Path | None:
        """Write a success/degraded/partial schema-v2 envelope to disk.

        Fatal pipeline failures are deliberately not persisted (FR-031): they
        do not contain a usable analysis result.

        Returns the written file path, or ``None`` for a fatal result.

        Args:
            symbol: Trading symbol (e.g., "XAUUSD")
            result: Pipeline output dict from TradingGraph.run()
            ohlc: Dict of timeframe -> list[OHLCBar]
            broker_now: Broker local time (used for path construction)

        Returns:
            Path to the written file, or ``None`` when a fatal result is skipped.
        """
        fatal_error = result.get("fatal_error")
        if fatal_error is not None:
            logger.warning(
                "Skipping persistence of failed analysis for %s: %s",
                symbol,
                fatal_error,
            )
            return None

        errors = result.get("errors", [])

        flat = self._resolve_analysis_result(symbol, result, errors, broker_now, ohlc)

        # The orchestrator (graph.py) is authoritative for status: it sets
        # "success", "partial", or "degraded" from validation and synthesis
        # outcome. An invalid deterministic result always persists as partial
        # (INV-011 / FR-023).
        if flat.validation_status == "INVALID":
            status = "partial"
        else:
            status = flat.status or ("partial" if errors else "success")

        try:
            envelope = self._build_envelope(symbol, result, flat, status, broker_now, ohlc)
        except ResultWriterContractError:
            raise
        except (ValidationError, TypeError, ValueError) as exc:
            raise ResultWriterContractError(
                "result does not satisfy the schema-v2 AnalysisEnvelope contract"
            ) from exc

        path = self._build_path(symbol, broker_now)
        content = json.dumps(envelope.model_dump(mode="json", by_alias=False), indent=2) + "\n"
        try:
            self._write_atomic(path, content)
        except OSError as exc:
            logger.error("Failed to persist v2 result for %s: %s", symbol, exc)
            raise ResultWriterContractError(f"failed to persist v2 result for {symbol}") from exc

        logger.info(
            "Wrote analysis result for %s (run_id=%s schema_version=%s validation_status=%s "
            "setup_status=%s action=%s synthesis_status=%s execution_status=%s error_codes=%s) "
            "to %s",
            symbol,
            envelope.run_id,
            envelope.schema_version,
            envelope.deterministic_facts.validation_status.value,
            envelope.deterministic_facts.setup_status.value,
            envelope.decision.action.value,
            envelope.synthesis.status.value,
            envelope.deterministic_facts.policy.execution_status,
            ",".join(self._bounded_error_codes(envelope)) or "-",
            path,
        )
        return path

    @staticmethod
    def _bounded_error_codes(envelope: AnalysisEnvelope) -> list[str]:
        """Collect stable, bounded error codes for the completion log.

        Combines policy reason codes, the synthesis error code, and validation
        errors (all machine-safe strings already present in the envelope),
        deduplicated and capped so the diagnostic line stays bounded (NFR-003).
        """
        codes: list[str] = []
        facts = envelope.deterministic_facts
        for code in facts.policy.reason_codes:
            if code and code not in codes:
                codes.append(str(code))
        synthesis_error = envelope.synthesis.error
        if synthesis_error and synthesis_error not in codes:
            codes.append(synthesis_error)
        for err in facts.validation_errors:
            if err and err not in codes:
                codes.append(str(err)[:120])
        return codes[:10]

    # ------------------------------------------------------------------
    # Envelope construction
    # ------------------------------------------------------------------

    def _resolve_analysis_result(
        self,
        symbol: str,
        result: dict[str, Any],
        errors: list[str],
        broker_now: datetime,
        ohlc: dict[str, list[OHLCBar]],
    ) -> AnalysisResult:
        """Validate and return the flat internal AnalysisResult for a run."""
        analysis_result_obj = result.get("analysis_result")
        if analysis_result_obj is not None:
            try:
                if isinstance(analysis_result_obj, AnalysisResult):
                    return analysis_result_obj
                if isinstance(analysis_result_obj, Mapping):
                    return AnalysisResult.model_validate(analysis_result_obj)
                return AnalysisResult.model_validate(analysis_result_obj, from_attributes=True)
            except (ValidationError, TypeError, ValueError) as exc:
                raise ResultWriterContractError(
                    "analysis_result does not satisfy the AnalysisResult contract"
                ) from exc

        # No analysis_result available (partial fallback path): derive an
        # empty envelope; successful results must contain deterministic facts.
        if not errors:
            raise ResultWriterContractError(
                "AnalysisResult is required to write deterministic trade levels"
            )
        ohlc_data = OHLCData(
            D1=ohlc.get("D1", []),
            H4=ohlc.get("H4", []),
            H1=ohlc.get("H1", []),
        )
        run_id = broker_now.strftime("%Y-%m-%dT%H:%M:%S")
        return AnalysisResult(
            symbol=symbol,
            run_id=run_id,
            started_at=broker_now,
            completed_at=broker_now,
            status="partial",
            errors=errors,
            fatal_error=result.get("fatal_error"),
            market_context=result.get("market_context"),
            decision=result.get("decision"),
            ohlc=ohlc_data,
        )

    def _build_envelope(
        self,
        symbol: str,
        result: dict[str, Any],
        flat: AnalysisResult,
        status: str,
        broker_now: datetime,
        ohlc: dict[str, list[OHLCBar]],
    ) -> AnalysisEnvelope:
        """Build the validated schema-v2 envelope from the flat result."""
        run_id = broker_now.strftime("%Y-%m-%dT%H:%M:%S")
        errors = list(result.get("errors", flat.errors))
        ohlc_data = OHLCData(
            D1=ohlc.get("D1", flat.ohlc.D1),
            H4=ohlc.get("H4", flat.ohlc.H4),
            H1=ohlc.get("H1", flat.ohlc.H1),
        )

        market_context = result.get("market_context", flat.market_context)
        structure_analysis = result.get("structure_analysis")

        facts = self._build_deterministic_facts(symbol, flat, market_context, structure_analysis)

        stored_action = flat.final_action
        if stored_action is None and flat.decision is not None:
            stored_action = flat.decision.action
        action = _resolve_action(stored_action)

        payload: dict[str, Any] = {
            "schema_version": "2",
            "symbol": symbol,
            "run_id": run_id,
            "started_at": broker_now,
            "completed_at": broker_now,
            "status": status,
            "errors": errors,
            "fatal_error": result.get("fatal_error"),
            "deterministic_facts": facts,
            "decision": {"action": action},
            "synthesis": self._build_synthesis(flat),
            "ohlc": ohlc_data,
        }
        return AnalysisEnvelope.model_validate(payload)

    def _build_synthesis(self, flat: AnalysisResult) -> SynthesisBlock:
        raw_status = (flat.synthesis_status or "SKIPPED").upper()
        if raw_status == SynthesisStatusV2.SUCCESS.value:
            status = SynthesisStatusV2.SUCCESS
        elif raw_status == SynthesisStatusV2.FAILED.value:
            status = SynthesisStatusV2.FAILED
        else:
            status = SynthesisStatusV2.SKIPPED
        return SynthesisBlock(
            status=status,
            explanation=flat.synthesis_explanation,
            risks=list(flat.synthesis_risks),
            confluences=list(flat.synthesis_confluences),
            error=flat.synthesis_error,
        )

    def _build_deterministic_facts(
        self,
        symbol: str,
        flat: AnalysisResult,
        market_context: Any,
        structure_analysis: Any,
    ) -> DeterministicFacts:
        """Map the flat result + structure analysis into v2 deterministic facts."""
        timeframes: dict[str, Any] = {}
        confidence_components: dict[str, Any] = {}
        latest_structural_events: dict[str, Any] = {}
        latest_liquidity_states: dict[str, Any] = {}
        event_history: dict[str, Any] = {}
        liquidity_history: dict[str, Any] = {}
        selected_levels: dict[str, Any] = {}

        raw_timeframes = self._raw_timeframes(structure_analysis)
        for tf_name in ("D1", "H4", "H1"):
            raw = raw_timeframes.get(tf_name)
            if not isinstance(raw, dict):
                continue
            compact = _compact_timeframe_facts(raw)
            timeframes[tf_name] = compact

            scoring = compact.get("scoring")
            if isinstance(scoring, dict):
                confidence_components[tf_name] = scoring

            events = compact.get("events")
            if isinstance(events, dict):
                if events.get("latest_material_event") is not None:
                    latest_structural_events[tf_name] = events["latest_material_event"]
                history = events.get("event_history")
                if isinstance(history, list):
                    event_history[tf_name] = history

            liquidity = compact.get("liquidity")
            if isinstance(liquidity, dict):
                if liquidity.get("current_state") is not None:
                    latest_liquidity_states[tf_name] = liquidity["current_state"]
                history = liquidity.get("event_history")
                if isinstance(history, list):
                    liquidity_history[tf_name] = history

            levels = compact.get("levels")
            if isinstance(levels, dict) and levels:
                selected_levels[tf_name] = levels

        confidence = self._deterministic_confidence(confidence_components, market_context)

        payload: dict[str, Any] = {
            "symbol": symbol,
            "timeframes": timeframes,
            "setup_status": flat.setup_status or "NO_SETUP",
            "direction": flat.direction or "NONE",
            "trade_direction": flat.trade_direction or "NEUTRAL",
            "setup_grade": flat.setup_grade,
            "setup_classification_status": flat.setup_classification_status or "NO_SETUP",
            "setup_lifecycle_status": flat.setup_lifecycle_status or "PENDING",
            "entry_plan": EntryPlan(
                current_price=None,
                entry_type=flat.order_type,
                entry_price=flat.sl_tp_overlay.entry_price,
                invalidation_price=flat.sl_tp_overlay.stop_loss,
                target_price=flat.sl_tp_overlay.take_profit,
                estimated_reward_risk=flat.estimated_reward_risk,
            ),
            "rr": RRInfo(
                calculated_rr=flat.calculated_rr if flat.calculated_rr is not None else flat.rr,
                minimum_required_rr=flat.minimum_required_rr,
                rr_pass=flat.rr_pass,
            ),
            "confidence_components": confidence_components,
            "policy": PolicyFacts(
                execution_status=flat.execution_status,
                actionable=flat.execution_status == "ACTIONABLE",
                blockers=list(flat.execution_blockers),
                reason_codes=list(flat.reason_codes),
            ),
            "selected_levels": selected_levels,
            "latest_structural_events": latest_structural_events,
            "latest_liquidity_states": latest_liquidity_states,
            "event_history": event_history,
            "liquidity_history": liquidity_history,
            "validation_status": flat.validation_status or "INVALID",
            "validation_errors": list(flat.validation_errors),
            "operational": flat.operational,
            "entry_authorized": False,
            "bias": flat.trade_direction or "NEUTRAL",
            "confidence": confidence,
        }
        return DeterministicFacts.model_validate(payload)

    @staticmethod
    def _raw_timeframes(structure_analysis: Any) -> dict[str, Any]:
        """Extract the raw per-timeframe engine output from structure_analysis."""
        if not isinstance(structure_analysis, dict):
            return {}
        full_mtf = structure_analysis.get("_full_multi_timeframe")
        if isinstance(full_mtf, dict):
            timeframes = full_mtf.get("timeframes")
            if isinstance(timeframes, dict):
                return timeframes
        timeframes = structure_analysis.get("timeframes")
        return timeframes if isinstance(timeframes, dict) else {}

    @staticmethod
    def _deterministic_confidence(
        confidence_components: dict[str, Any], market_context: Any
    ) -> float | None:
        """Prefer deterministic per-timeframe scoring (H1 > H4 > D1), then the
        interpretive market context as a last resort."""
        for tf_name in ("H1", "H4", "D1"):
            scoring = confidence_components.get(tf_name) or {}
            value = scoring.get("confidence_score")
            if isinstance(value, int | float) and not isinstance(value, bool):
                return float(value)
        if isinstance(market_context, dict):
            value = market_context.get("confidence")
            if isinstance(value, int | float) and not isinstance(value, bool):
                return float(value)
        elif market_context is not None and hasattr(market_context, "confidence"):
            return float(market_context.confidence)
        return None

    # ------------------------------------------------------------------
    # Atomic persistence
    # ------------------------------------------------------------------

    def _write_atomic(self, path: Path, content: str) -> None:
        """Write via a sibling temp file then atomically replace the target.

        Parent directories are created as needed. On any error the temp file
        is removed so no partial or corrupt final file remains (Section 13).
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path: Path | None = None
        try:
            fd, tmp_name = tempfile.mkstemp(
                dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp"
            )
            tmp_path = Path(tmp_name)
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp_path, path)
        except Exception:
            if tmp_path is not None:
                tmp_path.unlink(missing_ok=True)
            raise

    def _build_path(self, symbol: str, broker_now: datetime) -> Path:
        """Compute data/YYYY/MM/DD/SYMBOL/result-HH.json path."""
        return (
            self.base_dir
            / f"{broker_now:%Y}"
            / f"{broker_now:%m}"
            / f"{broker_now:%d}"
            / symbol
            / f"result-{broker_now:%H}.json"
        )
