"""File-based cache for SynthesizerAgent output, keyed by (symbol, broker-day).

Mirrors the same semantics as ``src.analysis.candle_cache`` — day boundaries are
derived from the calendar date of *broker_now* (not from the D1 candle period) so
they match the test expectations for day-rollover and cross-symbol isolation.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from src.decision.models import MarketContextSummary

logger = logging.getLogger(__name__)

_settings: Any | None = None  # Sentinel — lazily initialised Settings reference


def _get_settings() -> Any:
    """Lazy-load Settings singleton for this module.

    Mirrors ``src.analysis.candle_cache._get_settings()``. The sentinel is reset
    by the test autouse fixture ``reset_synthesizer_cache_settings``.
    """
    global _settings
    if _settings is None:
        from config.settings import Settings

        _settings = Settings()
    return _settings


def _get_cache_date(broker_now: datetime) -> str:
    """Derive the cache folder name from the calendar day.

    Uses the calendar date of *broker_now* directly (not the D1 candle period)
    so that day boundaries align with midnight rather than the D1 close time.
    """
    return broker_now.strftime("%Y-%m-%d")


def _cache_path(symbol: str, broker_now: datetime) -> Path:
    """Build the full cache file path."""
    settings = _get_settings()
    base = Path(settings.analysis_cache_dir)
    cache_date = _get_cache_date(broker_now)
    year, month, day = cache_date.split("-")
    return base / year / month / day / symbol / "synthesizer.json"


def should_run_synthesis(symbol: str, broker_now: datetime) -> bool:
    """Check if the synthesizer should run (cache miss, disabled, or no cached file).

    Returns ``True`` if:
    - The cache is disabled (``synthesizer_cache_enabled`` is ``False``)
    - No cached file exists for *symbol* on *broker_day*

    Returns ``False`` if a valid cache file exists (cache hit).
    """
    settings = _get_settings()
    if not settings.synthesizer_cache_enabled:
        return True

    path = _cache_path(symbol, broker_now)
    return not path.exists()


def save_synthesis(
    symbol: str,
    broker_now: datetime,
    summary: MarketContextSummary,
) -> None:
    """Persist *summary* to a JSON cache file for *symbol* on *broker_day*.

    Best-effort: logs a warning on write failure and returns without raising.
    The cache is only written when the cache is enabled.
    """
    settings = _get_settings()
    if not settings.synthesizer_cache_enabled:
        return

    path = _cache_path(symbol, broker_now)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = summary.model_dump()
        path.write_text(json.dumps(data, indent=2, default=str))
    except OSError:
        logger.warning("Failed to write synthesizer cache to %s", path)
    except (ValueError, TypeError, KeyError) as e:
        logger.warning("Unexpected error writing synthesizer cache to %s: %s", path, e)


def load_cached_synthesis(
    symbol: str,
    broker_now: datetime,
) -> MarketContextSummary | None:
    """Load a cached ``MarketContextSummary`` for *symbol* on *broker_day*.

    Returns ``None`` (without raising) when:
    - The file does not exist
    - The file contains invalid JSON
    - The JSON content does not match the ``MarketContextSummary`` schema
    - An OS-level read error occurs
    """
    path = _cache_path(symbol, broker_now)
    if not path.exists():
        return None

    try:
        with open(str(path)) as f:
            data: dict[str, Any] = json.load(f)
        return MarketContextSummary.model_validate(data)
    except (json.JSONDecodeError, OSError):
        logger.warning("Corrupt synthesizer cache file at %s — treating as miss", path)
        return None
    except Exception:
        logger.warning(
            "Unexpected error reading synthesizer cache at %s — treating as miss",
            path,
        )
        return None
