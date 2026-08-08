"""RunService — port of the TypeScript runner service.

Spawns the Python analyzer as an async subprocess, enforces a timeout,
captures stderr, and reads back persisted result files via ResultScanner.
Symbols are isolated: a process-level failure (timeout, non-zero exit) is
mapped to per-symbol errors for the symbols that did not persist a result,
so completed symbols are preserved (FR-033 / INV-014).
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.models import BatchStatus, SymbolError
from src.scanner import ResultScanner

logger = logging.getLogger(__name__)


@dataclass
class BatchResult:
    """Per-symbol terminal outcomes for one batch run (FR-033 / INV-014).

    ``results`` maps the normalized symbol to the full v2/legacy envelope;
    ``errors`` maps the normalized symbol to a safe per-symbol error. Every
    requested symbol appears in exactly one of the two maps.
    """

    results: dict[str, dict[str, Any]] = field(default_factory=dict)
    errors: dict[str, SymbolError] = field(default_factory=dict)

    @property
    def status(self) -> BatchStatus:
        """Batch status per FR-033: success / partial / error.

        ``success`` when all symbols complete without error, ``partial`` when
        at least one completes and at least one errors, ``error`` when none
        produces a reliable result.
        """
        if self.errors:
            if self.results:
                return "partial"
            return "error"
        return "success"


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
        base_url: str | None = None,
    ) -> BatchResult:
        """Run analysis for the given symbols as an isolated batch.

        Spawns: python main.py [--model <m>] [--base-url <url>] -- <symbols...>
        Returns a :class:`BatchResult` with exactly one terminal outcome per
        symbol. Process-level failures are mapped to per-symbol errors for the
        symbols that did not persist a result, never raised, so completed
        symbols are preserved (AC-016 / §15).
        """
        args = self._build_args(symbols, model, base_url)

        # Snapshot the pre-run result files so reads can be correlated to this
        # batch: a symbol whose run persists nothing (fatal/timeout) must not
        # report an older stale file as operational success (BATCH-001/FR-033).
        self._scanner.invalidate_cache()
        baseline = self._snapshot_baseline(symbols)

        process_error: SymbolError | None = None
        try:
            await self._spawn_process(args)
        except TimeoutError:
            process_error = SymbolError(
                code="SYMBOL_TIMEOUT",
                message=f"analysis timed out after {self.timeout_ms}ms",
            )
        except RuntimeError as exc:
            process_error = SymbolError(code="SYMBOL_PROCESS_FAILED", message=str(exc))

        await self._wait_for_results(symbols, baseline)
        results = self._read_results(symbols, baseline)
        self._scanner.invalidate_cache()

        errors: dict[str, SymbolError] = {}
        for symbol in symbols:
            if symbol not in results:
                errors[symbol] = process_error or SymbolError(
                    code="SYMBOL_NO_RESULT",
                    message="no result file was persisted for symbol",
                )
        return BatchResult(results=results, errors=errors)

    def _snapshot_baseline(self, symbols: list[str]) -> dict[str, dict[str, int]]:
        """Record the result files that exist before the run starts.

        Maps each symbol to ``{absolute file path: mtime_ns}`` for every result
        file already on disk. A result is only attributed to the current batch
        if its file is new or was rewritten since this snapshot (BATCH-001).
        """
        baseline: dict[str, dict[str, int]] = {}
        for symbol in symbols:
            baseline[symbol] = {}
            for run in self._scanner.list_runs(symbol=symbol):
                fpath = Path(self._data_dir) / run.file_path
                try:
                    baseline[symbol][str(fpath)] = fpath.stat().st_mtime_ns
                except OSError:
                    continue
        return baseline

    def _is_fresh(
        self,
        symbol: str,
        run: Any,
        baseline: dict[str, dict[str, int]],
    ) -> bool:
        """Return True when *run*'s file was produced by the current batch.

        A file is fresh if it did not exist at baseline or its mtime changed
        since the snapshot; an unchanged pre-existing file is a stale prior
        result and must not count as success (FR-033 missing-result semantics).
        """
        fpath = Path(self._data_dir) / run.file_path
        prior_mtime = baseline.get(symbol, {}).get(str(fpath))
        try:
            current_mtime = fpath.stat().st_mtime_ns
        except OSError:
            # Cannot stat: treat as fresh only when no pre-run record exists
            # (a recorded-but-gone file is picked up by get_run → None).
            return prior_mtime is None
        return prior_mtime is None or prior_mtime != current_mtime

    def _build_args(
        self,
        symbols: list[str],
        model: str | None = None,
        base_url: str | None = None,
    ) -> list[str]:
        """Build the analyzer CLI argument list."""
        args = ["main.py"]
        if model:
            args.extend(["--model", model])
        if base_url:
            args.extend(["--base-url", base_url])
        args.append("--")
        args.extend(symbols)
        return args

    async def _spawn_process(self, args: list[str]) -> None:
        """Spawn the Python process and wait for completion.

        On timeout the process is killed and TimeoutError is raised. On
        non-zero exit RuntimeError is raised; process stderr is drained but
        never propagated, so provider credentials in stderr cannot surface
        (FR-038).
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
            raise TimeoutError("analysis timed out") from None

        stderr = b""
        if process.stderr is not None:
            stderr = await process.stderr.read()

        if process.returncode != 0:
            # Never include stderr content — it may contain secrets.
            logger.info(
                "Analyzer exited with code %s (stderr %d bytes)",
                process.returncode,
                len(stderr),
            )
            raise RuntimeError(
                f"analyzer process exited with code {process.returncode}"
            )

    async def _wait_for_results(
        self, symbols: list[str], baseline: dict[str, dict[str, int]]
    ) -> None:
        """Retry reading result files with backoff.

        After a subprocess completes there may be a filesystem flush delay
        before the output files are visible. This method polls the scanner,
        retrying up to *retry_max_attempts* times with *retry_delay_ms*
        sleep between attempts. It never raises for a missing symbol: symbols
        without a freshly-produced result are reported as per-symbol errors
        by the caller.
        """
        for attempt in range(self.retry_max_attempts):
            # Invalidate cache before each check so we get fresh FS data
            self._scanner.invalidate_cache()
            missing = self._find_missing_symbols(symbols, baseline)
            if not missing:
                return
            if attempt < self.retry_max_attempts - 1:
                await asyncio.sleep(self.retry_delay_ms / 1000)

    def _find_missing_symbols(
        self, symbols: list[str], baseline: dict[str, dict[str, int]]
    ) -> set[str]:
        """Return the subset of *symbols* with no run freshly produced by the
        current batch (a stale pre-existing file does not count)."""
        missing: set[str] = set()
        for symbol in symbols:
            runs = self._scanner.list_runs(symbol=symbol)
            if not any(self._is_fresh(symbol, run, baseline) for run in runs):
                missing.add(symbol)
        return missing

    def _read_results(
        self, symbols: list[str], baseline: dict[str, dict[str, int]]
    ) -> dict[str, dict[str, Any]]:
        """Walk the data directory via ResultScanner and return the most recent
        freshly-produced result for each requested symbol, keyed by symbol.

        Only files written (created or rewritten) by the current batch are
        returned; fatal ``error`` files are skipped by the scanner and stale
        pre-existing files map to per-symbol errors (BATCH-001 / §15)."""
        results: dict[str, dict[str, Any]] = {}

        for symbol in symbols:
            runs = self._scanner.list_runs(symbol=symbol)
            fresh = [r for r in runs if self._is_fresh(symbol, r, baseline)]
            if not fresh:
                continue

            # list_runs returns newest-first
            newest = fresh[0]
            year, month, day = newest.date.split("-")
            full = self._scanner.get_run(
                symbol=newest.symbol,
                year=year,
                month=month,
                day=day,
                file=f"result-{newest.time}",
            )
            if full is not None:
                results[symbol] = full

        return results
