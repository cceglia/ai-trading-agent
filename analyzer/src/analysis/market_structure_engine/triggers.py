"""CHoCH/BOS trigger classification for the H1 timeframe.

This module implements ``classify_trigger()`` as specified in Section 6 of the
multi-timeframe pipeline redesign plan. It determines the confirmation status
of a price-action trigger event (BOS or CHoCH) based on three confirmation
paths for CHoCH events:

- **Path A** — CHoCH + confirmed retest of the broken level.
- **Path B** — CHoCH + continuation BOS in the same direction.
- **Path C** — CHoCH + sweep-and-reclaim pattern.

BOS events are confirmed immediately when they align with the preferred
direction (from H4 alignment). CHoCH events require additional confirmation
before they qualify for AAA/AA grading.

The module has no external dependencies beyond the models module, following
the Dependency Inversion Principle. It is a pure classification utility with
no side effects.
"""

from __future__ import annotations

from typing import Any

from .models import TriggerStatus, TriggerType

# ---------------------------------------------------------------------------
# Event-type mapping
# ---------------------------------------------------------------------------

_EVENT_TYPE_MAP: dict[str, TriggerType] = {
    "BULLISH_BOS": TriggerType.BULLISH_BOS,
    "BEARISH_BOS": TriggerType.BEARISH_BOS,
    "BULLISH_CHOCH": TriggerType.BULLISH_CHOCH,
    "BEARISH_CHOCH": TriggerType.BEARISH_CHOCH,
    "RECLAIM": TriggerType.RECLAIM,
    "RETEST": TriggerType.RETEST,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _resolve_trigger_type(event_type: str) -> TriggerType:
    """Map a raw event-type string to the corresponding TriggerType enum.

    Returns ``TriggerType.NONE`` for unrecognised event types so that
    callers never receive an unexpected value.
    """
    return _EVENT_TYPE_MAP.get(event_type, TriggerType.NONE)


def _direction_matches(trigger_type: TriggerType, preferred_direction: str) -> bool:
    """Return ``True`` when the trigger direction matches the preferred direction."""
    if preferred_direction == "NEUTRAL":
        return False
    return (
        (trigger_type == TriggerType.BULLISH_BOS and preferred_direction == "BULLISH")
        or (trigger_type == TriggerType.BEARISH_BOS and preferred_direction == "BEARISH")
        or (trigger_type == TriggerType.BULLISH_CHOCH and preferred_direction == "BULLISH")
        or (trigger_type == TriggerType.BEARISH_CHOCH and preferred_direction == "BEARISH")
    )


def _is_bos(trigger_type: TriggerType) -> bool:
    """Return ``True`` when the trigger is a Break-of-Structure event."""
    return trigger_type in (TriggerType.BULLISH_BOS, TriggerType.BEARISH_BOS)


def _is_choch(trigger_type: TriggerType) -> bool:
    """Return ``True`` when the trigger is a Change-of-Character event."""
    return trigger_type in (TriggerType.BULLISH_CHOCH, TriggerType.BEARISH_CHOCH)


# ---------------------------------------------------------------------------
# CHoCH confirmation path detection
# ---------------------------------------------------------------------------


def _check_path_a_confirmed_retest(
    confirmation_events: list[dict[str, Any]],
    trigger_type: TriggerType,
) -> bool:
    """Path A: CHoCH is confirmed by a retest of the broken level.

    A confirmed retest occurs when a subsequent event of type RETEST appears
    in the same direction as the original CHoCH, with quality classification
    MEDIUM_QUALITY or better.
    """
    retest_type = "RETEST"
    for event in confirmation_events:
        if (
            event.get("event_type") == retest_type
            and event.get("direction") == trigger_type.value.split("_")[0]
            and event.get("quality") in ("HIGH_QUALITY", "MEDIUM_QUALITY")
        ):
            return True
    return False


def _check_path_b_continuation_bos(
    confirmation_events: list[dict[str, Any]],
    trigger_type: TriggerType,
) -> bool:
    """Path B: CHoCH is confirmed by a continuation BOS in the same direction.

    A continuation BOS is a BOS event that follows the CHoCH and moves in the
    same direction, confirming the structural shift.
    """
    if trigger_type == TriggerType.BULLISH_CHOCH:
        expected_bos = TriggerType.BULLISH_BOS
    else:
        expected_bos = TriggerType.BEARISH_BOS
    for event in confirmation_events:
        if event.get("event_type") == expected_bos.value:
            return True
    return False


def _check_path_c_sweep_and_reclaim(
    liquidity_events: list[dict[str, Any]],
    trigger_type: TriggerType,
) -> bool:
    """Path C: CHoCH is confirmed by a sweep-and-reclaim pattern.

    A sweep-and-reclaim occurs when price sweeps a key level (liquidity event
    of type SWEEP_AND_RECLAIM) on the side opposite to the trigger direction
    (sell-side sweep for bullish CHoCH, buy-side sweep for bearish CHoCH),
    then closes back beyond the broken level.
    """
    expected_side = "SELL_SIDE" if trigger_type == TriggerType.BULLISH_CHOCH else "BUY_SIDE"
    for event in liquidity_events:
        if event.get("event_type") == "SWEEP_AND_RECLAIM" and event.get("side") == expected_side:
            return True
    return False


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def classify_trigger(
    trigger_event: dict[str, Any] | None,
    preferred_direction: str,
    confirmation_events: list[dict[str, Any]] | None = None,
    liquidity_events: list[dict[str, Any]] | None = None,
) -> tuple[TriggerType, TriggerStatus]:
    """Classify a price-action trigger event and determine its confirmation status.

    Implements the CHoCH/BOS trigger specification from Section 6:

    - BOS aligned → CONFIRMED_TRIGGER (eligible for AAA/AA).
    - CHoCH alone → PENDING_CONFIRMATION (not eligible).
    - CHoCH + confirmed retest (Path A) → CONFIRMED_TRIGGER.
    - CHoCH + continuation BOS (Path B) → CONFIRMED_TRIGGER.
    - CHoCH + sweep and reclaim (Path C) → CONFIRMED_TRIGGER.
    - CHoCH + next candle close only → PENDING_CONFIRMATION.
    - Opposite trigger → INVALIDATED_TRIGGER.

    Args:
        trigger_event: The raw trigger event dict from ``events.scan_events()``.
            Expected keys: ``event_type``, ``direction``, ``quality``, etc.
            Pass ``None`` when no trigger event exists.
        preferred_direction: The preferred trade direction derived from H4
            alignment (``"BULLISH"``, ``"BEARISH"``, or ``"NEUTRAL"``).
        confirmation_events: Optional list of subsequent events that may
            confirm a CHoCH trigger (Paths A and B). Each dict should have
            ``event_type``, ``direction``, and ``quality`` keys.
        liquidity_events: Optional list of liquidity events that may confirm
            a CHoCH trigger (Path C). Each dict should have ``event_type``
            and ``side`` keys.

    Returns:
        A ``(TriggerType, TriggerStatus)`` tuple representing the classified
        trigger type and its confirmation status.
    """
    if trigger_event is None:
        return (TriggerType.NONE, TriggerStatus.NO_TRIGGER)

    event_type_str = trigger_event.get("event_type", "NONE")
    trigger_type = _resolve_trigger_type(event_type_str)

    if trigger_type == TriggerType.NONE:
        return (TriggerType.NONE, TriggerStatus.NO_TRIGGER)

    confirmation_events = confirmation_events or []
    liquidity_events = liquidity_events or []

    # --- BOS classification ---
    if _is_bos(trigger_type):
        if _direction_matches(trigger_type, preferred_direction):
            return (trigger_type, TriggerStatus.CONFIRMED_TRIGGER)
        return (trigger_type, TriggerStatus.INVALIDATED_TRIGGER)

    # --- CHoCH classification ---
    if _is_choch(trigger_type):
        # Opposite direction → invalidated
        if not _direction_matches(trigger_type, preferred_direction):
            return (trigger_type, TriggerStatus.INVALIDATED_TRIGGER)

        # Path A: confirmed retest
        if _check_path_a_confirmed_retest(confirmation_events, trigger_type):
            return (trigger_type, TriggerStatus.CONFIRMED_TRIGGER)

        # Path B: continuation BOS
        if _check_path_b_continuation_bos(confirmation_events, trigger_type):
            return (trigger_type, TriggerStatus.CONFIRMED_TRIGGER)

        # Path C: sweep and reclaim
        if _check_path_c_sweep_and_reclaim(liquidity_events, trigger_type):
            return (trigger_type, TriggerStatus.CONFIRMED_TRIGGER)

        # No confirmation path met → pending (next candle close only)
        return (trigger_type, TriggerStatus.PENDING_CONFIRMATION)

    # --- RECLAIM / RETEST / unknown ---
    return (trigger_type, TriggerStatus.PENDING_CONFIRMATION)
