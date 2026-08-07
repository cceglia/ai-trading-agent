"""Validation of the deterministic facts contract.

This module is deliberately independent of the LLM layer.  It validates the
engine state and the raw evidence used to create that state before any
interpretive call is made.
"""

from __future__ import annotations

from datetime import datetime
from math import isfinite
from typing import Any

from pydantic import BaseModel, Field

from .entry_calculator import calculate_risk_reward
from .models import (
    DecisionAction,
    DeterministicSetupState,
    ExecutionPolicyState,
    SetupClassificationStatus,
    SetupLifecycleStatus,
    TradeDirection,
)

MINIMUM_REQUIRED_RR = 2.0


class ValidationStatus(str):
    VALID = "VALID"
    INVALID = "INVALID"


class DeterministicValidation(BaseModel, frozen=True):
    """Result of validating deterministic facts."""

    validation_status: str = ValidationStatus.VALID
    validation_errors: tuple[str, ...] = ()
    calculated_rr: float | None = None
    rr: float | None = None
    minimum_required_rr: float = MINIMUM_REQUIRED_RR
    rr_pass: bool = False
    deterministic_blockers: tuple[dict[str, Any], ...] = ()
    reason_codes: tuple[str, ...] = ()
    setup_status: str = "NO_SETUP"
    direction: str = "NONE"
    entry_authorized: bool = Field(default=False, frozen=True)

    @property
    def valid(self) -> bool:
        return self.validation_status == ValidationStatus.VALID


def _raw_timeframes(structure_analysis: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(structure_analysis, dict):
        return {}
    timeframes = structure_analysis.get("timeframes")
    return timeframes if isinstance(timeframes, dict) else {}


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _action_value(action: DecisionAction | str | None) -> str:
    return action.value if isinstance(action, DecisionAction) else str(action or "no_trade")


def _blockers(policy: ExecutionPolicyState | None) -> tuple[dict[str, Any], ...]:
    if policy is None:
        return ()
    return tuple(blocker.model_dump(mode="json") for blocker in policy.execution_blockers)


class DeterministicValidator:
    """Validate setup facts, policy facts, and their source evidence."""

    def validate(
        self,
        *,
        setup: DeterministicSetupState,
        policy: ExecutionPolicyState | None = None,
        structure_analysis: dict[str, Any] | None = None,
        action: DecisionAction | str | None = None,
        minimum_required_rr: float = MINIMUM_REQUIRED_RR,
    ) -> DeterministicValidation:
        errors: list[str] = []
        reason_codes: list[str] = [code.value for code in setup.rejection_codes]
        direction = (
            "NONE"
            if setup.setup_classification_status == SetupClassificationStatus.NO_SETUP
            else "LONG"
            if setup.trade_direction == TradeDirection.BULLISH
            else "SHORT"
            if setup.trade_direction == TradeDirection.BEARISH
            else "NONE"
        )
        executable = _action_value(action) in {"buy_setup", "sell_setup"}
        setup_status = (
            "NO_SETUP"
            if setup.setup_classification_status == SetupClassificationStatus.NO_SETUP
            else "READY"
            if setup.setup_lifecycle_status
            in (SetupLifecycleStatus.READY, SetupLifecycleStatus.TRIGGERED)
            else "INVALID"
        )

        if action is not None:
            expected = {"buy_setup": "LONG", "sell_setup": "SHORT", "no_trade": "NONE"}
            if _action_value(action) in expected and direction != expected[_action_value(action)]:
                errors.append("setup/action/direction consistency failed")
                reason_codes.append("ACTION_DIRECTION_MISMATCH")
        if setup_status == "NO_SETUP" and executable:
            errors.append("NO_SETUP cannot produce an executable action")
            reason_codes.append("NO_SETUP_ACTION_CONFLICT")

        entry, stop, target = setup.entry_price, setup.invalidation_price, setup.target_price
        calculated_rr: float | None = None
        if (
            isinstance(entry, int | float)
            and isinstance(stop, int | float)
            and isinstance(target, int | float)
            and isfinite(entry)
            and isfinite(stop)
            and isfinite(target)
        ):
            entry_value, stop_value, target_value = float(entry), float(stop), float(target)
            calculated_rr = calculate_risk_reward(
                setup.trade_direction, entry_value, stop_value, target_value
            )
            if setup.trade_direction == TradeDirection.BULLISH and not (
                stop_value < entry_value < target_value
            ):
                errors.append("LONG geometry requires stop < entry < target")
            if setup.trade_direction == TradeDirection.BEARISH and not (
                target_value < entry_value < stop_value
            ):
                errors.append("SHORT geometry requires target < entry < stop")
        elif setup_status == "READY":
            errors.append("READY setup is missing entry, stop, or target")
        if calculated_rr is None and setup_status == "READY":
            reason_codes.append("RR_CALCULATION_FAILED")
        if setup.estimated_reward_risk is not None and calculated_rr is not None:
            if abs(setup.estimated_reward_risk - calculated_rr) > 1e-3:
                errors.append("reported RR does not match deterministic price math")
                reason_codes.append("RR_MATH_MISMATCH")
        rr = calculated_rr
        rr_pass = rr is not None and rr >= minimum_required_rr
        if setup_status == "READY" and not rr_pass:
            errors.append(f"RR must meet minimum_required_rr={minimum_required_rr:.1f}")
            reason_codes.append("RR_BELOW_MINIMUM")

        if setup_status == "READY" and policy and policy.execution_blockers:
            errors.append("READY setup cannot contain deterministic blockers")
            reason_codes.append("READY_HAS_BLOCKERS")
        if setup_status == "NO_SETUP" and not setup.rejection_codes:
            errors.append("NO_SETUP requires a coherent deterministic reason code")
            reason_codes.append("NO_SETUP_REASON_MISSING")
        if setup.entry_type is not None and entry is not None and setup.current_price is not None:
            if (
                setup.trade_direction == TradeDirection.BULLISH
                and setup.entry_type.value == "STOP"
                and entry <= setup.current_price
            ):
                errors.append("LONG STOP entry must be above current price")
            if (
                setup.trade_direction == TradeDirection.BULLISH
                and setup.entry_type.value == "LIMIT"
                and entry >= setup.current_price
            ):
                errors.append("LONG LIMIT entry must be below current price")
            if (
                setup.trade_direction == TradeDirection.BEARISH
                and setup.entry_type.value == "STOP"
                and entry >= setup.current_price
            ):
                errors.append("SHORT STOP entry must be below current price")
            if (
                setup.trade_direction == TradeDirection.BEARISH
                and setup.entry_type.value == "LIMIT"
                and entry <= setup.current_price
            ):
                errors.append("SHORT LIMIT entry must be above current price")

        self._validate_evidence(structure_analysis, setup, errors, reason_codes)
        h1 = _raw_timeframes(structure_analysis).get("H1")
        if isinstance(h1, dict):
            context = h1.get("analysis_context") or {}
            setup_context = context.get("setup_context") or context
            if isinstance(setup_context, dict):
                reported_minimum = setup_context.get("minimum_required_rr")
                if reported_minimum is not None and reported_minimum != minimum_required_rr:
                    errors.append("minimum_required_rr is not the canonical 2.0 threshold")
                    reason_codes.append("RR_THRESHOLD_MISMATCH")
                reported_rr = setup_context.get("calculated_rr")
                if (
                    isinstance(reported_rr, int | float)
                    and calculated_rr is not None
                    and abs(reported_rr - calculated_rr) > 1e-3
                ):
                    errors.append("H1 calculated_rr does not match deterministic price math")
                    reason_codes.append("RR_MATH_MISMATCH")
        if setup.confirmed_at is not None and _parse_timestamp(setup.confirmed_at) is None:
            errors.append("setup confirmation timestamp is invalid")
            reason_codes.append("INVALID_TIMESTAMP")
        if setup.confirmed_bar_index is not None and setup.confirmed_bar_index < 0:
            errors.append("setup confirmation bar index is invalid")
            reason_codes.append("INVALID_TIMESTAMP")
        status = ValidationStatus.INVALID if errors else ValidationStatus.VALID
        return DeterministicValidation(
            validation_status=status,
            validation_errors=tuple(dict.fromkeys(errors)),
            calculated_rr=calculated_rr,
            rr=rr,
            minimum_required_rr=minimum_required_rr,
            rr_pass=rr_pass,
            deterministic_blockers=_blockers(policy),
            reason_codes=tuple(dict.fromkeys(reason_codes)),
            setup_status=setup_status if status == ValidationStatus.VALID else "INVALID",
            direction=direction,
        )

    def _validate_evidence(
        self,
        structure_analysis: dict[str, Any] | None,
        setup: DeterministicSetupState,
        errors: list[str],
        reason_codes: list[str],
    ) -> None:
        for timeframe, raw in _raw_timeframes(structure_analysis).items():
            if not isinstance(raw, dict):
                continue
            audit = raw.get("source_audit") or {}
            if audit.get("candle_closure_verified") is not True:
                errors.append(f"{timeframe} closed-candle audit failed")
                reason_codes.append("CLOSED_CANDLE_AUDIT_FAILED")
            latest = audit.get("latest_closed_candle_time")
            if latest is not None and _parse_timestamp(latest) is None:
                errors.append(f"{timeframe} latest closed candle timestamp is invalid")
                reason_codes.append("INVALID_TIMESTAMP")
            events = raw.get("events") or {}
            timeline = events.get("event_history", events.get("all_canonical_events", []))
            if not isinstance(timeline, list):
                timeline = []
            for event in timeline:
                if not isinstance(event, dict):
                    continue
                if event.get("structural_scope") not in {"PRIMARY", "INTERNAL"}:
                    errors.append(f"{timeframe} event scope was not preserved")
                    reason_codes.append("EVENT_SCOPE_LOST")
                timestamp = _parse_timestamp(event.get("timestamp"))
                if event.get("timestamp") is not None and timestamp is None:
                    errors.append(f"{timeframe} event timestamp is invalid")
                    reason_codes.append("INVALID_TIMESTAMP")
                event_type = str(event.get("event_type", ""))
                if "BULLISH_BOS" in event_type or "BULLISH_CHOCH" in event_type:
                    level, close = event.get("broken_level"), event.get("confirming_close")
                    if isinstance(level, int | float) and isinstance(close, int | float):
                        atr = (raw.get("technical_context") or {}).get("atr_14") or 0.0
                        buffer = ((raw.get("calculation_metadata") or {}).get("profile") or {}).get(
                            "bos_close_buffer_atr", 0.0
                        )
                        if close <= level + buffer * atr:
                            errors.append(
                                f"{timeframe} bullish breakout close lacks required buffer"
                            )
                            reason_codes.append("BREAKOUT_BUFFER_FAILED")
                if "BEARISH_BOS" in event_type or "BEARISH_CHOCH" in event_type:
                    level, close = event.get("broken_level"), event.get("confirming_close")
                    if isinstance(level, int | float) and isinstance(close, int | float):
                        atr = (raw.get("technical_context") or {}).get("atr_14") or 0.0
                        buffer = ((raw.get("calculation_metadata") or {}).get("profile") or {}).get(
                            "bos_close_buffer_atr", 0.0
                        )
                        if close >= level - buffer * atr:
                            errors.append(
                                f"{timeframe} bearish breakout close lacks required buffer"
                            )
                            reason_codes.append("BREAKOUT_BUFFER_FAILED")
            failed = events.get("failed_breakouts", [])
            confirmed = [
                event
                for event in timeline
                if isinstance(event, dict) and "FAILED_" not in str(event.get("event_type", ""))
            ]
            for failure in failed if isinstance(failed, list) else []:
                for event in confirmed:
                    if failure.get("broken_level") == event.get("broken_level") and failure.get(
                        "structural_scope"
                    ) == event.get("structural_scope"):
                        if failure.get("event_index", -1) >= event.get("event_index", -1):
                            errors.append(
                                f"{timeframe} confirmed event precedes failed breakout chronology"
                            )
                            reason_codes.append("EVENT_CHRONOLOGY_INVALID")
            levels = (raw.get("levels") or {}).get("support_levels", []) + (
                raw.get("levels") or {}
            ).get("resistance_levels", [])
            for level in levels:
                if not isinstance(level, dict) or level.get("price") != setup.invalidation_price:
                    continue
                if level.get("eligible_for_invalidation") is False or level.get(
                    "current_status"
                ) in {"BROKEN", "RECLAIMED"}:
                    errors.append("stale, broken, or reclaimed level used for invalidation")
                    reason_codes.append("INVALIDATION_LEVEL_INELIGIBLE")


def validate_deterministic_facts(**kwargs: Any) -> DeterministicValidation:
    return DeterministicValidator().validate(**kwargs)
