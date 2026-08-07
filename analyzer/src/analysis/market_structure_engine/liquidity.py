from __future__ import annotations

from collections import defaultdict
from typing import Any

from .config import TimeframeProfile
from .utils import round_or_none, stable_id


def _pool_status(
    pool: dict[str, Any],
    bars: list[dict[str, Any]],
) -> tuple[str, list[dict[str, Any]]]:
    source_last = pool["last_source_index"]
    price = pool["price"]
    side = pool["side"]
    state = "INTACT"
    history: list[dict[str, Any]] = []
    for index in range(source_last + 1, len(bars)):
        bar = bars[index]
        if side == "BUY_SIDE":
            if state in ("SWEPT", "SWEPT_AND_RECLAIMED") and bar["close"] > price:
                state = "ACCEPTED_BEYOND"
                history.append(
                    {"event_type": state, "event_index": index, "timestamp": bar["open_time"]}
                )
            elif bar["high"] > price:
                if bar["close"] <= price:
                    state = "SWEPT_AND_RECLAIMED"
                    history.append(
                        {"event_type": state, "event_index": index, "timestamp": bar["open_time"]}
                    )
                else:
                    state = "SWEPT"
                    history.append(
                        {"event_type": "SWEEP", "event_index": index, "timestamp": bar["open_time"]}
                    )
        else:
            if state in ("SWEPT", "SWEPT_AND_RECLAIMED") and bar["close"] < price:
                state = "ACCEPTED_BEYOND"
                history.append(
                    {"event_type": state, "event_index": index, "timestamp": bar["open_time"]}
                )
            elif bar["low"] < price:
                if bar["close"] >= price:
                    state = "SWEPT_AND_RECLAIMED"
                    history.append(
                        {"event_type": state, "event_index": index, "timestamp": bar["open_time"]}
                    )
                else:
                    state = "SWEPT"
                    history.append(
                        {"event_type": "SWEEP", "event_index": index, "timestamp": bar["open_time"]}
                    )
    return state, history


def _build_equal_pools(
    swings: list[dict[str, Any]],
    latest_atr: float,
    profile: TimeframeProfile,
) -> list[dict[str, Any]]:
    atr = latest_atr or 1e-12
    pools: list[dict[str, Any]] = []
    for side, label in (("HIGH", "BUY_SIDE"), ("LOW", "SELL_SIDE")):
        candidates = sorted(
            [s for s in swings if s["side"] == side and s["classification"] != "UNCONFIRMED_SWING"],
            key=lambda s: (s["price"], s["index"]),
        )
        groups: list[list[dict[str, Any]]] = []
        for swing in candidates:
            if not groups:
                groups.append([swing])
                continue
            center = sum(item["price"] for item in groups[-1]) / len(groups[-1])
            if abs(swing["price"] - center) <= profile.equal_level_tolerance_atr * atr:
                groups[-1].append(swing)
            else:
                groups.append([swing])
        for group in groups:
            if len(group) < 2:
                continue
            center = sum(item["price"] for item in group) / len(group)
            scope = (
                "EXTERNAL"
                if any(item["classification"] == "MAJOR_STRUCTURAL_SWING" for item in group)
                else "INTERNAL"
            )
            pools.append(
                {
                    "pool_id": stable_id(
                        "pool",
                        label,
                        f"{center:.10f}",
                        *[item["swing_id"] for item in group],
                    ),
                    "side": label,
                    "scope": scope,
                    "kind": "EQUAL_HIGHS" if side == "HIGH" else "EQUAL_LOWS",
                    "price": round_or_none(center),
                    "source_swing_ids": [item["swing_id"] for item in group],
                    "first_source_index": min(item["index"] for item in group),
                    "last_source_index": max(item["index"] for item in group),
                    "temporally_distant_sources_allowed": True,
                }
            )
    return pools


def _single_swing_pools(swings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pools = []
    for swing in swings:
        if swing["classification"] != "MAJOR_STRUCTURAL_SWING":
            continue
        side = "BUY_SIDE" if swing["side"] == "HIGH" else "SELL_SIDE"
        pools.append(
            {
                "pool_id": stable_id("pool", side, swing["swing_id"]),
                "side": side,
                "scope": "EXTERNAL",
                "kind": "MAJOR_SWING_HIGH" if side == "BUY_SIDE" else "MAJOR_SWING_LOW",
                "price": swing["price"],
                "source_swing_ids": [swing["swing_id"]],
                "first_source_index": swing["index"],
                "last_source_index": swing["index"],
                "temporally_distant_sources_allowed": False,
            }
        )
    return pools


def _dedupe_pools(pools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, float], list[dict[str, Any]]] = defaultdict(list)
    for pool in pools:
        grouped[(pool["side"], pool["scope"], round(pool["price"], 8))].append(pool)
    output = []
    for key in sorted(grouped):
        members = grouped[key]
        chosen = dict(
            sorted(
                members,
                key=lambda p: (
                    0 if p["kind"].startswith("EQUAL") else 1,
                    -len(p["source_swing_ids"]),
                ),
            )[0]
        )
        chosen["source_swing_ids"] = sorted(
            {sid for member in members for sid in member["source_swing_ids"]}
        )
        chosen["merged_pool_count"] = len(members)
        output.append(chosen)
    return output


def analyze_liquidity(
    bars: list[dict[str, Any]],
    swings: dict[str, Any],
    latest_atr: float,
    profile: TimeframeProfile,
) -> dict[str, Any]:
    atr = latest_atr or max(bars[-1]["high"] - bars[-1]["low"], 1e-12)
    close = bars[-1]["close"]
    pools = _dedupe_pools(
        _build_equal_pools(swings["all"], atr, profile) + _single_swing_pools(swings["major"])
    )
    events: list[dict[str, Any]] = []
    for pool in pools:
        status, history = _pool_status(pool, bars)
        pool["status"] = status
        pool["event_history"] = history
        pool["distance_atr"] = round_or_none(abs(pool["price"] - close) / atr, 6)
        pool["position"] = "ABOVE_PRICE" if pool["price"] > close else "BELOW_PRICE"
        for event in history:
            canonical_event = {
                "liquidity_event_id": stable_id(
                    "liqevt",
                    pool["pool_id"],
                    event["event_index"],
                    event["event_type"],
                ),
                "pool_id": pool["pool_id"],
                "pool_ids": [pool["pool_id"]],
                "source_swing_ids": pool["source_swing_ids"],
                "side": pool["side"],
                "scope": pool["scope"],
                "price": pool["price"],
                **event,
            }
            events.append(canonical_event)

    intact_buy = [
        p
        for p in pools
        if p["side"] == "BUY_SIDE" and p["status"] == "INTACT" and p["price"] > close
    ]
    intact_sell = [
        p
        for p in pools
        if p["side"] == "SELL_SIDE" and p["status"] == "INTACT" and p["price"] < close
    ]
    nearest_buy = min(intact_buy, key=lambda p: p["price"] - close, default=None)
    nearest_sell = min(intact_sell, key=lambda p: close - p["price"], default=None)
    if nearest_buy and nearest_sell:
        dominant = (
            "BUY_SIDE"
            if nearest_buy["distance_atr"] < nearest_sell["distance_atr"]
            else "SELL_SIDE"
        )
    elif nearest_buy:
        dominant = "BUY_SIDE"
    elif nearest_sell:
        dominant = "SELL_SIDE"
    else:
        dominant = "UNCLEAR"

    events.sort(key=lambda event: (event["event_index"], event["liquidity_event_id"]))
    return {
        "pools": sorted(pools, key=lambda p: (p["price"], p["pool_id"])),
        "events": events,
        "event_history": events,
        "current_state": {pool["pool_id"]: pool["status"] for pool in pools},
        "latest_event": events[-1] if events else None,
        "nearest_buy_side": nearest_buy,
        "nearest_sell_side": nearest_sell,
        "dominant_draw": dominant,
        "structural_liquidity_only": True,
        "actual_order_book_liquidity": False,
        "volume_profile_used": False,
    }
