from __future__ import annotations

import math
from typing import Any

from .utils import safe_div

# --- Constants for structural bias ---
# Number of major swings used for previous-structure classification.
_PREVIOUS_WINDOW_SIZE = 6

# Maximum number of major swings and bars used for structural_bias inference.
_BIAS_WINDOW_SIZE = 12
_BIAS_BAR_LIMIT = 120

# ATR multiples for displacement thresholds.  Asymmetric because high swings
# tend to be more volatile than low swings in trending markets.
_BIAS_HIGH_DISP_ATR = 2.0
_BIAS_LOW_DISP_ATR = 1.0
_BIAS_PRICE_DISP_ATR = 1.5


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


def _can_classify_sequence(swings: list[dict[str, Any]]) -> bool:
    """Require a complete 3-high/3-low window for previous-regime analysis.

    ``_sequence_classification`` operates on the last 3 alternating highs and
    the last 3 alternating lows.  This guard enforces those minimums so that
    the previous-structure window does not produce a classification from
    insufficient data.
    """
    highs = [s for s in swings if s["side"] == "HIGH"]
    lows = [s for s in swings if s["side"] == "LOW"]
    return len(highs) >= 3 and len(lows) >= 3


def _compute_structural_bias(
    primary: str,
    major: list[dict[str, Any]],
    bars: list[dict[str, Any]],
    indicators: dict[str, Any],
) -> str:
    """Infer broader directional context when local structure is non-directional.

    When ``primary_structure`` is RANGE or TRANSITION, this function checks
    swing displacement and price displacement over a wider window (up to
    ``_BIAS_WINDOW_SIZE`` swings, bounded by ``_BIAS_BAR_LIMIT`` bars) to
    determine whether the current consolidation sits inside a larger bearish
    or bullish move.

    When ``primary_structure`` is already BULLISH or BEARISH it returns
    *primary* directly — no inference is needed because the local swing
    classifier already expresses a clear direction.
    """
    if primary in ("BULLISH", "BEARISH"):
        return primary

    atr = indicators.get("latest", {}).get("atr_14")
    if atr is None or not math.isfinite(atr) or atr <= 0:
        return primary

    bias_swings = [
        s for s in major[-_BIAS_WINDOW_SIZE:] if s["index"] >= len(bars) - _BIAS_BAR_LIMIT
    ]
    highs = [s for s in bias_swings if s["side"] == "HIGH"]
    lows = [s for s in bias_swings if s["side"] == "LOW"]

    if len(highs) < 2 or len(lows) < 2:
        return primary

    high_disp = highs[-1]["price"] - highs[0]["price"]
    low_disp = lows[-1]["price"] - lows[0]["price"]

    bias_start = max(0, len(bars) - _BIAS_BAR_LIMIT)
    price_disp = bars[-1]["close"] - bars[bias_start]["close"]

    bearish = (
        high_disp <= -atr * _BIAS_HIGH_DISP_ATR
        and low_disp <= -atr * _BIAS_LOW_DISP_ATR
        and price_disp <= -atr * _BIAS_PRICE_DISP_ATR
    )
    bullish = (
        high_disp >= atr * _BIAS_HIGH_DISP_ATR
        and low_disp >= atr * _BIAS_LOW_DISP_ATR
        and price_disp >= atr * _BIAS_PRICE_DISP_ATR
    )

    if bearish:
        return "BEARISH"
    if bullish:
        return "BULLISH"
    return primary


def _structure_context(primary: str, structural_bias: str) -> str | None:
    """Map local structure + broader bias into a human-readable context label.

    Returns a string like ``"BEARISH_CONSOLIDATION"`` or ``None`` when no
    special context applies (i.e. the primary structure is already
    directional).
    """
    if primary == "RANGE":
        if structural_bias == "BEARISH":
            return "BEARISH_CONSOLIDATION"
        if structural_bias == "BULLISH":
            return "BULLISH_CONSOLIDATION"
        return "NEUTRAL_RANGE"
    if primary == "TRANSITION":
        if structural_bias in ("BULLISH", "BEARISH"):
            return f"{structural_bias}_TRANSITION"
        return "NEUTRAL_TRANSITION"
    return None


def classify_structure(
    bars: list[dict[str, Any]],
    swings: dict[str, Any],
    indicators: dict[str, Any],
) -> dict[str, Any]:
    major = swings["major"]
    primary = _sequence_classification(major) or _coarse_fallback(bars, indicators)

    # --- previous: non-overlapping adjacent window of 6 swings ---
    earlier = major[-2 * _PREVIOUS_WINDOW_SIZE : -_PREVIOUS_WINDOW_SIZE]
    previous = _sequence_classification(earlier) if _can_classify_sequence(earlier) else primary

    # --- structural bias ---
    structural_bias = _compute_structural_bias(primary, major, bars, indicators)

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

    structure_context = _structure_context(primary, structural_bias)

    return {
        "primary_structure": primary,
        "structural_bias": structural_bias,
        "structure_context": structure_context,
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
