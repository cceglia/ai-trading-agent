from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .config import TimeframeProfile
from .utils import round_or_none, safe_div, stable_id


@dataclass
class Swing:
    swing_id: str
    index: int
    timestamp: str
    side: str
    price: float
    classification: str
    prominence_atr: float
    plateau_start_index: int
    plateau_end_index: int
    status: str = "ACTIVE"

    def to_dict(self) -> dict[str, Any]:
        return {
            "swing_id": self.swing_id,
            "index": self.index,
            "timestamp": self.timestamp,
            "side": self.side,
            "price": round_or_none(self.price),
            "classification": self.classification,
            "prominence_atr": round_or_none(self.prominence_atr, 6),
            "plateau_start_index": self.plateau_start_index,
            "plateau_end_index": self.plateau_end_index,
            "status": self.status,
        }


def _candidate_indexes(bars: list[dict[str, Any]], window: int, side: str) -> list[int]:
    indexes: list[int] = []
    key = "high" if side == "HIGH" else "low"
    for index in range(window, len(bars) - window):
        center = bars[index][key]
        neighbors = [bars[i][key] for i in range(index - window, index + window + 1) if i != index]
        if side == "HIGH" and center >= max(neighbors):
            indexes.append(index)
        elif side == "LOW" and center <= min(neighbors):
            indexes.append(index)
    return indexes


def _group_local_plateaus(
    indexes: list[int],
    bars: list[dict[str, Any]],
    atr_series: list[float | None],
    profile: TimeframeProfile,
    side: str,
) -> list[list[int]]:
    if not indexes:
        return []
    key = "high" if side == "HIGH" else "low"
    groups: list[list[int]] = [[indexes[0]]]
    for index in indexes[1:]:
        current_group = groups[-1]
        previous = current_group[-1]
        atr = (
            atr_series[index]
            or atr_series[previous]
            or max(bars[index]["high"] - bars[index]["low"], 1e-12)
        )
        close_in_time = index - previous <= profile.plateau_max_bar_distance
        close_in_price = (
            abs(bars[index][key] - bars[previous][key]) <= profile.plateau_price_tolerance_atr * atr
        )
        if close_in_time and close_in_price:
            current_group.append(index)
        else:
            groups.append([index])
    return groups


def _representative(group: list[int], bars: list[dict[str, Any]], side: str) -> int:
    key = "high" if side == "HIGH" else "low"
    target = (
        max(bars[i][key] for i in group) if side == "HIGH" else min(bars[i][key] for i in group)
    )
    candidates = [i for i in group if bars[i][key] == target]
    return candidates[len(candidates) // 2]


def _prominence(
    index: int,
    bars: list[dict[str, Any]],
    atr: float,
    window: int,
    side: str,
) -> float:
    left = max(0, index - window * 2)
    right = min(len(bars), index + window * 2 + 1)
    if side == "HIGH":
        base = min(bar["low"] for bar in bars[left:right])
        distance = bars[index]["high"] - base
    else:
        base = max(bar["high"] for bar in bars[left:right])
        distance = base - bars[index]["low"]
    return safe_div(distance, atr, 0.0)


def _assign_status(swings: list[Swing], bars: list[dict[str, Any]]) -> None:
    for swing in swings:
        tested = False
        broken = False
        reclaimed = False
        for bar in bars[swing.index + 1 :]:
            if swing.side == "HIGH":
                if bar["high"] >= swing.price:
                    tested = True
                if bar["close"] > swing.price:
                    broken = True
                if broken and bar["close"] < swing.price:
                    reclaimed = True
            else:
                if bar["low"] <= swing.price:
                    tested = True
                if bar["close"] < swing.price:
                    broken = True
                if broken and bar["close"] > swing.price:
                    reclaimed = True
        swing.status = (
            "RECLAIMED" if reclaimed else "BROKEN" if broken else "TESTED" if tested else "ACTIVE"
        )


def detect_swings(
    bars: list[dict[str, Any]],
    atr_series: list[float | None],
    profile: TimeframeProfile,
) -> dict[str, Any]:
    swings: list[Swing] = []
    for side in ("HIGH", "LOW"):
        indexes = _candidate_indexes(bars, profile.internal_swing_window, side)
        groups = _group_local_plateaus(indexes, bars, atr_series, profile, side)
        key = "high" if side == "HIGH" else "low"
        for group in groups:
            index = _representative(group, bars, side)
            atr = atr_series[index] or max(bars[index]["high"] - bars[index]["low"], 1e-12)
            prominence = _prominence(index, bars, atr, profile.swing_window, side)
            if prominence >= profile.major_prominence_atr:
                classification = "MAJOR_STRUCTURAL_SWING"
            elif prominence >= profile.minor_prominence_atr:
                classification = "MINOR_INTERNAL_SWING"
            else:
                classification = "UNCONFIRMED_SWING"
            price = float(bars[index][key])
            swings.append(
                Swing(
                    swing_id=stable_id("swing", profile.timeframe, side, index, f"{price:.10f}"),
                    index=index,
                    timestamp=bars[index]["open_time"],
                    side=side,
                    price=price,
                    classification=classification,
                    prominence_atr=prominence,
                    plateau_start_index=min(group),
                    plateau_end_index=max(group),
                )
            )
    swings.sort(key=lambda swing: (swing.index, 0 if swing.side == "LOW" else 1, swing.price))
    _assign_status(swings, bars)
    major = [swing for swing in swings if swing.classification == "MAJOR_STRUCTURAL_SWING"]
    internal = [swing for swing in swings if swing.classification == "MINOR_INTERNAL_SWING"]
    return {
        "all": [swing.to_dict() for swing in swings],
        "major": [swing.to_dict() for swing in major],
        "internal": [swing.to_dict() for swing in internal],
        "latest_major_high": next((s.to_dict() for s in reversed(major) if s.side == "HIGH"), None),
        "latest_major_low": next((s.to_dict() for s in reversed(major) if s.side == "LOW"), None),
        "latest_internal_high": next(
            (s.to_dict() for s in reversed(internal) if s.side == "HIGH"),
            None,
        ),
        "latest_internal_low": next(
            (s.to_dict() for s in reversed(internal) if s.side == "LOW"),
            None,
        ),
        "metadata": {
            "local_plateau_rule": "same-side pivots grouped only when close in time and price",
            "distant_equal_price_swings_preserved": True,
        },
    }
