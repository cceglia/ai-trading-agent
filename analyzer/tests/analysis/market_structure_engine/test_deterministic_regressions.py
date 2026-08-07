from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from src.analysis.market_structure_engine.config import get_profile
from src.analysis.market_structure_engine.engine import analyze_snapshot
from src.analysis.market_structure_engine.events import scan_events
from src.analysis.market_structure_engine.levels import build_levels
from src.analysis.market_structure_engine.liquidity import analyze_liquidity


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


def test_liquidity_history_survives_reclaim_and_later_acceptance() -> None:
    bars = [_bar(0, 99), _bar(1, 100, high=101), _bar(2, 101, high=102)]
    swing = _swing(0, "HIGH", 100)
    result = analyze_liquidity(
        bars,
        {"all": [swing], "major": [swing]},
        1.0,
        get_profile("H1"),
    )

    pool = result["pools"][0]
    assert [item["event_type"] for item in pool["event_history"]] == [
        "SWEPT_AND_RECLAIMED",
        "ACCEPTED_BEYOND",
    ]
    assert result["event_history"] == result["events"]
    assert pool["status"] == "ACCEPTED_BEYOND"


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
    ("symbol", "filename"),
    [("GER40.cash", "ohlc-h1-13.json"), ("XAUUSD", "ohlc-h1-14.json")],
)
def test_available_real_h1_fixture_runs_with_configured_formulas(
    symbol: str, filename: str
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
