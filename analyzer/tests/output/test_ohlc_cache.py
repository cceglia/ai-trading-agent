"""Tests for OHLC bar cache."""

import json
import os
from datetime import datetime
from pathlib import Path

from src.analysis.candle_cache import get_cache_date
from src.output.ohlc_cache import load_ohlc_cache, ohlc_cache_path, save_ohlc_cache
from src.output.result_models import OHLCBar


class TestOhlcCachePath:
    def test_path_format_d1(self):
        cache_date = datetime(2026, 7, 26, 17, 0)
        path = ohlc_cache_path("D1", "XAUUSD", cache_date)
        assert "ohlc-D1.json" in path
        assert "XAUUSD" in path

    def test_path_format_h4(self):
        cache_date = datetime(2026, 7, 26, 16, 0)
        path = ohlc_cache_path("H4", "XAUUSD", cache_date)
        assert "ohlc-h4-16.json" in path

    def test_path_format_h1(self):
        cache_date = datetime(2026, 7, 26, 8, 0)
        path = ohlc_cache_path("H1", "XAUUSD", cache_date)
        assert "ohlc-h1-08.json" in path

    def test_directory_structure(self, monkeypatch):
        """Full path follows analysis/YYYY/MM/DD/SYMBOL/ pattern."""
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", "/tmp/test_analysis")
        # Reset ohlc_cache sentinel so it picks up the env var change
        import src.output.ohlc_cache as oc

        oc._settings = None

        cache_date = datetime(2026, 7, 26, 17, 0)
        path = ohlc_cache_path("D1", "XAUUSD", cache_date)
        assert path.startswith("/tmp/test_analysis/2026/07/26/XAUUSD/ohlc-D1.json")


class TestSaveLoadOhlcCache:
    def test_save_and_load_roundtrip(self, tmp_path: Path, monkeypatch):
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path))
        import src.output.ohlc_cache as oc

        oc._settings = None

        broker_now = datetime(2026, 7, 26, 8, 30)
        bars = [
            OHLCBar(time="2026-07-25T17:00", open=2350.0, high=2370.0, low=2345.0, close=2365.5),
            OHLCBar(time="2026-07-25T18:00", open=2365.0, high=2380.0, low=2355.0, close=2375.0),
        ]

        save_ohlc_cache("D1", "XAUUSD", broker_now, bars)
        loaded = load_ohlc_cache("D1", "XAUUSD", broker_now)

        assert loaded is not None
        assert len(loaded) == 2
        assert loaded[0].open == 2350.0
        assert loaded[1].close == 2375.0

    def test_load_missing_returns_none(self, tmp_path: Path, monkeypatch):
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path))
        import src.output.ohlc_cache as oc

        oc._settings = None

        broker_now = datetime(2026, 7, 26, 8, 30)
        loaded = load_ohlc_cache("D1", "NONEXISTENT", broker_now)
        assert loaded is None

    def test_save_creates_directory_tree(self, tmp_path: Path, monkeypatch):
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path))
        import src.output.ohlc_cache as oc

        oc._settings = None

        broker_now = datetime(2026, 7, 26, 8, 30)
        bars = [
            OHLCBar(time="2026-07-25T17:00", open=2350.0, high=2370.0, low=2345.0, close=2365.5)
        ]

        save_ohlc_cache("D1", "XAUUSD", broker_now, bars)

        cache_date = get_cache_date("D1", broker_now)
        expected_path = str(tmp_path / cache_date.strftime("%Y/%m/%d") / "XAUUSD" / "ohlc-D1.json")
        assert os.path.exists(expected_path)

    def test_corrupted_cache_returns_none(self, tmp_path: Path, monkeypatch):
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path))
        import src.output.ohlc_cache as oc

        oc._settings = None

        broker_now = datetime(2026, 7, 26, 8, 30)
        cache_date = get_cache_date("D1", broker_now)
        path = str(tmp_path / cache_date.strftime("%Y/%m/%d") / "XAUUSD" / "ohlc-D1.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write("not valid json")

        loaded = load_ohlc_cache("D1", "XAUUSD", broker_now)
        assert loaded is None

    def test_save_and_load_h4_roundtrip(self, tmp_path: Path, monkeypatch):
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path))
        import src.output.ohlc_cache as oc

        oc._settings = None

        # H4 period depends on settings; use a time that gives a predictable hour
        broker_now = datetime(2026, 7, 26, 14, 30)
        bars = [
            OHLCBar(time="2026-07-26T12:00", open=2350.0, high=2370.0, low=2345.0, close=2365.5)
        ]

        save_ohlc_cache("H4", "XAUUSD", broker_now, bars)
        loaded = load_ohlc_cache("H4", "XAUUSD", broker_now)

        assert loaded is not None
        assert len(loaded) == 1
        assert loaded[0].open == 2350.0

    def test_save_and_load_h1_roundtrip(self, tmp_path: Path, monkeypatch):
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path))
        import src.output.ohlc_cache as oc

        oc._settings = None

        broker_now = datetime(2026, 7, 26, 14, 30)
        bars = [
            OHLCBar(time="2026-07-26T14:00", open=2350.0, high=2370.0, low=2345.0, close=2365.5)
        ]

        save_ohlc_cache("H1", "XAUUSD", broker_now, bars)
        loaded = load_ohlc_cache("H1", "XAUUSD", broker_now)

        assert loaded is not None
        assert len(loaded) == 1

    def test_file_content_integrity(self, tmp_path: Path, monkeypatch):
        """Saved JSON file contains exactly the expected data."""
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path))
        import src.output.ohlc_cache as oc

        oc._settings = None

        broker_now = datetime(2026, 7, 26, 8, 30)
        bars = [
            OHLCBar(time="2026-07-25T17:00", open=2350.0, high=2370.0, low=2345.0, close=2365.5)
        ]

        save_ohlc_cache("D1", "XAUUSD", broker_now, bars)

        # Read the file directly and verify its content
        cache_date = get_cache_date("D1", broker_now)
        path = tmp_path / cache_date.strftime("%Y/%m/%d") / "XAUUSD" / "ohlc-D1.json"
        with open(path) as f:
            data = json.load(f)

        assert len(data) == 1
        assert data[0]["time"] == "2026-07-25T17:00"
        assert data[0]["open"] == 2350.0
        assert data[0]["high"] == 2370.0
        assert data[0]["low"] == 2345.0
        assert data[0]["close"] == 2365.5

    def test_empty_bars_list(self, tmp_path: Path, monkeypatch):
        """Saving an empty bar list should produce an empty JSON array."""
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path))
        import src.output.ohlc_cache as oc

        oc._settings = None

        broker_now = datetime(2026, 7, 26, 8, 30)
        save_ohlc_cache("D1", "XAUUSD", broker_now, [])

        cache_date = get_cache_date("D1", broker_now)
        path = tmp_path / cache_date.strftime("%Y/%m/%d") / "XAUUSD" / "ohlc-D1.json"
        with open(path) as f:
            data = json.load(f)
        assert data == []
