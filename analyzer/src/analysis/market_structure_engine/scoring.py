from __future__ import annotations

from typing import Any

from .utils import clamp

# Directional vote bonus applied when primary_structure is RANGE but the
# broader structural_bias indicates a dominant direction (e.g. bearish
# consolidation inside a larger downtrend).  Tune this value based on
# historical fixture results.
_STRUCTURAL_BIAS_VOTE = 8


def _directional_votes(
    structure: dict[str, Any],
    events: dict[str, Any],
    indicators: dict[str, Any],
    liquidity: dict[str, Any],
    candle: dict[str, Any],
) -> dict[str, float]:
    bullish = 0.0
    bearish = 0.0
    neutral = 0.0

    primary = structure["primary_structure"]
    if primary == "BULLISH":
        bullish += 35
    elif primary == "BEARISH":
        bearish += 35
    elif primary == "RANGE":
        neutral += 30
        # Structural bias reveals dominant direction even in a local range.
        # This bonus is applied only when primary == "RANGE" to avoid double-
        # counting when the swing classifier already returned BULLISH/BEARISH.
        sb = structure.get("structural_bias")
        if sb == "BEARISH":
            bearish += _STRUCTURAL_BIAS_VOTE
        elif sb == "BULLISH":
            bullish += _STRUCTURAL_BIAS_VOTE
    else:
        neutral += 18

    internal = structure["internal_structure"]["direction"]
    if internal == "BULLISH":
        bullish += 12
    elif internal == "BEARISH":
        bearish += 12
    else:
        neutral += 8

    latest_event = events.get("latest_material_event")
    if latest_event:
        event_type = latest_event["event_type"]
        quality_multiplier = {
            "HIGH_QUALITY": 1.0,
            "MEDIUM_QUALITY": 0.75,
            "LOW_QUALITY": 0.45,
        }.get(latest_event.get("quality"), 0.5)
        event_points = 22 * quality_multiplier
        if "BULLISH" in event_type and not event_type.startswith("FAILED"):
            bullish += event_points
        elif "BEARISH" in event_type and not event_type.startswith("FAILED"):
            bearish += event_points
        elif event_type == "FAILED_BEARISH_BREAKOUT":
            bullish += 8
        elif event_type == "FAILED_BULLISH_BREAKOUT":
            bearish += 8

    alignment = indicators["latest"]["ema_alignment"]
    if alignment == "BULLISH":
        bullish += 10
    elif alignment == "BEARISH":
        bearish += 10
    else:
        neutral += 4

    histogram = indicators["latest"].get("macd_histogram")
    if histogram is not None:
        if histogram > 0:
            bullish += 4
        elif histogram < 0:
            bearish += 4

    latest_liquidity = liquidity.get("latest_event")
    if latest_liquidity and latest_liquidity["event_type"] == "SWEEP_AND_RECLAIM":
        if latest_liquidity["side"] == "SELL_SIDE":
            bullish += 9
        else:
            bearish += 9

    if candle["direction"] == "BULLISH" and candle["body_to_range_ratio"] >= 0.55:
        bullish += 4
    elif candle["direction"] == "BEARISH" and candle["body_to_range_ratio"] >= 0.55:
        bearish += 4

    return {"bullish": bullish, "bearish": bearish, "neutral": neutral}


def calculate_score(
    structure: dict[str, Any],
    events: dict[str, Any],
    indicators: dict[str, Any],
    liquidity: dict[str, Any],
    candle: dict[str, Any],
) -> dict[str, Any]:
    votes = _directional_votes(structure, events, indicators, liquidity, candle)
    directional = votes["bullish"] - votes["bearish"]
    conflict = min(votes["bullish"], votes["bearish"])
    evidence = max(votes["bullish"], votes["bearish"], votes["neutral"])
    confidence = int(round(clamp(55 + evidence * 0.45 - conflict * 0.60, 0, 100)))
    if abs(directional) < 8:
        bias = "NEUTRAL"
    elif directional >= 48:
        bias = "STRONG_BULLISH"
    elif directional >= 18:
        bias = "BULLISH"
    elif directional > 0:
        bias = "NEUTRAL_BULLISH"
    elif directional <= -48:
        bias = "STRONG_BEARISH"
    elif directional <= -18:
        bias = "BEARISH"
    else:
        bias = "NEUTRAL_BEARISH"

    components = {
        # structural_bias affects direction, but local RANGE remains lower-
        # confidence than a confirmed directional swing sequence.
        "structure": min(
            40, 35 if structure["primary_structure"] in ("BULLISH", "BEARISH") else 25
        ),
        "events": min(25, 25 if events.get("latest_material_event") else 8),
        "liquidity": min(15, 15 if liquidity.get("latest_event") else 7),
        "technical": min(12, 12 if indicators["latest"]["ema_alignment"] != "MIXED" else 6),
        "candle": min(8, int(round(8 * candle["body_to_range_ratio"]))),
    }
    assert sum(components.values()) <= 100
    return {
        "bias": bias,
        "confidence_score": confidence,
        "directional_score": round(directional, 4),
        "votes": {key: round(value, 4) for key, value in votes.items()},
        "confidence_components": components,
        "component_maximums": {
            "structure": 40,
            "events": 25,
            "liquidity": 15,
            "technical": 12,
            "candle": 8,
        },
        "maximum_total": 100,
    }
