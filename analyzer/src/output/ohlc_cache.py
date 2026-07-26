from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import Any

from config.settings import Settings
from src.analysis.candle_cache import get_cache_date
from src.output.result_models import OHLCBar

logger = logging.getLogger(__name__)

_settings: Settings | None = None


def _get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def ohlc_cache_path(timeframe: str, symbol: str, cache_date: datetime) -> str:
    """Compute OHLC cache file path, parallel to analysis cache.

    Cache path convention (aligned with analysis cache):
        data/YYYY/MM/DD/SYMBOL/ohlc-D1.json
        data/YYYY/MM/DD/SYMBOL/ohlc-h4-16.json
        data/YYYY/MM/DD/SYMBOL/ohlc-h1-08.json

    Args:
        timeframe: "D1", "H4", or "H1"
        symbol: Trading symbol (e.g., "XAUUSD")
        cache_date: Datetime from get_cache_date (date=period_start.date,
            hour=closing hour)

    Returns:
        Path like "2026/07/21/XAUUSD/ohlc-h4-16.json"
    """
    settings = _get_settings()

    if timeframe == "D1":
        filename = "ohlc-D1.json"
    elif timeframe == "H4":
        filename = f"ohlc-h4-{cache_date.hour:02d}.json"
    elif timeframe == "H1":
        filename = f"ohlc-h1-{cache_date.hour:02d}.json"
    else:
        raise ValueError(f"Unsupported timeframe: {timeframe}")

    return f"{settings.analysis_cache_dir}/{cache_date.strftime('%Y/%m/%d')}/{symbol}/{filename}"


def save_ohlc_cache(timeframe: str, symbol: str, broker_now: datetime, bars: list[OHLCBar]) -> None:
    """Save OHLC bars to cache, same directory structure as analysis cache.

    Args:
        timeframe: "D1", "H4", or "H1"
        symbol: Trading symbol (e.g., "XAUUSD")
        broker_now: Naive datetime in broker-local time
        bars: List of OHLCBar objects to cache

    Raises:
        OSError: If file write fails
    """
    cache_date = get_cache_date(timeframe, broker_now)
    path = ohlc_cache_path(timeframe, symbol, cache_date)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    data = [bar.model_dump() for bar in bars]
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    logger.info("Saved OHLC cache for %s/%s to %s (%d bars)", timeframe, symbol, path, len(bars))


def load_ohlc_cache(timeframe: str, symbol: str, broker_now: datetime) -> list[OHLCBar] | None:
    """Load cached OHLC bars from disk if available.

    Args:
        timeframe: "D1", "H4", or "H1"
        symbol: Trading symbol (e.g., "XAUUSD")
        broker_now: Naive datetime in broker-local time

    Returns:
        List of OHLCBar objects if cache exists and is valid, None otherwise
    """
    cache_date = get_cache_date(timeframe, broker_now)
    path = ohlc_cache_path(timeframe, symbol, cache_date)

    if not os.path.exists(path):
        return None

    try:
        with open(path) as f:
            data: list[dict[str, Any]] = json.load(f)
        bars = [OHLCBar(**item) for item in data]
        logger.info(
            "Loaded OHLC cache for %s/%s from %s (%d bars)",
            timeframe,
            symbol,
            path,
            len(bars),
        )
        return bars
    except (json.JSONDecodeError, OSError, TypeError, KeyError) as exc:
        logger.warning(
            "Failed to load OHLC cache for %s/%s from %s: %s",
            timeframe,
            symbol,
            path,
            exc,
        )
        return None
