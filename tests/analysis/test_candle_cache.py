# tests/analysis/test_candle_cache.py
"""Tests for broker-timezone-aligned analysis caching.

All datetimes are naive (no tzinfo). No datetime mocking needed —
pure logic with naive datetimes and tmp_path for filesystem access.
"""

import json
from datetime import datetime

# =============================================================================
# RED Tests for _cache_path
# =============================================================================


def test_cache_path_d1_uses_folder_date_not_broker_now():
    """D1 file path uses folder_date from _get_cache_date, not raw broker_now."""
    from src.analysis.candle_cache import _cache_path, _get_cache_date

    broker_now = datetime(2026, 7, 21, 14, 0)  # naive
    cache_date = _get_cache_date("D1", broker_now)
    path = _cache_path("D1", "XAUUSD", cache_date)
    assert path.endswith("d1-analysis.json")
    assert "2026/07/21" in path or "2026/07/20" in path  # depends on close time


def test_cache_path_d1_no_hour_suffix():
    """D1 cache filename has no hour suffix — always d1-analysis.json."""
    from src.analysis.candle_cache import _cache_path, _get_cache_date

    broker_now = datetime(2026, 7, 21, 14, 0)
    cache_date = _get_cache_date("D1", broker_now)
    path = _cache_path("D1", "XAUUSD", cache_date)
    assert path == f"analysis/{cache_date.strftime('%Y/%m/%d')}/XAUUSD/d1-analysis.json"


def test_cache_path_h4_includes_closing_hour():
    """H4 filename includes the closing hour (e.g. h4-16-analysis.json)."""
    from src.analysis.candle_cache import _cache_path, _get_cache_date

    # H4 period 12-16 -> closing hour = 16
    broker_now = datetime(2026, 7, 21, 14, 30)
    cache_date = _get_cache_date("H4", broker_now)
    path = _cache_path("H4", "XAUUSD", cache_date)
    # closing hour = period_end.hour = 16
    assert "h4-16-analysis.json" in path


def test_cache_path_h1_includes_closing_hour():
    """H1 filename includes the closing hour (e.g. h1-14-analysis.json)."""
    from src.analysis.candle_cache import _cache_path, _get_cache_date

    broker_now = datetime(2026, 7, 21, 14, 30)
    cache_date = _get_cache_date("H1", broker_now)
    path = _cache_path("H1", "XAUUSD", cache_date)
    assert "h1-15-analysis.json" in path


def test_cache_path_zero_padded_hour():
    """Midnight-boundary candles use 00 as the hour suffix (h4-00, h1-00)."""
    from src.analysis.candle_cache import _cache_path, _get_cache_date

    # Midnight candle -> h4-00 or h1-00
    broker_now = datetime(2026, 7, 21, 0, 15)
    cache_date_h4 = _get_cache_date("H4", broker_now)
    path_h4 = _cache_path("H4", "XAUUSD", cache_date_h4)
    assert "h4-04-analysis.json" in path_h4

    cache_date_h1 = _get_cache_date("H1", broker_now)
    path_h1 = _cache_path("H1", "XAUUSD", cache_date_h1)
    assert "h1-01-analysis.json" in path_h1


def test_cache_path_h4_hour_04_is_zero_padded():
    """H4 hour 04 is zero-padded to two digits (h4-04, not h4-4)."""
    from src.analysis.candle_cache import _cache_path, _get_cache_date

    broker_now = datetime(2026, 7, 21, 3, 30)
    cache_date = _get_cache_date("H4", broker_now)
    path = _cache_path("H4", "XAUUSD", cache_date)
    assert "h4-04-analysis.json" in path  # not h4-4-analysis.json


# =============================================================================
# RED Tests for _candle_period
# =============================================================================


def test_d1_candle_period_before_close(monkeypatch):
    """Before D1 close (17:00), the last closed candle is yesterday's."""
    from src.analysis.candle_cache import _candle_period

    monkeypatch.setenv("TRADING_D1_CLOSE_TIME", "17:00")
    # Before D1 close (17:00) -> last candle is yesterday's
    now = datetime(2026, 7, 21, 14, 0)
    start, end = _candle_period("D1", now)
    assert start == datetime(2026, 7, 20, 17, 0)
    assert end == datetime(2026, 7, 21, 17, 0)


def test_d1_candle_period_after_close(monkeypatch):
    """After D1 close (17:00), the current candle is today's."""
    from src.analysis.candle_cache import _candle_period

    monkeypatch.setenv("TRADING_D1_CLOSE_TIME", "17:00")
    now = datetime(2026, 7, 21, 18, 0)
    start, end = _candle_period("D1", now)
    assert start == datetime(2026, 7, 21, 17, 0)
    assert end == datetime(2026, 7, 22, 17, 0)


def test_h4_candle_period():
    """H4 period containing the given time, anchored at 00:00."""
    from src.analysis.candle_cache import _candle_period

    now = datetime(2026, 7, 21, 14, 30)
    start, end = _candle_period("H4", now)
    assert start == datetime(2026, 7, 21, 12, 0)
    assert end == datetime(2026, 7, 21, 16, 0)


def test_h4_candle_period_at_boundary():
    """At exact H4 boundary, the period starts at that boundary."""
    from src.analysis.candle_cache import _candle_period

    now = datetime(2026, 7, 21, 16, 0)
    start, end = _candle_period("H4", now)
    assert start == datetime(2026, 7, 21, 16, 0)
    assert end == datetime(2026, 7, 21, 20, 0)


def test_h1_candle_period():
    """H1 period is floored to the current hour."""
    from src.analysis.candle_cache import _candle_period

    now = datetime(2026, 7, 21, 14, 30)
    start, end = _candle_period("H1", now)
    assert start == datetime(2026, 7, 21, 14, 0)
    assert end == datetime(2026, 7, 21, 15, 0)


def test_h1_candle_period_at_boundary():
    """At exact H1 boundary, period starts at that time."""
    from src.analysis.candle_cache import _candle_period

    now = datetime(2026, 7, 21, 15, 0)
    start, end = _candle_period("H1", now)
    assert start == datetime(2026, 7, 21, 15, 0)
    assert end == datetime(2026, 7, 21, 16, 0)


def test_h1_candle_period_midnight():
    """H1 period crossing midnight boundary works correctly."""
    from src.analysis.candle_cache import _candle_period

    now = datetime(2026, 7, 22, 0, 15)
    start, end = _candle_period("H1", now)
    assert start == datetime(2026, 7, 22, 0, 0)
    assert end == datetime(2026, 7, 22, 1, 0)


# =============================================================================
# RED Tests for _get_cache_date
# =============================================================================


def test_get_cache_date_d1_before_close(monkeypatch):
    """Before D1 close, cache date is yesterday's date (from period_start)."""
    from src.analysis.candle_cache import _get_cache_date

    monkeypatch.setenv("TRADING_D1_CLOSE_TIME", "17:00")
    now = datetime(2026, 7, 21, 14, 0)  # before close -> yesterday's candle
    cache_date = _get_cache_date("D1", now)
    # folder date = 2026-07-20 (yesterday's candle), no hour needed for D1
    assert cache_date.date() == datetime(2026, 7, 20).date()


def test_get_cache_date_d1_after_close():
    """After D1 close, cache date is today's date (from period_start)."""
    from src.analysis.candle_cache import _get_cache_date

    now = datetime(2026, 7, 21, 18, 0)  # after close -> today's candle
    cache_date = _get_cache_date("D1", now)
    assert cache_date.date() == datetime(2026, 7, 21).date()


def test_get_cache_date_h4_returns_closing_hour():
    """H4 cache date includes the closing hour in cache_date.hour."""
    from src.analysis.candle_cache import _get_cache_date

    now = datetime(2026, 7, 21, 14, 30)  # H4 period 12-16
    cache_date = _get_cache_date("H4", now)
    # hour should be period_end.hour = 16 (closing hour)
    assert cache_date.hour == 16
    assert cache_date.date() == datetime(2026, 7, 21).date()


# =============================================================================
# RED Tests for should_run_analysis
# =============================================================================


def test_should_run_d1_without_cache(tmp_path, monkeypatch):
    """D1 should run analysis when no cache file exists."""
    from src.analysis.candle_cache import should_run_analysis

    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
    now = datetime(2026, 7, 21, 14, 0)
    # Before close, no cache -> should run
    assert should_run_analysis("D1", "XAUUSD", now) is True


def test_should_run_h4_with_cache(tmp_path, monkeypatch):
    """H4 should skip analysis when cache file exists for that period."""
    from src.analysis.candle_cache import should_run_analysis

    tmp = tmp_path / "analysis"
    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp))
    now = datetime(2026, 7, 21, 14, 30)  # H4 period 12-16
    # Create cache file for this period
    cache_dir = tmp / "2026" / "07" / "21" / "XAUUSD"
    cache_dir.mkdir(parents=True)
    (cache_dir / "h4-16-analysis.json").write_text(json.dumps({"cached": True}))
    assert should_run_analysis("H4", "XAUUSD", now) is False


def test_should_run_h4_without_cache(tmp_path, monkeypatch):
    """H4 should run analysis when no cache file exists."""
    from src.analysis.candle_cache import should_run_analysis

    tmp = tmp_path / "analysis"
    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp))
    now = datetime(2026, 7, 21, 14, 30)
    # No cache file -> should run
    assert should_run_analysis("H4", "XAUUSD", now) is True


# =============================================================================
# RED Tests for D1 should_run_analysis with staleness logic
# =============================================================================


def test_should_run_d1_before_close(tmp_path, monkeypatch):
    """D1 before close should always run analysis (candle not closed)."""
    from src.analysis.candle_cache import should_run_analysis

    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
    # 14:00 broker time, close_time=17:00 -> before close
    now = datetime(2026, 7, 21, 14, 0)
    assert should_run_analysis("D1", "XAUUSD", now) is True


def test_should_run_d1_after_close_with_cache(tmp_path, monkeypatch):
    """D1 after close with existing cache should skip analysis."""
    from src.analysis.candle_cache import should_run_analysis

    tmp = tmp_path / "analysis"
    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp))
    # 18:00 broker time, close_time=17:00 -> after close
    now = datetime(2026, 7, 21, 18, 0)
    # Create cache file for the current D1 period
    cache_dir = tmp / "2026" / "07" / "21" / "XAUUSD"
    cache_dir.mkdir(parents=True)
    (cache_dir / "d1-analysis.json").write_text(json.dumps({"cached": True}))
    assert should_run_analysis("D1", "XAUUSD", now) is False


def test_should_run_d1_after_close_without_cache(tmp_path, monkeypatch):
    """D1 after close without cache should run analysis."""
    from src.analysis.candle_cache import should_run_analysis

    tmp = tmp_path / "analysis"
    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp))
    now = datetime(2026, 7, 21, 18, 0)
    # No cache file -> should run
    assert should_run_analysis("D1", "XAUUSD", now) is True


def test_should_run_d1_cache_in_wrong_folder(tmp_path, monkeypatch):
    """Verify the path check uses the correct folder date, not a stale one."""
    from src.analysis.candle_cache import should_run_analysis

    tmp = tmp_path / "analysis"
    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp))
    now = datetime(2026, 7, 21, 18, 0)
    # Create cache in wrong folder (yesterday)
    wrong_dir = tmp / "2026" / "07" / "20" / "XAUUSD"
    wrong_dir.mkdir(parents=True)
    (wrong_dir / "d1-analysis.json").write_text(json.dumps({"cached": True}))
    # Cache not in correct period's folder -> should run
    assert should_run_analysis("D1", "XAUUSD", now) is True


# =============================================================================
# RED Tests for H1 should_run_analysis (no longer always-fresh)
# =============================================================================


def test_should_run_h1_without_cache(tmp_path, monkeypatch):
    """H1 should run analysis when no H1 cache file exists."""
    from src.analysis.candle_cache import should_run_analysis

    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
    now = datetime(2026, 7, 21, 14, 30)
    # No H1 cache -> should run
    assert should_run_analysis("H1", "XAUUSD", now) is True


def test_should_run_h1_with_cache(tmp_path, monkeypatch):
    """H1 should skip analysis when cache file exists for that period."""
    from src.analysis.candle_cache import should_run_analysis

    tmp = tmp_path / "analysis"
    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp))
    now = datetime(2026, 7, 21, 14, 30)
    # Create cache file for H1 period 14-15
    period_dir = tmp / "2026" / "07" / "21" / "XAUUSD"
    period_dir.mkdir(parents=True)
    (period_dir / "h1-15-analysis.json").write_text(json.dumps({"cached": True}))
    assert should_run_analysis("H1", "XAUUSD", now) is False


def test_should_run_h1_different_period(tmp_path, monkeypatch):
    """H1 should run when cache exists for a different period."""
    from src.analysis.candle_cache import should_run_analysis

    tmp = tmp_path / "analysis"
    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp))
    now = datetime(2026, 7, 21, 14, 30)
    # Create cache for H1 period 13-14 only
    period_dir = tmp / "2026" / "07" / "21" / "XAUUSD"
    period_dir.mkdir(parents=True)
    (period_dir / "h1-13-analysis.json").write_text(json.dumps({"cached": True}))
    # Current period is 14-15, no cache -> should run
    assert should_run_analysis("H1", "XAUUSD", now) is True


# =============================================================================
# RED Tests for save/load round-trip
# =============================================================================


def test_save_and_load_d1_round_trip(tmp_path, monkeypatch):
    """D1 save then load returns identical dict (round-trip fidelity)."""
    from src.analysis.candle_cache import load_cached_analysis, save_analysis

    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
    now = datetime(2026, 7, 21, 18, 0)
    result = {"confluence": {"entry_authorized": False}}
    save_analysis("D1", "XAUUSD", now, result)
    loaded = load_cached_analysis("D1", "XAUUSD", now)
    assert loaded == result


def test_save_and_load_h4_round_trip(tmp_path, monkeypatch):
    """H4 save then load returns identical dict."""
    from src.analysis.candle_cache import load_cached_analysis, save_analysis

    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
    now = datetime(2026, 7, 21, 14, 30)  # H4 period 12-16
    result = {"market_structure": {"primary_structure": "BULLISH"}}
    save_analysis("H4", "XAUUSD", now, result)
    loaded = load_cached_analysis("H4", "XAUUSD", now)
    assert loaded == result


def test_save_and_load_h1_round_trip(tmp_path, monkeypatch):
    """H1 save then load returns identical dict."""
    from src.analysis.candle_cache import load_cached_analysis, save_analysis

    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
    now = datetime(2026, 7, 21, 14, 30)  # H1 period 14-15
    result = {"market_structure": {"primary_structure": "BULLISH"}}
    save_analysis("H1", "XAUUSD", now, result)
    loaded = load_cached_analysis("H1", "XAUUSD", now)
    assert loaded == result


def test_load_returns_none_when_missing(tmp_path, monkeypatch):
    """Load returns None when no cache file exists."""
    from src.analysis.candle_cache import load_cached_analysis

    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
    now = datetime(2026, 7, 21, 14, 0)
    assert load_cached_analysis("D1", "XAUUSD", now) is None


def test_save_analysis_creates_directories(tmp_path, monkeypatch):
    """Save creates all necessary directories."""
    from src.analysis.candle_cache import save_analysis

    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
    now = datetime(2026, 7, 21, 18, 0)
    save_analysis("D1", "XAUUSD", now, {"test": True})
    assert (tmp_path / "analysis" / "2026" / "07" / "21" / "XAUUSD" / "d1-analysis.json").exists()


def test_save_h1_creates_hour_suffixed_file(tmp_path, monkeypatch):
    """H1 save creates a file with the hour suffix."""
    from src.analysis.candle_cache import save_analysis

    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
    now = datetime(2026, 7, 21, 14, 30)
    save_analysis("H1", "XAUUSD", now, {"test": True})
    expected = tmp_path / "analysis" / "2026" / "07" / "21" / "XAUUSD" / "h1-15-analysis.json"
    assert expected.exists()


def test_save_h4_creates_hour_suffixed_file(tmp_path, monkeypatch):
    """H4 save creates a file with the hour suffix."""
    from src.analysis.candle_cache import save_analysis

    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
    now = datetime(2026, 7, 21, 14, 30)  # H4 period 12-16
    save_analysis("H4", "XAUUSD", now, {"test": True})
    expected = tmp_path / "analysis" / "2026" / "07" / "21" / "XAUUSD" / "h4-16-analysis.json"
    assert expected.exists()


def test_load_handles_corrupt_json(tmp_path, monkeypatch):
    """Load returns None for corrupt JSON (does not raise)."""
    from src.analysis.candle_cache import load_cached_analysis

    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
    now = datetime(2026, 7, 21, 18, 0)
    path = tmp_path / "analysis" / "2026" / "07" / "21" / "XAUUSD"
    path.mkdir(parents=True)
    (path / "d1-analysis.json").write_text("not json")
    assert load_cached_analysis("D1", "XAUUSD", now) is None


def test_midnight_boundary_h4_save_and_load(tmp_path, monkeypatch):
    """H4 period ending at 00:00 stores under that date with h4-00 filename."""
    from src.analysis.candle_cache import load_cached_analysis, save_analysis

    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
    monkeypatch.setenv("TRADING_H4_CLOSE_TIME", "20:00")
    now = datetime(2026, 7, 21, 22, 0)  # H4 period 20:00-00:00
    result = {"test": True}
    save_analysis("H4", "XAUUSD", now, result)
    # File should be at date = 2026-07-21 (period start), hour = 00
    expected = tmp_path / "analysis" / "2026" / "07" / "21" / "XAUUSD" / "h4-00-analysis.json"
    assert expected.exists(), f"Expected {expected} to exist"
    loaded = load_cached_analysis("H4", "XAUUSD", now)
    assert loaded == result


def test_midnight_boundary_h1_save_and_load(tmp_path, monkeypatch):
    """H1 period ending at 00:00 stores under that date with h1-00 filename."""
    from src.analysis.candle_cache import load_cached_analysis, save_analysis

    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
    now = datetime(2026, 7, 22, 0, 30)  # H1 period 00-01
    result = {"test": True}
    save_analysis("H1", "XAUUSD", now, result)
    expected = tmp_path / "analysis" / "2026" / "07" / "22" / "XAUUSD" / "h1-01-analysis.json"
    assert expected.exists(), f"Expected {expected} to exist"
    loaded = load_cached_analysis("H1", "XAUUSD", now)
    assert loaded == result


# =============================================================================
# RED Tests for MTF cache support
# =============================================================================


def test_cache_path_mtf(tmp_path, monkeypatch):
    """MTF cache path must end with mtf-analysis.json."""
    from src.analysis.candle_cache import _cache_path, _get_cache_date

    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
    broker_now = datetime(2026, 7, 21, 14, 0)
    cache_date = _get_cache_date("MTF", broker_now)
    path = _cache_path("MTF", "XAUUSD", cache_date)
    assert path.endswith("mtf-analysis.json")


def test_cache_path_mtf_uses_d1_date(tmp_path, monkeypatch):
    """MTF cache path must use the same date as D1 cache path."""
    from src.analysis.candle_cache import _get_cache_date

    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
    broker_now = datetime(2026, 7, 21, 14, 0)
    mtf_cache_date = _get_cache_date("MTF", broker_now)
    d1_cache_date = _get_cache_date("D1", broker_now)
    assert mtf_cache_date.date() == d1_cache_date.date()


# =============================================================================
# Remaining existing tests (settings, DST) — untouched from original
# =============================================================================


def test_settings_has_d1_close_time(monkeypatch):
    from config.settings import Settings

    # Explicitly set the env so it's not influenced by .env
    monkeypatch.setenv("TRADING_D1_CLOSE_TIME", "17:00")
    s = Settings()
    assert hasattr(s, "d1_close_time")
    assert s.d1_close_time == "17:00"


def test_settings_has_h4_close_time():
    from config.settings import Settings

    s = Settings()
    assert hasattr(s, "h4_close_time")
    assert s.h4_close_time == "00:00"


def test_settings_has_h4_close_interval_hours():
    from config.settings import Settings

    s = Settings()
    assert hasattr(s, "h4_close_interval_hours")
    assert s.h4_close_interval_hours == 4


def test_settings_has_analysis_cache_dir():
    from config.settings import Settings

    s = Settings()
    assert hasattr(s, "analysis_cache_dir")
    assert s.analysis_cache_dir == "analysis"
