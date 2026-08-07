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
        scope_multiplier = {"PRIMARY": 1.0, "INTERNAL": 0.5}.get(
            latest_event.get("structural_scope"), 1.0
        )
        event_points = 22 * quality_multiplier * scope_multiplier
        if "BULLISH" in event_type and not event_type.startswith("FAILED"):
            bullish += event_points
        elif "BEARISH" in event_type and not event_type.startswith("FAILED"):
            bearish += event_points

    # Failed breakouts remain evidence even when a later confirmation becomes
    # the latest material event. Score the bounded canonical failed history
    # separately so the confirmation cannot erase that evidence.
    failed_events = events.get("failed_breakouts", [])
    if not failed_events and latest_event and latest_event["event_type"].startswith("FAILED"):
        # Keep the compact single-event seam backward-compatible while the
        # engine output supplies the full failed history.
        failed_events = [latest_event]
    for failed_event in failed_events:
        scope_multiplier = {"PRIMARY": 1.0, "INTERNAL": 0.5}.get(
            failed_event.get("structural_scope"), 1.0
        )
        failed_points = 8 * scope_multiplier
        if failed_event["event_type"] == "FAILED_BEARISH_BREAKOUT":
            bullish += failed_points
        elif failed_event["event_type"] == "FAILED_BULLISH_BREAKOUT":
            bearish += failed_points

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
    if latest_liquidity and latest_liquidity["event_type"] in (
        "RECLAIMED",
        "RECLAIMED_AGAIN",
        "SWEEP_AND_RECLAIM",
    ):
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

    primary_event = events.get("latest_primary_event")
    internal_event = events.get("latest_internal_event")
    event_evidence = 0.0
    if primary_event and not primary_event["event_type"].startswith("FAILED"):
        event_evidence += 1.0
    if internal_event and not internal_event["event_type"].startswith("FAILED"):
        event_evidence += 0.5
    components = {
        "structure": {
            "normalized": 1.0 if structure["primary_structure"] in ("BULLISH", "BEARISH") else 0.5,
            "weight": 0.30,
        },
        "events": {
            "normalized": min(event_evidence / 1.5, 1.0),
            "weight": 0.30,
            "primary_event_weight": 1.0,
            "internal_event_weight": 0.5,
        },
        "liquidity": {"normalized": 1.0 if liquidity.get("latest_event") else 0.0, "weight": 0.15},
        "technical": {
            "normalized": 1.0 if indicators["latest"]["ema_alignment"] != "MIXED" else 0.5,
            "weight": 0.15,
        },
        "candle": {"normalized": clamp(candle["body_to_range_ratio"], 0.0, 1.0), "weight": 0.10},
    }
    for component in components.values():
        component["contribution"] = round(component["normalized"] * component["weight"], 6)
    confidence_components = {name: dict(value) for name, value in components.items()}
    confidence = int(round(100 * sum(item["contribution"] for item in components.values())))
    return {
        "bias": bias,
        "confidence_score": confidence,
        "directional_score": round(directional, 4),
        "votes": {key: round(value, 4) for key, value in votes.items()},
        "confidence_components": confidence_components,
        "component_maximums": {
            "structure": 30,
            "events": 30,
            "liquidity": 15,
            "technical": 15,
            "candle": 10,
        },
        "maximum_total": 100,
    }
