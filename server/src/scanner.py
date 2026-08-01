"""ResultScanner — port of the TypeScript scanner service."""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any

from src.models import RunSummary

logger = logging.getLogger(__name__)


def _normalize_legacy_result(data: dict[str, Any]) -> dict[str, Any]:
    """Normalize legacy result JSON to current schema.

    - Derive ``review.status`` from ``review.approved`` when missing.
    - Create ``sl_tp_overlay`` from legacy ``decision`` price fields
      when the overlay is absent.
    """
    review = data.get("review")
    if isinstance(review, dict):
        if "status" not in review and "approved" in review:
            review["status"] = "APPROVED" if review["approved"] else "REJECTED"

    sl_tp = data.get("sl_tp_overlay")
    if sl_tp is None:
        decision = data.get("decision") or {}
        entry = decision.get("entry_price")
        sl = decision.get("stop_loss")
        tp = decision.get("take_profit")
        if entry is not None or sl is not None or tp is not None:
            data["sl_tp_overlay"] = {
                "entry_price": entry,
                "stop_loss": sl,
                "take_profit": tp,
            }

    return data


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
        """Get a single run's full result. Returns None if not found."""
        fpath = self.data_dir / year / month / day / symbol / f"{file}.json"
        if not fpath.exists():
            return None
        try:
            data = json.loads(fpath.read_text(encoding="utf-8"))
            return _normalize_legacy_result(data) if isinstance(data, dict) else data
        except (json.JSONDecodeError, OSError):
            return None

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
        """
        try:
            # Extract path components relative to data_dir
            rel = fpath.relative_to(self.data_dir)
            parts = rel.parts  # (YYYY, MM, DD, SYMBOL, filename)
            if len(parts) != 5:
                return None

            year, month, day, _symbol_from_path, filename = parts
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

            symbol = data.get("symbol", _symbol_from_path)
            market_ctx = data.get("market_context") or {}
            decision = data.get("decision") or {}
            review = data.get("review") or {}

            return RunSummary(
                symbol=symbol,
                date=date,
                time=time_str,
                bias=market_ctx.get("bias", "unknown"),
                confidence=market_ctx.get("confidence", 0),
                action=decision.get("action", "unknown"),
                review_approved=review.get("status") == "APPROVED",
                current_price=market_ctx.get("current_price"),
                file_path=str(rel),
            )
        except (json.JSONDecodeError, OSError, ValueError, KeyError):
            logger.debug("Skipping unparseable file: %s", fpath)
            return None
