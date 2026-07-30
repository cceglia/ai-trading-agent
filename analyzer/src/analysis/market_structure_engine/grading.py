"""Deterministic setup grading for the multi-timeframe pipeline.

This module implements the structural grading logic as specified in Section 5.1
of the multi-timeframe pipeline redesign plan. It determines:

- Setup grade (AAA, AA, COUNTERTREND) based on timeframe alignment
- Lifecycle status based on trigger confirmation
- Geometry status based on entry plan validity

The grading is purely structural — no R/R thresholds, no calendar,
no risk policy. It depends only on the models module for type definitions.
"""

from __future__ import annotations

from typing import Any

from .models import (
    BiasLevel,
    DeterministicSetupState,
    GeometryStatus,
    SetupClassificationStatus,
    SetupGrade,
    SetupLifecycleStatus,
    TradeDirection,
    TriggerStatus,
    TriggerType,
)


def _determine_trade_direction(
    d1_bias: str,
    h4_preferred_direction: str,
) -> TradeDirection:
    """Determine trade direction from D1 bias and H4 preferred direction.

    Args:
        d1_bias: D1 bias level string (e.g., "BULLISH", "STRONG_BEARISH").
        h4_preferred_direction: H4 preferred direction (e.g., "BULLISH", "BEARISH").

    Returns:
        TradeDirection enum value.
    """
    if h4_preferred_direction in ("BULLISH", "BEARISH"):
        return TradeDirection(h4_preferred_direction)

    if "BULLISH" in d1_bias:
        return TradeDirection.BULLISH
    if "BEARISH" in d1_bias:
        return TradeDirection.BEARISH
    return TradeDirection.NEUTRAL


def _determine_d1_directional(d1_bias: str) -> bool:
    """Determine if D1 shows clear directional bias.

    Args:
        d1_bias: D1 bias level string.

    Returns:
        True if D1 shows clear direction (not NEUTRAL or neutral-biased).
    """
    neutral_values = ("NEUTRAL", "NEUTRAL_BULLISH", "NEUTRAL_BEARISH")
    return d1_bias not in neutral_values


def _determine_h4_aligned(
    h4_alignment_status: str,
    d1_direction: TradeDirection,
    h4_direction: TradeDirection,
) -> bool:
    """Determine if H4 is aligned with D1.

    Args:
        h4_alignment_status: H4 alignment status string from context.
        d1_direction: D1 directional bias.
        h4_direction: H4 directional bias.

    Returns:
        True if H4 is aligned with D1.
    """
    if h4_alignment_status in ("ALIGNED_CONTINUATION", "ALIGNED_PULLBACK"):
        return True
    if h4_alignment_status == "TRANSITION":
        return False
    return h4_direction == d1_direction and h4_direction != TradeDirection.NEUTRAL


def _determine_h1_trigger_confirmed(
    h1_setup_status: str,
    h1_trigger_type: str,
    h1_trigger_status: str,
) -> bool:
    """Determine if H1 trigger is confirmed.

    BOS triggers are considered confirmed when the setup status is
    VALID_SETUP (the BOS breakout itself is the confirmation).

    CHoCH triggers require explicit CONFIRMED_TRIGGER status because
    a change-of-character must go through the Path A/B/C lifecycle
    before the trigger is considered confirmed.  Without this
    distinction, CHoCH-based setups would incorrectly show as
    TRIGGERED when they should remain PENDING_CONFIRMATION.

    Args:
        h1_setup_status: H1 setup status string from context.
        h1_trigger_type: H1 trigger type string.
        h1_trigger_status: H1 trigger status string.

    Returns:
        True if H1 trigger is confirmed.
    """
    if h1_setup_status == "VALID_SETUP":
        # BOS triggers are confirmed by a valid setup alone.
        # CHoCH triggers need explicit CONFIRMED_TRIGGER status
        # (they must pass through the Path A/B/C lifecycle).
        if h1_trigger_type in ("BULLISH_CHOCH", "BEARISH_CHOCH"):
            return h1_trigger_status == "CONFIRMED_TRIGGER"
        return True
    if h1_trigger_type in ("BULLISH_BOS", "BEARISH_BOS"):
        return h1_trigger_status == "CONFIRMED_TRIGGER"
    return False


def _determine_h1_choch_based(
    h1_trigger_type: str,
) -> bool:
    """Determine if H1 trigger is CHoCH-based.

    Args:
        h1_trigger_type: H1 trigger type string.

    Returns:
        True if H1 trigger is CHoCH-based.
    """
    return h1_trigger_type in ("BULLISH_CHOCH", "BEARISH_CHOCH")


def _determine_geometry_status(
    h1_setup_status: str,
    room_to_target: bool,
    reward_risk_ok: bool,
) -> GeometryStatus:
    """Determine geometry status based on entry plan validity.

    Args:
        h1_setup_status: H1 setup status string.
        room_to_target: Whether there's room to target.
        reward_risk_ok: Whether reward/risk is acceptable.

    Returns:
        GeometryStatus enum value.
    """
    if h1_setup_status == "VALID_SETUP" and room_to_target and reward_risk_ok:
        return GeometryStatus.VALID
    if h1_setup_status == "BLOCKED_BY_LIQUIDITY":
        return GeometryStatus.TEMPORARILY_UNAVAILABLE
    if h1_setup_status == "CONFLICT_WITH_HIGHER_TIMEFRAME":
        return GeometryStatus.PERMANENTLY_INVALID
    return GeometryStatus.TEMPORARILY_UNAVAILABLE


def _determine_lifecycle_status(
    h1_trigger_confirmed: bool,
    h1_trigger_status: str,
    h1_setup_status: str,
) -> SetupLifecycleStatus:
    """Determine lifecycle status based on trigger confirmation.

    Args:
        h1_trigger_confirmed: Whether H1 trigger is confirmed.
        h1_trigger_status: H1 trigger status string.
        h1_setup_status: H1 setup status string.

    Returns:
        SetupLifecycleStatus enum value.
    """
    if h1_trigger_confirmed and h1_setup_status == "VALID_SETUP":
        return SetupLifecycleStatus.TRIGGERED
    if h1_trigger_status in ("EARLY_TRANSITION", "PENDING_CONFIRMATION"):
        return SetupLifecycleStatus.PENDING
    if h1_setup_status == "VALID_SETUP":
        return SetupLifecycleStatus.READY
    if h1_setup_status in ("NO_SETUP", "CONFLICT_WITH_HIGHER_TIMEFRAME"):
        return SetupLifecycleStatus.INVALIDATED
    return SetupLifecycleStatus.PENDING


def grade_setup(
    h1_context: dict[str, Any],
    h4_context: dict[str, Any],
    d1_context: dict[str, Any],
) -> DeterministicSetupState:
    """Grade a trading setup based on multi-timeframe structural analysis.

    This function determines the setup grade, lifecycle status, and geometry
    status purely from structural analysis of the three timeframes. It contains
    no R/R thresholds, calendar logic, or risk policy.

    Args:
        h1_context: H1 analysis context (setup_context from engine).
        h4_context: H4 analysis context (operational_context from engine).
        d1_context: D1 analysis context (strategic_bias from engine).

    Returns:
        DeterministicSetupState with all fields populated.
    """
    # Extract D1 data
    strategic_bias = d1_context.get("strategic_bias") or d1_context
    d1_bias_str = strategic_bias.get("bias", "NEUTRAL")
    d1_direction = _determine_d1_directional(d1_bias_str)
    d1_trade_direction = _determine_trade_direction(d1_bias_str, "NEUTRAL")

    # Extract H4 data
    operational = h4_context.get("operational_context") or h4_context
    h4_alignment = operational.get("alignment_status", "UNKNOWN")
    h4_direction_str = operational.get("preferred_direction", "NEUTRAL")
    if h4_direction_str in ("BULLISH", "BEARISH"):
        h4_trade_direction = TradeDirection(h4_direction_str)
    else:
        h4_trade_direction = TradeDirection.NEUTRAL
    h4_aligned = _determine_h4_aligned(h4_alignment, d1_trade_direction, h4_trade_direction)

    # Extract H1 data
    setup = h1_context.get("setup_context") or h1_context
    h1_setup_status = setup.get("setup_status", "NO_SETUP")
    h1_trigger_event = setup.get("latest_trigger_event") or {}
    h1_trigger_type_str = h1_trigger_event.get("event_type", "NONE")
    h1_trigger_status_str = "CONFIRMED_TRIGGER" if h1_trigger_event else "NO_TRIGGER"
    h1_trigger_confirmed = _determine_h1_trigger_confirmed(
        h1_setup_status, h1_trigger_type_str, h1_trigger_status_str
    )
    h1_choch_based = _determine_h1_choch_based(h1_trigger_type_str)

    # Determine trade direction
    trade_direction = _determine_trade_direction(d1_bias_str, h4_direction_str)

    # Grade determination logic
    if not d1_direction:
        # D1 is neutral — no setup
        setup_classification = SetupClassificationStatus.NO_SETUP
        setup_grade = None
    elif trade_direction == TradeDirection.NEUTRAL:
        # No clear direction
        setup_classification = SetupClassificationStatus.NO_SETUP
        setup_grade = None
    elif not h4_aligned:
        # H4 not aligned with D1 — counter-trend
        setup_classification = SetupClassificationStatus.CLASSIFIED
        setup_grade = SetupGrade.COUNTERTREND
    elif h1_trigger_confirmed and not h1_choch_based:
        # All three aligned: D1 directional, H4 aligned, H1 BOS trigger confirmed
        setup_classification = SetupClassificationStatus.CLASSIFIED
        setup_grade = SetupGrade.AAA
    elif h1_trigger_confirmed and h1_choch_based:
        # Two aligned: D1 directional, H4 aligned, but H1 trigger is CHoCH-based
        setup_classification = SetupClassificationStatus.CLASSIFIED
        setup_grade = SetupGrade.AA
    elif h1_trigger_status_str in ("EARLY_TRANSITION", "PENDING_CONFIRMATION"):
        # H1 trigger pending
        setup_classification = SetupClassificationStatus.CLASSIFIED
        setup_grade = SetupGrade.AA
    else:
        # No valid setup
        setup_classification = SetupClassificationStatus.NO_SETUP
        setup_grade = None

    # Determine geometry and lifecycle
    room_to_target = setup.get("room_to_target_passed", False)
    reward_risk_ok = setup.get("reward_risk_filter_passed", False)
    geometry_status = _determine_geometry_status(h1_setup_status, room_to_target, reward_risk_ok)
    lifecycle_status = _determine_lifecycle_status(
        h1_trigger_confirmed, h1_trigger_status_str, h1_setup_status
    )

    # Map bias strings to BiasLevel enums
    bias_map = {
        "STRONG_BULLISH": BiasLevel.STRONG_BULLISH,
        "BULLISH": BiasLevel.BULLISH,
        "NEUTRAL_BULLISH": BiasLevel.NEUTRAL_BULLISH,
        "NEUTRAL": BiasLevel.NEUTRAL,
        "NEUTRAL_BEARISH": BiasLevel.NEUTRAL_BEARISH,
        "BEARISH": BiasLevel.BEARISH,
        "STRONG_BEARISH": BiasLevel.STRONG_BEARISH,
    }
    d1_bias_enum = bias_map.get(d1_bias_str, BiasLevel.NEUTRAL)
    h4_bias_str = operational.get("parent_daily_bias", d1_bias_str)
    h4_bias_enum = bias_map.get(h4_bias_str, BiasLevel.NEUTRAL)
    h1_bias_str = setup.get("preferred_direction", "NEUTRAL")
    h1_bias_enum = bias_map.get(h1_bias_str, BiasLevel.NEUTRAL)

    # Map trigger type strings to TriggerType enums
    trigger_type_map = {
        "BULLISH_BOS": TriggerType.BULLISH_BOS,
        "BEARISH_BOS": TriggerType.BEARISH_BOS,
        "BULLISH_CHOCH": TriggerType.BULLISH_CHOCH,
        "BEARISH_CHOCH": TriggerType.BEARISH_CHOCH,
        "RECLAIM": TriggerType.RECLAIM,
        "RETEST": TriggerType.RETEST,
        "NONE": TriggerType.NONE,
    }
    h1_trigger_type_enum = trigger_type_map.get(h1_trigger_type_str, TriggerType.NONE)

    # Map trigger status strings to TriggerStatus enums
    trigger_status_map = {
        "CONFIRMED_TRIGGER": TriggerStatus.CONFIRMED_TRIGGER,
        "PENDING_CONFIRMATION": TriggerStatus.PENDING_CONFIRMATION,
        "EARLY_TRANSITION": TriggerStatus.EARLY_TRANSITION,
        "INVALIDATED_TRIGGER": TriggerStatus.INVALIDATED_TRIGGER,
        "NO_TRIGGER": TriggerStatus.NO_TRIGGER,
    }
    h1_trigger_status_enum = trigger_status_map.get(h1_trigger_status_str, TriggerStatus.NO_TRIGGER)

    # Build the DeterministicSetupState
    return DeterministicSetupState(
        # Classification
        setup_classification_status=setup_classification,
        setup_grade=setup_grade,
        trade_direction=trade_direction,
        # Lifecycle
        setup_lifecycle_status=lifecycle_status,
        geometry_status=geometry_status,
        confirmed_at=None,
        confirmed_bar_index=None,
        expires_after_h1_bars=None,
        invalidation_reason=None,
        # D1 timeframe data
        d1_bias=d1_bias_enum,
        d1_direction=d1_trade_direction,
        d1_is_directional=d1_direction,
        d1_structure_status=strategic_bias.get("primary_structure", "UNKNOWN"),
        d1_regime=strategic_bias.get("structure_context", "UNKNOWN") or "UNKNOWN",
        d1_invalidation_status=None,
        # H4 timeframe data
        h4_bias=h4_bias_enum,
        h4_direction=h4_trade_direction,
        h4_alignment_status=h4_alignment,
        h4_structure_status=operational.get("h4_structure", "UNKNOWN"),
        h4_pullback_status=operational.get("h4_internal_structure", {}).get("phase", "UNKNOWN"),
        # H1 timeframe data
        h1_bias=h1_bias_enum,
        h1_direction=trade_direction,
        h1_trigger_type=h1_trigger_type_enum,
        h1_trigger_status=h1_trigger_status_enum,
        h1_setup_status=h1_setup_status,
        # Entry plan
        current_price=None,
        entry_price=None,
        entry_zone_low=None,
        entry_zone_high=None,
        trigger_level=None,
        invalidation_price=None,
        target_price=None,
        estimated_reward_risk=None,
    )
