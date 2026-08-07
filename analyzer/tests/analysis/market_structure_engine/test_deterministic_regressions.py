from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from src.analysis.market_structure_engine.config import get_profile
from src.analysis.market_structure_engine.context import build_timeframe_context
from src.analysis.market_structure_engine.engine import analyze_snapshot
from src.analysis.market_structure_engine.events import scan_events
from src.analysis.market_structure_engine.levels import build_levels
from src.analysis.market_structure_engine.liquidity import analyze_liquidity
from src.analysis.market_structure_engine.scoring import calculate_score


def _bar(
    index: int, close: float, high: float | None = None, low: float | None = None
) -> dict[str, Any]:
    return {
        "open_time": f"2026-08-07T{index:02d}:00:00+00:00",
        "open": close,
        "high": high if high is not None else close + 0.5,
        "low": low if low is not None else close - 0.5,
        "close": close,
    }


def _swing(
    index: int, side: str, price: float, classification: str = "MAJOR_STRUCTURAL_SWING"
) -> dict[str, Any]:
    return {
        "swing_id": f"s-{side}-{index}",
        "index": index,
        "side": side,
        "price": price,
        "classification": classification,
    }


def test_failed_breakout_remains_history_and_later_confirmation_is_latest() -> None:
    bars = [_bar(0, 99), _bar(1, 99, high=101), _bar(2, 102, high=103)]
    swings = {"all": [_swing(0, "HIGH", 100)], "major": [_swing(0, "HIGH", 100)], "internal": []}
    result = scan_events(
        bars,
        swings,
        {
            "primary_structure": "RANGE",
            "previous_primary_structure": "RANGE",
            "internal_structure": {"direction": "RANGE"},
        },
        [1.0] * len(bars),
        get_profile("H1"),
    )

    assert [item["event_type"] for item in result["event_history"]] == [
        "FAILED_BULLISH_BREAKOUT",
        "BULLISH_STRUCTURAL_BREAK",
    ]
    assert result["latest_material_event"]["event_type"] == "BULLISH_STRUCTURAL_BREAK"
    assert result["failed_breakouts"]


@pytest.mark.parametrize(
    ("side", "failed_bar", "confirmed_bar", "failed_type", "confirmed_type"),
    [
        (
            "HIGH",
            _bar(1, 99, high=101),
            _bar(2, 102, high=103),
            "FAILED_BULLISH_BREAKOUT",
            "BULLISH_STRUCTURAL_BREAK",
        ),
        (
            "LOW",
            _bar(1, 101, low=99),
            _bar(2, 98, low=97),
            "FAILED_BEARISH_BREAKOUT",
            "BEARISH_STRUCTURAL_BREAK",
        ),
    ],
)
def test_failed_breakout_sequences_are_symmetric(
    side: str,
    failed_bar: dict[str, Any],
    confirmed_bar: dict[str, Any],
    failed_type: str,
    confirmed_type: str,
) -> None:
    result = scan_events(
        [_bar(0, 100), failed_bar, confirmed_bar],
        {"all": [_swing(0, side, 100)], "major": [_swing(0, side, 100)], "internal": []},
        {
            "primary_structure": "RANGE",
            "previous_primary_structure": "RANGE",
            "internal_structure": {"direction": "RANGE"},
        },
        [1.0] * 3,
        get_profile("H1"),
    )

    assert [event["event_type"] for event in result["event_history"]] == [
        failed_type,
        confirmed_type,
    ]
    assert result["latest_material_event"]["event_type"] == confirmed_type


def test_failed_only_sequence_keeps_failed_event_latest() -> None:
    result = scan_events(
        [_bar(0, 100), _bar(1, 99, high=101)],
        {"all": [_swing(0, "HIGH", 100)], "major": [], "internal": []},
        {
            "primary_structure": "RANGE",
            "previous_primary_structure": "RANGE",
            "internal_structure": {"direction": "RANGE"},
        },
        [1.0] * 2,
        get_profile("H1"),
    )

    assert result["latest_material_event"]["event_type"] == "FAILED_BULLISH_BREAKOUT"
    assert result["latest_material_event"]["event_index"] == 1


def test_event_classification_replays_regime_per_scope() -> None:
    bars = [_bar(0, 100), _bar(1, 101.2), _bar(2, 102.2)]
    primary = [_swing(0, "HIGH", 100), _swing(1, "HIGH", 101)]
    internal = [
        _swing(0, "HIGH", 100, "INTERNAL_SWING"),
        _swing(1, "HIGH", 101, "INTERNAL_SWING"),
    ]
    result = scan_events(
        bars,
        {"all": primary + internal, "major": primary, "internal": internal},
        {
            "primary_structure": "BEARISH",
            "previous_primary_structure": "BEARISH",
            "internal_structure": {"direction": "BEARISH"},
        },
        [1.0] * len(bars),
        get_profile("H1"),
    )

    primary_types = [event["event_type"] for event in result["primary_events"]]
    internal_types = [event["event_type"] for event in result["internal_events"]]
    assert primary_types == ["BULLISH_CHOCH", "BULLISH_BOS"]
    assert internal_types == ["BULLISH_CHOCH", "BULLISH_BOS"]
    assert {event["structural_scope"] for event in result["primary_events"]} == {"PRIMARY"}
    assert {event["structural_scope"] for event in result["internal_events"]} == {"INTERNAL"}


def test_range_event_is_unclassified_before_later_bos() -> None:
    result = scan_events(
        [_bar(0, 100), _bar(1, 101.2), _bar(2, 102.2)],
        {
            "all": [_swing(0, "HIGH", 100), _swing(1, "HIGH", 101)],
            "major": [_swing(0, "HIGH", 100), _swing(1, "HIGH", 101)],
            "internal": [],
        },
        {
            "primary_structure": "RANGE",
            "previous_primary_structure": "RANGE",
            "internal_structure": {"direction": "RANGE"},
        },
        [1.0] * 3,
        get_profile("H1"),
    )

    assert [event["event_type"] for event in result["primary_events"]] == [
        "BULLISH_STRUCTURAL_BREAK",
        "BULLISH_BOS",
    ]
    assert result["primary_events"][0]["classification"] == "STRUCTURAL_BREAK"


@pytest.mark.parametrize("current_state", ["RANGE", "TRANSITION", "UNKNOWN"])
@pytest.mark.parametrize(
    ("direction", "previous_state", "side", "structural_event", "internal_state"),
    [
        ("BULLISH", "BEARISH", "HIGH", "BULLISH_STRUCTURAL_BREAK", "BEARISH"),
        ("BEARISH", "BULLISH", "LOW", "BEARISH_STRUCTURAL_BREAK", "BULLISH"),
    ],
)
def test_transition_origin_does_not_promote_previous_primary_regime(
    current_state: str,
    direction: str,
    previous_state: str,
    side: str,
    structural_event: str,
    internal_state: str,
) -> None:
    primary_swing = _swing(0, side, 100)
    internal_swing = _swing(0, side, 100, "INTERNAL_SWING")
    result = scan_events(
        [_bar(0, 100), _bar(1, 101.2 if direction == "BULLISH" else 98.8)],
        {
            "all": [primary_swing, internal_swing],
            "major": [primary_swing],
            "internal": [internal_swing],
        },
        {
            "primary_structure": current_state,
            "previous_primary_structure": previous_state,
            "internal_structure": {"direction": internal_state},
        },
        [1.0] * 2,
        get_profile("H1"),
    )

    assert result["primary_events"][0]["event_type"] == structural_event
    assert result["internal_events"][0]["event_type"] == f"{direction}_CHOCH"


def test_event_history_uses_event_id_as_chronological_tiebreak() -> None:
    result = scan_events(
        [_bar(0, 100), _bar(1, 101.2)],
        {
            "all": [_swing(0, "HIGH", 100), _swing(0, "HIGH", 100, "INTERNAL_SWING")],
            "major": [_swing(0, "HIGH", 100)],
            "internal": [_swing(0, "HIGH", 100, "INTERNAL_SWING")],
        },
        {
            "primary_structure": "RANGE",
            "previous_primary_structure": "RANGE",
            "internal_structure": {"direction": "RANGE"},
        },
        [1.0] * 2,
        get_profile("H1"),
    )

    assert result["event_history"] == sorted(
        result["event_history"], key=lambda event: (event["event_index"], event["event_id"])
    )


def test_combined_event_history_applies_limit_after_merging_event_categories() -> None:
    bars = [
        _bar(0, 90),
        _bar(1, 99, high=101),
        _bar(2, 102, high=103),
        _bar(3, 109, high=111),
        _bar(4, 112, high=113),
        _bar(5, 119, high=121),
        _bar(6, 122, high=123),
    ]
    swings = [_swing(0, "HIGH", 100), _swing(2, "HIGH", 110), _swing(4, "HIGH", 120)]
    result = scan_events(
        bars,
        {"all": swings, "major": swings, "internal": []},
        {
            "primary_structure": "RANGE",
            "previous_primary_structure": "RANGE",
            "internal_structure": {"direction": "RANGE"},
        },
        [1.0] * len(bars),
        get_profile("H1", {"max_events_per_category": 2}),
    )

    assert len(result["event_history"]) == 2
    assert [event["event_index"] for event in result["event_history"]] == [5, 6]
    assert [event["event_type"] for event in result["event_history"]] == [
        "FAILED_BULLISH_BREAKOUT",
        "BULLISH_BOS",
    ]
    assert result["latest_material_event"]["event_index"] == 6


def test_latest_scope_events_are_replayed_before_public_history_is_bounded() -> None:
    primary = [_swing(0, "HIGH", 100)]
    internal = [
        _swing(1, "HIGH", 101, "INTERNAL_SWING"),
        _swing(2, "HIGH", 102, "INTERNAL_SWING"),
    ]
    result = scan_events(
        [_bar(0, 99), _bar(1, 101.2), _bar(2, 102.2), _bar(3, 103.2)],
        {"all": primary + internal, "major": primary, "internal": internal},
        {
            "primary_structure": "RANGE",
            "previous_primary_structure": "RANGE",
            "internal_structure": {"direction": "RANGE"},
        },
        [1.0] * 4,
        get_profile("H1", {"max_events_per_category": 2}),
    )

    assert [event["event_index"] for event in result["event_history"]] == [2, 3]
    assert [event["event_index"] for event in result["all_canonical_events"]] == [2, 3]
    assert [event["event_index"] for event in result["internal_events"]] == [2, 3]
    assert [event["event_index"] for event in result["primary_events"]] == [1]
    assert result["latest_primary_event"]["event_index"] == 1
    assert result["latest_internal_event"]["event_index"] == 3


def test_liquidity_history_survives_reclaim_and_later_acceptance() -> None:
    bars = [
        _bar(0, 99),
        _bar(1, 100, high=101),
        _bar(2, 101, high=102),
        _bar(3, 99, high=101),
        _bar(4, 101, high=102),
    ]
    swing = _swing(0, "HIGH", 100)
    result = analyze_liquidity(
        bars,
        {"all": [swing], "major": [swing]},
        1.0,
        get_profile("H1"),
    )

    pool = result["pools"][0]
    assert [item["event_type"] for item in pool["event_history"]] == [
        "RECLAIMED",
        "ACCEPTED_BEYOND",
        "RECLAIMED_AGAIN",
        "ACCEPTED_BEYOND",
    ]
    assert result["event_history"] == result["events"]
    assert pool["status"] == "ACCEPTED_BEYOND"
    assert result["current_state"][pool["pool_id"]] == "ACCEPTED_BEYOND"


@pytest.mark.parametrize(
    ("side", "bars", "expected_history"),
    [
        (
            "HIGH",
            [
                _bar(0, 99),
                _bar(1, 101, high=102),
                _bar(2, 100, high=102),
                _bar(3, 101, high=102),
                _bar(4, 100, high=102),
            ],
            ["SWEPT", "RECLAIMED", "ACCEPTED_BEYOND", "RECLAIMED_AGAIN"],
        ),
        (
            "LOW",
            [
                _bar(0, 101),
                _bar(1, 99, low=98),
                _bar(2, 100, low=98),
                _bar(3, 99, low=98),
                _bar(4, 100, low=98),
            ],
            ["SWEPT", "RECLAIMED", "ACCEPTED_BEYOND", "RECLAIMED_AGAIN"],
        ),
    ],
)
def test_direct_reclaim_is_distinct_from_reclaim_after_acceptance(
    side: str, bars: list[dict[str, Any]], expected_history: list[str]
) -> None:
    swing = _swing(0, side, 100)
    result = analyze_liquidity(
        bars,
        {"all": [swing], "major": [swing]},
        1.0,
        get_profile("H1"),
    )

    pool = result["pools"][0]
    assert [event["event_type"] for event in pool["event_history"]] == expected_history


def test_liquidity_public_histories_are_bounded_after_full_replay() -> None:
    bars = [
        _bar(0, 99),
        _bar(1, 100, high=101),
        _bar(2, 101, high=102),
        _bar(3, 99, high=101),
        _bar(4, 101, high=102),
    ]
    swing = _swing(0, "HIGH", 100)
    result = analyze_liquidity(
        bars,
        {"all": [swing], "major": [swing]},
        1.0,
        get_profile("H1", {"max_events_per_category": 2}),
    )

    pool = result["pools"][0]
    assert [event["event_index"] for event in pool["event_history"]] == [3, 4]
    assert [event["event_index"] for event in result["event_history"]] == [3, 4]
    assert result["latest_event"]["event_index"] == 4
    assert result["current_state"][pool["pool_id"]] == "ACCEPTED_BEYOND"


@pytest.mark.parametrize("event_type", ["RECLAIMED", "RECLAIMED_AGAIN"])
def test_reclaim_evidence_is_consumed_by_context_and_scoring(event_type: str) -> None:
    liquidity_event = {"event_type": event_type, "side": "SELL_SIDE"}
    score = calculate_score(
        {"primary_structure": "RANGE", "internal_structure": {"direction": "RANGE"}},
        {"latest_material_event": None},
        {"latest": {"ema_alignment": "MIXED", "macd_histogram": 0.0}},
        {"latest_event": liquidity_event},
        {"direction": "NEUTRAL", "body_to_range_ratio": 0.3},
    )
    assert score["votes"]["bullish"] == pytest.approx(9.0)

    market = {"symbol": "TEST", "provider": "fixture"}
    parent_context = {
        "D1": {
            "approved_for_decision_agent": True,
            "market": market,
            "strategic_bias": {"bias": "STRONG_BULLISH"},
        },
        "H4": {
            "approved_for_decision_agent": True,
            "market": market,
            "operational_context": {
                "alignment_status": "ALIGNED_CONTINUATION",
                "preferred_direction": "BULLISH",
            },
        },
    }
    context = build_timeframe_context(
        "H1",
        market,
        {
            "primary_structure": "BULLISH",
            "internal_structure": {"phase": "CONTINUATION"},
        },
        {"latest_material_event": None},
        {
            "nearest_support": {"price": 98},
            "nearest_eligible_support": {"price": 98},
            "nearest_resistance": None,
        },
        {"latest_event": liquidity_event, "nearest_buy_side": {"price": 105, "distance_atr": 2}},
        {"latest_close": 100},
        parent_context,
        "PARENT_APPROVED",
    )
    assert context["setup_context"]["setup_status"] == "CONFIRMATION_PENDING"
    assert context["setup_context"]["supportive_liquidity_event"] == liquidity_event


def test_primary_directional_event_is_exactly_twice_internal_event() -> None:
    def score_for_scope(scope: str) -> float:
        result = calculate_score(
            {
                "primary_structure": "RANGE",
                "internal_structure": {"direction": "RANGE"},
            },
            {
                "latest_material_event": {
                    "event_type": "BULLISH_BOS",
                    "quality": "HIGH_QUALITY",
                    "structural_scope": scope,
                }
            },
            {"latest": {"ema_alignment": "MIXED", "macd_histogram": 0.0}},
            {},
            {"direction": "NEUTRAL", "body_to_range_ratio": 0.3},
        )
        return result["votes"]["bullish"]

    primary_points = score_for_scope("PRIMARY")
    internal_points = score_for_scope("INTERNAL")

    assert primary_points == pytest.approx(22.0)
    assert internal_points == pytest.approx(11.0)
    assert primary_points == pytest.approx(internal_points * 2)


def test_failed_breakout_evidence_uses_scope_multiplier() -> None:
    def score_for_scope(scope: str) -> float:
        result = calculate_score(
            {
                "primary_structure": "RANGE",
                "internal_structure": {"direction": "RANGE"},
            },
            {
                "latest_material_event": {
                    "event_type": "FAILED_BEARISH_BREAKOUT",
                    "structural_scope": scope,
                }
            },
            {"latest": {"ema_alignment": "MIXED", "macd_histogram": 0.0}},
            {},
            {"direction": "NEUTRAL", "body_to_range_ratio": 0.3},
        )
        return result["votes"]["bullish"]

    primary_points = score_for_scope("PRIMARY")
    internal_points = score_for_scope("INTERNAL")

    assert primary_points == pytest.approx(8.0)
    assert internal_points == pytest.approx(4.0)
    assert primary_points == pytest.approx(internal_points * 2)


def test_failed_breakout_evidence_is_scored_when_confirmation_is_latest() -> None:
    result = calculate_score(
        {"primary_structure": "RANGE", "internal_structure": {"direction": "RANGE"}},
        {
            "latest_material_event": {
                "event_type": "BULLISH_BOS",
                "quality": "HIGH_QUALITY",
                "structural_scope": "PRIMARY",
            },
            "failed_breakouts": [
                {"event_type": "FAILED_BEARISH_BREAKOUT", "structural_scope": "PRIMARY"}
            ],
        },
        {"latest": {"ema_alignment": "MIXED", "macd_histogram": 0.0}},
        {},
        {"direction": "NEUTRAL", "body_to_range_ratio": 0.3},
    )

    assert result["votes"]["bullish"] == pytest.approx(30.0)


def test_confidence_uses_required_component_weights() -> None:
    result = calculate_score(
        {"primary_structure": "BULLISH", "internal_structure": {"direction": "BULLISH"}},
        {},
        {"latest": {"ema_alignment": "BULLISH", "macd_histogram": 1.0}},
        {"latest_event": {"event_type": "RECLAIMED", "side": "SELL_SIDE"}},
        {"direction": "BULLISH", "body_to_range_ratio": 1.0},
    )

    assert {
        name: component["weight"] for name, component in result["confidence_components"].items()
    } == {
        "structure": 0.30,
        "event": 0.30,
        "liquidity": 0.15,
        "technical": 0.15,
        "candle": 0.10,
    }


def test_unclassified_structural_break_does_not_trigger_h1_setup() -> None:
    market = {"symbol": "TEST", "provider": "fixture"}
    parent_context = {
        "D1": {
            "approved_for_decision_agent": True,
            "market": market,
            "strategic_bias": {"bias": "STRONG_BULLISH"},
        },
        "H4": {
            "approved_for_decision_agent": True,
            "market": market,
            "operational_context": {
                "alignment_status": "ALIGNED_CONTINUATION",
                "preferred_direction": "BULLISH",
            },
        },
    }
    context = build_timeframe_context(
        "H1",
        market,
        {"primary_structure": "BULLISH", "internal_structure": {"phase": "CONTINUATION"}},
        {"latest_material_event": {"event_type": "BULLISH_STRUCTURAL_BREAK"}},
        {
            "nearest_support": {"price": 98},
            "nearest_eligible_support": {"price": 98},
            "nearest_resistance": None,
        },
        {"latest_event": None, "nearest_buy_side": {"price": 105, "distance_atr": 2}},
        {"latest_close": 100},
        parent_context,
        "PARENT_APPROVED",
    )

    assert context["setup_context"]["setup_status"] == "NO_SETUP"


def test_h1_context_does_not_fallback_to_historical_invalidation_level() -> None:
    market = {"symbol": "TEST", "provider": "fixture"}
    parent_context = {
        "D1": {
            "approved_for_decision_agent": True,
            "market": market,
            "strategic_bias": {"bias": "STRONG_BULLISH"},
        },
        "H4": {
            "approved_for_decision_agent": True,
            "market": market,
            "operational_context": {
                "alignment_status": "ALIGNED_CONTINUATION",
                "preferred_direction": "BULLISH",
            },
        },
    }

    context = build_timeframe_context(
        "H1",
        market,
        {"primary_structure": "BULLISH", "internal_structure": {"phase": "CONTINUATION"}},
        {"latest_material_event": {"event_type": "BULLISH_BOS"}},
        {
            "nearest_support": {"price": 98},
            "nearest_resistance": None,
        },
        {"latest_event": None, "nearest_buy_side": {"price": 105, "distance_atr": 2}},
        {"latest_close": 100},
        parent_context,
        "PARENT_APPROVED",
    )

    assert context["setup_context"]["setup_status"] == "BLOCKED_BY_INVALIDATION_LEVEL"
    assert context["setup_context"]["entry_interest_zone"] is None


def test_level_lifecycle_exposes_policy_fields() -> None:
    bars = [_bar(0, 99), _bar(1, 99, high=100), _bar(2, 99)]
    swing = _swing(0, "HIGH", 100)
    result = build_levels(
        bars,
        {"all": [swing], "major": [swing]},
        1.0,
        get_profile("H1"),
    )
    level = result["resistance_levels"][0]
    assert {
        "age_bars",
        "touch_count",
        "break_count",
        "reclaim_count",
        "current_status",
        "freshness",
        "eligible_for_invalidation",
    } <= level.keys()
    assert level["break_count"] == 0
    assert level["freshness"] in ("FRESH", "TESTED")
    assert level["eligible_for_invalidation"] is True


@pytest.mark.parametrize(
    ("symbol", "filename", "expected_close", "failed_level"),
    [
        ("GER40.cash", "ohlc-h1-13.json", 26315.24, None),
        ("XAUUSD", "ohlc-h1-14.json", 4315.98, 4308.84),
    ],
)
def test_available_real_h1_fixture_runs_with_configured_formulas(
    symbol: str, filename: str, expected_close: float, failed_level: float | None
) -> None:
    roots = (Path(__file__).parents[4], Path(__file__).parents[3], Path.cwd())
    path = next(
        (
            root / "data/2026/08/07" / symbol / filename
            for root in roots
            if (root / "data/2026/08/07" / symbol / filename).exists()
        ),
        None,
    )
    if path is None:
        pytest.skip(f"fixture not available in this checkout: {symbol}/{filename}")

    raw = json.loads(path.read_text())
    raw_bars = raw if isinstance(raw, list) else raw.get("bars", raw.get("ohlc", []))
    bars = []
    for item in raw_bars:
        bars.append(
            {
                "open_time": item.get("open_time", item.get("time")),
                "open": item["open"],
                "high": item["high"],
                "low": item["low"],
                "close": item["close"],
                "closed": True,
            }
        )
    assert bars
    assert all(
        set(("open_time", "open", "high", "low", "close", "closed")) <= bar.keys() for bar in bars
    )
    if len(bars) < get_profile("H1").minimum_bars:
        pytest.skip("fixture does not contain the configured H1 minimum history")
    snapshot = {
        "source": {"type": "TRADINGVIEW_MCP"},
        "market": {"symbol": symbol, "provider": "fixture"},
        "timeframe": "H1",
        "requested_timeframe": "H1",
        "returned_timeframe": "H1",
        "retrieved_at": bars[-1]["open_time"],
        "latest_closed_candle_time": bars[-1]["open_time"],
        "candle_closure_verified": True,
        "bars": bars,
    }
    result = analyze_snapshot(snapshot, timeframe="H1")
    assert result["technical_context"]["atr_14"] is not None
    assert (
        result["calculation_metadata"]["profile"]["bos_close_buffer_atr"]
        == get_profile("H1").bos_close_buffer_atr
    )
    history = result["events"]["event_history"]
    assert result["events"]["latest_material_event"]["confirming_close"] == expected_close
    assert any(
        event["event_type"].startswith("FAILED")
        and (failed_level is None or event["broken_level"] == failed_level)
        for event in history
    )
