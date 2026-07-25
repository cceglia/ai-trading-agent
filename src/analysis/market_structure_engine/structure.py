from __future__ import annotations

from typing import Any

from .utils import safe_div


def _alternating_major(swings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for swing in swings:
        if not result or swing["side"] != result[-1]["side"]:
            result.append(swing)
            continue
        previous = result[-1]
        replace = (
            swing["price"] > previous["price"]
            if swing["side"] == "HIGH"
            else swing["price"] < previous["price"]
        )
        if replace:
            result[-1] = swing
    return result


def _sequence_classification(swings: list[dict[str, Any]]) -> str | None:
    alternating = _alternating_major(swings)
    highs = [s for s in alternating if s["side"] == "HIGH"][-3:]
    lows = [s for s in alternating if s["side"] == "LOW"][-3:]
    if len(highs) >= 2 and len(lows) >= 2:
        higher_highs = highs[-1]["price"] > highs[-2]["price"]
        higher_lows = lows[-1]["price"] > lows[-2]["price"]
        lower_highs = highs[-1]["price"] < highs[-2]["price"]
        lower_lows = lows[-1]["price"] < lows[-2]["price"]
        if higher_highs and higher_lows:
            return "BULLISH"
        if lower_highs and lower_lows:
            return "BEARISH"
        if (higher_highs and lower_lows) or (lower_highs and higher_lows):
            return "RANGE"
        return "TRANSITION"
    return None


def _coarse_fallback(bars: list[dict[str, Any]], indicators: dict[str, Any]) -> str:
    closes = [bar["close"] for bar in bars]
    lookback = min(80, len(closes) - 1)
    start = closes[-lookback - 1]
    end = closes[-1]
    atr = indicators["latest"]["atr_14"] or max(abs(end) * 0.001, 1e-12)
    displacement_atr = safe_div(end - start, atr)
    ema_alignment = indicators["latest"]["ema_alignment"]
    if displacement_atr >= 2.0 and ema_alignment == "BULLISH":
        return "BULLISH"
    if displacement_atr <= -2.0 and ema_alignment == "BEARISH":
        return "BEARISH"
    high = max(bar["high"] for bar in bars[-lookback:])
    low = min(bar["low"] for bar in bars[-lookback:])
    location = safe_div(end - low, high - low, 0.5)
    if 0.35 <= location <= 0.65:
        return "RANGE"
    return "TRANSITION"


def classify_structure(
    bars: list[dict[str, Any]],
    swings: dict[str, Any],
    indicators: dict[str, Any],
) -> dict[str, Any]:
    major = swings["major"]
    primary = _sequence_classification(major) or _coarse_fallback(bars, indicators)
    recent_major = [s for s in major if s["index"] >= len(bars) - 160]
    earlier = [
        s for s in major if s["index"] < (recent_major[0]["index"] if recent_major else len(bars))
    ]
    previous = _sequence_classification(earlier) if len(earlier) >= 4 else primary

    internal_source = swings["internal"][-12:] or major[-8:]
    internal_base = _sequence_classification(internal_source)
    if internal_base == "BULLISH":
        internal_direction = "BULLISH"
    elif internal_base == "BEARISH":
        internal_direction = "BEARISH"
    elif internal_base == "RANGE":
        internal_direction = "RANGE"
    else:
        internal_direction = "TRANSITION"

    if primary == "BULLISH" and internal_direction == "BEARISH":
        phase = "PULLBACK"
    elif primary == "BEARISH" and internal_direction == "BULLISH":
        phase = "PULLBACK"
    elif primary in ("BULLISH", "BEARISH") and internal_direction == primary:
        phase = "CONTINUATION"
    elif internal_direction == "RANGE":
        phase = "CONSOLIDATION"
    else:
        phase = "TRANSITION"

    return {
        "primary_structure": primary,
        "previous_primary_structure": previous,
        "internal_structure": {
            "direction": internal_direction,
            "phase": phase,
        },
        "alternating_major_swings": _alternating_major(major)[-12:],
        "classification_method": (
            "SWING_SEQUENCE" if _sequence_classification(major) else "COARSE_FALLBACK"
        ),
    }
