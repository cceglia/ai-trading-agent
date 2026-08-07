from __future__ import annotations

from typing import Any

import pytest

from src.analysis.market_structure_engine.config import MIN_RR, get_profile
from src.analysis.market_structure_engine.deterministic_validator import DeterministicValidator
from src.analysis.market_structure_engine.entry_calculator import calculate_risk_reward
from src.analysis.market_structure_engine.levels import build_levels
from src.analysis.market_structure_engine.models import (
    DeterministicSetupState,
    EntryType,
    SetupClassificationStatus,
    SetupLifecycleStatus,
    SetupRejectionCode,
    TradeDirection,
)
from src.analysis.market_structure_engine.utils import stable_id


def _bar(
    index: int, close: float, *, high: float | None = None, low: float | None = None
) -> dict[str, Any]:
    return {
        "open_time": f"2026-08-07T{index:02d}:00:00+00:00",
        "open": close,
        "high": high if high is not None else close + 0.25,
        "low": low if low is not None else close - 0.25,
        "close": close,
    }


def _swing() -> dict[str, Any]:
    return {
        "swing_id": "s-high-0",
        "index": 0,
        "side": "HIGH",
        "price": 100.0,
        "classification": "MAJOR_STRUCTURAL_SWING",
    }


def _level(bars: list[dict[str, Any]]) -> dict[str, Any]:
    result = build_levels(
        bars,
        {"all": [_swing()], "major": [_swing()]},
        1.0,
        get_profile("H1"),
    )
    return result["resistance_levels"][0]


def test_level_lifecycle_precedence_and_accepted_beyond_block() -> None:
    stale = _level([_bar(index, 99.0) for index in range(102)])
    assert stale["current_status"] == "STALE"
    assert stale["eligible_for_invalidation"] is False

    broken = _level([_bar(0, 99.0), _bar(1, 101.0), _bar(2, 101.0)])
    assert broken["current_status"] == "BROKEN"
    assert broken["accepted_beyond"] is True
    assert broken["eligible_for_invalidation"] is False

    reclaimed = _level([_bar(0, 99.0), _bar(1, 101.0), _bar(2, 99.0)])
    assert reclaimed["current_status"] == "RECLAIMED"
    assert reclaimed["reclaim_count"] == 1
    assert reclaimed["eligible_for_invalidation"] is False


def test_levels_block_when_only_one_directional_candidate_is_eligible() -> None:
    result = build_levels(
        [_bar(0, 99.0), _bar(1, 99.0, high=100.0)],
        {"all": [_swing()], "major": [_swing()]},
        1.0,
        get_profile("H1"),
    )

    assert result["nearest_eligible_resistance"] is not None
    assert result["nearest_eligible_support"] is None
    assert result["invalidation_blocker"] == "NO_ELIGIBLE_INVALIDATION_LEVEL"


def test_clustered_level_id_uses_serialized_rounded_price() -> None:
    swings = [
        {
            "swing_id": "s-high-1",
            "index": 0,
            "side": "HIGH",
            "price": 100.000000004,
            "classification": "MAJOR_STRUCTURAL_SWING",
        },
        {
            "swing_id": "s-high-2",
            "index": 1,
            "side": "HIGH",
            "price": 100.000000005,
            "classification": "MAJOR_STRUCTURAL_SWING",
        },
    ]
    level = build_levels(
        [_bar(0, 99.0), _bar(1, 99.0)],
        {"all": swings, "major": swings},
        1.0,
        get_profile("H1"),
    )["resistance_levels"][0]

    expected_id = stable_id(
        "level",
        "HIGH",
        f"{level['price']:.10f}",
        "s-high-1",
        "s-high-2",
    )
    assert level["price"] == 100.0
    assert level["level_id"] == expected_id


@pytest.mark.parametrize(
    ("direction", "entry", "stop", "target", "expected"),
    [
        (TradeDirection.BULLISH, 101.0, 100.0, 102.99, 1.99),
        (TradeDirection.BULLISH, 101.0, 100.0, 103.0, 2.0),
        (TradeDirection.BEARISH, 101.0, 102.0, 99.01, 1.99),
        (TradeDirection.BEARISH, 101.0, 102.0, 99.0, 2.0),
    ],
)
def test_directional_rr_uses_canonical_boundary(
    direction: TradeDirection,
    entry: float,
    stop: float,
    target: float,
    expected: float,
) -> None:
    ratio = calculate_risk_reward(direction, entry, stop, target)
    assert ratio == pytest.approx(expected)
    assert (ratio is not None and ratio >= MIN_RR) is (expected >= MIN_RR)


def _validator_setup(**overrides: object) -> DeterministicSetupState:
    values: dict[str, object] = {
        "setup_classification_status": SetupClassificationStatus.CLASSIFIED,
        "setup_lifecycle_status": SetupLifecycleStatus.TRIGGERED,
        "trade_direction": TradeDirection.BULLISH,
        "current_price": 100.0,
        "entry_price": 101.0,
        "invalidation_price": 99.0,
        "target_price": 105.0,
        "estimated_reward_risk": 2.0,
        "entry_type": EntryType.STOP,
        "invalidation_level_id": stable_id("level", "LOW", "99.0000000000", "s-1"),
        "invalidation_timeframe": "H1",
    }
    values.update(overrides)
    return DeterministicSetupState(**values)


def _validator_level(**overrides: object) -> dict[str, object]:
    level: dict[str, object] = {
        "level_id": stable_id("level", "LOW", "99.0000000000", "s-1"),
        "side": "LOW",
        "price": 99.0,
        "source_swing_ids": ["s-1"],
        "eligible_for_invalidation": True,
        "current_status": "FRESH",
        "freshness": "FRESH",
        "age_bars": 1,
        "touch_count": 1,
        "break_count": 0,
        "reclaim_count": 0,
        "accepted_beyond_count": 0,
        "accepted_beyond": False,
    }
    level.update(overrides)
    return level


def _validator_result(
    *,
    level: dict[str, object] | None = None,
    setup: DeterministicSetupState | None = None,
) -> object:
    return DeterministicValidator().validate(
        setup=setup or _validator_setup(),
        structure_analysis={
            "timeframes": {
                "H1": {
                    "source_audit": {"candle_closure_verified": True},
                    "events": {"event_history": []},
                    "levels": {
                        "support_levels": [level or _validator_level()],
                        "resistance_levels": [],
                    },
                }
            }
        },
    )


def test_validator_requires_non_negative_integer_touch_count_on_selected_level() -> None:
    for value in (None, -1, 1.5, "1"):
        level = _validator_level()
        if value is None:
            del level["touch_count"]
        else:
            level["touch_count"] = value

        result = _validator_result(level=level)

        assert result.validation_status == "INVALID"
        assert "INVALIDATION_LEVEL_TOUCH_COUNT_INVALID" in result.reason_codes


@pytest.mark.parametrize("age_bars", (-1, 1.5, float("nan"), float("inf"), "1"))
def test_validator_rejects_malformed_level_age(age_bars: object) -> None:
    result = _validator_result(level=_validator_level(age_bars=age_bars))

    assert result.validation_status == "INVALID"
    assert "INVALIDATION_LEVEL_AGE_INVALID" in result.reason_codes


def test_validator_rejects_level_age_over_timeframe_limit_with_stable_code() -> None:
    result = _validator_result(level=_validator_level(age_bars=101))

    assert result.validation_status == "INVALID"
    assert "INVALIDATION_LEVEL_AGE_LIMIT_EXCEEDED" in result.reason_codes


def test_validator_accepts_over_age_historical_level_with_valid_selected_level() -> None:
    historical = _validator_level(
        level_id=stable_id("level", "LOW", "98.0000000000", "s-old"),
        price=98.0,
        source_swing_ids=["s-old"],
        eligible_for_invalidation=False,
        current_status="STALE",
        freshness="STALE",
        age_bars=101,
    )
    result = DeterministicValidator().validate(
        setup=_validator_setup(),
        structure_analysis={
            "timeframes": {
                "H1": {
                    "source_audit": {"candle_closure_verified": True},
                    "events": {"event_history": []},
                    "levels": {
                        "support_levels": [_validator_level(), historical],
                        "resistance_levels": [],
                    },
                }
            }
        },
    )

    assert result.validation_status == "VALID"
    assert "INVALIDATION_LEVEL_AGE_LIMIT_EXCEEDED" not in result.reason_codes


def test_validator_accepts_no_setup_with_over_age_historical_level() -> None:
    result = DeterministicValidator().validate(
        setup=_validator_setup(
            setup_classification_status=SetupClassificationStatus.NO_SETUP,
            rejection_codes=(SetupRejectionCode.TRIGGER_NOT_CONFIRMED,),
            invalidation_price=None,
            invalidation_level_id=None,
            invalidation_timeframe=None,
        ),
        structure_analysis={
            "timeframes": {
                "H1": {
                    "source_audit": {"candle_closure_verified": True},
                    "events": {"event_history": []},
                    "levels": {
                        "support_levels": [
                            _validator_level(
                                eligible_for_invalidation=False,
                                current_status="STALE",
                                freshness="STALE",
                                age_bars=101,
                            )
                        ],
                        "resistance_levels": [],
                    },
                }
            }
        },
    )

    assert result.validation_status == "VALID"
    assert "INVALIDATION_LEVEL_AGE_LIMIT_EXCEEDED" not in result.reason_codes


@pytest.mark.parametrize(
    ("setup_update", "reason_code"),
    [
        (
            {"trade_direction": TradeDirection.BULLISH, "invalidation_price": 102.0},
            "INVALID_LONG_GEOMETRY",
        ),
        (
            {
                "trade_direction": TradeDirection.BEARISH,
                "entry_price": 101.0,
                "invalidation_price": 100.0,
            },
            "INVALID_SHORT_GEOMETRY",
        ),
    ],
)
def test_validator_returns_stable_directional_geometry_reason_codes(
    setup_update: dict[str, object], reason_code: str
) -> None:
    result = _validator_result(setup=_validator_setup(**setup_update))

    assert result.validation_status == "INVALID"
    assert reason_code in result.reason_codes


@pytest.mark.parametrize(
    ("setup_update", "reason_code"),
    [
        (
            {"current_price": 100.0, "entry_price": 99.0, "entry_type": EntryType.STOP},
            "LONG_ENTRY_PRICE_VIOLATION",
        ),
        (
            {"current_price": 100.0, "entry_price": 101.0, "entry_type": EntryType.LIMIT},
            "LONG_ENTRY_PRICE_VIOLATION",
        ),
        (
            {
                "trade_direction": TradeDirection.BEARISH,
                "current_price": 100.0,
                "entry_price": 101.0,
                "entry_type": EntryType.STOP,
            },
            "SHORT_ENTRY_PRICE_VIOLATION",
        ),
        (
            {
                "trade_direction": TradeDirection.BEARISH,
                "current_price": 100.0,
                "entry_price": 99.0,
                "entry_type": EntryType.LIMIT,
            },
            "SHORT_ENTRY_PRICE_VIOLATION",
        ),
    ],
)
def test_validator_returns_stable_directional_entry_reason_codes(
    setup_update: dict[str, object], reason_code: str
) -> None:
    result = _validator_result(setup=_validator_setup(**setup_update))

    assert result.validation_status == "INVALID"
    assert reason_code in result.reason_codes
