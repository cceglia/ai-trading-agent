"""Unit tests for ResultScanner."""

from __future__ import annotations

import json
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
        fpath = tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08-30.json"
        _write_result(fpath)

        s = ResultScanner(tmp_path)
        runs = s.list_runs()

        assert len(runs) == 1
        assert runs[0].symbol == "XAUUSD"
        assert runs[0].date == "2026-07-26"
        assert runs[0].time == "08-30"
        assert runs[0].bias == "bullish"
        assert runs[0].action == "buy_setup"
        assert runs[0].review_approved is True

    def test_filter_by_symbol(self, tmp_path: Path):
        for sym in ["XAUUSD", "EURUSD"]:
            fpath = tmp_path / "2026" / "07" / "26" / sym / "result-08-30.json"
            _write_result(fpath)

        s = ResultScanner(tmp_path)
        runs = s.list_runs(symbol="XAUUSD")

        assert len(runs) == 1
        assert runs[0].symbol == "XAUUSD"

    def test_filter_by_symbol_case_insensitive(self, tmp_path: Path):
        fpath = tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08-30.json"
        _write_result(fpath)

        s = ResultScanner(tmp_path)
        # The scanner uppercases the filter, so "xauusd" becomes "XAUUSD"
        runs = s.list_runs(symbol="xauusd")

        assert len(runs) == 1

    def test_filter_by_date_range(self, tmp_path: Path):
        for day in ["25", "26", "27"]:
            fpath = tmp_path / "2026" / "07" / day / "XAUUSD" / "result-08-30.json"
            _write_result(fpath)

        s = ResultScanner(tmp_path)
        runs = s.list_runs(from_date="2026-07-26", to_date="2026-07-26")

        assert len(runs) == 1
        assert runs[0].date == "2026-07-26"

    def test_filter_by_date_range_inclusive(self, tmp_path: Path):
        for day in ["25", "26", "27"]:
            fpath = tmp_path / "2026" / "07" / day / "XAUUSD" / "result-08-30.json"
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
        fpath = tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08-30.txt"
        _write_result(fpath)

        s = ResultScanner(tmp_path)
        runs = s.list_runs()

        assert len(runs) == 0

    def test_skips_non_object_json(self, tmp_path: Path):
        fpath = tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08-30.json"
        fpath.parent.mkdir(parents=True)
        fpath.write_text(json.dumps([1, 2, 3]))

        s = ResultScanner(tmp_path)
        runs = s.list_runs()

        assert len(runs) == 0

    def test_skips_malformed_json_in_list(self, tmp_path: Path):
        # Good file
        good = tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08-30.json"
        _write_result(good)

        # Bad file
        bad = tmp_path / "2026" / "07" / "25" / "XAUUSD" / "result-09-00.json"
        bad.parent.mkdir(parents=True)
        bad.write_text("not json")

        s = ResultScanner(tmp_path)
        runs = s.list_runs()

        assert len(runs) == 1

    def test_skips_wrong_path_depth(self, tmp_path: Path):
        """Files not in YYYY/MM/DD/SYMBOL/ pattern are skipped."""
        fpath = tmp_path / "2026" / "07" / "result-08-30.json"
        fpath.parent.mkdir(parents=True)
        fpath.write_text(
            json.dumps({"market_context": {}, "decision": {}, "review": {}})
        )

        s = ResultScanner(tmp_path)
        runs = s.list_runs()

        assert len(runs) == 0

    def test_uses_symbol_from_json_if_present(self, tmp_path: Path):
        """When JSON has a 'symbol' field, it overrides the path-derived symbol."""
        fpath = tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08-30.json"
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
        fpath = tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08-30.json"
        _write_result(fpath, sample_full_result)

        s = ResultScanner(tmp_path)
        result = s.get_run("XAUUSD", "2026", "07", "26", "result-08-30")

        assert result is not None
        assert result["decision"]["action"] == "buy_setup"
        assert result["market_context"]["bias"] == "bullish"

    def test_returns_none_for_missing(self, tmp_path: Path):
        s = ResultScanner(tmp_path)
        result = s.get_run("XAUUSD", "2026", "07", "26", "result-08-30")

        assert result is None

    def test_returns_none_for_malformed_json(self, tmp_path: Path):
        fpath = tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08-30.json"
        fpath.parent.mkdir(parents=True)
        fpath.write_text("not json {{{")

        s = ResultScanner(tmp_path)
        result = s.get_run("XAUUSD", "2026", "07", "26", "result-08-30")

        assert result is None

    def test_returns_none_for_missing_file(self, tmp_path: Path):
        fpath = tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08-30.json"
        fpath.parent.mkdir(parents=True)
        # Don't write the file

        s = ResultScanner(tmp_path)
        result = s.get_run("XAUUSD", "2026", "07", "26", "result-08-30")

        assert result is None
