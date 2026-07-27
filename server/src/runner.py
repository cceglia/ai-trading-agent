"""RunService — port of the TypeScript runner service.

Spawns the Python analyzer as an async subprocess, enforces a timeout,
captures stderr, and reads back written result files via ResultScanner.
"""

from __future__ import annotations

import asyncio

from src.scanner import ResultScanner


class RunService:
    """Spawn Python subprocess to run analysis, enforce timeout,
    capture stderr, and read back results via ResultScanner."""

    def __init__(
        self,
        python_cmd: str,
        analyzer_dir: str,
        data_dir: str,
        timeout_ms: int = 600_000,
    ) -> None:
        self.python_cmd = python_cmd
        self.analyzer_dir = analyzer_dir
        self.data_dir = data_dir
        self.timeout_ms = timeout_ms

    async def run_analysis(
        self,
        symbols: list[str],
        model: str | None = None,
    ) -> list[dict]:
        """Run analysis for the given symbols.

        Spawns: python main.py --output-dir <dir> [--model <m>] -- <symbols...>
        Returns list of full result dicts, one per symbol.
        """
        args = ["main.py", "--output-dir", self.data_dir]
        if model:
            args.extend(["--model", model])
        args.append("--")
        args.extend(symbols)

        await self._spawn_process(args)
        return self._read_results(symbols)

    async def _spawn_process(self, args: list[str]) -> None:
        """Spawn the Python process and wait for completion.

        On timeout the process is killed and TimeoutError is raised.
        On non-zero exit RuntimeError is raised with captured stderr.
        """
        timeout_seconds = self.timeout_ms / 1000

        try:
            process = await asyncio.create_subprocess_exec(
                self.python_cmd,
                *args,
                cwd=self.analyzer_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except FileNotFoundError as exc:
            raise RuntimeError(f"Python command not found: {self.python_cmd}") from exc

        try:
            await asyncio.wait_for(process.wait(), timeout=timeout_seconds)
        except TimeoutError:
            process.kill()
            await process.wait()
            raise TimeoutError(
                f"Python process timed out after {self.timeout_ms}ms"
            ) from None

        stderr = b""
        if process.stderr is not None:
            stderr = await process.stderr.read()

        if process.returncode != 0:
            stderr_text = stderr.decode("utf-8", errors="replace").strip()
            raise RuntimeError(
                f"Python process exited with code {process.returncode}: {stderr_text}"
            )

    def _read_results(self, symbols: list[str]) -> list[dict]:
        """Walk the data directory via ResultScanner and return the
        most recent result for each requested symbol."""
        scanner = ResultScanner(self.data_dir)
        results: list[dict] = []

        for symbol in symbols:
            runs = scanner.list_runs(symbol=symbol)
            if not runs:
                continue

            # list_runs returns newest-first
            newest = runs[0]
            year, month, day = newest.date.split("-")
            full = scanner.get_run(
                symbol=newest.symbol,
                year=year,
                month=month,
                day=day,
                file=f"result-{newest.time}",
            )
            if full is not None:
                results.append(full)

        return results
