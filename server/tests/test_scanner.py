"""Unit tests for ResultScanner."""

from __future__ import annotations

import json
import os
from pathlib import Path

from src.scanner import ResultScanner


def _write_result(fpath: Path, data: dict | None = None) -> None:
    """Helper to write a result JSON file."""
    if data is None:
        data = {
            "market_context": {"current_price": 2400.0, "bias": "bullish"},
            "decision": {"action": "buy_setup", "confidence": 0.85},
            "review": {"approved": True},
        }
    fpath.parent.mkdir(parents=True, exist_ok=True)
    fpath.write_text(json.dumps(data))


class TestListRuns:
    """Tests for ResultScanner.list_runs()."""

    def test_empty_dir_returns_empty_list(self, tmp_path: Path):
        s = ResultScanner(tmp_path)
        assert s.list_runs() == []

    def test_missing_dir_returns_empty_list(self, tmp_path: Path):
        s = ResultScanner(tmp_path / "nonexistent")
        assert s.list_runs() == []

    def test_finds_result_files(self, tmp_path: Path):
        fpath = tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08.json"
        _write_result(fpath)

        s = ResultScanner(tmp_path)
        runs = s.list_runs()

        assert len(runs) == 1
        assert runs[0].symbol == "XAUUSD"
        assert runs[0].date == "2026-07-26"
        assert runs[0].time == "08"
        assert runs[0].bias == "bullish"
        assert runs[0].action == "buy_setup"
        assert runs[0].review_approved is True

    def test_filter_by_symbol(self, tmp_path: Path):
        for sym in ["XAUUSD", "EURUSD"]:
            fpath = tmp_path / "2026" / "07" / "26" / sym / "result-08.json"
            _write_result(fpath)

        s = ResultScanner(tmp_path)
        runs = s.list_runs(symbol="XAUUSD")

        assert len(runs) == 1
        assert runs[0].symbol == "XAUUSD"

    def test_filter_by_symbol_case_insensitive(self, tmp_path: Path):
        fpath = tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08.json"
        _write_result(fpath)

        s = ResultScanner(tmp_path)
        # The scanner uppercases the filter, so "xauusd" becomes "XAUUSD"
        runs = s.list_runs(symbol="xauusd")

        assert len(runs) == 1

    def test_filter_by_date_range(self, tmp_path: Path):
        for day in ["25", "26", "27"]:
            fpath = tmp_path / "2026" / "07" / day / "XAUUSD" / "result-08.json"
            _write_result(fpath)

        s = ResultScanner(tmp_path)
        runs = s.list_runs(from_date="2026-07-26", to_date="2026-07-26")

        assert len(runs) == 1
        assert runs[0].date == "2026-07-26"

    def test_filter_by_date_range_inclusive(self, tmp_path: Path):
        for day in ["25", "26", "27"]:
            fpath = tmp_path / "2026" / "07" / day / "XAUUSD" / "result-08.json"
            _write_result(fpath)

        s = ResultScanner(tmp_path)
        runs = s.list_runs(from_date="2026-07-26", to_date="2026-07-27")

        assert len(runs) == 2

    def test_sort_order_date_desc_time_desc(self, tmp_path: Path):
        for day, time_str in [("25", "10-00"), ("26", "08-30"), ("26", "09-00")]:
            fpath = (
                tmp_path / "2026" / "07" / day / "XAUUSD" / f"result-{time_str}.json"
            )
            _write_result(fpath)

        s = ResultScanner(tmp_path)
        runs = s.list_runs()

        assert len(runs) == 3
        # Newest first: 2026-07-26 09-00, then 2026-07-26 08-30, then 2026-07-25 10-00
        assert runs[0].date == "2026-07-26" and runs[0].time == "09-00"
        assert runs[1].date == "2026-07-26" and runs[1].time == "08-30"
        assert runs[2].date == "2026-07-25"

    def test_skips_non_json_files(self, tmp_path: Path):
        fpath = tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08.txt"
        _write_result(fpath)

        s = ResultScanner(tmp_path)
        runs = s.list_runs()

        assert len(runs) == 0

    def test_skips_non_object_json(self, tmp_path: Path):
        fpath = tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08.json"
        fpath.parent.mkdir(parents=True)
        fpath.write_text(json.dumps([1, 2, 3]))

        s = ResultScanner(tmp_path)
        runs = s.list_runs()

        assert len(runs) == 0

    def test_skips_malformed_json_in_list(self, tmp_path: Path):
        # Good file
        good = tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08.json"
        _write_result(good)

        # Bad file
        bad = tmp_path / "2026" / "07" / "25" / "XAUUSD" / "result-09.json"
        bad.parent.mkdir(parents=True)
        bad.write_text("not json")

        s = ResultScanner(tmp_path)
        runs = s.list_runs()

        assert len(runs) == 1

    def test_skips_wrong_path_depth(self, tmp_path: Path):
        """Files not in YYYY/MM/DD/SYMBOL/ pattern are skipped."""
        fpath = tmp_path / "2026" / "07" / "result-08.json"
        fpath.parent.mkdir(parents=True)
        fpath.write_text(
            json.dumps({"market_context": {}, "decision": {}, "review": {}})
        )

        s = ResultScanner(tmp_path)
        runs = s.list_runs()

        assert len(runs) == 0

    def test_uses_symbol_from_json_if_present(self, tmp_path: Path):
        """When JSON has a 'symbol' field, it overrides the path-derived symbol."""
        fpath = tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08.json"
        _write_result(
            fpath,
            data={
                "symbol": "GOLD",
                "market_context": {"current_price": 2400.0, "bias": "bullish"},
                "decision": {"action": "buy_setup", "confidence": 0.85},
                "review": {"approved": True},
            },
        )

        s = ResultScanner(tmp_path)
        runs = s.list_runs()

        assert runs[0].symbol == "GOLD"


class TestGetRun:
    """Tests for ResultScanner.get_run()."""

    def test_returns_full_result(self, tmp_path: Path, sample_full_result: dict):
        fpath = tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08.json"
        _write_result(fpath, sample_full_result)

        s = ResultScanner(tmp_path)
        result = s.get_run("XAUUSD", "2026", "07", "26", "result-08")

        assert result is not None
        assert result["decision"]["action"] == "buy_setup"
        assert result["market_context"]["bias"] == "bullish"

    def test_returns_none_for_missing(self, tmp_path: Path):
        s = ResultScanner(tmp_path)
        result = s.get_run("XAUUSD", "2026", "07", "26", "result-08")

        assert result is None

    def test_returns_none_for_malformed_json(self, tmp_path: Path):
        fpath = tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08.json"
        fpath.parent.mkdir(parents=True)
        fpath.write_text("not json {{{")

        s = ResultScanner(tmp_path)
        result = s.get_run("XAUUSD", "2026", "07", "26", "result-08")

        assert result is None

    def test_returns_none_for_missing_file(self, tmp_path: Path):
        fpath = tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08.json"
        fpath.parent.mkdir(parents=True)
        # Don't write the file

        s = ResultScanner(tmp_path)
        result = s.get_run("XAUUSD", "2026", "07", "26", "result-08")

        assert result is None


class TestListRunsPruning:
    """Directory pruning: when symbol is provided only matching dirs are walked."""

    def test_empty_dir_returns_empty_list_with_symbol(self, tmp_path: Path):
        s = ResultScanner(tmp_path)
        assert s.list_runs(symbol="XAUUSD") == []

    def test_only_walks_matching_symbol(self, tmp_path: Path):
        """EURUSD must NOT be discovered when scanning for XAUUSD."""
        for sym in ["XAUUSD", "EURUSD"]:
            _write_result(tmp_path / "2026" / "07" / "26" / sym / "result-08.json")

        s = ResultScanner(tmp_path)
        runs = s.list_runs(symbol="XAUUSD")

        assert len(runs) == 1
        assert runs[0].symbol == "XAUUSD"

    def test_pruning_avoids_os_walk(self, tmp_path: Path):
        """The pruned path does *not* call os.walk."""
        for sym in ["XAUUSD", "EURUSD", "GBPUSD"]:
            _write_result(tmp_path / "2026" / "07" / "26" / sym / "result-08.json")

        s = ResultScanner(tmp_path)

        # Patch os.walk so it would fail if called
        original_walk = os.walk
        failed = False

        def _raising_walk(*args, **_kwargs):
            nonlocal failed
            failed = True
            return original_walk(*args, **_kwargs)

        import src.scanner as scanner_mod

        scanner_mod.os.walk = _raising_walk
        try:
            runs = s.list_runs(symbol="XAUUSD")
        finally:
            scanner_mod.os.walk = original_walk

        assert len(runs) == 1
        assert runs[0].symbol == "XAUUSD"
        assert not failed, "os.walk was called despite symbol filter"

    def test_pruning_with_date_filter(self, tmp_path: Path):
        """Date ranges narrow the walked directories."""
        for day in ["25", "26", "27"]:
            _write_result(tmp_path / "2026" / "07" / day / "XAUUSD" / "result-08.json")

        s = ResultScanner(tmp_path)
        runs = s.list_runs(
            symbol="XAUUSD", from_date="2026-07-26", to_date="2026-07-26"
        )

        assert len(runs) == 1
        assert runs[0].date == "2026-07-26"

    def test_pruning_no_matching_symbol_returns_empty(self, tmp_path: Path):
        _write_result(tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08.json")

        s = ResultScanner(tmp_path)
        runs = s.list_runs(symbol="EURUSD")

        assert len(runs) == 0


class TestListRunsCache:
    """LRU caching with TTL."""

    def test_cache_returns_results_without_io(self, tmp_path: Path):
        """Second identical call returns cached results; deleting files has no effect."""
        for sym in ["XAUUSD", "EURUSD"]:
            _write_result(tmp_path / "2026" / "07" / "26" / sym / "result-08.json")

        s = ResultScanner(tmp_path, cache_ttl=60)

        # First call — populates cache
        runs1 = s.list_runs()
        assert len(runs1) == 2

        # Wipe all result files
        for f in tmp_path.rglob("*.json"):
            f.unlink()

        # Second call — must return cached result (no IO)
        runs2 = s.list_runs()
        assert len(runs2) == 2
        assert runs2 == runs1

    def test_invalidate_cache_clears_entries(self, tmp_path: Path):
        """After invalidate_cache a subsequent read picks up disk changes."""
        _write_result(tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08.json")

        s = ResultScanner(tmp_path, cache_ttl=60)

        runs1 = s.list_runs(symbol="XAUUSD")
        assert len(runs1) == 1

        # Add a second file without invalidating — cache is still fresh
        _write_result(tmp_path / "2026" / "07" / "25" / "XAUUSD" / "result-09.json")
        runs2 = s.list_runs(symbol="XAUUSD")
        assert len(runs2) == 1  # still cached

        # Invalidate — fresh read must pick up both files
        s.invalidate_cache()
        runs3 = s.list_runs(symbol="XAUUSD")
        assert len(runs3) == 2

    def test_invalidate_cache_clears_entries_no_recreation(self, tmp_path: Path):
        """After invalidate_cache and file deletion, fresh read returns empty."""
        _write_result(tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08.json")

        s = ResultScanner(tmp_path, cache_ttl=60)

        runs1 = s.list_runs(symbol="XAUUSD")
        assert len(runs1) == 1

        # Delete the file, invalidate, re-read
        for f in tmp_path.rglob("*.json"):
            f.unlink()
        s.invalidate_cache()

        runs2 = s.list_runs(symbol="XAUUSD")
        assert len(runs2) == 0

    def test_cache_respects_ttl(self, tmp_path: Path):
        _write_result(tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08.json")

        s = ResultScanner(tmp_path, cache_ttl=0)  # 0 TTL = immediate expiry

        runs1 = s.list_runs(symbol="XAUUSD")
        assert len(runs1) == 1

        # Add a second file after first call
        _write_result(tmp_path / "2026" / "07" / "25" / "XAUUSD" / "result-09.json")

        # TTL is 0 so this must re-read from disk
        runs2 = s.list_runs(symbol="XAUUSD")
        assert len(runs2) == 2

    def test_cache_key_separation(self, tmp_path: Path):
        """Different filter tuples produce different cache entries."""
        for sym in ["XAUUSD", "EURUSD"]:
            _write_result(tmp_path / "2026" / "07" / "26" / sym / "result-08.json")

        s = ResultScanner(tmp_path, cache_ttl=60)

        # Populate cache for two different queries
        runs_xau = s.list_runs(symbol="XAUUSD")
        assert len(runs_xau) == 1

        runs_all = s.list_runs()
        assert len(runs_all) == 2

        # Wipe disk
        for f in tmp_path.rglob("*.json"):
            f.unlink()

        # Each key still returns its own cached result
        assert len(s.list_runs(symbol="XAUUSD")) == 1
        assert len(s.list_runs()) == 2

    def test_cache_not_used_after_ttl_expiry(self, tmp_path: Path, monkeypatch):
        """Force TTL expiry by monkey-patching time.monotonic."""
        import time

        _write_result(tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08.json")

        s = ResultScanner(tmp_path, cache_ttl=60)

        runs1 = s.list_runs(symbol="XAUUSD")
        assert len(runs1) == 1

        # Add a second file
        _write_result(tmp_path / "2026" / "07" / "25" / "XAUUSD" / "result-09.json")

        # Advance monotonic clock past TTL
        original_monotonic = time.monotonic

        class _FakeClock:
            def __init__(self):
                self.base = original_monotonic()
                self.offset = 0

            def __call__(self):
                return self.base + self.offset

        fake = _FakeClock()
        monkeypatch.setattr(time, "monotonic", fake)
        fake.offset = 120  # past the 60s TTL

        # Must re-read, picking up the new file
        runs2 = s.list_runs(symbol="XAUUSD")
        assert len(runs2) == 2

    def test_cache_empty_result(self, tmp_path: Path):
        """Empty list results are also cached."""
        s = ResultScanner(tmp_path, cache_ttl=60)

        # First read on empty dir
        runs1 = s.list_runs(symbol="XAUUSD")
        assert runs1 == []

        # Create a file — should not be picked up because cache is still valid
        _write_result(tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08.json")

        runs2 = s.list_runs(symbol="XAUUSD")
        assert runs2 == []  # still cached empty

        s.invalidate_cache()
        runs3 = s.list_runs(symbol="XAUUSD")
        assert len(runs3) == 1
