from __future__ import annotations

from collections import defaultdict
from typing import Any

from .config import TimeframeProfile
from .utils import round_or_none, safe_div, stable_id


def _scope(swing: dict[str, Any]) -> str:
    return "PRIMARY" if swing["classification"] == "MAJOR_STRUCTURAL_SWING" else "INTERNAL"


def _event_type(direction: str, structure_at_start: str) -> tuple[str, str]:
    if structure_at_start not in ("BULLISH", "BEARISH"):
        return f"{direction}_STRUCTURAL_BREAK", "STRUCTURAL_BREAK"
    if direction == "BULLISH":
        return (
            ("BULLISH_BOS", "BOS")
            if structure_at_start == "BULLISH"
            else ("BULLISH_CHOCH", "CHOCH")
        )
    return ("BEARISH_BOS", "BOS") if structure_at_start == "BEARISH" else ("BEARISH_CHOCH", "CHOCH")


def _quality(close_distance_atr: float, body_ratio: float) -> str:
    if close_distance_atr >= 0.25 and body_ratio >= 0.55:
        return "HIGH_QUALITY"
    if close_distance_atr >= 0.08 and body_ratio >= 0.35:
        return "MEDIUM_QUALITY"
    return "LOW_QUALITY"


def _canonicalize(
    events: list[dict[str, Any]],
    max_events: int,
) -> tuple[list[dict[str, Any]], int]:
    grouped: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        key = (
            event["event_index"],
            event["event_type"],
            event["direction"],
            event["structural_scope"],
        )
        grouped[key].append(event)
    canonical: list[dict[str, Any]] = []
    removed = 0
    for key in sorted(grouped):
        candidates = grouped[key]
        removed += len(candidates) - 1
        close = candidates[0]["confirming_close"]
        candidates.sort(
            key=lambda event: (
                0 if event["structural_scope"] == "PRIMARY" else 1,
                abs(close - event["broken_level"]),
                -event["source_swing_index"],
                event["source_swing_id"],
            )
        )
        chosen = dict(candidates[0])
        chosen["source_swing_ids"] = sorted({item["source_swing_id"] for item in candidates})
        chosen["broken_levels"] = sorted({round(item["broken_level"], 10) for item in candidates})
        chosen["merged_event_count"] = len(candidates)
        chosen["event_id"] = stable_id("event", *key, *chosen["source_swing_ids"])
        chosen.pop("source_swing_id", None)
        chosen.pop("source_swing_index", None)
        canonical.append(chosen)
    canonical.sort(key=lambda event: (event["event_index"], event["event_type"], event["event_id"]))
    return canonical[-max_events:], removed


def scan_events(
    bars: list[dict[str, Any]],
    swings: dict[str, Any],
    structure: dict[str, Any],
    atr_series: list[float | None],
    profile: TimeframeProfile,
) -> dict[str, Any]:
    start_index = max(1, len(bars) - profile.event_lookback_bars)
    raw: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []
    usable_swings = [s for s in swings["all"] if s["classification"] != "UNCONFIRMED_SWING"]
    regimes = {
        "PRIMARY": structure.get("previous_primary_structure")
        if structure.get("previous_primary_structure") in ("BULLISH", "BEARISH")
        else structure.get("primary_structure")
        if structure.get("primary_structure") in ("BULLISH", "BEARISH")
        else "UNKNOWN",
        "INTERNAL": structure.get("internal_structure", {}).get("direction", "UNKNOWN"),
    }
    if regimes["INTERNAL"] not in ("BULLISH", "BEARISH"):
        regimes["INTERNAL"] = "UNKNOWN"
    initial_regimes = dict(regimes)

    for swing in usable_swings:
        for index in range(max(start_index, swing["index"] + 1), len(bars)):
            bar = bars[index]
            atr = atr_series[index] or atr_series[index - 1] or max(bar["high"] - bar["low"], 1e-12)
            candle_range = max(bar["high"] - bar["low"], 1e-12)
            body_ratio = abs(bar["close"] - bar["open"]) / candle_range
            if swing["side"] == "HIGH":
                if bar["high"] > swing["price"] and bar["close"] <= swing["price"]:
                    failed.append(
                        {
                            "event_index": index,
                            "event_type": "FAILED_BULLISH_BREAKOUT",
                            "direction": "BULLISH",
                            "structural_scope": _scope(swing),
                            "broken_level": swing["price"],
                            "source_swing_id": swing["swing_id"],
                            "source_swing_index": swing["index"],
                            "timestamp": bar["open_time"],
                            "confirming_close": bar["close"],
                        }
                    )
                    continue
                threshold = swing["price"] + profile.bos_close_buffer_atr * atr
                if bar["close"] > threshold:
                    distance = safe_div(bar["close"] - swing["price"], atr)
                    event_type, classification = _event_type("BULLISH", regimes[_scope(swing)])
                    raw.append(
                        {
                            "event_index": index,
                            "event_type": event_type,
                            "classification": classification,
                            "direction": "BULLISH",
                            "structural_scope": _scope(swing),
                            "broken_level": swing["price"],
                            "source_swing_id": swing["swing_id"],
                            "source_swing_index": swing["index"],
                            "timestamp": bar["open_time"],
                            "confirming_close": bar["close"],
                            "close_distance_atr": round_or_none(distance, 6),
                            "body_ratio": round_or_none(body_ratio, 6),
                            "quality": _quality(distance, body_ratio),
                        }
                    )
                    regimes[_scope(swing)] = "BULLISH"
                    break
            else:
                if bar["low"] < swing["price"] and bar["close"] >= swing["price"]:
                    failed.append(
                        {
                            "event_index": index,
                            "event_type": "FAILED_BEARISH_BREAKOUT",
                            "direction": "BEARISH",
                            "structural_scope": _scope(swing),
                            "broken_level": swing["price"],
                            "source_swing_id": swing["swing_id"],
                            "source_swing_index": swing["index"],
                            "timestamp": bar["open_time"],
                            "confirming_close": bar["close"],
                        }
                    )
                    continue
                threshold = swing["price"] - profile.bos_close_buffer_atr * atr
                if bar["close"] < threshold:
                    distance = safe_div(swing["price"] - bar["close"], atr)
                    event_type, classification = _event_type("BEARISH", regimes[_scope(swing)])
                    raw.append(
                        {
                            "event_index": index,
                            "event_type": event_type,
                            "classification": classification,
                            "direction": "BEARISH",
                            "structural_scope": _scope(swing),
                            "broken_level": swing["price"],
                            "source_swing_id": swing["swing_id"],
                            "source_swing_index": swing["index"],
                            "timestamp": bar["open_time"],
                            "confirming_close": bar["close"],
                            "close_distance_atr": round_or_none(distance, 6),
                            "body_ratio": round_or_none(body_ratio, 6),
                            "quality": _quality(distance, body_ratio),
                        }
                    )
                    regimes[_scope(swing)] = "BEARISH"
                    break

    # A swing is discovered in source order, but break classification is a
    # property of the event timeline. Replaying confirmed events after sorting
    # prevents a later source swing from changing the regime of an earlier bar.
    replay_regimes = {
        "PRIMARY": initial_regimes["PRIMARY"],
        "INTERNAL": initial_regimes["INTERNAL"],
    }
    for event in sorted(
        raw,
        key=lambda item: (item["event_index"], item["source_swing_index"], item["source_swing_id"]),
    ):
        scope = event["structural_scope"]
        event_type, classification = _event_type(event["direction"], replay_regimes[scope])
        event["event_type"] = event_type
        event["classification"] = classification
        replay_regimes[scope] = event["direction"]

    canonical, removed = _canonicalize(raw, profile.max_events_per_category)
    canonical_failed, failed_removed = _canonicalize(failed, profile.max_events_per_category)
    combined = sorted(
        canonical + canonical_failed,
        key=lambda event: (event["event_index"], event["event_type"]),
    )
    primary = [event for event in combined if event["structural_scope"] == "PRIMARY"]
    internal = [event for event in combined if event["structural_scope"] == "INTERNAL"]
    return {
        "all_canonical_events": combined,
        "primary_events": primary,
        "internal_events": internal,
        "failed_breakouts": canonical_failed,
        "event_history": combined,
        "latest_material_event": combined[-1] if combined else None,
        "latest_primary_event": primary[-1] if primary else None,
        "latest_internal_event": internal[-1] if internal else None,
        "deduplication": {
            "raw_event_count": len(raw) + len(failed),
            "canonical_event_count": len(combined),
            "duplicates_removed": removed + failed_removed,
            "key": ["event_index", "event_type", "direction", "structural_scope"],
            "source_traceability_preserved": True,
        },
    }
