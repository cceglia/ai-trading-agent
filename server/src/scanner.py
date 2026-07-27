"""ResultScanner — port of the TypeScript scanner service."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from src.models import RunSummary


class ResultScanner:
    """Walk the data directory tree, read/parse JSON result files,
    filter/sort into RunSummary list."""

    def __init__(self, data_dir: str | Path) -> None:
        self.data_dir = Path(data_dir)

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
        if not self.data_dir.exists():
            return []

        results: list[RunSummary] = []
        for root, _dirs, files in os.walk(self.data_dir):
            for fname in files:
                if not fname.endswith(".json"):
                    continue
                fpath = Path(root) / fname
                summary = self._to_summary(fpath)
                if summary is None:
                    continue
                # Apply filters
                if symbol and summary.symbol != symbol.upper():
                    continue
                if from_date and summary.date < from_date:
                    continue
                if to_date and summary.date > to_date:
                    continue
                results.append(summary)

        # Sort by date desc, then time desc
        results.sort(key=lambda r: (r.date, r.time), reverse=True)
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
            return json.loads(fpath.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

    def _to_summary(self, fpath: Path) -> RunSummary | None:
        """Parse a result JSON file into a RunSummary.

        Path convention: data/YYYY/MM/DD/SYMBOL/result-HH-MM.json
        Returns None on any parse error (malformed JSON, missing fields, bad path).
        """
        try:
            # Extract path components relative to data_dir
            rel = fpath.relative_to(self.data_dir)
            parts = rel.parts  # (YYYY, MM, DD, SYMBOL, result-HH-MM.json)
            if len(parts) != 5:
                return None

            year, month, day, _symbol_from_path, filename = parts
            date = f"{year}-{month}-{day}"

            # Parse time from filename: result-HH-MM.json -> HH-MM
            time_str = filename.removeprefix("result-").removesuffix(".json")

            # Read and parse JSON
            data = json.loads(fpath.read_text(encoding="utf-8"))

            # Skip non-object JSON (OHLC arrays, etc.)
            if not isinstance(data, dict):
                return None

            # Extract summary fields — mirrors the TypeScript FullResult shape:
            #   result.symbol, result.market_context.{bias,confidence,current_price},
            #   result.decision.action, result.review.approved
            symbol = data.get("symbol", _symbol_from_path)
            market_ctx = data.get("market_context", {})
            decision = data.get("decision", {})
            review = data.get("review", {})

            return RunSummary(
                symbol=symbol,
                date=date,
                time=time_str,
                bias=market_ctx.get("bias", "unknown"),
                confidence=market_ctx.get("confidence", 0),
                action=decision.get("action", "unknown"),
                review_approved=review.get("approved", False),
                current_price=market_ctx.get("current_price"),
                file_path=str(rel),  # includes .json, matching TS
            )
        except (json.JSONDecodeError, OSError, ValueError, KeyError):
            return None
