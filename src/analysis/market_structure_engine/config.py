from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

SUPPORTED_TIMEFRAMES = ("D1", "H4", "H1")


@dataclass(frozen=True)
class TimeframeProfile:
    timeframe: str
    role: str
    minimum_bars: int
    preferred_bars: int
    maximum_bars: int
    swing_window: int
    internal_swing_window: int
    major_prominence_atr: float
    minor_prominence_atr: float
    plateau_max_bar_distance: int
    plateau_price_tolerance_atr: float
    equal_level_tolerance_atr: float
    level_cluster_tolerance_atr: float
    bos_close_buffer_atr: float
    event_lookback_bars: int
    max_events_per_category: int
    atr_length: int = 14
    atr_average_length: int = 50
    rsi_length: int = 14
    adx_length: int = 14
    roc_length: int = 14
    ema_fast: int = 20
    ema_medium: int = 50
    ema_slow: int = 200
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def with_overrides(self, overrides: dict[str, Any] | None) -> TimeframeProfile:
        if not overrides:
            return self
        unknown = sorted(set(overrides) - set(asdict(self)))
        if unknown:
            raise ValueError(f"Unknown profile override(s): {', '.join(unknown)}")
        return replace(self, **overrides)


PROFILES: dict[str, TimeframeProfile] = {
    "D1": TimeframeProfile(
        timeframe="D1",
        role="STRATEGIC_BIAS",
        minimum_bars=250,
        preferred_bars=500,
        maximum_bars=1000,
        swing_window=5,
        internal_swing_window=3,
        major_prominence_atr=0.80,
        minor_prominence_atr=0.35,
        plateau_max_bar_distance=3,
        plateau_price_tolerance_atr=0.05,
        equal_level_tolerance_atr=0.12,
        level_cluster_tolerance_atr=0.18,
        bos_close_buffer_atr=0.05,
        event_lookback_bars=180,
        max_events_per_category=50,
    ),
    "H4": TimeframeProfile(
        timeframe="H4",
        role="OPERATIONAL_CONTEXT",
        minimum_bars=300,
        preferred_bars=750,
        maximum_bars=1500,
        swing_window=4,
        internal_swing_window=2,
        major_prominence_atr=0.65,
        minor_prominence_atr=0.28,
        plateau_max_bar_distance=3,
        plateau_price_tolerance_atr=0.06,
        equal_level_tolerance_atr=0.14,
        level_cluster_tolerance_atr=0.20,
        bos_close_buffer_atr=0.04,
        event_lookback_bars=240,
        max_events_per_category=50,
    ),
    "H1": TimeframeProfile(
        timeframe="H1",
        role="SETUP_CONFIRMATION",
        minimum_bars=500,
        preferred_bars=1000,
        maximum_bars=2500,
        swing_window=3,
        internal_swing_window=2,
        major_prominence_atr=0.50,
        minor_prominence_atr=0.22,
        plateau_max_bar_distance=2,
        plateau_price_tolerance_atr=0.07,
        equal_level_tolerance_atr=0.16,
        level_cluster_tolerance_atr=0.22,
        bos_close_buffer_atr=0.03,
        event_lookback_bars=360,
        max_events_per_category=50,
    ),
}


def get_profile(timeframe: str, overrides: dict[str, Any] | None = None) -> TimeframeProfile:
    normalized = timeframe.upper()
    if normalized not in PROFILES:
        raise ValueError(
            f"UNSUPPORTED_TIMEFRAME: {timeframe!r}. Supported timeframes are D1, H4 and H1."
        )
    return PROFILES[normalized].with_overrides(overrides)
