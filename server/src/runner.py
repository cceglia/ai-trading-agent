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
        retry_max_attempts: int = 5,
        retry_delay_ms: int = 100,
    ) -> None:
        self.python_cmd = python_cmd
        self.analyzer_dir = analyzer_dir
        self._data_dir = data_dir
        self.timeout_ms = timeout_ms
        self.retry_max_attempts = retry_max_attempts
        self.retry_delay_ms = retry_delay_ms
        self.__scanner: ResultScanner | None = None

    @property
    def _scanner(self) -> ResultScanner:
        if self.__scanner is None:
            self.__scanner = ResultScanner(self._data_dir, cache_ttl=60)
        return self.__scanner

    async def run_analysis(
        self,
        symbols: list[str],
        model: str | None = None,
    ) -> list[dict]:
        """Run analysis for the given symbols.

        Spawns: python main.py [--model <m>] -- <symbols...>
        Returns list of full result dicts, one per symbol.
        """
        args = ["main.py"]
        if model:
            args.extend(["--model", model])
        args.append("--")
        args.extend(symbols)

        await self._spawn_process(args)
        await self._wait_for_results(symbols)
        results = self._read_results(symbols)
        self._scanner.invalidate_cache()
        return results

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

    async def _wait_for_results(self, symbols: list[str]) -> None:
        """Retry reading result files with backoff.

        After a subprocess completes there may be a filesystem flush delay
        before the output files are visible. This method polls the scanner,
        retrying up to *retry_max_attempts* times with *retry_delay_ms*
        sleep between attempts. If any symbol's result is still missing
        after all retries, a TimeoutError is raised listing the missing
        symbols.
        """
        missing = set(symbols)
        for attempt in range(self.retry_max_attempts):
            if not missing:
                return
            if attempt > 0:
                await asyncio.sleep(self.retry_delay_ms / 1000)
            # Invalidate cache before each check so we get fresh FS data
            self._scanner.invalidate_cache()
            missing = self._find_missing_symbols(symbols)

        raise TimeoutError(
            f"Results not available after retries: {', '.join(sorted(missing))}"
        )

    def _find_missing_symbols(self, symbols: list[str]) -> set[str]:
        """Return the subset of *symbols* that have no run in the scanner."""
        missing: set[str] = set()
        for symbol in symbols:
            runs = self._scanner.list_runs(symbol=symbol)
            if not runs:
                missing.add(symbol)
        return missing

    def _read_results(self, symbols: list[str]) -> list[dict]:
        """Walk the data directory via ResultScanner and return the
        most recent result for each requested symbol."""
        results: list[dict] = []

        for symbol in symbols:
            runs = self._scanner.list_runs(symbol=symbol)
            if not runs:
                continue

            # list_runs returns newest-first
            newest = runs[0]
            year, month, day = newest.date.split("-")
            full = self._scanner.get_run(
                symbol=newest.symbol,
                year=year,
                month=month,
                day=day,
                file=f"result-{newest.time}",
            )
            if full is not None:
                results.append(full)

        return results
