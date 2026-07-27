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

        async def mock_create(cmd, *args, **kwargs):
            process = AsyncMock()
            process.returncode = -1
            process.stderr = MagicMock()
            process.stderr.read = AsyncMock(return_value=b"")

            async def _wait():
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
            with patch.object(
                runner, "_read_results", return_value=mock_results
            ) as mock_read:
                result = await runner.run_analysis(["XAUUSD"])

        mock_read.assert_called_once_with(["XAUUSD"])
        assert result == mock_results
