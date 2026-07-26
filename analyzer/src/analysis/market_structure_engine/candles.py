from __future__ import annotations

from typing import Any

from .utils import round_or_none, safe_div


def _classify_engulfing(previous: dict[str, Any], current: dict[str, Any]) -> str:
    previous_low = min(previous["open"], previous["close"])
    previous_high = max(previous["open"], previous["close"])
    current_low = min(current["open"], current["close"])
    current_high = max(current["open"], current["close"])
    if (
        current["close"] > current["open"]
        and previous["close"] < previous["open"]
        and current_low <= previous_low
        and current_high >= previous_high
    ):
        return "BULLISH_ENGULFING"
    if (
        current["close"] < current["open"]
        and previous["close"] > previous["open"]
        and current_low <= previous_low
        and current_high >= previous_high
    ):
        return "BEARISH_ENGULFING"
    return "NONE"


def analyze_candles(bars: list[dict[str, Any]], latest_atr: float | None) -> dict[str, Any]:
    current = bars[-1]
    previous = bars[-2]
    candle_range = current["high"] - current["low"]
    body = abs(current["close"] - current["open"])
    upper_wick = current["high"] - max(current["open"], current["close"])
    lower_wick = min(current["open"], current["close"]) - current["low"]
    gap = current["open"] - previous["close"]
    atr = latest_atr or max(candle_range, 1e-12)
    inside = current["high"] <= previous["high"] and current["low"] >= previous["low"]
    outside = current["high"] > previous["high"] and current["low"] < previous["low"]
    return {
        "direction": (
            "BULLISH"
            if current["close"] > current["open"]
            else "BEARISH"
            if current["close"] < current["open"]
            else "DOJI"
        ),
        "range": round_or_none(candle_range),
        "range_atr": round_or_none(safe_div(candle_range, atr), 6),
        "body": round_or_none(body),
        "body_to_range_ratio": round_or_none(safe_div(body, candle_range), 6),
        "upper_wick": round_or_none(upper_wick),
        "lower_wick": round_or_none(lower_wick),
        "upper_wick_ratio": round_or_none(safe_div(upper_wick, candle_range), 6),
        "lower_wick_ratio": round_or_none(safe_div(lower_wick, candle_range), 6),
        "gap_from_previous_close": round_or_none(gap),
        "gap_atr": round_or_none(safe_div(gap, atr), 6),
        "inside_bar": inside,
        "outside_bar": outside,
        "engulfing": _classify_engulfing(previous, current),
        "zero_range": candle_range == 0,
    }
