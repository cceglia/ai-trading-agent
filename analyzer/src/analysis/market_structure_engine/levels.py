from __future__ import annotations

from typing import Any

from .config import MAX_LEVEL_AGE, TimeframeProfile
from .utils import canonical_level_id, round_or_none, safe_div


def _cluster_side(
    swings: list[dict[str, Any]],
    side: str,
    atr: float,
    tolerance_atr: float,
) -> list[dict[str, Any]]:
    selected = sorted(
        (s for s in swings if s["side"] == side),
        key=lambda s: (s["price"], s["index"]),
    )
    clusters: list[list[dict[str, Any]]] = []
    for swing in selected:
        if not clusters:
            clusters.append([swing])
            continue
        center = sum(item["price"] for item in clusters[-1]) / len(clusters[-1])
        if abs(swing["price"] - center) <= tolerance_atr * atr:
            clusters[-1].append(swing)
        else:
            clusters.append([swing])
    output: list[dict[str, Any]] = []
    for members in clusters:
        prices = [item["price"] for item in members]
        center = sum(prices) / len(prices)
        output.append(
            {
                "level_id": canonical_level_id(side, center, [m["swing_id"] for m in members]),
                "side": side,
                "price": round_or_none(center),
                "zone_low": round_or_none(min(prices)),
                "zone_high": round_or_none(max(prices)),
                "touch_count": len(members),
                "source_swing_ids": [item["swing_id"] for item in members],
                "first_index": min(item["index"] for item in members),
                "last_index": max(item["index"] for item in members),
                "structural_importance": (
                    "MAJOR"
                    if any(item["classification"] == "MAJOR_STRUCTURAL_SWING" for item in members)
                    else "INTERNAL"
                ),
                "temporally_distinct_swings_preserved": (
                    len({item["index"] for item in members}) == len(members)
                ),
            }
        )
    return output


def build_levels(
    bars: list[dict[str, Any]],
    swings: dict[str, Any],
    latest_atr: float,
    profile: TimeframeProfile,
) -> dict[str, Any]:
    atr = latest_atr or max(bars[-1]["high"] - bars[-1]["low"], 1e-12)
    confirmed = [s for s in swings["all"] if s["classification"] != "UNCONFIRMED_SWING"]
    resistance = _cluster_side(confirmed, "HIGH", atr, profile.level_cluster_tolerance_atr)
    support = _cluster_side(confirmed, "LOW", atr, profile.level_cluster_tolerance_atr)
    close = bars[-1]["close"]

    for level in resistance + support:
        level["age_bars"] = max(0, len(bars) - 1 - level["last_index"])
        level["break_count"] = 0
        level["reclaim_count"] = 0
        level["accepted_beyond_count"] = 0
        level["accepted_beyond"] = False
        touches = len(level["source_swing_ids"])
        broken = False
        reclaimed = False
        for bar in bars[level["last_index"] + 1 :]:
            touched = (
                bar["high"] >= level["price"]
                if level["side"] == "HIGH"
                else bar["low"] <= level["price"]
            )
            if touched:
                touches += 1
            crossed = (
                bar["close"] > level["price"]
                if level["side"] == "HIGH"
                else bar["close"] < level["price"]
            )
            returned = (
                bar["close"] < level["price"]
                if level["side"] == "HIGH"
                else bar["close"] > level["price"]
            )
            if crossed and not broken:
                level["break_count"] += 1
                broken = True
            if broken and returned:
                level["reclaim_count"] += 1
                reclaimed = True
                broken = False
            elif broken and crossed:
                level["accepted_beyond_count"] += 1
                level["accepted_beyond"] = True
        level["touch_count"] = touches
        level["current_status"] = (
            "STALE"
            if level["age_bars"] > MAX_LEVEL_AGE[profile.timeframe]
            else "BROKEN"
            if broken
            else "RECLAIMED"
            if reclaimed
            else "TESTED"
            if touches > len(level["source_swing_ids"])
            else "FRESH"
        )
        level["freshness"] = "FRESH" if touches == len(level["source_swing_ids"]) else "TESTED"
        level["eligible_for_invalidation"] = (
            level["freshness"] in ("FRESH", "TESTED")
            and level["break_count"] == 0
            and not level["accepted_beyond"]
            and level["age_bars"] <= MAX_LEVEL_AGE[profile.timeframe]
        )
        level["distance_atr"] = round_or_none(abs(level["price"] - close) / atr, 6)
        if level["side"] == "HIGH":
            level["location"] = "ABOVE_PRICE" if level["price"] > close else "BELOW_PRICE"
            level["role"] = "RESISTANCE" if level["price"] > close else "BROKEN_RESISTANCE"
        else:
            level["location"] = "BELOW_PRICE" if level["price"] < close else "ABOVE_PRICE"
            level["role"] = "SUPPORT" if level["price"] < close else "BROKEN_SUPPORT"

    nearest_resistance = min(
        (level for level in resistance if level["price"] > close),
        key=lambda level: level["price"] - close,
        default=None,
    )
    nearest_support = min(
        (level for level in support if level["price"] < close),
        key=lambda level: close - level["price"],
        default=None,
    )
    eligible_resistance = [level for level in resistance if level["eligible_for_invalidation"]]
    eligible_support = [level for level in support if level["eligible_for_invalidation"]]
    nearest_eligible_resistance = min(
        (level for level in eligible_resistance if level["price"] > close),
        key=lambda level: level["price"] - close,
        default=None,
    )
    nearest_eligible_support = min(
        (level for level in eligible_support if level["price"] < close),
        key=lambda level: close - level["price"],
        default=None,
    )

    # Previous-period levels are derived only from OHLC. For H1/H4 these are rolling
    # period proxies, while the orchestrator may also supply parent levels separately.
    prior = bars[-2]
    recent_window = bars[-min(20, len(bars)) :]
    return {
        "support_levels": sorted(support, key=lambda level: level["price"]),
        "resistance_levels": sorted(resistance, key=lambda level: level["price"]),
        "nearest_support": nearest_support,
        "nearest_resistance": nearest_resistance,
        "nearest_eligible_support": nearest_eligible_support,
        "nearest_eligible_resistance": nearest_eligible_resistance,
        "invalidation_blocker": (
            "NO_ELIGIBLE_INVALIDATION_LEVEL"
            if nearest_eligible_support is None or nearest_eligible_resistance is None
            else None
        ),
        "reference_levels": {
            "previous_bar_high": round_or_none(prior["high"]),
            "previous_bar_low": round_or_none(prior["low"]),
            "rolling_20_bar_high": round_or_none(max(bar["high"] for bar in recent_window)),
            "rolling_20_bar_low": round_or_none(min(bar["low"] for bar in recent_window)),
            "range_position_20": round_or_none(
                safe_div(
                    close - min(bar["low"] for bar in recent_window),
                    max(bar["high"] for bar in recent_window)
                    - min(bar["low"] for bar in recent_window),
                    0.5,
                ),
                6,
            ),
        },
        "metadata": {
            "level_clustering_merges_price_zones_not_swing_identity": True,
            "cluster_tolerance_atr": profile.level_cluster_tolerance_atr,
        },
    }
