"""ResultScanner — reads schema-v2 envelopes and adapts legacy files.

The scanner is the server-side read boundary. New files are schema-v2 nested
envelopes and are returned as-is (they are validated by the analyzer writer).
Legacy review-based files are normalized through a read-only, idempotent
adapter that marks them ``schema_version=legacy``, ``validation_status=UNKNOWN``
and ``operational=false`` and never exposes review fields (FR-034 / AC-015).
"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any

from src.models import RunSummary

logger = logging.getLogger(__name__)

_SCHEMA_V2 = "2"
_LEGACY_SCHEMA = "legacy"


class LegacyAdapter:
    """Server-owned, read-only, idempotent adapter for legacy result files.

    Produces a schema-v2-shaped envelope with ``schema_version="legacy"``,
    ``validation_status=UNKNOWN`` and ``operational=false``. Fields that
    cannot be reconstructed from a legacy file are null/empty. No ``review``
    field is ever copied, and the adapter never mutates its input.

    Synthesis status is ``SKIPPED``: legacy files predate the v2 Synthesizer
    contract (``SUCCESS``/``FAILED`` for an attempted call), so no synthesis
    was made for them. This mirrors the analyzer's deterministic no-LLM path,
    where an invalid run is also persisted with ``SKIPPED`` — the parent
    contract's ``SUCCESS``/``FAILED`` pair describes attempted calls only.
    """

    def adapt(self, data: dict[str, Any]) -> dict[str, Any]:
        """Normalize a legacy review-based result dict into the public shape.

        The returned dict is freshly built (whitelist projection) so any
        ``review``/``reviewer``/``decider`` key in the source cannot leak
        into the public v2 response. Applying ``adapt`` twice is a no-op on
        the output values (idempotent).
        """
        symbol = data.get("symbol") or ""

        # First pass: legacy top-level fields; second pass (idempotency):
        # the already-normalized nested fields are preferred.
        facts = data.get("deterministic_facts")
        facts = facts if isinstance(facts, dict) else {}
        decision = data.get("decision")
        decision = decision if isinstance(decision, dict) else {}
        market_context = data.get("market_context")
        market_context = market_context if isinstance(market_context, dict) else {}

        bias = facts.get("bias")
        if bias is None:
            bias = market_context.get("bias")
        confidence = facts.get("confidence")
        if confidence is None:
            confidence = market_context.get("confidence")
        action = decision.get("action")

        ohlc = data.get("ohlc")
        return {
            "schema_version": _LEGACY_SCHEMA,
            "symbol": symbol,
            "run_id": data.get("run_id"),
            "started_at": data.get("started_at"),
            "completed_at": data.get("completed_at"),
            "status": data.get("status", "success"),
            "errors": data.get("errors") or [],
            "fatal_error": data.get("fatal_error"),
            "deterministic_facts": {
                "symbol": symbol,
                "timeframes": {},
                "setup_status": "UNKNOWN",
                "direction": "NONE",
                "trade_direction": "NEUTRAL",
                "setup_grade": None,
                "setup_classification_status": "NO_SETUP",
                "setup_lifecycle_status": "UNKNOWN",
                "entry_plan": {},
                "rr": {
                    "calculated_rr": None,
                    "minimum_required_rr": 2.0,
                    "rr_pass": False,
                },
                "confidence_components": {},
                "policy": {
                    "execution_status": "NON_EXECUTABLE",
                    "actionable": False,
                    "blockers": [],
                    "reason_codes": [],
                },
                "selected_levels": {},
                "latest_structural_events": {},
                "latest_liquidity_states": {},
                "event_history": {},
                "liquidity_history": {},
                "validation_status": "UNKNOWN",
                "validation_errors": [],
                "operational": False,
                "entry_authorized": False,
                "bias": bias,
                "confidence": confidence,
            },
            "decision": {"action": action or "no_trade"},
            "synthesis": {
                "status": "SKIPPED",
                "explanation": None,
                "risks": [],
                "confluences": [],
                "error": None,
            },
            "ohlc": ohlc if isinstance(ohlc, dict) else {},
        }


class ResultScanner:
    """Walk the data directory tree, read/parse JSON result files,
    filter/sort into RunSummary list.

    Directory pruning: when a symbol filter is supplied only the matching
    subdirectory under each date is traversed, avoiding a full walk.

    LRU caching: repeated calls with the same filter tuple return cached
    results without disk I/O until the TTL expires.
    """

    def __init__(self, data_dir: str | Path, cache_ttl: int = 60) -> None:
        self.data_dir = Path(data_dir)
        self.cache_ttl = cache_ttl
        self._cache: dict[
            tuple[str | None, str | None, str | None], tuple[float, list[RunSummary]]
        ] = {}
        self._legacy_adapter = LegacyAdapter()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def list_runs(
        self,
        symbol: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> list[RunSummary]:
        """List all runs, optionally filtered by symbol and date range.

        Returns sorted by date desc, then time desc.
        Returns an empty list if the data directory does not exist.
        """
        # --- Cache lookup ---
        key = self._cache_key(symbol, from_date, to_date)
        cached = self._cache_get(key)
        if cached is not None:
            return cached

        # --- Walk ---
        if not self.data_dir.exists():
            return []

        if symbol:
            results = self._walk_pruned(symbol.upper(), from_date, to_date)
        else:
            results = self._walk_full(from_date, to_date)

        # Sort by date desc, then time desc
        results.sort(key=lambda r: (r.date, r.time), reverse=True)

        # --- Cache store ---
        self._cache_set(key, results)
        return results

    def get_run(
        self,
        symbol: str,
        year: str,
        month: str,
        day: str,
        file: str,
    ) -> dict[str, Any] | None:
        """Get a single run's full result.

        v2 envelopes are returned as-is; legacy files are normalized through
        the read-only LegacyAdapter. Malformed or non-object JSON is skipped
        with a safe diagnostic and returns ``None``. Returns ``None`` when
        the file does not exist.
        """
        fpath = self.data_dir / year / month / day / symbol / f"{file}.json"
        if not fpath.exists():
            return None
        try:
            data = json.loads(fpath.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning(
                "Skipping malformed result file (legacy read): %s — %s", fpath, exc
            )
            return None
        if not isinstance(data, dict):
            logger.warning("Skipping non-object result file (legacy read): %s", fpath)
            return None
        if data.get("schema_version") == _SCHEMA_V2:
            return data
        logger.info("Legacy read (schema_version=%s) from %s", _LEGACY_SCHEMA, fpath)
        return self._legacy_adapter.adapt(data)

    def invalidate_cache(self) -> None:
        """Clear all cached list_runs results."""
        self._cache.clear()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _cache_key(
        self,
        symbol: str | None,
        from_date: str | None,
        to_date: str | None,
    ) -> tuple[str | None, str | None, str | None]:
        return (symbol, from_date, to_date)

    def _cache_get(
        self, key: tuple[str | None, str | None, str | None]
    ) -> list[RunSummary] | None:
        entry = self._cache.get(key)
        if entry is None:
            return None
        ts, results = entry
        if time.monotonic() - ts > self.cache_ttl:
            del self._cache[key]
            return None
        return results

    def _cache_set(
        self, key: tuple[str | None, str | None, str | None], results: list[RunSummary]
    ) -> None:
        self._cache[key] = (time.monotonic(), results)

    def _walk_full(
        self,
        from_date: str | None,
        to_date: str | None,
    ) -> list[RunSummary]:
        """Full directory walk (fallback when no symbol is specified)."""
        results: list[RunSummary] = []
        for root, _dirs, files in os.walk(self.data_dir):
            for fname in files:
                if not fname.endswith(".json"):
                    continue
                fpath = Path(root) / fname
                summary = self._to_summary(fpath)
                if summary is None:
                    continue
                if from_date and summary.date < from_date:
                    continue
                if to_date and summary.date > to_date:
                    continue
                results.append(summary)
        return results

    def _walk_pruned(
        self,
        symbol_upper: str,
        from_date: str | None,
        to_date: str | None,
    ) -> list[RunSummary]:
        """Walk only directories that match *symbol_upper*.

        Directory layout:  data_dir/YYYY/MM/DD/SYMBOL/result-HH-MM.json
        """
        results: list[RunSummary] = []

        # Check whether from_date / to_date can narrow year/month/day
        min_year: int | None = None
        max_year: int | None = None
        min_month: int | None = None
        max_month: int | None = None
        min_day: int | None = None
        max_day: int | None = None

        if from_date:
            parts = from_date.split("-")
            if len(parts) == 3:
                min_year = int(parts[0])
                min_month = int(parts[1])
                min_day = int(parts[2])
        if to_date:
            parts = to_date.split("-")
            if len(parts) == 3:
                max_year = int(parts[0])
                max_month = int(parts[1])
                max_day = int(parts[2])

        # Iterate year directories
        for year_dir in sorted(self.data_dir.iterdir()):
            if not year_dir.is_dir():
                continue
            try:
                year = int(year_dir.name)
            except ValueError:
                continue
            if min_year is not None and year < min_year:
                continue
            if max_year is not None and year > max_year:
                continue

            # Iterate month directories
            for month_dir in sorted(year_dir.iterdir()):
                if not month_dir.is_dir():
                    continue
                try:
                    month = int(month_dir.name)
                except ValueError:
                    continue
                if (
                    min_year is not None
                    and year == min_year
                    and min_month is not None
                    and month < min_month
                ):
                    continue
                if (
                    max_year is not None
                    and year == max_year
                    and max_month is not None
                    and month > max_month
                ):
                    continue

                # Iterate day directories
                for day_dir in sorted(month_dir.iterdir()):
                    if not day_dir.is_dir():
                        continue
                    try:
                        day = int(day_dir.name)
                    except ValueError:
                        continue
                    if (
                        min_year is not None
                        and year == min_year
                        and min_month is not None
                        and month == min_month
                        and min_day is not None
                        and day < min_day
                    ):
                        continue
                    if (
                        max_year is not None
                        and year == max_year
                        and max_month is not None
                        and month == max_month
                        and max_day is not None
                        and day > max_day
                    ):
                        continue

                    # Only check the symbol that matches (pruning)
                    symbol_dir = day_dir / symbol_upper
                    if not symbol_dir.is_dir():
                        continue

                    for fname in sorted(symbol_dir.iterdir()):
                        if not fname.name.endswith(".json"):
                            continue
                        fpath = symbol_dir / fname.name
                        summary = self._to_summary(fpath)
                        if summary is None:
                            continue
                        # Date/from/to already handled by directory iteration,
                        # but also apply the filters so edge-cases are covered.
                        if from_date and summary.date < from_date:
                            continue
                        if to_date and summary.date > to_date:
                            continue
                        results.append(summary)

        return results

    def _to_summary(self, fpath: Path) -> RunSummary | None:
        """Parse a result JSON file into a RunSummary.

        Path convention: data/YYYY/MM/DD/SYMBOL/result-HH.json
        Returns None on any parse error (malformed JSON, missing fields, bad path).
        Only result-*.json files are recognized — synthesizer files are ignored.

        ``bias``/``confidence`` are passed through without rescaling: v2
        confidence is the deterministic 0–100 score with uppercase trade
        direction bias, while legacy confidence is the 0–1 interpretive value
        with stored-case bias (see ``RunSummary`` docstring).
        """
        try:
            # Extract path components relative to data_dir
            rel = fpath.relative_to(self.data_dir)
            parts = rel.parts  # (YYYY, MM, DD, SYMBOL, filename)
            if len(parts) != 5:
                return None

            year, month, day, symbol_from_path, filename = parts
            date = f"{year}-{month}-{day}"

            # Only accept result-*.json files
            if not filename.startswith("result-"):
                return None

            # Parse time from filename: result-HH.json -> HH
            time_str = filename.removeprefix("result-").removesuffix(".json")

            # Read and parse JSON
            data = json.loads(fpath.read_text(encoding="utf-8"))

            # Skip non-object JSON (OHLC arrays, etc.)
            if not isinstance(data, dict):
                return None

            # Fatal pipeline failures are not displayable run summaries. This
            # also protects the dashboard from legacy error files written by
            # older analyzer versions.
            if data.get("status") == "error":
                logger.info("Skipping failed result file: %s", fpath)
                return None

            symbol = data.get("symbol", symbol_from_path)
            if data.get("schema_version") == _SCHEMA_V2:
                envelope = data
            else:
                envelope = self._legacy_adapter.adapt(data)

            facts = envelope.get("deterministic_facts") or {}
            decision = envelope.get("decision") or {}

            return RunSummary(
                symbol=symbol,
                date=date,
                time=time_str,
                bias=facts.get("bias") or "unknown",
                confidence=facts.get("confidence") or 0,
                action=(decision.get("action") if isinstance(decision, dict) else None)
                or "unknown",
                validation_status=facts.get("validation_status") or "UNKNOWN",
                setup_status=facts.get("setup_status") or "UNKNOWN",
                direction=facts.get("direction") or "NONE",
                operational=bool(facts.get("operational", False)),
                file_path=str(rel),
            )
        except (json.JSONDecodeError, OSError, ValueError, KeyError):
            logger.debug("Skipping unparseable file: %s", fpath)
            return None
