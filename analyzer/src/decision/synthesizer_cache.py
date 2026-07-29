"""File-based cache for SynthesizerAgent output, keyed by (symbol, day, H1-closing-hour).

Day boundaries are derived from the calendar date of *broker_now* (not from the
D1 candle period) so they match the test expectations for day-rollover and
cross-symbol isolation.  Within a day the cache is further scoped to the current
H1 candle closing hour — borrowed from ``src.analysis.candle_cache.get_cache_date``
— so each run within a different H1 period gets its own cached summary.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from src.analysis.candle_cache import get_cache_date
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
    """Derive the cache directory date from the calendar day.

    Uses the calendar date of *broker_now* directly (not the D1 candle period)
    so that day boundaries align with midnight rather than the D1 close time.
    The H1 closing hour is added by ``_cache_path`` via ``candle_cache.get_cache_date``.
    """
    return broker_now.strftime("%Y-%m-%d")


def _cache_path(symbol: str, broker_now: datetime) -> Path:
    """Build the full cache file path.

    Returns a path like ``…/2026/07/29/XAUUSD/synthesizer-h1-15.json`` where
    ``15`` is the H1 closing hour derived from ``broker_now`` via
    ``candle_cache.get_cache_date("H1", …)``.
    """
    settings = _get_settings()
    base = Path(settings.analysis_cache_dir)
    cache_date = _get_cache_date(broker_now)
    year, month, day = cache_date.split("-")
    h1_cache_date = get_cache_date("H1", broker_now)
    filename = f"synthesizer-h1-{h1_cache_date.hour:02d}.json"
    return base / year / month / day / symbol / filename


def should_run_synthesis(symbol: str, broker_now: datetime) -> bool:
    """Check if the synthesizer should run (cache miss, disabled, or no cached file).

    Returns ``True`` if:
    - The cache is disabled (``synthesizer_cache_enabled`` is ``False``)
    - No cached file exists for *symbol* on *broker_day* at the current H1 hour

    Returns ``False`` if a valid cache file exists (cache hit).

    Debug-logs when a file for the same symbol and day exists at a different
    H1 hour — useful for observability when the analyzer runs across multiple
    H1 periods.
    """
    settings = _get_settings()
    if not settings.synthesizer_cache_enabled:
        return True

    path = _cache_path(symbol, broker_now)
    if path.exists():
        return False

    # Log when same-day files exist at a different H1 hour (observability)
    day_dir = path.parent
    if day_dir.is_dir():
        same_day_files = sorted(day_dir.glob("synthesizer-h1-*.json"))
        if same_day_files:
            logger.debug(
                "Synthesizer cache miss for %s at H1-%02d, but %d file(s) exist "
                "for a different H1 hour on the same day: %s",
                symbol,
                get_cache_date("H1", broker_now).hour,
                len(same_day_files),
                ", ".join(f.name for f in same_day_files),
            )

    return True


def save_synthesis(
    symbol: str,
    broker_now: datetime,
    summary: MarketContextSummary,
) -> None:
    """Persist *summary* to a JSON cache file for *symbol* on *broker_day*.

    Best-effort: logs a warning on write failure and returns without raising.
    The cache is only written when the cache is enabled.

    After writing, any legacy ``synthesizer.json`` (without H1-hour suffix) in
    the same directory is deleted to keep the data tree clean.
    """
    settings = _get_settings()
    if not settings.synthesizer_cache_enabled:
        return

    path = _cache_path(symbol, broker_now)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = summary.model_dump()
        path.write_text(json.dumps(data, indent=2, default=str))

        # Clean up legacy file (pre-H1-hour-suffix format)
        legacy = path.parent / "synthesizer.json"
        if legacy.exists() and legacy != path:
            try:
                legacy.unlink()
                logger.debug("Removed legacy synthesizer cache file %s", legacy)
            except OSError:
                logger.debug("Failed to remove legacy synthesizer cache file %s", legacy)
    except OSError:
        logger.warning("Failed to write synthesizer cache to %s", path)
    except (ValueError, TypeError, KeyError) as e:
        logger.warning("Unexpected error writing synthesizer cache to %s: %s", path, e)


def load_cached_synthesis(
    symbol: str,
    broker_now: datetime,
) -> MarketContextSummary | None:
    """Load a cached ``MarketContextSummary`` for *symbol* at the current H1 hour.

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
