"""Tests for synthesizer_cache — day-based synthesizer output caching.

``src/decision/synthesizer_cache.py`` does not exist yet, so all tests
fail RED with ``ModuleNotFoundError``.
"""

from __future__ import annotations

import json
import os
import pathlib
from datetime import datetime
from unittest.mock import patch

import pytest

from src.decision.models import MarketContextSummary

# This import will fail with ModuleNotFoundError — expected RED behaviour.
from src.decision.synthesizer_cache import (  # type: ignore[import-untyped]
    _get_settings,
    load_cached_synthesis,
    save_synthesis,
    should_run_synthesis,
)


# ---------------------------------------------------------------------------
# Autouse fixture
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def reset_synthesizer_cache_settings():
    """Reset the _settings sentinel before and after every test.

    Mirrors ``reset_candle_cache_settings`` in ``tests/conftest.py``.
    """
    import src.decision.synthesizer_cache

    src.decision.synthesizer_cache._settings = None
    yield
    src.decision.synthesizer_cache._settings = None


# ---------------------------------------------------------------------------
# Helper — shortcut for the most common MarketContextSummary
# ---------------------------------------------------------------------------
def _make_summary(**overrides: object) -> MarketContextSummary:
    defaults: dict[str, object] = {
        "symbol": "EURUSD",
        "bias": "bullish",
        "confidence": 75.0,
        "reasoning": "Test reasoning",
        "key_levels": [],
        "structural_events": [],
        "calendar_context": "",
        "current_price": 1.0,
    }
    defaults.update(overrides)
    return MarketContextSummary(**defaults)  # type: ignore[arg-type]


# ===================================================================
# Round-trip & miss / hit (basic)
# ===================================================================
class TestRoundTripAndMissHit:
    """Save→load round trip, cache miss, and cache hit scenarios."""

    # ------------------------------------------------------------------
    # 1. Round-trip
    # ------------------------------------------------------------------
    def test_save_and_load_round_trip(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Save a MarketContextSummary, load it back, assert deep equality."""
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
        summary = _make_summary()
        now = datetime(2026, 7, 25, 12, 0, 0)
        save_synthesis("EURUSD", now, summary)
        loaded = load_cached_synthesis("EURUSD", now)
        assert loaded is not None
        assert loaded.symbol == summary.symbol
        assert loaded.bias == summary.bias
        assert loaded.confidence == summary.confidence
        assert loaded.reasoning == summary.reasoning
        assert loaded.key_levels == summary.key_levels
        assert loaded.structural_events == summary.structural_events
        assert loaded.current_price == summary.current_price

    # ------------------------------------------------------------------
    # 2. Load returns None when file missing
    # ------------------------------------------------------------------
    def test_load_returns_none_when_file_missing(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Never saved — load_cached_synthesis returns None."""
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
        now = datetime(2026, 7, 25, 12, 0, 0)
        assert load_cached_synthesis("EURUSD", now) is None

    # ------------------------------------------------------------------
    # 3. should_run returns True on miss
    # ------------------------------------------------------------------
    def test_should_run_returns_true_on_miss(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Fresh cache directory — should_run_synthesis returns True."""
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
        now = datetime(2026, 7, 25, 12, 0, 0)
        assert should_run_synthesis("EURUSD", now) is True

    # ------------------------------------------------------------------
    # 4. should_run returns False on hit
    # ------------------------------------------------------------------
    def test_should_run_returns_false_on_hit(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """After save — should_run_synthesis returns False."""
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
        now = datetime(2026, 7, 25, 12, 0, 0)
        save_synthesis("EURUSD", now, _make_summary())
        assert should_run_synthesis("EURUSD", now) is False


# ===================================================================
# Corruption / edge cases
# ===================================================================
class TestCorruptionAndEdgeCases:
    """Corrupt JSON, pydantic validation failure, disk errors."""

    # ------------------------------------------------------------------
    # 6. Corrupt JSON
    # ------------------------------------------------------------------
    def test_load_returns_none_on_corrupt_json(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Write invalid JSON to cache file — load returns None (not crash)."""
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
        now = datetime(2026, 7, 25, 12, 0, 0)
        _write_raw_cache(tmp_path, "EURUSD", now, "not json")
        assert load_cached_synthesis("EURUSD", now) is None

    # ------------------------------------------------------------------
    # 7. Pydantic validation error
    # ------------------------------------------------------------------
    def test_load_returns_none_on_pydantic_validation_error(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Write dict missing required fields — load returns None (not crash)."""
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
        now = datetime(2026, 7, 25, 12, 0, 0)
        _write_raw_cache(
            tmp_path,
            "EURUSD",
            now,
            json.dumps({"symbol": "EURUSD"}),  # missing bias, confidence, etc.
        )
        assert load_cached_synthesis("EURUSD", now) is None

    # ------------------------------------------------------------------
    # 8. Save handles disk error gracefully
    # ------------------------------------------------------------------
    def test_save_does_not_raise_on_disk_error(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """When os.makedirs raises, save_synthesis logs warning and returns."""
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))

        def _failing_makedirs(path: str, exist_ok: bool = False) -> None:
            raise PermissionError(f"Permission denied: {path}")

        monkeypatch.setattr(os, "makedirs", _failing_makedirs)
        now = datetime(2026, 7, 25, 12, 0, 0)
        # Should not raise — just log a warning
        save_synthesis("EURUSD", now, _make_summary())

    # ------------------------------------------------------------------
    # 9. Load handles OS error gracefully
    # ------------------------------------------------------------------
    def test_load_does_not_raise_on_oserror(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """When open() raises, load_cached_synthesis returns None."""
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
        now = datetime(2026, 7, 25, 12, 0, 0)
        # Write a valid cache file first
        save_synthesis("EURUSD", now, _make_summary())

        # Then monkeypatch builtins.open to raise
        def _failing_open(*args: object, **kwargs: object) -> object:
            raise OSError("Simulated I/O error")

        monkeypatch.setattr("builtins.open", _failing_open)
        assert load_cached_synthesis("EURUSD", now) is None

    # ------------------------------------------------------------------
    # 10. Save propagates unexpected errors (RED — should fail now)
    # ------------------------------------------------------------------
    def test_save_propagates_unexpected_errors(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """save_synthesis should NOT catch errors that aren't OSError or
        pydantic ValidationError — only those specific types are expected."""
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))

        def _raising_dump(self, *args: object, **kwargs: object) -> dict:
            raise RuntimeError("unexpected error")

        with patch.object(MarketContextSummary, "model_dump", _raising_dump):
            with pytest.raises(RuntimeError, match="unexpected"):
                save_synthesis("EURUSD", datetime(2026, 7, 25, 12, 0), _make_summary())


# ===================================================================
# Settings / sentinel
# ===================================================================
class TestSettingsSentinel:
    """Lazy sentinel initialisation and env-driven disable."""

    # ------------------------------------------------------------------
    # 10. _get_settings uses sentinel
    # ------------------------------------------------------------------
    def test_get_settings_uses_sentinel(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """_settings is lazy-initialised; second call returns same instance."""
        import src.decision.synthesizer_cache

        src.decision.synthesizer_cache._settings = None
        s1 = _get_settings()
        s2 = _get_settings()
        assert s1 is s2

    # ------------------------------------------------------------------
    # 11. Sentinel can be reset
    # ------------------------------------------------------------------
    def test_settings_sentinel_can_be_reset(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Setting _settings = None re-reads Settings from env."""
        import src.decision.synthesizer_cache

        monkeypatch.setenv("TRADING_SYNTHESIZER_CACHE_ENABLED", "false")
        src.decision.synthesizer_cache._settings = None
        s1 = _get_settings()
        assert s1.synthesizer_cache_enabled is False

        monkeypatch.setenv("TRADING_SYNTHESIZER_CACHE_ENABLED", "true")
        src.decision.synthesizer_cache._settings = None
        s2 = _get_settings()
        assert s2.synthesizer_cache_enabled is True

        assert s1 is not s2  # different instances

    # ------------------------------------------------------------------
    # 12. Cache disabled by env
    # ------------------------------------------------------------------
    def test_cache_disabled_by_env(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Env false → should_run_synthesis returns True even after save."""
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
        monkeypatch.setenv("TRADING_SYNTHESIZER_CACHE_ENABLED", "false")
        now = datetime(2026, 7, 25, 12, 0, 0)
        save_synthesis("EURUSD", now, _make_summary())
        assert should_run_synthesis("EURUSD", now) is True


# ===================================================================
# Day key / cross-symbol
# ===================================================================
class TestDayKeyAndCrossSymbol:
    """Cache scoped by (symbol, day)."""

    # ------------------------------------------------------------------
    # 13. Day rollover
    # ------------------------------------------------------------------
    def test_day_rollover_invalidates_cache(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Save at 23:59 → load at 00:01 next day ⇒ miss."""
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
        evening = datetime(2026, 7, 25, 23, 59, 0)
        next_morning = datetime(2026, 7, 26, 0, 1, 0)
        save_synthesis("EURUSD", evening, _make_summary())
        assert should_run_synthesis("EURUSD", next_morning) is True
        assert load_cached_synthesis("EURUSD", next_morning) is None

    # ------------------------------------------------------------------
    # 14. Cross-symbol isolation
    # ------------------------------------------------------------------
    def test_cross_symbol_does_not_share_cache(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Save EURUSD → should_run_synthesis('XAUUSD', same time) ⇒ True."""
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
        now = datetime(2026, 7, 25, 12, 0, 0)
        save_synthesis("EURUSD", now, _make_summary())
        assert should_run_synthesis("XAUUSD", now) is True
        assert load_cached_synthesis("XAUUSD", now) is None

    # ------------------------------------------------------------------
    # 15. Cache file path format
    # ------------------------------------------------------------------
    def test_cache_file_path_format(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """File path is ``<analysis_cache_dir>/<YYYY>/<MM>/<DD>/<symbol>/synthesizer.json``."""
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
        now = datetime(2026, 7, 25, 12, 0, 0)
        save_synthesis("EURUSD", now, _make_summary())
        expected = tmp_path / "analysis" / "2026" / "07" / "25" / "EURUSD" / "synthesizer.json"
        assert expected.exists()

    # ------------------------------------------------------------------
    # 16. Save updates should_run to false
    # ------------------------------------------------------------------
    def test_save_updates_should_run_to_false(
        self, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """After save, next should_run for same symbol+day returns False."""
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
        now = datetime(2026, 7, 25, 12, 0, 0)
        assert should_run_synthesis("EURUSD", now) is True
        save_synthesis("EURUSD", now, _make_summary())
        assert should_run_synthesis("EURUSD", now) is False


# ===================================================================
# Internal helpers (not exported from the test module)
# ===================================================================
def _write_raw_cache(
    tmp_path: pathlib.Path,
    symbol: str,
    dt: datetime,
    content: str,
) -> None:
    """Write arbitrary content to where the cache file would live.

    This lets us simulate corrupt files, invalid JSON, etc. without
    going through ``save_synthesis``.
    """
    cache_dir = (
        tmp_path / "analysis" / f"{dt.year:04d}" / f"{dt.month:02d}" / f"{dt.day:02d}" / symbol
    )
    cache_dir.mkdir(parents=True, exist_ok=True)
    (cache_dir / "synthesizer.json").write_text(content)
