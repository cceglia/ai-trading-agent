"""Unit tests for RunService."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.runner import RunService


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
    summary.review_approved = False
    summary.current_price = 2000.0
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

        with patch("asyncio.create_subprocess_exec", side_effect=mock_create):
            with patch.object(runner, "_wait_for_results"):
                with patch.object(runner, "_read_results", return_value=[]):
                    await runner.run_analysis(["XAUUSD", "EURUSD"])

        assert captured["cmd"] == "python3"
        assert "main.py" in captured["args"]
        assert "--output-dir" in captured["args"]
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

        with patch("asyncio.create_subprocess_exec", side_effect=mock_create):
            with patch.object(runner, "_wait_for_results"):
                with patch.object(runner, "_read_results", return_value=[]):
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

        with patch("asyncio.create_subprocess_exec", side_effect=mock_create):
            with patch.object(runner, "_wait_for_results"):
                with patch.object(runner, "_read_results", return_value=[]):
                    await runner.run_analysis(["XAUUSD"])

        assert "--model" not in captured["args"]

    @pytest.mark.asyncio
    async def test_nonzero_exit_raises_runtime_error(self, runner: RunService):
        """Non-zero exit code should raise RuntimeError with stderr."""
        stderr_msg = b"analysis failed"
        process = _mock_process(returncode=1, stderr=stderr_msg)

        async def mock_create(cmd, *args, **kwargs):
            return process

        with patch("asyncio.create_subprocess_exec", side_effect=mock_create):
            with pytest.raises(RuntimeError, match="exited with code 1"):
                await runner.run_analysis(["XAUUSD"])

    @pytest.mark.asyncio
    async def test_timeout_kills_process(self):
        """Process should be killed on timeout."""
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
        with patch("asyncio.create_subprocess_exec", side_effect=mock_create):
            with pytest.raises(TimeoutError, match="timed out"):
                await short_runner.run_analysis(["XAUUSD"])

        assert len(killed) > 0

    @pytest.mark.asyncio
    async def test_bad_python_cmd_raises(self):
        """Non-existent Python command should raise RuntimeError."""
        bad_runner = RunService("nonexistent_python_xyz", "/app/analyzer", "/app/data")
        with pytest.raises(RuntimeError, match="not found"):
            await bad_runner.run_analysis(["XAUUSD"])

    @pytest.mark.asyncio
    async def test_read_results_called_with_symbols(self, runner: RunService):
        """Verify _read_results is called with the requested symbols."""

        async def mock_create(cmd, *args, **kwargs):
            return _mock_process(returncode=0)

        mock_results = [{"symbol": "XAUUSD"}]
        with patch("asyncio.create_subprocess_exec", side_effect=mock_create):
            with patch.object(runner, "_wait_for_results"):
                with patch.object(
                    runner, "_read_results", return_value=mock_results
                ) as mock_read:
                    result = await runner.run_analysis(["XAUUSD"])

        mock_read.assert_called_once_with(["XAUUSD"])
        assert result == mock_results

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

        with patch("asyncio.create_subprocess_exec", side_effect=mock_create):
            with patch.object(ResultScanner, "__init__", counting_init):
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

        with patch("asyncio.create_subprocess_exec", side_effect=mock_create):
            with patch.object(ResultScanner, "__init__", mock_init):
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

        with patch("asyncio.create_subprocess_exec", side_effect=mock_create):
            with patch.object(ResultScanner, "__init__", mock_init):
                # Should not raise — succeeds on 3rd attempt
                await runner_fast.run_analysis(["XAUUSD"])

        assert call_count >= 3, f"list_runs called {call_count} times, expected >= 3"

    @pytest.mark.asyncio
    async def test_read_results_gives_up_after_max_retries(
        self, runner_fast: RunService
    ):
        """Scanner always returns empty → TimeoutError after max retries."""
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

        with patch("asyncio.create_subprocess_exec", side_effect=mock_create):
            with patch.object(ResultScanner, "__init__", mock_init):
                with pytest.raises(
                    TimeoutError, match="Results not available after retries: XAUUSD"
                ):
                    await runner_fast.run_analysis(["XAUUSD"])

        assert call_count == 5, f"list_runs called {call_count} times, expected 5"

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

        with patch("asyncio.create_subprocess_exec", side_effect=mock_create):
            with patch.object(ResultScanner, "__init__", mock_init):
                await runner_fast.run_analysis(["XAUUSD"])

        # One call from _wait_for_results (attempt 0 succeeds),
        # one from _read_results.
        assert call_count == 2, f"list_runs called {call_count} times, expected 2"

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
