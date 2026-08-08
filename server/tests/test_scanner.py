"""Unit tests for ResultScanner (v2 envelopes + legacy adapter)."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from src.scanner import LegacyAdapter, ResultScanner

_LEGACY_FIXTURE = {
    "version": "1.0",
    "symbol": "XAUUSD",
    "market_context": {"current_price": 2400.0, "bias": "bullish", "confidence": 0.85},
    "decision": {"action": "buy_setup", "confidence": 0.85},
    "review": {"status": "APPROVED", "approved": True},
}


def _write_result(fpath: Path, data: dict | None = None) -> None:
    """Helper to write a result JSON file."""
    if data is None:
        data = _LEGACY_FIXTURE
    fpath.parent.mkdir(parents=True, exist_ok=True)
    fpath.write_text(json.dumps(data))


def _v2_envelope(**overrides) -> dict:
    """Minimal schema-v2 envelope mirroring the analyzer writer output."""
    data = {
        "schema_version": "2",
        "symbol": "XAUUSD",
        "run_id": "2026-07-26T08:30:00",
        "started_at": "2026-07-26T08:30:00",
        "completed_at": "2026-07-26T08:31:00",
        "status": "success",
        "errors": [],
        "fatal_error": None,
        "deterministic_facts": {
            "symbol": "XAUUSD",
            "timeframes": {},
            "setup_status": "READY",
            "direction": "LONG",
            "trade_direction": "BULLISH",
            "setup_grade": "AAA",
            "setup_classification_status": "CLASSIFIED",
            "setup_lifecycle_status": "TRIGGERED",
            "entry_plan": {},
            "rr": {"calculated_rr": 2.0, "minimum_required_rr": 2.0, "rr_pass": True},
            "confidence_components": {},
            "policy": {
                "execution_status": "ACTIONABLE",
                "actionable": True,
                "blockers": [],
                "reason_codes": [],
            },
            "selected_levels": {},
            "latest_structural_events": {},
            "latest_liquidity_states": {},
            "event_history": {},
            "liquidity_history": {},
            "validation_status": "VALID",
            "validation_errors": [],
            "operational": True,
            "entry_authorized": False,
            "bias": "BULLISH",
            "confidence": 72.0,
        },
        "decision": {"action": "buy_setup"},
        "synthesis": {
            "status": "SUCCESS",
            "explanation": "deterministic context is bullish",
            "risks": [],
            "confluences": [],
            "error": None,
        },
        "ohlc": {"D1": [], "H4": [], "H1": []},
    }
    data.update(overrides)
    return data


class TestListRuns:
    """Tests for ResultScanner.list_runs()."""

    def test_empty_dir_returns_empty_list(self, tmp_path: Path):
        s = ResultScanner(tmp_path)
        assert s.list_runs() == []

    def test_missing_dir_returns_empty_list(self, tmp_path: Path):
        s = ResultScanner(tmp_path / "nonexistent")
        assert s.list_runs() == []

    def test_finds_legacy_result_files(self, tmp_path: Path):
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
        assert runs[0].validation_status == "UNKNOWN"
        assert runs[0].setup_status == "UNKNOWN"
        assert runs[0].direction == "NONE"
        assert runs[0].operational is False

    def test_v2_summary_contract(self, tmp_path: Path):
        fpath = tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08.json"
        _write_result(fpath, _v2_envelope())

        s = ResultScanner(tmp_path)
        runs = s.list_runs()

        assert len(runs) == 1
        summary = runs[0]
        assert summary.validation_status == "VALID"
        assert summary.setup_status == "READY"
        assert summary.direction == "LONG"
        assert summary.operational is True
        assert summary.action == "buy_setup"
        assert summary.bias == "BULLISH"
        assert summary.confidence == 72.0

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

    def test_skips_error_results_without_analysis_context(self, tmp_path: Path):
        """Legacy fatal results must not make the run list endpoint fail."""
        fpath = tmp_path / "2026" / "07" / "31" / "EURUSD" / "result-07.json"
        _write_result(
            fpath,
            data={
                "symbol": "EURUSD",
                "status": "error",
                "fatal_error": "Data fetch failed",
                "market_context": None,
                "decision": None,
                "review": None,
            },
        )

        s = ResultScanner(tmp_path)

        assert s.list_runs() == []

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
        fpath.write_text(json.dumps({"market_context": {}, "decision": {}}))

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
            },
        )

        s = ResultScanner(tmp_path)
        runs = s.list_runs()

        assert runs[0].symbol == "GOLD"


class TestGetRun:
    """Tests for ResultScanner.get_run()."""

    def test_v2_result_returned_as_is(self, tmp_path: Path):
        fpath = tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08.json"
        _write_result(fpath, _v2_envelope())

        s = ResultScanner(tmp_path)
        result = s.get_run("XAUUSD", "2026", "07", "26", "result-08")

        assert result is not None
        assert result["schema_version"] == "2"
        assert result["decision"]["action"] == "buy_setup"
        assert result["deterministic_facts"]["validation_status"] == "VALID"
        assert "review" not in result

    def test_legacy_result_is_adapted(self, tmp_path: Path):
        fpath = tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08.json"
        _write_result(
            fpath,
            data={
                "symbol": "XAUUSD",
                "market_context": {"bias": "bullish", "confidence": 0.85},
                "decision": {"action": "buy_setup"},
                "review": {"status": "APPROVED", "approved": True},
            },
        )

        s = ResultScanner(tmp_path)
        result = s.get_run("XAUUSD", "2026", "07", "26", "result-08")

        assert result is not None
        assert result["schema_version"] == "legacy"
        facts = result["deterministic_facts"]
        assert facts["validation_status"] == "UNKNOWN"
        assert facts["operational"] is False
        assert facts["entry_authorized"] is False
        assert result["decision"]["action"] == "buy_setup"
        assert "review" not in result
        assert "review_approved" not in json.dumps(result)

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

    def test_returns_none_for_non_object_json(self, tmp_path: Path):
        fpath = tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08.json"
        fpath.parent.mkdir(parents=True)
        fpath.write_text(json.dumps([1, 2, 3]))

        s = ResultScanner(tmp_path)
        result = s.get_run("XAUUSD", "2026", "07", "26", "result-08")

        assert result is None


class TestLegacyAdapter:
    """The legacy adapter is read-only, idempotent, and review-free (AC-015)."""

    def test_adapt_is_idempotent(self):
        adapter = LegacyAdapter()
        data = {
            "symbol": "XAUUSD",
            "market_context": {"bias": "bearish", "confidence": 0.4},
            "decision": {"action": "no_trade"},
            "review": {"approved": False, "reasoning": "legacy"},
        }
        once = adapter.adapt(data)
        twice = adapter.adapt(once)
        assert twice == once

    def test_adapt_never_mutates_source(self):
        adapter = LegacyAdapter()
        data = {
            "symbol": "XAUUSD",
            "market_context": {"bias": "bearish"},
            "decision": {"action": "no_trade"},
            "review": {"approved": True},
        }
        snapshot = json.dumps(data, sort_keys=True)
        adapter.adapt(data)
        assert json.dumps(data, sort_keys=True) == snapshot

    def test_adapt_drops_all_review_fields(self):
        adapter = LegacyAdapter()
        data = {
            "symbol": "XAUUSD",
            "market_context": {"bias": "bullish"},
            "decision": {"action": "buy_setup"},
            "review": {"status": "APPROVED", "approved": True},
            "review_advisory_levels": {"entry_price": 1.0},
            "reviewer": "legacy-reviewer",
        }
        result = adapter.adapt(data)
        dumped = json.dumps(result)
        assert "review" not in dumped
        assert "reviewer" not in dumped

    def test_adapt_marks_unknown_and_non_operational(self):
        adapter = LegacyAdapter()
        result = adapter.adapt(
            {
                "symbol": "XAUUSD",
                "market_context": {"bias": "bullish", "confidence": 0.9},
                "decision": {"action": "buy_setup"},
            }
        )
        facts = result["deterministic_facts"]
        assert result["schema_version"] == "legacy"
        assert facts["validation_status"] == "UNKNOWN"
        assert facts["setup_status"] == "UNKNOWN"
        assert facts["direction"] == "NONE"
        assert facts["operational"] is False
        assert facts["entry_authorized"] is False
        assert facts["bias"] == "bullish"
        assert facts["confidence"] == 0.9
        assert result["decision"]["action"] == "buy_setup"

    def test_adapt_handles_missing_context(self):
        adapter = LegacyAdapter()
        result = adapter.adapt({"symbol": "XAUUSD"})
        facts = result["deterministic_facts"]
        assert facts["validation_status"] == "UNKNOWN"
        assert facts["operational"] is False
        assert result["decision"]["action"] == "no_trade"
        assert facts["bias"] is None
        assert facts["confidence"] is None

    @pytest.mark.parametrize(
        "raw",
        [
            None,
            "",
            "wait_for_setup",
            "wait_for_entry",
            "whatever",
            "NO_TRADE",
            42,
            ["buy_setup"],
        ],
    )
    def test_adapt_collapses_non_canonical_actions_to_no_trade(self, raw):
        """Any non-canonical legacy action collapses to ``no_trade`` (DEC-002)."""
        adapter = LegacyAdapter()
        result = adapter.adapt({"symbol": "XAUUSD", "decision": {"action": raw}})
        assert result["decision"]["action"] == "no_trade"

    @pytest.mark.parametrize("action", ["buy_setup", "sell_setup"])
    def test_adapt_passes_through_setup_actions(self, action):
        adapter = LegacyAdapter()
        result = adapter.adapt({"symbol": "XAUUSD", "decision": {"action": action}})
        assert result["decision"]["action"] == action

    def test_adapt_wait_for_setup_is_idempotent(self):
        """Collapsing ``wait_for_setup`` still yields a stable second pass."""
        adapter = LegacyAdapter()
        data = {"symbol": "XAUUSD", "decision": {"action": "wait_for_setup"}}
        once = adapter.adapt(data)
        assert once["decision"]["action"] == "no_trade"
        assert adapter.adapt(once) == once


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


class TestSharedRootRoundTrip:
    """TEST-014 / AC-014: a v2 file written by the analyzer at the shared
    project-root data directory is immediately discoverable by the server
    scanner."""

    @staticmethod
    def _project_root() -> Path:
        return Path(__file__).resolve().parent.parent.parent

    def test_analyzer_written_v2_file_is_discoverable(self, tmp_path: Path):
        import os
        import subprocess
        import sys
        import textwrap

        root = tmp_path
        analyzer_dir = str(self._project_root() / "analyzer")
        snippet = textwrap.dedent(
            """
            import os
            import sys

            sys.path.insert(0, os.environ["ANALYZER_DIR"])
            from datetime import datetime

            from src.output.result_models import AnalysisResult, SLTPOverlay
            from src.output.result_writer import ResultWriter

            res = AnalysisResult(
                symbol="XAUUSD",
                run_id="shared-root-run",
                started_at=datetime(2026, 8, 7, 12, 0),
                completed_at=datetime(2026, 8, 7, 12, 1),
                status="success",
                validation_status="INVALID",
                setup_status="INVALID",
                direction="NONE",
                final_action="no_trade",
                sl_tp_overlay=SLTPOverlay(),
            )
            writer = ResultWriter(os.environ["SHARED_ROOT"])
            path = writer.write(
                "XAUUSD",
                {"analysis_result": res, "errors": [], "fatal_error": None},
                {},
                datetime(2026, 8, 7, 12, 0),
            )
            assert path is not None
            print(path)
            """
        )
        env = {
            **os.environ,
            "ANALYZER_DIR": analyzer_dir,
            "SHARED_ROOT": str(root),
        }
        subprocess.run(
            [sys.executable, "-c", snippet],
            check=True,
            capture_output=True,
            text=True,
            cwd=str(self._project_root() / "analyzer"),
            env=env,
        )

        s = ResultScanner(root)
        runs = s.list_runs()
        assert len(runs) == 1
        summary = runs[0]
        assert summary.symbol == "XAUUSD"
        assert summary.date == "2026-08-07"
        assert summary.validation_status == "INVALID"
        assert summary.setup_status == "INVALID"
        assert summary.operational is False
        assert summary.action == "no_trade"

        full = s.get_run("XAUUSD", "2026", "08", "07", "result-12")
        assert full is not None
        assert full["schema_version"] == "2"
        assert full["deterministic_facts"]["validation_status"] == "INVALID"
        assert full["decision"]["action"] == "no_trade"
        assert "review" not in full

    def test_relative_shared_root_writer_and_scanner_same_absolute_root(
        self, tmp_path: Path
    ):
        """ROOT-001 / AC-014: with a RELATIVE TRADING_ANALYSIS_CACHE_DIR the
        analyzer writer (built through the real ``main._initialize_pipeline``
        seam) and the server scanner resolve to the SAME absolute project-root
        root; a freshly written v2 file is immediately discoverable.

        The raw possibly-relative value (default ``"data"``) must never reach
        ``ResultWriter`` directly — the seam hands it the resolved absolute
        path so analyzer and server share one root regardless of CWD.
        """
        import os
        import subprocess
        import sys
        import textwrap

        root = tmp_path
        project_root = self._project_root()
        analyzer_dir = str(project_root / "analyzer")
        # A relative value that resolves (against project root) to tmp_path.
        relative = os.path.relpath(str(root), str(project_root))

        snippet = textwrap.dedent(
            """
            import os
            import sys
            from datetime import datetime
            from pathlib import Path
            from unittest.mock import MagicMock

            sys.path.insert(0, os.environ["ANALYZER_DIR"])

            import main
            from config.settings import Settings
            from src.output.result_models import AnalysisResult, SLTPOverlay

            # Build the writer through the same seam main.run() uses.
            main.TerminalDataProvider = MagicMock()
            main.MarketStructureEngine = MagicMock()
            main.ForexFactoryCalendar = MagicMock()
            main._create_agents = MagicMock(return_value=MagicMock())
            main.TradingGraph = MagicMock()

            settings = Settings()
            _graph, writer = main._initialize_pipeline(settings, MagicMock())

            # ROOT-001: the writer must target the resolved absolute root,
            # never the raw possibly-relative value (CWD-relative).
            expected = Path(settings.resolved_analysis_cache_dir)
            assert writer.base_dir == expected, (writer.base_dir, expected)
            assert writer.base_dir.is_absolute(), writer.base_dir
            assert expected.is_absolute(), expected

            res = AnalysisResult(
                symbol="XAUUSD",
                run_id="relative-shared-root-run",
                started_at=datetime(2026, 8, 7, 12, 0),
                completed_at=datetime(2026, 8, 7, 12, 1),
                status="success",
                validation_status="INVALID",
                setup_status="INVALID",
                direction="NONE",
                final_action="no_trade",
                sl_tp_overlay=SLTPOverlay(),
            )
            path = writer.write(
                "XAUUSD",
                {"analysis_result": res, "errors": [], "fatal_error": None},
                {},
                datetime(2026, 8, 7, 12, 0),
            )
            assert path is not None
            print(path)
            """
        )
        env = {
            **os.environ,
            "ANALYZER_DIR": analyzer_dir,
            "TRADING_ANALYSIS_CACHE_DIR": relative,
        }
        subprocess.run(
            [sys.executable, "-c", snippet],
            check=True,
            capture_output=True,
            text=True,
            cwd=str(project_root / "analyzer"),
            env=env,
        )

        # Server side: the same relative value must resolve to the same root.
        from src.settings import WebSettings

        server_root = WebSettings(analysis_cache_dir=relative).resolved_cache_dir
        assert server_root.resolve() == root.resolve()

        s = ResultScanner(server_root)
        runs = s.list_runs()
        assert len(runs) == 1
        summary = runs[0]
        assert summary.symbol == "XAUUSD"
        assert summary.date == "2026-08-07"
        assert summary.validation_status == "INVALID"
        assert summary.setup_status == "INVALID"
        assert summary.operational is False
        assert summary.action == "no_trade"

        full = s.get_run("XAUUSD", "2026", "08", "07", "result-12")
        assert full is not None
        assert full["schema_version"] == "2"
        assert "review" not in full


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


class TestLegacyReadDiagnostics:
    """Legacy reads increment a bounded counter and emit a warning (NFR §18)."""

    def test_get_run_counts_legacy_reads(self, tmp_path: Path):
        _write_result(tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08.json")
        s = ResultScanner(tmp_path)
        assert s.legacy_reads == 0
        s.get_run("XAUUSD", "2026", "07", "26", "result-08")
        assert s.legacy_reads == 1
        # Reading again increments the bounded counter.
        s.get_run("XAUUSD", "2026", "07", "26", "result-08")
        assert s.legacy_reads == 2

    def test_list_runs_counts_legacy_reads(self, tmp_path: Path):
        _write_result(tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08.json")
        s = ResultScanner(tmp_path)
        assert s.list_runs(symbol="XAUUSD")
        assert s.legacy_reads == 1

    def test_v2_reads_do_not_count_as_legacy(self, tmp_path: Path):
        _write_result(
            tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08.json",
            data=_v2_envelope(),
        )
        s = ResultScanner(tmp_path)
        s.get_run("XAUUSD", "2026", "07", "26", "result-08")
        assert s.legacy_reads == 0

    def test_legacy_read_logs_warning(self, tmp_path: Path, caplog):
        _write_result(tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08.json")
        s = ResultScanner(tmp_path)
        with caplog.at_level("WARNING", logger="src.scanner"):
            s.get_run("XAUUSD", "2026", "07", "26", "result-08")
        assert any(
            record.levelname == "WARNING" and "Legacy read" in record.message
            for record in caplog.records
        )
