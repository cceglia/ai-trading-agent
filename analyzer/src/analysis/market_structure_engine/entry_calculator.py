"""Entry plan calculation for the multi-timeframe pipeline.

This module implements the entry plan calculation as specified in Section 7 of
the multi-timeframe pipeline redesign plan. It determines:

- Entry price, stop loss, and take profit levels
- Geometry validation for the trade direction
- Reward-to-risk ratio calculation

The entry prices are deterministic — computed from the engine's structural
analysis, not from LLM output. This module depends only on the models module
for type definitions, following the Dependency Inversion Principle.
"""

from __future__ import annotations

import logging
from typing import Any

from .errors import InvalidTradeDirectionError
from .models import (
    DeterministicSetupState,
    EntryType,
    GeometryStatus,
    SetupClassificationStatus,
    SetupRejectionCode,
    TradeDirection,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Geometry validation
# ---------------------------------------------------------------------------


def validate_geometry(
    trade_direction: TradeDirection,
    entry: float,
    stop: float,
    target: float,
) -> bool:
    """Validate that geometry is correct for the trade direction.

    For BULLISH: entry > stop, target > entry
    For BEARISH: entry < stop, target < entry
    For NEUTRAL: always returns False (no valid geometry)

    Args:
        trade_direction: Direction of the trade.
        entry: Entry price level.
        stop: Stop loss price level.
        target: Take profit price level.

    Returns:
        True if geometry is valid for the trade direction, False otherwise.
    """
    if trade_direction == TradeDirection.BULLISH:
        return entry > stop and target > entry
    if trade_direction == TradeDirection.BEARISH:
        return entry < stop and target < entry
    return False


# ---------------------------------------------------------------------------
# Risk/Reward calculation
# ---------------------------------------------------------------------------


def calculate_risk_reward(
    trade_direction: TradeDirection,
    entry: float,
    stop: float,
    target: float,
) -> float | None:
    """Calculate the reward-to-risk ratio directionally.

    For BULLISH: risk = entry - stop, reward = target - entry
    For BEARISH: risk = stop - entry, reward = entry - target

    Returns None if geometry is invalid or risk <= 0.

    Args:
        trade_direction: Direction of the trade.
        entry: Entry price level.
        stop: Stop loss price level.
        target: Take profit price level.

    Returns:
        The reward-to-risk ratio, or None if calculation is not possible.
    """
    if not validate_geometry(trade_direction, entry, stop, target):
        return None

    if trade_direction == TradeDirection.BULLISH:
        risk = entry - stop
        reward = target - entry
    elif trade_direction == TradeDirection.BEARISH:
        risk = stop - entry
        reward = entry - target
    else:
        return None

    if risk <= 0:
        return None

    return reward / risk


# ---------------------------------------------------------------------------
# Entry plan calculation
# ---------------------------------------------------------------------------


def _extract_entry_prices(setup_data: dict[str, Any]) -> dict[str, Any]:
    """Extract and normalize entry price data from setup context.

    Args:
        setup_data: Raw entry data from structure analysis.

    Returns:
        Dictionary with normalized entry price fields.
    """
    return {
        "current_price": setup_data.get("current_price"),
        "entry_price": setup_data.get("entry_price"),
        "entry_zone_low": setup_data.get("entry_zone_low"),
        "entry_zone_high": setup_data.get("entry_zone_high"),
        "trigger_level": setup_data.get("trigger_level"),
        "invalidation_price": setup_data.get("invalidation_price"),
        "target_price": setup_data.get("target_price"),
    }


def _determine_entry_type(
    entry_price: float | None,
    current_price: float | None,
) -> EntryType:
    """Determine the entry type based on price relationship.

    Args:
        entry_price: Target entry price.
        current_price: Current market price.

    Returns:
        EntryType enum value.
    """
    if entry_price is None or current_price is None:
        return EntryType.MARKET
    if entry_price > current_price:
        return EntryType.STOP
    if entry_price < current_price:
        return EntryType.LIMIT
    return EntryType.MARKET


def calculate_entry_plan(setup_data: dict[str, Any]) -> DeterministicSetupState:
    """Calculate entry plan from raw setup data.

    Accepts the raw entry data from the structure analysis, validates geometry,
    calculates R/R, and returns a DeterministicSetupState with entry plan
    fields populated.

    When the trade direction is invalid, returns a rejected state with
    ``INSUFFICIENT_DATA`` classification and an ``INVALID_TRADE_DIRECTION``
    rejection code instead of raising.

    Args:
        setup_data: Raw entry data from structure analysis. Expected keys:
            - trade_direction: TradeDirection enum or string
            - entry_price: Target entry price
            - stop_price: Stop loss price
            - target_price: Take profit price
            - current_price: Current market price
            - entry_zone_low: Lower bound of entry zone
            - entry_zone_high: Upper bound of entry zone
            - trigger_level: Price level for trigger
            - invalidation_price: Price that invalidates the setup
            - setup_classification_status: SetupClassificationStatus or string
            - setup_grade: SetupGrade or string
            - geometry_status: GeometryStatus or string
            - And other DeterministicSetupState fields

    Returns:
        DeterministicSetupState with entry plan fields populated, or a
        rejected state when the trade direction is invalid.
    """
    try:
        return _calculate_entry_plan_inner(setup_data)
    except InvalidTradeDirectionError as exc:
        logger.error("Invalid trade direction: %s", exc)
        return DeterministicSetupState(
            setup_classification_status=SetupClassificationStatus.INSUFFICIENT_DATA,
            trade_direction=TradeDirection.NEUTRAL,
            rejection_codes=(SetupRejectionCode.INVALID_TRADE_DIRECTION,),
        )


def _calculate_entry_plan_inner(setup_data: dict[str, Any]) -> DeterministicSetupState:
    """Inner implementation that may raise InvalidTradeDirectionError."""
    # Extract trade direction
    trade_dir_raw = setup_data.get("trade_direction", TradeDirection.NEUTRAL)
    if isinstance(trade_dir_raw, TradeDirection):
        trade_direction = trade_dir_raw
    elif isinstance(trade_dir_raw, str):
        try:
            trade_direction = TradeDirection(trade_dir_raw)
        except (TypeError, ValueError) as exc:
            raise InvalidTradeDirectionError(
                f"Unsupported trade direction: {trade_dir_raw!r}"
            ) from exc
    else:
        raise InvalidTradeDirectionError(
            f"Unsupported trade direction type: {type(trade_dir_raw).__name__}"
        )

    # Extract entry prices
    prices = _extract_entry_prices(setup_data)
    entry_price = prices["entry_price"]
    stop_price = setup_data.get("stop_price")
    target_price = prices["target_price"]
    current_price = prices["current_price"]

    # Validate geometry
    geometry_valid = False
    if (
        entry_price is not None
        and stop_price is not None
        and target_price is not None
        and trade_direction != TradeDirection.NEUTRAL
    ):
        geometry_valid = validate_geometry(trade_direction, entry_price, stop_price, target_price)

    # Calculate R/R
    reward_risk = None
    if (
        geometry_valid
        and entry_price is not None
        and stop_price is not None
        and target_price is not None
    ):
        reward_risk = calculate_risk_reward(trade_direction, entry_price, stop_price, target_price)

    # Determine geometry status
    if geometry_valid:
        geometry_status = GeometryStatus.VALID
    else:
        geometry_status = GeometryStatus.TEMPORARILY_UNAVAILABLE

    # Determine entry type
    entry_type = _determine_entry_type(entry_price, current_price)

    # Extract classification fields with defaults
    setup_classification_status = setup_data.get("setup_classification_status", "NO_SETUP")
    setup_grade = setup_data.get("setup_grade")
    lifecycle_status = setup_data.get("setup_lifecycle_status", "PENDING")

    # Build and return the DeterministicSetupState
    return DeterministicSetupState(
        # Classification
        setup_classification_status=setup_classification_status,
        setup_grade=setup_grade,
        trade_direction=trade_direction,
        # Lifecycle
        setup_lifecycle_status=lifecycle_status,
        geometry_status=geometry_status,
        confirmed_at=setup_data.get("confirmed_at"),
        confirmed_bar_index=setup_data.get("confirmed_bar_index"),
        expires_after_h1_bars=setup_data.get("expires_after_h1_bars"),
        invalidation_reason=setup_data.get("invalidation_reason"),
        # D1 timeframe data
        d1_bias=setup_data.get("d1_bias", "NEUTRAL"),
        d1_direction=setup_data.get("d1_direction", "NEUTRAL"),
        d1_is_directional=setup_data.get("d1_is_directional", False),
        d1_structure_status=setup_data.get("d1_structure_status", "UNKNOWN"),
        d1_regime=setup_data.get("d1_regime", "UNKNOWN"),
        d1_invalidation_status=setup_data.get("d1_invalidation_status"),
        # H4 timeframe data
        h4_bias=setup_data.get("h4_bias", "NEUTRAL"),
        h4_direction=setup_data.get("h4_direction", "NEUTRAL"),
        h4_alignment_status=setup_data.get("h4_alignment_status", "UNKNOWN"),
        h4_structure_status=setup_data.get("h4_structure_status", "UNKNOWN"),
        h4_pullback_status=setup_data.get("h4_pullback_status", "UNKNOWN"),
        # H1 timeframe data
        h1_bias=setup_data.get("h1_bias", "NEUTRAL"),
        h1_direction=setup_data.get("h1_direction", "NEUTRAL"),
        h1_trigger_type=setup_data.get("h1_trigger_type", "NONE"),
        h1_trigger_status=setup_data.get("h1_trigger_status", "NO_TRIGGER"),
        h1_setup_status=setup_data.get("h1_setup_status", "UNKNOWN"),
        # Entry plan
        current_price=current_price,
        entry_type=entry_type,
        entry_price=entry_price,
        entry_zone_low=prices["entry_zone_low"],
        entry_zone_high=prices["entry_zone_high"],
        trigger_level=prices["trigger_level"],
        invalidation_price=prices["invalidation_price"],
        target_price=target_price,
        estimated_reward_risk=reward_risk,
    )
