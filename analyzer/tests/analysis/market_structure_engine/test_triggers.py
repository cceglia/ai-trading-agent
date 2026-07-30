"""Tests for CHoCH/BOS trigger classification (Section 16.5).

Tests the triggers.py module:
- BOS confirmed when aligned with preferred direction
- CHoCH alone → PENDING_CONFIRMATION
- CHoCH + retest (Path A) → CONFIRMED_TRIGGER
- CHoCH + continuation BOS (Path B) → CONFIRMED_TRIGGER
- CHoCH + sweep and reclaim (Path C) → CONFIRMED_TRIGGER
- Opposite direction triggers → INVALIDATED_TRIGGER
"""

from __future__ import annotations

from typing import Any

from src.analysis.market_structure_engine.models import TriggerStatus, TriggerType
from src.analysis.market_structure_engine.triggers import (
    _check_path_a_confirmed_retest,
    _check_path_b_continuation_bos,
    _check_path_c_sweep_and_reclaim,
    _direction_matches,
    _is_bos,
    _is_choch,
    _resolve_trigger_type,
    classify_trigger,
)

# ============================================================================
# _resolve_trigger_type
# ============================================================================


class TestResolveTriggerType:
    def test_bullish_bos(self) -> None:
        assert _resolve_trigger_type("BULLISH_BOS") == TriggerType.BULLISH_BOS

    def test_bearish_bos(self) -> None:
        assert _resolve_trigger_type("BEARISH_BOS") == TriggerType.BEARISH_BOS

    def test_bullish_choch(self) -> None:
        assert _resolve_trigger_type("BULLISH_CHOCH") == TriggerType.BULLISH_CHOCH

    def test_bearish_choch(self) -> None:
        assert _resolve_trigger_type("BEARISH_CHOCH") == TriggerType.BEARISH_CHOCH

    def test_reclaim(self) -> None:
        assert _resolve_trigger_type("RECLAIM") == TriggerType.RECLAIM

    def test_retest(self) -> None:
        assert _resolve_trigger_type("RETEST") == TriggerType.RETEST

    def test_none(self) -> None:
        assert _resolve_trigger_type("NONE") == TriggerType.NONE

    def test_unknown(self) -> None:
        assert _resolve_trigger_type("SOME_UNKNOWN_EVENT") == TriggerType.NONE


# ============================================================================
# _direction_matches
# ============================================================================


class TestDirectionMatches:
    def test_bullish_bos_matches_bullish(self) -> None:
        assert _direction_matches(TriggerType.BULLISH_BOS, "BULLISH") is True

    def test_bearish_bos_matches_bearish(self) -> None:
        assert _direction_matches(TriggerType.BEARISH_BOS, "BEARISH") is True

    def test_bullish_choch_matches_bullish(self) -> None:
        assert _direction_matches(TriggerType.BULLISH_CHOCH, "BULLISH") is True

    def test_bearish_choch_matches_bearish(self) -> None:
        assert _direction_matches(TriggerType.BEARISH_CHOCH, "BEARISH") is True

    def test_bullish_bos_does_not_match_bearish(self) -> None:
        assert _direction_matches(TriggerType.BULLISH_BOS, "BEARISH") is False

    def test_bearish_bos_does_not_match_bullish(self) -> None:
        assert _direction_matches(TriggerType.BEARISH_BOS, "BULLISH") is False

    def test_neutral_direction_never_matches(self) -> None:
        assert _direction_matches(TriggerType.BULLISH_BOS, "NEUTRAL") is False
        assert _direction_matches(TriggerType.BEARISH_CHOCH, "NEUTRAL") is False

    def test_none_trigger_never_matches(self) -> None:
        assert _direction_matches(TriggerType.NONE, "BULLISH") is False


# ============================================================================
# _is_bos / _is_choch
# ============================================================================


class TestIsBos:
    def test_bullish_bos(self) -> None:
        assert _is_bos(TriggerType.BULLISH_BOS) is True

    def test_bearish_bos(self) -> None:
        assert _is_bos(TriggerType.BEARISH_BOS) is True

    def test_choch_not_bos(self) -> None:
        assert _is_bos(TriggerType.BULLISH_CHOCH) is False

    def test_none_not_bos(self) -> None:
        assert _is_bos(TriggerType.NONE) is False


class TestIsChoch:
    def test_bullish_choch(self) -> None:
        assert _is_choch(TriggerType.BULLISH_CHOCH) is True

    def test_bearish_choch(self) -> None:
        assert _is_choch(TriggerType.BEARISH_CHOCH) is True

    def test_bos_not_choch(self) -> None:
        assert _is_choch(TriggerType.BULLISH_BOS) is False

    def test_none_not_choch(self) -> None:
        assert _is_choch(TriggerType.NONE) is False


# ============================================================================
# CHoCH confirmation path helpers
# ============================================================================


class TestCheckPathAConfirmedRetest:
    """Path A: CHoCH confirmed by a retest of the broken level."""

    def test_confirmed_retest_high_quality(self) -> None:
        events: list[dict[str, Any]] = [
            {"event_type": "RETEST", "direction": "BULLISH", "quality": "HIGH_QUALITY"},
        ]
        assert _check_path_a_confirmed_retest(events, TriggerType.BULLISH_CHOCH) is True

    def test_confirmed_retest_medium_quality(self) -> None:
        events: list[dict[str, Any]] = [
            {"event_type": "RETEST", "direction": "BULLISH", "quality": "MEDIUM_QUALITY"},
        ]
        assert _check_path_a_confirmed_retest(events, TriggerType.BULLISH_CHOCH) is True

    def test_low_quality_retest_not_confirmed(self) -> None:
        events: list[dict[str, Any]] = [
            {"event_type": "RETEST", "direction": "BULLISH", "quality": "LOW_QUALITY"},
        ]
        assert _check_path_a_confirmed_retest(events, TriggerType.BULLISH_CHOCH) is False

    def test_wrong_direction_not_confirmed(self) -> None:
        events: list[dict[str, Any]] = [
            {"event_type": "RETEST", "direction": "BEARISH", "quality": "HIGH_QUALITY"},
        ]
        assert _check_path_a_confirmed_retest(events, TriggerType.BULLISH_CHOCH) is False

    def test_no_retest_events(self) -> None:
        assert _check_path_a_confirmed_retest([], TriggerType.BULLISH_CHOCH) is False

    def test_wrong_event_type(self) -> None:
        events: list[dict[str, Any]] = [
            {"event_type": "BULLISH_BOS", "direction": "BULLISH", "quality": "HIGH_QUALITY"},
        ]
        assert _check_path_a_confirmed_retest(events, TriggerType.BULLISH_CHOCH) is False

    def test_bearish_choch_with_bearish_retest(self) -> None:
        events: list[dict[str, Any]] = [
            {"event_type": "RETEST", "direction": "BEARISH", "quality": "HIGH_QUALITY"},
        ]
        assert _check_path_a_confirmed_retest(events, TriggerType.BEARISH_CHOCH) is True


class TestCheckPathBContinuationBos:
    """Path B: CHoCH confirmed by a continuation BOS in the same direction."""

    def test_bullish_choch_with_bullish_bos(self) -> None:
        events: list[dict[str, Any]] = [
            {"event_type": "BULLISH_BOS"},
        ]
        assert _check_path_b_continuation_bos(events, TriggerType.BULLISH_CHOCH) is True

    def test_bearish_choch_with_bearish_bos(self) -> None:
        events: list[dict[str, Any]] = [
            {"event_type": "BEARISH_BOS"},
        ]
        assert _check_path_b_continuation_bos(events, TriggerType.BEARISH_CHOCH) is True

    def test_no_bos_events(self) -> None:
        assert _check_path_b_continuation_bos([], TriggerType.BULLISH_CHOCH) is False

    def test_wrong_direction_bos(self) -> None:
        events: list[dict[str, Any]] = [
            {"event_type": "BEARISH_BOS"},
        ]
        assert _check_path_b_continuation_bos(events, TriggerType.BULLISH_CHOCH) is False

    def test_wrong_event_type(self) -> None:
        events: list[dict[str, Any]] = [
            {"event_type": "RETEST", "direction": "BULLISH"},
        ]
        assert _check_path_b_continuation_bos(events, TriggerType.BULLISH_CHOCH) is False


class TestCheckPathCSweepAndReclaim:
    """Path C: CHoCH confirmed by a sweep-and-reclaim pattern."""

    def test_bullish_choch_with_sell_side_sweep(self) -> None:
        events: list[dict[str, Any]] = [
            {"event_type": "SWEEP_AND_RECLAIM", "side": "SELL_SIDE"},
        ]
        assert _check_path_c_sweep_and_reclaim(events, TriggerType.BULLISH_CHOCH) is True

    def test_bearish_choch_with_buy_side_sweep(self) -> None:
        events: list[dict[str, Any]] = [
            {"event_type": "SWEEP_AND_RECLAIM", "side": "BUY_SIDE"},
        ]
        assert _check_path_c_sweep_and_reclaim(events, TriggerType.BEARISH_CHOCH) is True

    def test_wrong_side_sweep(self) -> None:
        events: list[dict[str, Any]] = [
            {"event_type": "SWEEP_AND_RECLAIM", "side": "BUY_SIDE"},
        ]
        assert _check_path_c_sweep_and_reclaim(events, TriggerType.BULLISH_CHOCH) is False

    def test_no_sweep_events(self) -> None:
        assert _check_path_c_sweep_and_reclaim([], TriggerType.BULLISH_CHOCH) is False

    def test_wrong_event_type(self) -> None:
        events: list[dict[str, Any]] = [
            {"event_type": "RETEST", "side": "SELL_SIDE"},
        ]
        assert _check_path_c_sweep_and_reclaim(events, TriggerType.BULLISH_CHOCH) is False


# ============================================================================
# classify_trigger — public API
# ============================================================================


class TestClassifyTriggerBOS:
    """BOS classification."""

    def test_bullish_bos_aligned_confirmed(self) -> None:
        trigger = {"event_type": "BULLISH_BOS"}
        ttype, tstatus = classify_trigger(trigger, "BULLISH")
        assert ttype == TriggerType.BULLISH_BOS
        assert tstatus == TriggerStatus.CONFIRMED_TRIGGER

    def test_bearish_bos_aligned_confirmed(self) -> None:
        trigger = {"event_type": "BEARISH_BOS"}
        ttype, tstatus = classify_trigger(trigger, "BEARISH")
        assert ttype == TriggerType.BEARISH_BOS
        assert tstatus == TriggerStatus.CONFIRMED_TRIGGER

    def test_bullish_bos_opposite_invalidated(self) -> None:
        trigger = {"event_type": "BULLISH_BOS"}
        ttype, tstatus = classify_trigger(trigger, "BEARISH")
        assert ttype == TriggerType.BULLISH_BOS
        assert tstatus == TriggerStatus.INVALIDATED_TRIGGER

    def test_bearish_bos_opposite_invalidated(self) -> None:
        trigger = {"event_type": "BEARISH_BOS"}
        ttype, tstatus = classify_trigger(trigger, "BULLISH")
        assert ttype == TriggerType.BEARISH_BOS
        assert tstatus == TriggerStatus.INVALIDATED_TRIGGER


class TestClassifyTriggerCHoCH:
    """CHoCH classification with all confirmation paths."""

    def test_choch_alone_pending(self) -> None:
        """CHoCH without any confirmation path → PENDING_CONFIRMATION."""
        trigger = {"event_type": "BULLISH_CHOCH"}
        ttype, tstatus = classify_trigger(trigger, "BULLISH")
        assert ttype == TriggerType.BULLISH_CHOCH
        assert tstatus == TriggerStatus.PENDING_CONFIRMATION

    def test_choch_opposite_direction_invalidated(self) -> None:
        trigger = {"event_type": "BULLISH_CHOCH"}
        ttype, tstatus = classify_trigger(trigger, "BEARISH")
        assert ttype == TriggerType.BULLISH_CHOCH
        assert tstatus == TriggerStatus.INVALIDATED_TRIGGER

    def test_choch_path_a_retest(self) -> None:
        """CHoCH + retest (Path A) → CONFIRMED."""
        trigger = {"event_type": "BULLISH_CHOCH"}
        confirmations = [
            {"event_type": "RETEST", "direction": "BULLISH", "quality": "HIGH_QUALITY"},
        ]
        ttype, tstatus = classify_trigger(trigger, "BULLISH", confirmation_events=confirmations)
        assert tstatus == TriggerStatus.CONFIRMED_TRIGGER

    def test_choch_path_b_continuation_bos(self) -> None:
        """CHoCH + continuation BOS (Path B) → CONFIRMED."""
        trigger = {"event_type": "BULLISH_CHOCH"}
        confirmations = [
            {"event_type": "BULLISH_BOS"},
        ]
        ttype, tstatus = classify_trigger(trigger, "BULLISH", confirmation_events=confirmations)
        assert tstatus == TriggerStatus.CONFIRMED_TRIGGER

    def test_choch_path_c_sweep_and_reclaim(self) -> None:
        """CHoCH + sweep-and-reclaim (Path C) → CONFIRMED."""
        trigger = {"event_type": "BULLISH_CHOCH"}
        liquidity = [
            {"event_type": "SWEEP_AND_RECLAIM", "side": "SELL_SIDE"},
        ]
        ttype, tstatus = classify_trigger(trigger, "BULLISH", liquidity_events=liquidity)
        assert tstatus == TriggerStatus.CONFIRMED_TRIGGER

    def test_bearish_choch_path_a_retest(self) -> None:
        trigger = {"event_type": "BEARISH_CHOCH"}
        confirmations = [
            {"event_type": "RETEST", "direction": "BEARISH", "quality": "HIGH_QUALITY"},
        ]
        ttype, tstatus = classify_trigger(trigger, "BEARISH", confirmation_events=confirmations)
        assert ttype == TriggerType.BEARISH_CHOCH
        assert tstatus == TriggerStatus.CONFIRMED_TRIGGER

    def test_bearish_choch_path_b_continuation_bos(self) -> None:
        trigger = {"event_type": "BEARISH_CHOCH"}
        confirmations = [
            {"event_type": "BEARISH_BOS"},
        ]
        ttype, tstatus = classify_trigger(trigger, "BEARISH", confirmation_events=confirmations)
        assert tstatus == TriggerStatus.CONFIRMED_TRIGGER

    def test_bearish_choch_path_c_sweep(self) -> None:
        trigger = {"event_type": "BEARISH_CHOCH"}
        liquidity = [
            {"event_type": "SWEEP_AND_RECLAIM", "side": "BUY_SIDE"},
        ]
        ttype, tstatus = classify_trigger(trigger, "BEARISH", liquidity_events=liquidity)
        assert tstatus == TriggerStatus.CONFIRMED_TRIGGER


class TestClassifyTriggerNull:
    """None trigger event handling."""

    def test_none_trigger_event(self) -> None:
        ttype, tstatus = classify_trigger(None, "BULLISH")
        assert ttype == TriggerType.NONE
        assert tstatus == TriggerStatus.NO_TRIGGER


class TestClassifyTriggerReclaimRetest:
    """RECLAIM and RETEST trigger types."""

    def test_reclaim_pending(self) -> None:
        trigger = {"event_type": "RECLAIM"}
        ttype, tstatus = classify_trigger(trigger, "BULLISH")
        assert ttype == TriggerType.RECLAIM
        assert tstatus == TriggerStatus.PENDING_CONFIRMATION

    def test_retest_pending(self) -> None:
        trigger = {"event_type": "RETEST"}
        ttype, tstatus = classify_trigger(trigger, "BULLISH")
        assert ttype == TriggerType.RETEST
        assert tstatus == TriggerStatus.PENDING_CONFIRMATION

    def test_unknown_event_type(self) -> None:
        trigger = {"event_type": "UNKNOWN_EVENT"}
        ttype, tstatus = classify_trigger(trigger, "BULLISH")
        assert ttype == TriggerType.NONE
        assert tstatus == TriggerStatus.NO_TRIGGER


class TestClassifyTriggerMultiplePaths:
    """When multiple confirmation events are provided, any one path suffices."""

    def test_path_a_takes_priority_over_pending(self) -> None:
        trigger = {"event_type": "BULLISH_CHOCH"}
        confirmations = [
            {"event_type": "RETEST", "direction": "BULLISH", "quality": "HIGH_QUALITY"},
            {"event_type": "BULLISH_BOS"},
        ]
        ttype, tstatus = classify_trigger(trigger, "BULLISH", confirmation_events=confirmations)
        assert tstatus == TriggerStatus.CONFIRMED_TRIGGER

    def test_path_b_if_path_a_fails(self) -> None:
        trigger = {"event_type": "BULLISH_CHOCH"}
        confirmations = [
            {"event_type": "RETEST", "direction": "BULLISH", "quality": "LOW_QUALITY"},
            {"event_type": "BULLISH_BOS"},
        ]
        ttype, tstatus = classify_trigger(trigger, "BULLISH", confirmation_events=confirmations)
        assert tstatus == TriggerStatus.CONFIRMED_TRIGGER

    def test_path_a_plus_c_both_present(self) -> None:
        trigger = {"event_type": "BULLISH_CHOCH"}
        confirmations = [
            {"event_type": "RETEST", "direction": "BULLISH", "quality": "HIGH_QUALITY"},
        ]
        liquidity = [
            {"event_type": "SWEEP_AND_RECLAIM", "side": "SELL_SIDE"},
        ]
        ttype, tstatus = classify_trigger(
            trigger, "BULLISH", confirmation_events=confirmations, liquidity_events=liquidity
        )
        assert tstatus == TriggerStatus.CONFIRMED_TRIGGER
