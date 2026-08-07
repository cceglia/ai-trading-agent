"""Validation of the deterministic facts contract.

This module is deliberately independent of the LLM layer.  It validates the
engine state and the raw evidence used to create that state before any
interpretive call is made.
"""

from __future__ import annotations

from datetime import datetime
from math import isfinite
from typing import Any, cast

from pydantic import BaseModel, Field

from .config import MAX_LEVEL_AGE, MIN_RR
from .entry_calculator import calculate_risk_reward
from .models import (
    DecisionAction,
    DeterministicSetupState,
    ExecutionPolicyState,
    SetupClassificationStatus,
    SetupLifecycleStatus,
    TradeDirection,
)
from .utils import canonical_level_id

MINIMUM_REQUIRED_RR = MIN_RR


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


def _finite_number(value: Any) -> bool:
    if not isinstance(value, int | float) or isinstance(value, bool):
        return False
    try:
        return isfinite(value)
    except OverflowError:
        return False


def _non_negative_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


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
        if minimum_required_rr != MIN_RR:
            errors.append("minimum_required_rr is not the canonical 2.0 threshold")
            reason_codes.append("RR_THRESHOLD_MISMATCH")
        minimum_required_rr = MIN_RR
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
            action_value = _action_value(action)
            if action_value not in {"buy_setup", "sell_setup", "no_trade"}:
                errors.append("supplied action is not a valid deterministic action")
                reason_codes.append("ACTION_INVALID")
            allowed_actions = (
                {
                    item.value if isinstance(item, DecisionAction) else str(item)
                    for item in policy.allowed_actions
                }
                if policy is not None
                else set()
            )
            if policy is not None and action_value not in allowed_actions:
                errors.append("supplied action is not allowed by deterministic policy")
                reason_codes.append("POLICY_ACTION_NOT_ALLOWED")
            expected = {"buy_setup": "LONG", "sell_setup": "SHORT", "no_trade": "NONE"}
            if action_value in expected and direction != expected[action_value]:
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
                reason_codes.append("INVALID_LONG_GEOMETRY")
            if setup.trade_direction == TradeDirection.BEARISH and not (
                target_value < entry_value < stop_value
            ):
                errors.append("SHORT geometry requires target < entry < stop")
                reason_codes.append("INVALID_SHORT_GEOMETRY")
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
        if setup_status == "READY" and policy and action is None:
            expected_action = {
                TradeDirection.BULLISH: DecisionAction.BUY_SETUP.value,
                TradeDirection.BEARISH: DecisionAction.SELL_SETUP.value,
            }.get(setup.trade_direction, DecisionAction.NO_TRADE.value)
            if expected_action not in {item.value for item in policy.allowed_actions}:
                errors.append("policy allowed action contradicts setup direction")
                reason_codes.append("POLICY_ACTION_DIRECTION_MISMATCH")
        if setup.entry_type is not None and entry is not None and setup.current_price is not None:
            if (
                setup.trade_direction == TradeDirection.BULLISH
                and setup.entry_type.value == "STOP"
                and entry <= setup.current_price
            ):
                errors.append("LONG STOP entry must be above current price")
                reason_codes.append("LONG_ENTRY_PRICE_VIOLATION")
            if (
                setup.trade_direction == TradeDirection.BULLISH
                and setup.entry_type.value == "LIMIT"
                and entry >= setup.current_price
            ):
                errors.append("LONG LIMIT entry must be below current price")
                reason_codes.append("LONG_ENTRY_PRICE_VIOLATION")
            if (
                setup.trade_direction == TradeDirection.BEARISH
                and setup.entry_type.value == "STOP"
                and entry >= setup.current_price
            ):
                errors.append("SHORT STOP entry must be below current price")
                reason_codes.append("SHORT_ENTRY_PRICE_VIOLATION")
            if (
                setup.trade_direction == TradeDirection.BEARISH
                and setup.entry_type.value == "LIMIT"
                and entry <= setup.current_price
            ):
                errors.append("SHORT LIMIT entry must be above current price")
                reason_codes.append("SHORT_ENTRY_PRICE_VIOLATION")

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
        def malformed(label: str) -> None:
            errors.append(f"{label} has a malformed evidence shape")
            reason_codes.append("MALFORMED_EVIDENCE_SHAPE")

        matching_lifecycle_level = False
        for timeframe, raw in _raw_timeframes(structure_analysis).items():
            if not isinstance(raw, dict):
                malformed(timeframe)
                continue
            audit_value = raw.get("source_audit")
            if audit_value is not None and not isinstance(audit_value, dict):
                malformed(f"{timeframe} source_audit")
            audit = audit_value if isinstance(audit_value, dict) else {}
            if audit.get("candle_closure_verified") is not True:
                errors.append(f"{timeframe} closed-candle audit failed")
                reason_codes.append("CLOSED_CANDLE_AUDIT_FAILED")
            latest = audit.get("latest_closed_candle_time")
            if latest is not None and _parse_timestamp(latest) is None:
                errors.append(f"{timeframe} latest closed candle timestamp is invalid")
                reason_codes.append("INVALID_TIMESTAMP")
            technical_value = raw.get("technical_context")
            if technical_value is not None and not isinstance(technical_value, dict):
                malformed(f"{timeframe} technical_context")
            technical_context = technical_value if isinstance(technical_value, dict) else {}
            metadata_value = raw.get("calculation_metadata")
            if metadata_value is not None and not isinstance(metadata_value, dict):
                malformed(f"{timeframe} calculation_metadata")
            calculation_metadata = metadata_value if isinstance(metadata_value, dict) else {}
            profile_value = calculation_metadata.get("profile")
            if profile_value is not None and not isinstance(profile_value, dict):
                malformed(f"{timeframe} calculation_metadata.profile")
            profile = profile_value if isinstance(profile_value, dict) else {}
            events_value = raw.get("events")
            if events_value is not None and not isinstance(events_value, dict):
                malformed(f"{timeframe} events")
            events = events_value if isinstance(events_value, dict) else {}
            timeline = events.get("event_history", events.get("all_canonical_events", []))
            if not isinstance(timeline, list):
                malformed(f"{timeframe} event history")
                timeline = []
            histories: dict[str, list[Any]] = {"event history": timeline}
            for history_name in (
                "all_canonical_events",
                "primary_events",
                "internal_events",
                "failed_breakouts",
            ):
                history = events.get(history_name)
                if history is not None and not isinstance(history, list):
                    malformed(f"{timeframe} {history_name}")
                elif isinstance(history, list) and history is not timeline:
                    histories[history_name] = history

            canonical_history = timeline
            canonical_by_scope = {
                scope: (
                    events[history_name]
                    if isinstance(events.get(history_name), list)
                    else [
                        event
                        for event in canonical_history
                        if isinstance(event, dict) and event.get("structural_scope") == scope
                    ]
                )
                for scope, history_name in (
                    ("PRIMARY", "primary_events"),
                    ("INTERNAL", "internal_events"),
                )
            }
            canonical_failed = [
                event
                for event in canonical_history
                if isinstance(event, dict) and "FAILED_" in str(event.get("event_type", ""))
            ]

            def projection_content_invalid(label: str) -> None:
                errors.append(f"{timeframe} {label} content is not canonical")
                reason_codes.append("EVENT_PROJECTION_CONTENT_INVALID")

            expected_histories = {
                "all_canonical_events": canonical_history,
                "failed_breakouts": canonical_failed,
            }
            for history_name, expected in expected_histories.items():
                supplied = events.get(history_name)
                if isinstance(supplied, list) and supplied != expected:
                    projection_content_invalid(history_name)

            events_by_id = {
                event["event_id"]: event
                for event in canonical_history
                if isinstance(event, dict) and isinstance(event.get("event_id"), str)
            }
            for history_name in ("primary_events", "internal_events"):
                supplied = events.get(history_name)
                if not isinstance(supplied, list):
                    continue
                for event in supplied:
                    if not isinstance(event, dict):
                        continue
                    event_id = event.get("event_id")
                    if event_id in events_by_id and event != events_by_id[event_id]:
                        projection_content_invalid(history_name)

            for history_name, history in histories.items():
                self._validate_chronology(
                    history, f"{timeframe} {history_name}", errors, reason_codes
                )
                for event in history:
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
                        atr = technical_context.get("atr_14")
                        buffer = profile.get("bos_close_buffer_atr")
                        if not all(_finite_number(value) for value in (level, close, atr, buffer)):
                            errors.append(f"{timeframe} bullish breakout evidence is incomplete")
                            reason_codes.append(
                                "BREAKOUT_EVIDENCE_INCOMPLETE"
                                if any(value is None for value in (level, close, atr, buffer))
                                else "MALFORMED_BREAKOUT_NUMERIC"
                            )
                        elif cast(float, atr) < 0 or cast(float, buffer) < 0:
                            errors.append(f"{timeframe} bullish breakout buffer inputs are invalid")
                            reason_codes.append("MALFORMED_BREAKOUT_NUMERIC")
                        else:
                            try:
                                level_value = float(cast(float, level))
                                close_value = float(cast(float, close))
                                atr_value = float(cast(float, atr))
                                buffer_value = float(cast(float, buffer))
                                breakout_passed = close_value > (
                                    level_value + buffer_value * atr_value
                                )
                            except OverflowError:
                                breakout_passed = False
                            if not breakout_passed:
                                errors.append(
                                    f"{timeframe} bullish breakout close lacks required buffer"
                                )
                                reason_codes.append("BREAKOUT_BUFFER_FAILED")
                    if "BEARISH_BOS" in event_type or "BEARISH_CHOCH" in event_type:
                        level, close = event.get("broken_level"), event.get("confirming_close")
                        atr = technical_context.get("atr_14")
                        buffer = profile.get("bos_close_buffer_atr")
                        if not all(_finite_number(value) for value in (level, close, atr, buffer)):
                            errors.append(f"{timeframe} bearish breakout evidence is incomplete")
                            reason_codes.append(
                                "BREAKOUT_EVIDENCE_INCOMPLETE"
                                if any(value is None for value in (level, close, atr, buffer))
                                else "MALFORMED_BREAKOUT_NUMERIC"
                            )
                        elif cast(float, atr) < 0 or cast(float, buffer) < 0:
                            errors.append(f"{timeframe} bearish breakout buffer inputs are invalid")
                            reason_codes.append("MALFORMED_BREAKOUT_NUMERIC")
                        else:
                            try:
                                level_value = float(cast(float, level))
                                close_value = float(cast(float, close))
                                atr_value = float(cast(float, atr))
                                buffer_value = float(cast(float, buffer))
                                breakout_passed = close_value < (
                                    level_value - buffer_value * atr_value
                                )
                            except OverflowError:
                                breakout_passed = False
                            if not breakout_passed:
                                errors.append(
                                    f"{timeframe} bearish breakout close lacks required buffer"
                                )
                                reason_codes.append("BREAKOUT_BUFFER_FAILED")
            for latest_name in (
                "latest_material_event",
                "latest_primary_event",
                "latest_internal_event",
            ):
                latest_event = events.get(latest_name)
                if latest_event is not None and not isinstance(latest_event, dict):
                    malformed(f"{timeframe} {latest_name}")
                elif isinstance(latest_event, dict) and latest_event.get(
                    "structural_scope"
                ) not in {
                    "PRIMARY",
                    "INTERNAL",
                }:
                    errors.append(f"{timeframe} event scope was not preserved")
                    reason_codes.append("EVENT_SCOPE_LOST")
                if isinstance(latest_event, dict):
                    projection_timestamp = _parse_timestamp(latest_event.get("timestamp"))
                    if projection_timestamp is None:
                        errors.append(f"{timeframe} {latest_name} timestamp is invalid")
                        reason_codes.append("INVALID_TIMESTAMP")
                    projection_history = histories.get(
                        "event history"
                        if latest_name == "latest_material_event"
                        else "primary_events"
                        if latest_name == "latest_primary_event"
                        else "internal_events",
                        [],
                    )
                    scope = (
                        None
                        if latest_name == "latest_material_event"
                        else "PRIMARY"
                        if latest_name == "latest_primary_event"
                        else "INTERNAL"
                    )
                    expected_latest = (
                        canonical_history[-1]
                        if scope is None and canonical_history
                        else canonical_by_scope[scope][-1]
                        if scope is not None and canonical_by_scope[scope]
                        else None
                    )
                    if latest_event != expected_latest:
                        projection_content_invalid(latest_name)
                    projection_index = latest_event.get("event_index")
                    if not _non_negative_integer(projection_index):
                        errors.append(f"{timeframe} {latest_name} event index is invalid")
                        reason_codes.append("EVENT_PROJECTION_CHRONOLOGY_INVALID")
                    if projection_history and projection_timestamp is not None:
                        last_event = projection_history[-1]
                        if isinstance(last_event, dict):
                            last_timestamp = _parse_timestamp(last_event.get("timestamp"))
                            if last_timestamp is not None and projection_timestamp < last_timestamp:
                                errors.append(
                                    f"{timeframe} {latest_name} chronology is not monotonic"
                                )
                                reason_codes.append("EVENT_PROJECTION_CHRONOLOGY_INVALID")
                            last_index = last_event.get("event_index")
                            if (
                                _non_negative_integer(projection_index)
                                and _non_negative_integer(last_index)
                                and projection_index != last_index
                            ):
                                errors.append(
                                    f"{timeframe} {latest_name} event index is not canonical"
                                )
                                reason_codes.append("EVENT_PROJECTION_CHRONOLOGY_INVALID")
            liquidity_value = raw.get("liquidity")
            if liquidity_value is not None and not isinstance(liquidity_value, dict):
                malformed(f"{timeframe} liquidity")
            liquidity = liquidity_value if isinstance(liquidity_value, dict) else {}
            if isinstance(liquidity, dict):

                def validate_liquidity_scope(event: Any, label: str) -> None:
                    if isinstance(event, dict) and event.get("scope") not in {
                        "EXTERNAL",
                        "INTERNAL",
                    }:
                        errors.append(f"{label} scope was not preserved")
                        reason_codes.append("LIQUIDITY_SCOPE_LOST")

                liquidity_history = liquidity.get("event_history", liquidity.get("events", []))
                if not isinstance(liquidity_history, list):
                    malformed(f"{timeframe} liquidity history")
                    liquidity_history = []
                self._validate_chronology(
                    liquidity_history,
                    f"{timeframe} liquidity",
                    errors,
                    reason_codes,
                )
                for event in liquidity_history:
                    validate_liquidity_scope(event, f"{timeframe} liquidity event")
                pools = liquidity.get("pools", [])
                if not isinstance(pools, list):
                    malformed(f"{timeframe} liquidity pools")
                    pools = []
                for pool in pools:
                    if isinstance(pool, dict):
                        pool_history = pool.get("event_history", [])
                        if not isinstance(pool_history, list):
                            malformed(f"{timeframe} liquidity pool history")
                        self._validate_chronology(
                            pool_history,
                            f"{timeframe} liquidity pool",
                            errors,
                            reason_codes,
                        )
                        for event in pool_history:
                            validate_liquidity_scope(
                                event,
                                f"{timeframe} liquidity pool event",
                            )
                    else:
                        malformed(f"{timeframe} liquidity pool")
                validate_liquidity_scope(
                    liquidity.get("latest_event"),
                    f"{timeframe} latest liquidity event",
                )
            levels_value = raw.get("levels")
            if levels_value is not None and not isinstance(levels_value, dict):
                malformed(f"{timeframe} levels")
            levels_container = levels_value if isinstance(levels_value, dict) else {}
            support_levels = levels_container.get("support_levels", [])
            resistance_levels = levels_container.get("resistance_levels", [])
            if not isinstance(support_levels, list):
                malformed(f"{timeframe} support levels")
                support_levels = []
            if not isinstance(resistance_levels, list):
                malformed(f"{timeframe} resistance levels")
                resistance_levels = []
            levels = support_levels + resistance_levels
            for level in levels:
                if not isinstance(level, dict):
                    malformed(f"{timeframe} level")
                    continue
                timeframe_limit = MAX_LEVEL_AGE.get(timeframe)
                eligible = level.get("eligible_for_invalidation") is True
                status = level.get("current_status")
                break_count = level.get("break_count")
                reclaim_count = level.get("reclaim_count")
                accepted_beyond_count = level.get("accepted_beyond_count")
                accepted_beyond = level.get("accepted_beyond") is True
                counters_valid = True
                for counter_name, counter in (
                    ("break_count", break_count),
                    ("reclaim_count", reclaim_count),
                    ("accepted_beyond_count", accepted_beyond_count),
                ):
                    if counter is not None and not _non_negative_integer(counter):
                        counters_valid = False
                        errors.append(f"{timeframe} level {counter_name} is invalid")
                        reason_codes.append("INVALIDATION_LEVEL_LIFECYCLE_INVALID")
                age_bars = level.get("age_bars")
                age_valid = _non_negative_integer(age_bars)
                age_value = cast(int, age_bars) if age_valid else None
                if not age_valid:
                    errors.append(f"{timeframe} level age_bars is invalid")
                    reason_codes.append("INVALIDATION_LEVEL_AGE_INVALID")
                age_exceeded = (
                    age_value is not None
                    and isinstance(timeframe_limit, int)
                    and age_value > timeframe_limit
                )
                # Historical levels can outlive the eligibility window. Only a
                # selected level or an explicit eligibility claim is actionable.
                selected = level.get("price") == setup.invalidation_price
                if age_exceeded and (selected or eligible):
                    errors.append(f"{timeframe} level age_bars exceeds timeframe limit")
                    reason_codes.append("INVALIDATION_LEVEL_AGE_LIMIT_EXCEEDED")
                contradictory = eligible and (
                    status not in {"FRESH", "TESTED"}
                    or level.get("freshness") not in {None, "FRESH", "TESTED"}
                    or accepted_beyond
                    or (
                        counters_valid
                        and isinstance(accepted_beyond_count, int)
                        and accepted_beyond_count > 0
                    )
                    or (age_exceeded)
                    or (counters_valid and isinstance(break_count, int) and break_count > 0)
                    or (counters_valid and isinstance(reclaim_count, int) and reclaim_count > 0)
                    or (status in {"FRESH", "TESTED"} and counters_valid and (break_count or 0) > 0)
                    or (status == "FRESH" and counters_valid and (reclaim_count or 0) > 0)
                    or (status == "RECLAIMED" and counters_valid and (reclaim_count or 0) == 0)
                )
                if (
                    counters_valid
                    and isinstance(reclaim_count, int)
                    and reclaim_count > 0
                    and status in {"FRESH", "TESTED"}
                ):
                    contradictory = True
                if contradictory:
                    errors.append("eligible invalidation level contradicts lifecycle evidence")
                    reason_codes.append("INVALIDATION_LEVEL_CONTRADICTION")
                if level.get("price") != setup.invalidation_price:
                    continue
                expected_side = "LOW" if setup.trade_direction == TradeDirection.BULLISH else "HIGH"
                canonical_id = (
                    canonical_level_id(level.get("side"), level["price"], level["source_swing_ids"])
                    if isinstance(level.get("price"), int | float)
                    and isinstance(level.get("source_swing_ids"), list)
                    else None
                )
                if level.get("side") != expected_side:
                    errors.append("selected invalidation level side contradicts setup direction")
                    reason_codes.append("INVALIDATION_LEVEL_DIRECTION_MISMATCH")
                if setup.invalidation_timeframe != timeframe:
                    errors.append("selected invalidation level belongs to the wrong timeframe")
                    reason_codes.append("INVALIDATION_LEVEL_TIMEFRAME_MISMATCH")
                if (
                    setup.invalidation_level_id is None
                    or canonical_id is None
                    or level.get("level_id") != canonical_id
                    or setup.invalidation_level_id != level.get("level_id")
                ):
                    errors.append("selected invalidation level identity is not canonical")
                    reason_codes.append("INVALIDATION_LEVEL_IDENTITY_INVALID")
                lifecycle_fields = {
                    "eligible_for_invalidation",
                    "current_status",
                    "freshness",
                    "age_bars",
                    "touch_count",
                    "break_count",
                    "reclaim_count",
                    "accepted_beyond_count",
                    "accepted_beyond",
                }
                if not lifecycle_fields.issubset(level):
                    errors.append("selected invalidation level lacks complete lifecycle evidence")
                    reason_codes.append("INVALIDATION_LEVEL_EVIDENCE_INCOMPLETE")
                if not _non_negative_integer(level.get("touch_count")):
                    errors.append("selected invalidation level touch_count is invalid")
                    reason_codes.append("INVALIDATION_LEVEL_TOUCH_COUNT_INVALID")
                if not eligible or level.get("current_status") in {"BROKEN", "RECLAIMED"}:
                    errors.append("stale, broken, or reclaimed level used for invalidation")
                    reason_codes.append("INVALIDATION_LEVEL_INELIGIBLE")
                elif lifecycle_fields.issubset(level) and not contradictory:
                    matching_lifecycle_level = True

        if (
            setup.setup_lifecycle_status
            in (SetupLifecycleStatus.READY, SetupLifecycleStatus.TRIGGERED)
            and setup.invalidation_price is not None
            and _raw_timeframes(structure_analysis)
            and not matching_lifecycle_level
        ):
            errors.append(
                "READY setup lacks matching lifecycle-eligible invalidation level evidence"
            )
            reason_codes.append("INVALIDATION_LEVEL_EVIDENCE_MISSING")

    @staticmethod
    def _validate_chronology(
        timeline: Any,
        label: str,
        errors: list[str],
        reason_codes: list[str],
    ) -> None:
        if not isinstance(timeline, list):
            return
        previous_index: int | float | None = None
        previous_timestamp: datetime | None = None
        for event in timeline:
            if not isinstance(event, dict):
                errors.append(f"{label} contains a malformed event")
                reason_codes.append("MALFORMED_EVIDENCE_SHAPE")
                continue
            event_index = event.get("event_index")
            if not _non_negative_integer(event_index):
                errors.append(f"{label} event index is invalid")
                reason_codes.append("EVENT_CHRONOLOGY_INVALID")
            valid_event_index = (
                cast(int, event_index) if _non_negative_integer(event_index) else None
            )
            timestamp = _parse_timestamp(event.get("timestamp"))
            if "timestamp" in event and timestamp is None:
                errors.append(f"{label} event timestamp is invalid")
                reason_codes.append("INVALID_TIMESTAMP")
            index_regressed = (
                _non_negative_integer(event_index)
                and previous_index is not None
                and valid_event_index is not None
                and valid_event_index < previous_index
            )
            timestamp_regressed = False
            if timestamp is not None and previous_timestamp is not None:
                try:
                    timestamp_regressed = timestamp < previous_timestamp
                except TypeError:
                    errors.append(f"{label} event timestamps use incompatible timezones")
                    reason_codes.append("INVALID_TIMESTAMP")
            if index_regressed or timestamp_regressed:
                errors.append(f"{label} chronology is not monotonic")
                reason_codes.append("EVENT_CHRONOLOGY_INVALID")
            if valid_event_index is not None:
                previous_index = valid_event_index
            if timestamp is not None:
                previous_timestamp = timestamp


def validate_deterministic_facts(**kwargs: Any) -> DeterministicValidation:
    return DeterministicValidator().validate(**kwargs)
