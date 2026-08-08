"""Unit tests for RunService."""

from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.models import SymbolError
from src.runner import BatchResult, RunService


@pytest.fixture
def runner() -> RunService:
    """Create a RunService with test defaults."""
    return RunService(
        python_cmd="python3",
        analyzer_dir="/app/analyzer",
        data_dir="/app/data",
        timeout_ms=600_000,
    )


def _mock_process(returncode: int = 0, stderr: bytes | None = None):
    """Create a mock asyncio subprocess."""
    process = AsyncMock()
    process.returncode = returncode
    process.stderr = MagicMock()

    async def _read():
        return stderr or b""

    process.stderr.read = _read
    process.wait = AsyncMock(return_value=returncode)
    process.kill = MagicMock()
    return process


def _make_run_summary(
    symbol: str, date: str = "2026-07-28", time: str = "10-00"
) -> MagicMock:
    """Create a minimal RunSummary-like mock for the scanner."""
    summary = MagicMock()
    summary.symbol = symbol
    summary.date = date
    summary.time = time
    summary.bias = "bullish"
    summary.confidence = 0.8
    summary.action = "buy"
    summary.validation_status = "VALID"
    summary.setup_status = "READY"
    summary.direction = "LONG"
    summary.operational = True
    summary.file_path = f"{date.replace('-', '/')}/{symbol}/result-{time}.json"
    return summary


class TestRunAnalysis:
    """Tests for RunService.run_analysis()."""

    @pytest.mark.asyncio
    async def test_correct_args_construction(self, runner: RunService):
        """Verify subprocess is spawned with correct arguments."""
        captured = {}

        async def mock_create(cmd, *args, **kwargs):
            captured["cmd"] = cmd
            captured["args"] = args
            return _mock_process(returncode=0)

        with (
            patch("asyncio.create_subprocess_exec", side_effect=mock_create),
            patch.object(runner, "_wait_for_results"),
            patch.object(runner, "_read_results", return_value=[]),
        ):
            await runner.run_analysis(["XAUUSD", "EURUSD"])

        assert captured["cmd"] == "python3"
        assert "main.py" in captured["args"]
        assert "--" in captured["args"]
        dd_idx = captured["args"].index("--")
        assert captured["args"][dd_idx + 1] == "XAUUSD"
        assert captured["args"][dd_idx + 2] == "EURUSD"

    @pytest.mark.asyncio
    async def test_model_argument(self, runner: RunService):
        """Verify --model flag is added when model is provided."""
        captured = {}

        async def mock_create(cmd, *args, **kwargs):
            captured["args"] = args
            return _mock_process(returncode=0)

        with (
            patch("asyncio.create_subprocess_exec", side_effect=mock_create),
            patch.object(runner, "_wait_for_results"),
            patch.object(runner, "_read_results", return_value=[]),
        ):
            await runner.run_analysis(["XAUUSD"], model="gpt-4")

        assert "--model" in captured["args"]
        idx = captured["args"].index("--model")
        assert captured["args"][idx + 1] == "gpt-4"

    @pytest.mark.asyncio
    async def test_no_model_argument_when_none(self, runner: RunService):
        """Verify --model flag is absent when model is None."""
        captured = {}

        async def mock_create(cmd, *args, **kwargs):
            captured["args"] = args
            return _mock_process(returncode=0)

        with (
            patch("asyncio.create_subprocess_exec", side_effect=mock_create),
            patch.object(runner, "_wait_for_results"),
            patch.object(runner, "_read_results", return_value=[]),
        ):
            await runner.run_analysis(["XAUUSD"])

        assert "--model" not in captured["args"]

    @pytest.mark.asyncio
    async def test_base_url_argument(self, runner: RunService):
        """A resolved provider base_url is passed as --base-url to the analyzer."""
        captured = {}

        async def mock_create(cmd, *args, **kwargs):
            captured["args"] = args
            return _mock_process(returncode=0)

        with (
            patch("asyncio.create_subprocess_exec", side_effect=mock_create),
            patch.object(runner, "_wait_for_results"),
            patch.object(runner, "_read_results", return_value={}),
        ):
            await runner.run_analysis(["XAUUSD"], base_url="http://127.0.0.1:11434/v1")

        assert "--base-url" in captured["args"]
        idx = captured["args"].index("--base-url")
        assert captured["args"][idx + 1] == "http://127.0.0.1:11434/v1"

    @pytest.mark.asyncio
    async def test_no_base_url_argument_when_none(self, runner: RunService):
        """Verify --base-url is absent when base_url is None."""
        captured = {}

        async def mock_create(cmd, *args, **kwargs):
            captured["args"] = args
            return _mock_process(returncode=0)

        with (
            patch("asyncio.create_subprocess_exec", side_effect=mock_create),
            patch.object(runner, "_wait_for_results"),
            patch.object(runner, "_read_results", return_value={}),
        ):
            await runner.run_analysis(["XAUUSD"])

        assert "--base-url" not in captured["args"]

    @pytest.mark.asyncio
    async def test_process_failure_maps_to_symbol_errors(self, runner: RunService):
        """Non-zero exit yields a per-symbol error; stderr secrets never surface."""
        stderr = b"Traceback ... API key SECRET123 leaked"
        process = _mock_process(returncode=1, stderr=stderr)

        async def mock_create(cmd, *args, **kwargs):
            return process

        with (
            patch("asyncio.create_subprocess_exec", side_effect=mock_create),
            patch.object(runner, "_wait_for_results"),
            patch.object(runner, "_read_results", return_value={}),
        ):
            outcome = await runner.run_analysis(["XAUUSD"])

        assert outcome.status == "error"
        assert outcome.results == {}
        err = outcome.errors["XAUUSD"]
        assert err.code == "SYMBOL_PROCESS_FAILED"
        assert "SECRET123" not in err.message
        assert "SECRET123" not in str(outcome)

    @pytest.mark.asyncio
    async def test_timeout_kills_process(self):
        """Process should be killed on timeout and mapped to per-symbol errors."""
        killed = []
        wait_call_count = 0

        async def mock_create(cmd, *args, **kwargs):
            process = AsyncMock()
            process.returncode = -1
            process.stderr = MagicMock()
            process.stderr.read = AsyncMock(return_value=b"")

            async def _wait():
                nonlocal wait_call_count
                wait_call_count += 1
                # First call: sleep long enough to trigger timeout.
                # Second call (in except handler): return immediately.
                if wait_call_count == 1:
                    await asyncio.sleep(100)

            process.wait = _wait

            def _kill():
                killed.append(True)

            process.kill = _kill
            return process

        short_runner = RunService(
            "python3", "/app/analyzer", "/app/data", timeout_ms=100
        )
        with (
            patch("asyncio.create_subprocess_exec", side_effect=mock_create),
            patch.object(short_runner, "_wait_for_results"),
            patch.object(short_runner, "_read_results", return_value={}),
        ):
            outcome = await short_runner.run_analysis(["XAUUSD"])

        assert len(killed) > 0
        assert outcome.status == "error"
        assert outcome.errors["XAUUSD"].code == "SYMBOL_TIMEOUT"

    @pytest.mark.asyncio
    async def test_timeout_preserves_partial_results(self, runner: RunService):
        """A timeout after some symbols completed keeps the completed results."""
        results = {"XAUUSD": {"symbol": "XAUUSD", "status": "success"}}
        wait_call_count = 0

        async def mock_create(cmd, *args, **kwargs):
            process = AsyncMock()
            process.returncode = -1
            process.stderr = MagicMock()
            process.stderr.read = AsyncMock(return_value=b"")

            async def _wait():
                nonlocal wait_call_count
                wait_call_count += 1
                if wait_call_count == 1:
                    await asyncio.sleep(100)

            process.wait = _wait
            process.kill = MagicMock()
            return process

        short_runner = RunService(
            "python3", "/app/analyzer", "/app/data", timeout_ms=100
        )
        with (
            patch("asyncio.create_subprocess_exec", side_effect=mock_create),
            patch.object(short_runner, "_wait_for_results"),
            patch.object(short_runner, "_read_results", return_value=results),
        ):
            outcome = await short_runner.run_analysis(["XAUUSD", "EURUSD"])

        assert outcome.status == "partial"
        assert outcome.results == {"XAUUSD": {"symbol": "XAUUSD", "status": "success"}}
        assert outcome.errors["EURUSD"].code == "SYMBOL_TIMEOUT"

    @pytest.mark.asyncio
    async def test_bad_python_cmd_yields_symbol_errors(self):
        """A missing Python command is a per-symbol error, not a raise."""
        bad_runner = RunService("nonexistent_python_xyz", "/app/analyzer", "/app/data")
        with (
            patch.object(bad_runner, "_wait_for_results"),
            patch.object(bad_runner, "_read_results", return_value={}),
        ):
            outcome = await bad_runner.run_analysis(["XAUUSD"])

        assert outcome.status == "error"
        assert "not found" in outcome.errors["XAUUSD"].message

    @pytest.mark.asyncio
    async def test_read_results_called_with_symbols(self, runner: RunService):
        """Verify _read_results is called with the requested symbols."""

        async def mock_create(cmd, *args, **kwargs):
            return _mock_process(returncode=0)

        mock_results = {"XAUUSD": {"symbol": "XAUUSD"}}
        with (
            patch("asyncio.create_subprocess_exec", side_effect=mock_create),
            patch.object(runner, "_wait_for_results"),
            patch.object(
                runner, "_read_results", return_value=mock_results
            ) as mock_read,
        ):
            result = await runner.run_analysis(["XAUUSD"])

        assert mock_read.call_args.args[0] == ["XAUUSD"]
        assert result.results == mock_results

    @pytest.mark.asyncio
    async def test_scanner_created_once(self, runner: RunService):
        """ResultScanner constructor is called at most once across
        multiple run_analysis calls."""
        from src.scanner import ResultScanner

        async def mock_create(cmd, *args, **kwargs):
            return _mock_process(returncode=0)

        init_count = 0

        def counting_init(self, data_dir, cache_ttl=60):
            nonlocal init_count
            init_count += 1
            # Minimal setup so the scanner instance is usable
            self.data_dir = data_dir
            self.cache_ttl = cache_ttl
            self._cache = {}
            self.list_runs = MagicMock(return_value=[_make_run_summary("XAUUSD")])
            self.get_run = MagicMock(return_value=None)
            self.invalidate_cache = MagicMock()

        with (
            patch("asyncio.create_subprocess_exec", side_effect=mock_create),
            patch.object(ResultScanner, "__init__", counting_init),
        ):
            await runner.run_analysis(["XAUUSD"])
            await runner.run_analysis(["EURUSD"])

        assert init_count == 1, (
            f"ResultScanner.__init__ called {init_count} times, expected 1"
        )

    @pytest.mark.asyncio
    async def test_scanner_invalidated_after_run(self, runner: RunService):
        """invalidate_cache is called after a successful run."""
        from src.scanner import ResultScanner

        async def mock_create(cmd, *args, **kwargs):
            return _mock_process(returncode=0)

        invalidate_mock = MagicMock()

        def mock_init(self, data_dir, cache_ttl=60):
            self.data_dir = data_dir
            self.cache_ttl = cache_ttl
            self._cache = {}
            self.list_runs = MagicMock(return_value=[_make_run_summary("XAUUSD")])
            self.get_run = MagicMock(return_value=None)
            self.invalidate_cache = invalidate_mock

        with (
            patch("asyncio.create_subprocess_exec", side_effect=mock_create),
            patch.object(ResultScanner, "__init__", mock_init),
        ):
            await runner.run_analysis(["XAUUSD"])

        # invalidate_cache is called once by _wait_for_results (attempt 0,
        # no retry needed) and once by run_analysis after _read_results.
        assert invalidate_mock.call_count >= 1


class TestWaitForResults:
    """Tests for RunService._wait_for_results()."""

    @pytest.fixture
    def runner_fast(self) -> RunService:
        """RunService with minimal retry delays for fast tests."""
        return RunService(
            python_cmd="python3",
            analyzer_dir="/app/analyzer",
            data_dir="/app/data",
            timeout_ms=600_000,
            retry_max_attempts=5,
            retry_delay_ms=10,
        )

    @pytest.mark.asyncio
    async def test_read_results_retries_on_empty_read(self, runner_fast: RunService):
        """Scanner returns empty on first N-1 calls, then succeeds."""
        from src.scanner import ResultScanner

        call_count = 0
        summary = _make_run_summary("XAUUSD")

        def mock_list_runs(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            # Return empty on first 2 calls, non-empty on 3rd
            if call_count <= 2:
                return []
            return [summary]

        def mock_init(self, data_dir, cache_ttl=60):
            self.data_dir = data_dir
            self.cache_ttl = cache_ttl
            self._cache = {}
            self.list_runs = MagicMock(side_effect=mock_list_runs)
            self.get_run = MagicMock(return_value=None)
            self.invalidate_cache = MagicMock()

        async def mock_create(cmd, *args, **kwargs):
            return _mock_process(returncode=0)

        with (
            patch("asyncio.create_subprocess_exec", side_effect=mock_create),
            patch.object(ResultScanner, "__init__", mock_init),
        ):
            # Should not raise — succeeds on 3rd attempt
            await runner_fast.run_analysis(["XAUUSD"])

        assert call_count >= 3, f"list_runs called {call_count} times, expected >= 3"

    @pytest.mark.asyncio
    async def test_read_results_gives_up_after_max_retries(
        self, runner_fast: RunService
    ):
        """Scanner always returns empty → missing symbols get a safe error."""
        from src.scanner import ResultScanner

        call_count = 0

        def mock_list_runs(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return []

        def mock_init(self, data_dir, cache_ttl=60):
            self.data_dir = data_dir
            self.cache_ttl = cache_ttl
            self._cache = {}
            self.list_runs = MagicMock(side_effect=mock_list_runs)
            self.get_run = MagicMock(return_value=None)
            self.invalidate_cache = MagicMock()

        async def mock_create(cmd, *args, **kwargs):
            return _mock_process(returncode=0)

        with (
            patch("asyncio.create_subprocess_exec", side_effect=mock_create),
            patch.object(ResultScanner, "__init__", mock_init),
        ):
            outcome = await runner_fast.run_analysis(["XAUUSD"])

        # 1 baseline snapshot + 5 polling attempts + 1 read attempt.
        assert call_count == 7, f"list_runs called {call_count} times, expected 7"
        assert outcome.status == "error"
        assert outcome.errors["XAUUSD"].code == "SYMBOL_NO_RESULT"

    @pytest.mark.asyncio
    async def test_read_results_succeeds_on_first_try(self, runner_fast: RunService):
        """Files available immediately — happy path, no retries needed."""
        from src.scanner import ResultScanner

        call_count = 0

        def mock_list_runs(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return [_make_run_summary("XAUUSD")]

        def mock_init(self, data_dir, cache_ttl=60):
            self.data_dir = data_dir
            self.cache_ttl = cache_ttl
            self._cache = {}
            self.list_runs = MagicMock(side_effect=mock_list_runs)
            self.get_run = MagicMock(return_value=None)
            self.invalidate_cache = MagicMock()

        async def mock_create(cmd, *args, **kwargs):
            return _mock_process(returncode=0)

        with (
            patch("asyncio.create_subprocess_exec", side_effect=mock_create),
            patch.object(ResultScanner, "__init__", mock_init),
        ):
            await runner_fast.run_analysis(["XAUUSD"])

        # 1 baseline snapshot + 1 poll (attempt 0 succeeds) + 1 read.
        assert call_count == 3, f"list_runs called {call_count} times, expected 3"

    @pytest.mark.asyncio
    async def test_retry_configurable(self):
        """Verify retry_max_attempts parameter is honoured."""
        runner_custom = RunService(
            python_cmd="python3",
            analyzer_dir="/app/analyzer",
            data_dir="/app/data",
            timeout_ms=600_000,
            retry_max_attempts=3,
            retry_delay_ms=5,
        )
        assert runner_custom.retry_max_attempts == 3
        assert runner_custom.retry_delay_ms == 5

    @pytest.mark.asyncio
    async def test_retry_without_wait_configured(self):
        """retry_max_attempts is 5 by default."""
        runner_default = RunService(
            python_cmd="python3",
            analyzer_dir="/app/analyzer",
            data_dir="/app/data",
            timeout_ms=600_000,
        )
        assert runner_default.retry_max_attempts == 5
        assert runner_default.retry_delay_ms == 100


class TestBatchIsolation:
    """FR-033 / INV-014 / AC-016 — per-symbol terminal outcomes."""

    @pytest.mark.asyncio
    async def test_success_keeps_all_results(self, runner: RunService):
        results = {
            "XAUUSD": {"symbol": "XAUUSD", "status": "success"},
            "EURUSD": {"symbol": "EURUSD", "status": "success"},
        }

        async def mock_create(cmd, *args, **kwargs):
            return _mock_process(returncode=0)

        with (
            patch("asyncio.create_subprocess_exec", side_effect=mock_create),
            patch.object(runner, "_wait_for_results"),
            patch.object(runner, "_read_results", return_value=results),
        ):
            outcome = await runner.run_analysis(["XAUUSD", "EURUSD"])

        assert outcome.status == "success"
        assert set(outcome.results) == {"XAUUSD", "EURUSD"}
        assert outcome.errors == {}

    @pytest.mark.asyncio
    async def test_partial_keeps_other_symbols(self, runner: RunService):
        """One symbol missing → the other symbol's result is retained (AC-016)."""
        results = {"XAUUSD": {"symbol": "XAUUSD", "status": "success"}}

        async def mock_create(cmd, *args, **kwargs):
            return _mock_process(returncode=0)

        with (
            patch("asyncio.create_subprocess_exec", side_effect=mock_create),
            patch.object(runner, "_wait_for_results"),
            patch.object(runner, "_read_results", return_value=results),
        ):
            outcome = await runner.run_analysis(["XAUUSD", "EURUSD"])

        assert outcome.status == "partial"
        assert outcome.results == {"XAUUSD": {"symbol": "XAUUSD", "status": "success"}}
        assert outcome.errors["EURUSD"].code == "SYMBOL_NO_RESULT"

    @pytest.mark.asyncio
    async def test_missing_result_is_safe_error_not_success(self, runner: RunService):
        """Missing/malformed result is a safe error, never operational success."""

        async def mock_create(cmd, *args, **kwargs):
            return _mock_process(returncode=0)

        with (
            patch("asyncio.create_subprocess_exec", side_effect=mock_create),
            patch.object(runner, "_wait_for_results"),
            patch.object(runner, "_read_results", return_value={}),
        ):
            outcome = await runner.run_analysis(["XAUUSD"])

        assert outcome.status == "error"
        assert outcome.results == {}
        assert outcome.errors["XAUUSD"].code == "SYMBOL_NO_RESULT"

    def test_batch_status_semantics(self):
        """FR-033 status rules: success / partial / error."""
        assert BatchResult(results={"X": {}}, errors={}).status == "success"
        assert (
            BatchResult(
                results={"X": {}}, errors={"Y": SymbolError(code="E", message="e")}
            ).status
            == "partial"
        )
        assert (
            BatchResult(
                results={}, errors={"Y": SymbolError(code="E", message="e")}
            ).status
            == "error"
        )

    @pytest.mark.asyncio
    async def test_polls_only_persisted_non_fatal_results(self, tmp_path):
        """A fatal ``error`` result file is not a result — its symbol gets a
        per-symbol error while the healthy symbol is retained (FR-033, §15)."""
        v2 = {
            "schema_version": "2",
            "symbol": "XAUUSD",
            "status": "success",
            "deterministic_facts": {"symbol": "XAUUSD", "operational": True},
            "decision": {"action": "buy_setup"},
        }
        fatal = {"symbol": "EURUSD", "status": "error", "fatal_error": "fetch failed"}

        real_runner = RunService(
            "python3", "/app/analyzer", str(tmp_path), retry_delay_ms=1
        )

        async def mock_create(cmd, *args, **kwargs):
            # Simulate the analyzer persisting its outputs during the run.
            for sym, content in (("XAUUSD", v2), ("EURUSD", fatal)):
                path = tmp_path / "2026" / "08" / "08" / sym / "result-10.json"
                path.parent.mkdir(parents=True)
                path.write_text(json.dumps(content))
            return _mock_process(returncode=0)

        with patch("asyncio.create_subprocess_exec", side_effect=mock_create):
            outcome = await real_runner.run_analysis(["XAUUSD", "EURUSD"])

        assert outcome.status == "partial"
        assert "XAUUSD" in outcome.results
        assert "EURUSD" not in outcome.results
        assert outcome.errors["EURUSD"].code == "SYMBOL_NO_RESULT"

    @pytest.mark.asyncio
    async def test_stale_prior_file_with_fatal_failure_is_error(self, tmp_path):
        """BATCH-001: a symbol with only a stale prior file and a current fatal
        failure is a per-symbol error, not operational success (§15/FR-033)."""
        stale = {
            "schema_version": "2",
            "symbol": "XAUUSD",
            "status": "success",
            "deterministic_facts": {"symbol": "XAUUSD", "operational": True},
            "decision": {"action": "buy_setup"},
        }
        stale_path = tmp_path / "2026" / "08" / "08" / "XAUUSD" / "result-09.json"
        stale_path.parent.mkdir(parents=True)
        stale_path.write_text(json.dumps(stale))

        real_runner = RunService(
            "python3", "/app/analyzer", str(tmp_path), retry_delay_ms=1
        )

        async def mock_create(cmd, *args, **kwargs):
            # Current run fails before persisting anything for XAUUSD.
            return _mock_process(returncode=1)

        with patch("asyncio.create_subprocess_exec", side_effect=mock_create):
            outcome = await real_runner.run_analysis(["XAUUSD"])

        assert outcome.status == "error"
        assert outcome.results == {}
        assert outcome.errors["XAUUSD"].code == "SYMBOL_PROCESS_FAILED"

    @pytest.mark.asyncio
    async def test_stale_prior_file_yields_partial_batch(self, tmp_path):
        """BATCH-001: one stale-only symbol fails while a fresh symbol succeeds
        → batch status is ``partial`` with a per-symbol error for the stale one."""
        stale = {
            "schema_version": "2",
            "symbol": "EURUSD",
            "status": "success",
            "deterministic_facts": {"symbol": "EURUSD", "operational": True},
            "decision": {"action": "buy_setup"},
        }
        stale_path = tmp_path / "2026" / "08" / "08" / "EURUSD" / "result-09.json"
        stale_path.parent.mkdir(parents=True)
        stale_path.write_text(json.dumps(stale))

        fresh = {
            "schema_version": "2",
            "symbol": "XAUUSD",
            "status": "success",
            "deterministic_facts": {"symbol": "XAUUSD", "operational": True},
            "decision": {"action": "buy_setup"},
        }

        real_runner = RunService(
            "python3", "/app/analyzer", str(tmp_path), retry_delay_ms=1
        )

        async def mock_create(cmd, *args, **kwargs):
            # The run persists a fresh result only for XAUUSD; EURUSD keeps
            # its stale prior file untouched.
            path = tmp_path / "2026" / "08" / "08" / "XAUUSD" / "result-10.json"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps(fresh))
            return _mock_process(returncode=1)

        with patch("asyncio.create_subprocess_exec", side_effect=mock_create):
            outcome = await real_runner.run_analysis(["XAUUSD", "EURUSD"])

        assert outcome.status == "partial"
        assert "XAUUSD" in outcome.results
        assert "EURUSD" not in outcome.results
        assert outcome.errors["EURUSD"].code == "SYMBOL_PROCESS_FAILED"

    @pytest.mark.asyncio
    async def test_fresh_file_produced_during_run_is_success(self, tmp_path):
        """BATCH-001: a file produced during the current run is operational
        success (contrast with a stale pre-existing file)."""
        fresh = {
            "schema_version": "2",
            "symbol": "XAUUSD",
            "status": "success",
            "deterministic_facts": {"symbol": "XAUUSD", "operational": True},
            "decision": {"action": "buy_setup"},
        }

        real_runner = RunService(
            "python3", "/app/analyzer", str(tmp_path), retry_delay_ms=1
        )

        async def mock_create(cmd, *args, **kwargs):
            path = tmp_path / "2026" / "08" / "08" / "XAUUSD" / "result-10.json"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps(fresh))
            return _mock_process(returncode=0)

        with patch("asyncio.create_subprocess_exec", side_effect=mock_create):
            outcome = await real_runner.run_analysis(["XAUUSD"])

        assert outcome.status == "success"
        assert "XAUUSD" in outcome.results
        assert outcome.errors == {}
