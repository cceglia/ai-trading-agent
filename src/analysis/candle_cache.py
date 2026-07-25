# src/analysis/candle_cache.py
"""Candle-aligned caching for market structure analysis."""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any

from config.settings import Settings

_settings: Settings | None = None

logger = logging.getLogger(__name__)


def _get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def _cache_path(timeframe: str, symbol: str, cache_date: datetime) -> str:
    """Compute cache file path.

    Args:
        timeframe: "D1", "H4", or "H1"
        symbol: Trading symbol (e.g., "XAUUSD")
        cache_date: Datetime from _get_cache_date (date=period_start.date, hour=closing hour)

    Returns:
        Path like "analysis/2026/07/21/XAUUSD/h4-16-analysis.json"
    """
    settings = _get_settings()

    if timeframe == "D1":
        filename = "d1-analysis.json"
    elif timeframe == "H4":
        filename = f"h4-{cache_date.hour:02d}-analysis.json"
    elif timeframe == "H1":
        filename = f"h1-{cache_date.hour:02d}-analysis.json"
    elif timeframe == "MTF":
        filename = "mtf-analysis.json"
    else:
        raise ValueError(f"Unsupported timeframe: {timeframe}")

    return f"{settings.analysis_cache_dir}/{cache_date.strftime('%Y/%m/%d')}/{symbol}/{filename}"


def _candle_period(timeframe: str, broker_now: datetime) -> tuple[datetime, datetime]:
    """Compute the start and end of a candle period.

    Args:
        timeframe: "D1", "H4", or "H1"
        broker_now: Naive datetime in broker-local time

    Returns:
        Tuple of (period_start, period_end) as naive datetimes

    Raises:
        ValueError: If timeframe is not supported for caching
    """
    settings = _get_settings()

    if timeframe == "MTF":
        return _candle_period("D1", broker_now)
    elif timeframe == "D1":
        close_h, close_m = map(int, settings.d1_close_time.split(":"))
        today_close = broker_now.replace(hour=close_h, minute=close_m, second=0, microsecond=0)
        if broker_now < today_close:
            return today_close - timedelta(days=1), today_close
        else:
            return today_close, today_close + timedelta(days=1)
    elif timeframe == "H4":
        anchor_h, anchor_m = map(int, settings.h4_close_time.split(":"))
        interval = timedelta(hours=settings.h4_close_interval_hours)
        anchor = broker_now.replace(hour=anchor_h, minute=anchor_m, second=0, microsecond=0)
        periods_from_anchor = int((broker_now - anchor) / interval)
        period_start = anchor + interval * periods_from_anchor
        return period_start, period_start + interval
    elif timeframe == "H1":
        start = broker_now.replace(minute=0, second=0, microsecond=0)
        return (start, start + timedelta(hours=1))
    else:
        raise ValueError(f"Unsupported timeframe for caching: {timeframe}")


def _get_cache_date(timeframe: str, broker_now: datetime) -> datetime:
    """Return the cache date for the given timeframes.

    Returns a datetime whose date is the period_start's date
    and whose hour is the period_end's hour (the closing hour).

    Args:
        timeframe: "D1", "H4", or "H1"
        broker_now: Naive datetime in broker-local time

    Returns:
        Datetime with date=period_start.date(), hour=period_end.hour
    """
    period_start, period_end = _candle_period(timeframe, broker_now)
    return period_start.replace(hour=period_end.hour, minute=0, second=0, microsecond=0)


def should_run_analysis(timeframe: str, symbol: str, broker_now: datetime) -> bool:
    """Determine if analysis should run for this timeframe.

    Args:
        timeframe: "D1", "H4", or "H1"
        symbol: Trading symbol (e.g., "XAUUSD")
        broker_now: Naive datetime in broker-local time

    Returns:
        True if analysis should run (no valid cache), False if cache is valid
    """
    cache_date = _get_cache_date(timeframe, broker_now)
    path = _cache_path(timeframe, symbol, cache_date)
    exists = os.path.exists(path)
    if exists:
        logger.info("Cache valid for %s/%s at %s", timeframe, symbol, path)
    else:
        logger.info("Cache expired/missing for %s/%s at %s", timeframe, symbol, path)
    return not exists


def save_analysis(
    timeframe: str, symbol: str, broker_now: datetime, result: dict[str, Any]
) -> None:
    """Save analysis result to disk.

    Args:
        timeframe: "D1", "H4", or "H1"
        symbol: Trading symbol
        broker_now: Naive datetime in broker-local time
        result: Analysis result dictionary

    Raises:
        OSError: If file write fails
    """
    cache_date = _get_cache_date(timeframe, broker_now)
    path = _cache_path(timeframe, symbol, cache_date)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(result, f, indent=2)
    logger.info("Saved %s analysis cache for %s to %s", timeframe, symbol, path)


def load_cached_analysis(
    timeframe: str, symbol: str, broker_now: datetime
) -> dict[str, Any] | None:
    """Load cached analysis from disk if available.

    Args:
        timeframe: "D1", "H4", or "H1"
        symbol: Trading symbol
        broker_now: Naive datetime in broker-local time

    Returns:
        Analysis dict if cache exists and is valid, None otherwise
    """
    cache_date = _get_cache_date(timeframe, broker_now)
    path = _cache_path(timeframe, symbol, cache_date)
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            loaded: dict[str, Any] = json.load(f)
            logger.info("Loaded %s analysis cache for %s from %s", timeframe, symbol, path)
            return loaded
    except (json.JSONDecodeError, OSError):
        logger.warning(
            "Failed to load %s analysis cache for %s from %s (corrupt or unreadable)",
            timeframe,
            symbol,
            path,
        )
        return None
