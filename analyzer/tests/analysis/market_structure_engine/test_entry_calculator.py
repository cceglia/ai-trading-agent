"""Tests for entry plan calculation and geometry validation (Section 16.4).

Tests the entry_calculator.py module:
- validate_geometry() for BULLISH, BEARISH, NEUTRAL directions
- calculate_risk_reward() directional calculation
- calculate_entry_plan() integration
- Edge cases for zero risk, None prices
"""

from __future__ import annotations

import pytest

from src.analysis.market_structure_engine.entry_calculator import (
    _determine_entry_type,
    _extract_entry_prices,
    calculate_entry_plan,
    calculate_risk_reward,
    validate_geometry,
)
from src.analysis.market_structure_engine.models import (
    EntryType,
    GeometryStatus,
    SetupClassificationStatus,
    SetupRejectionCode,
    TradeDirection,
)

# ============================================================================
# validate_geometry
# ============================================================================


class TestValidateGeometry:
    """validate_geometry checks entry/stop/target ordering by direction."""

    def test_bullish_valid(self) -> None:
        assert (
            validate_geometry(TradeDirection.BULLISH, entry=1.1010, stop=1.0980, target=1.1100)
            is True
        )

    def test_bullish_entry_not_above_stop(self) -> None:
        assert (
            validate_geometry(TradeDirection.BULLISH, entry=1.0980, stop=1.0980, target=1.1100)
            is False
        )

    def test_bullish_target_not_above_entry(self) -> None:
        assert (
            validate_geometry(TradeDirection.BULLISH, entry=1.1010, stop=1.0980, target=1.0990)
            is False
        )

    def test_bearish_valid(self) -> None:
        assert (
            validate_geometry(TradeDirection.BEARISH, entry=1.1010, stop=1.1040, target=1.0920)
            is True
        )

    def test_bearish_entry_not_below_stop(self) -> None:
        assert (
            validate_geometry(TradeDirection.BEARISH, entry=1.1040, stop=1.1040, target=1.0920)
            is False
        )

    def test_bearish_target_not_below_entry(self) -> None:
        assert (
            validate_geometry(TradeDirection.BEARISH, entry=1.1010, stop=1.1040, target=1.1020)
            is False
        )

    def test_neutral_always_false(self) -> None:
        assert validate_geometry(TradeDirection.NEUTRAL, entry=1.0, stop=0.9, target=1.1) is False

    def test_all_equal_returns_false(self) -> None:
        assert validate_geometry(TradeDirection.BULLISH, entry=1.0, stop=1.0, target=1.0) is False


# ============================================================================
# calculate_risk_reward
# ============================================================================


class TestCalculateRiskReward:
    """calculate_risk_reward computes directional R/R ratio."""

    def test_bullish_basic(self) -> None:
        # entry=101, stop=100, target=105
        # risk = 1, reward = 4 → R/R = 4.0
        result = calculate_risk_reward(
            TradeDirection.BULLISH, entry=101.0, stop=100.0, target=105.0
        )
        assert result == pytest.approx(4.0)

    def test_bullish_typical(self) -> None:
        # entry=1.1010, stop=1.0980, target=1.1100
        # risk = 0.0030, reward = 0.0090 → R/R = 3.0
        result = calculate_risk_reward(
            TradeDirection.BULLISH, entry=1.1010, stop=1.0980, target=1.1100
        )
        assert result == pytest.approx(3.0)

    def test_bearish_basic(self) -> None:
        # entry=101, stop=102, target=97
        # risk = 1, reward = 4 → R/R = 4.0
        result = calculate_risk_reward(TradeDirection.BEARISH, entry=101.0, stop=102.0, target=97.0)
        assert result == pytest.approx(4.0)

    def test_bearish_typical(self) -> None:
        # entry=1.1010, stop=1.1040, target=1.0920
        # risk = 0.0030, reward = 0.0090 → R/R = 3.0
        result = calculate_risk_reward(
            TradeDirection.BEARISH, entry=1.1010, stop=1.1040, target=1.0920
        )
        assert result == pytest.approx(3.0)

    def test_neutral_returns_none(self) -> None:
        result = calculate_risk_reward(TradeDirection.NEUTRAL, entry=1.0, stop=0.9, target=1.1)
        assert result is None

    def test_invalid_geometry_returns_none(self) -> None:
        """When validate_geometry returns False, R/R is None."""
        result = calculate_risk_reward(TradeDirection.BULLISH, entry=1.0, stop=1.0, target=1.0)
        assert result is None

    def test_zero_risk_returns_none(self) -> None:
        """R/R cannot be calculated when risk is zero."""
        result = calculate_risk_reward(TradeDirection.BULLISH, entry=1.0, stop=1.0, target=2.0)
        assert result is None  # stopped by validate_geometry first


# ============================================================================
# _determine_entry_type
# ============================================================================


class TestDetermineEntryType:
    """_determine_entry_type classifies entry based on price relationship."""

    def test_entry_above_current_is_stop(self) -> None:
        assert _determine_entry_type(entry_price=1.1010, current_price=1.1000) == EntryType.STOP

    def test_entry_below_current_is_limit(self) -> None:
        assert _determine_entry_type(entry_price=1.0990, current_price=1.1000) == EntryType.LIMIT

    def test_entry_equals_current_is_market(self) -> None:
        assert _determine_entry_type(entry_price=1.1000, current_price=1.1000) == EntryType.MARKET

    def test_entry_none_is_market(self) -> None:
        assert _determine_entry_type(entry_price=None, current_price=1.1000) == EntryType.MARKET

    def test_current_none_is_market(self) -> None:
        assert _determine_entry_type(entry_price=1.1010, current_price=None) == EntryType.MARKET

    def test_both_none_is_market(self) -> None:
        assert _determine_entry_type(entry_price=None, current_price=None) == EntryType.MARKET


# ============================================================================
# _extract_entry_prices
# ============================================================================


class TestExtractEntryPrices:
    """_extract_entry_prices normalizes entry price data."""

    def test_extracts_all_fields(self) -> None:
        data = {
            "current_price": 1.1000,
            "entry_price": 1.1010,
            "entry_zone_low": 1.1005,
            "entry_zone_high": 1.1015,
            "trigger_level": 1.1010,
            "invalidation_price": 1.0980,
            "target_price": 1.1100,
        }
        result = _extract_entry_prices(data)
        assert result["current_price"] == 1.1000
        assert result["entry_price"] == 1.1010
        assert result["entry_zone_low"] == 1.1005
        assert result["entry_zone_high"] == 1.1015
        assert result["trigger_level"] == 1.1010
        assert result["invalidation_price"] == 1.0980
        assert result["target_price"] == 1.1100

    def test_missing_fields_default_to_none(self) -> None:
        result = _extract_entry_prices({})
        assert result["current_price"] is None
        assert result["entry_price"] is None
        assert result["target_price"] is None


# ============================================================================
# calculate_entry_plan
# ============================================================================


class TestCalculateEntryPlan:
    """calculate_entry_plan integration test."""

    def _make_setup_data(
        self,
        *,
        trade_direction: str = "BULLISH",
        entry_price: float = 1.1010,
        stop_price: float = 1.0980,
        target_price: float = 1.1100,
        current_price: float = 1.1000,
        setup_status: str = "VALID_SETUP",
        grade: str = "AAA",
    ) -> dict:
        return {
            "trade_direction": trade_direction,
            "entry_price": entry_price,
            "stop_price": stop_price,
            "target_price": target_price,
            "current_price": current_price,
            "entry_zone_low": 1.1005,
            "entry_zone_high": 1.1015,
            "trigger_level": 1.1010,
            "invalidation_price": 1.0980,
            "setup_classification_status": "CLASSIFIED",
            "setup_grade": grade,
            "setup_lifecycle_status": "TRIGGERED",
            "setup_status": setup_status,
            "h1_setup_status": setup_status,
        }

    def test_bullish_valid_geometry(self) -> None:
        result = calculate_entry_plan(self._make_setup_data())
        assert result.trade_direction == TradeDirection.BULLISH
        assert result.geometry_status == GeometryStatus.VALID
        assert result.estimated_reward_risk == pytest.approx(3.0)  # (0.0090 / 0.0030)
        assert result.entry_type == EntryType.STOP  # entry > current
        assert result.entry_price == 1.1010
        assert result.target_price == 1.1100

    def test_bearish_valid_geometry(self) -> None:
        result = calculate_entry_plan(
            self._make_setup_data(
                trade_direction="BEARISH",
                entry_price=1.1010,
                stop_price=1.1040,
                target_price=1.0920,
            )
        )
        assert result.trade_direction == TradeDirection.BEARISH
        assert result.geometry_status == GeometryStatus.VALID
        assert result.estimated_reward_risk == pytest.approx(3.0)

    def test_invalid_geometry_temporarily_unavailable(self) -> None:
        """When geometry is invalid, status is TEMPORARILY_UNAVAILABLE."""
        result = calculate_entry_plan(
            self._make_setup_data(
                entry_price=1.1010,
                stop_price=1.1010,  # entry == stop → invalid geometry
                target_price=1.1100,
            )
        )
        assert result.geometry_status == GeometryStatus.TEMPORARILY_UNAVAILABLE
        assert result.estimated_reward_risk is None

    def test_missing_prices_handles_gracefully(self) -> None:
        result = calculate_entry_plan({"trade_direction": "BULLISH"})
        assert result.trade_direction == TradeDirection.BULLISH
        assert result.geometry_status == GeometryStatus.TEMPORARILY_UNAVAILABLE
        assert result.estimated_reward_risk is None
        assert result.entry_price is None

    def test_trade_direction_from_string(self) -> None:
        """Entry calculator accepts TradeDirection as string."""
        result = calculate_entry_plan({"trade_direction": "BEARISH"})
        assert result.trade_direction == TradeDirection.BEARISH

    def test_trade_direction_from_enum(self) -> None:
        """Entry calculator accepts TradeDirection as enum."""
        result = calculate_entry_plan({"trade_direction": TradeDirection.BULLISH})
        assert result.trade_direction == TradeDirection.BULLISH

    def test_invalid_trade_direction_returns_rejected_state(self) -> None:
        """Invalid trade direction returns rejected state, not NEUTRAL fallback."""
        result = calculate_entry_plan({"trade_direction": "INVALID"})
        assert result.trade_direction == TradeDirection.NEUTRAL
        assert result.setup_classification_status == SetupClassificationStatus.INSUFFICIENT_DATA
        assert SetupRejectionCode.INVALID_TRADE_DIRECTION in result.rejection_codes

    def test_none_trade_direction_returns_rejected_state(self) -> None:
        """Non-string/enum trade direction returns rejected state."""
        result = calculate_entry_plan({"trade_direction": 12345})
        assert result.trade_direction == TradeDirection.NEUTRAL
        assert result.setup_classification_status == SetupClassificationStatus.INSUFFICIENT_DATA
        assert SetupRejectionCode.INVALID_TRADE_DIRECTION in result.rejection_codes

    def test_preserves_classification_fields(self) -> None:
        data = self._make_setup_data()
        data["setup_classification_status"] = "CLASSIFIED"
        result = calculate_entry_plan(data)
        assert result.setup_classification_status == "CLASSIFIED"
        assert result.setup_grade == "AAA"
        assert result.setup_lifecycle_status == "TRIGGERED"
