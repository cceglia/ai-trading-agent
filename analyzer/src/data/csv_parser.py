"""Shared CSV parsing utility for candle data.

Provides a single function used by both SnapshotBuilder and the OHLC
extractor, avoiding duplication of CSV parsing logic.

The CSV format matches the MCP terminal data provider output with columns:
time, open, high, low, close, tick_volume, spread, real_volume.
"""

from __future__ import annotations

import csv
import io
import logging
from typing import Any

logger = logging.getLogger(__name__)


def parse_csv_to_rows(csv_data: str) -> list[dict[str, Any]]:
    """Parse CSV candle data into raw row dicts.

    Shared utility used by both SnapshotBuilder and OHLC extractor.

    Args:
        csv_data: Raw CSV string with header row containing the standard
            MCP columns (time, open, high, low, close, tick_volume,
            spread, real_volume).

    Returns:
        List of dicts with keys: time (str), open (float), high (float),
        low (float), close (float). Only columns up to ``close`` are
                required; extra columns are silently ignored.

    Raises:
        ValueError: If CSV is empty or contains no valid rows after
            skipping malformed entries.

    Notes:
        - Rows with missing ``time`` are skipped.
        - Rows where ``high`` < max(open, close, low) are skipped
          (high is inconsistent).
        - Rows where ``low`` > min(open, close, high) are skipped
          (low is inconsistent).
        - Terminal date format ``YYYY.MM.DD HH:MM:SS`` is normalised to
          ISO-8601 (``YYYY-MM-DDTHH:MM:SS``).
    """
    if not csv_data or not csv_data.strip():
        raise ValueError("Empty CSV data")

    reader = csv.DictReader(io.StringIO(csv_data))
    rows: list[dict[str, Any]] = []

    for row_num, row in enumerate(reader):
        try:
            time_str = row.get("time", "").strip()
            if not time_str:
                logger.warning("Skipping row %d: missing time", row_num + 1)
                continue

            # Normalize terminal date format (YYYY.MM.DD HH:MM:SS) to ISO-8601
            if "." in time_str and " " in time_str:
                time_str = time_str.replace(".", "-").replace(" ", "T")

            open_val = float(row.get("open", 0))
            high_val = float(row.get("high", 0))
            low_val = float(row.get("low", 0))
            close_val = float(row.get("close", 0))

            if high_val < max(open_val, close_val, low_val):
                logger.warning(
                    "Skipping row %d: high %.5f < max(open=%.5f, close=%.5f, low=%.5f)",
                    row_num + 1,
                    high_val,
                    open_val,
                    close_val,
                    low_val,
                )
                continue
            if low_val > min(open_val, close_val, high_val):
                logger.warning(
                    "Skipping row %d: low %.5f > min(open=%.5f, close=%.5f, high=%.5f)",
                    row_num + 1,
                    low_val,
                    open_val,
                    close_val,
                    high_val,
                )
                continue

            rows.append(
                {
                    "time": time_str,
                    "open": open_val,
                    "high": high_val,
                    "low": low_val,
                    "close": close_val,
                }
            )
        except (ValueError, KeyError) as e:
            logger.warning("Skipping malformed bar at row %d: %s", row_num + 1, e)
            continue

    if not rows:
        raise ValueError("No valid bars found in CSV")

    return rows
