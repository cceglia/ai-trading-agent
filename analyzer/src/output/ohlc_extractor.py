"""OHLC data extractor — parses CSV candle data into structured OHLCBar objects.

Provides a standalone utility for extracting OHLC bars from the same CSV
format produced by the MCP terminal data provider
(:class:`src.data.terminal_data_provider.TerminalDataProvider`).

CSV columns: time, open, high, low, close, tick_volume, spread, real_volume.
"""

from __future__ import annotations

from typing import Any

from src.data.csv_parser import parse_csv_to_rows
from src.output.result_models import OHLCBar


def extract_ohlc_from_csv(csv_data: str) -> list[OHLCBar]:
    """Parse CSV candle data into a list of OHLCBar objects.

    Uses the shared :func:`~src.data.csv_parser.parse_csv_to_rows` utility.

    Args:
        csv_data: Raw CSV string with header row containing at least
            ``time``, ``open``, ``high``, ``low``, ``close`` columns.

    Returns:
        List of :class:`OHLCBar` objects, ordered oldest to newest.

    Raises:
        ValueError: If CSV is empty or contains no valid rows after
            skipping malformed entries.

    Example:
        >>> csv = (
        ...     "time,open,high,low,close,tick_volume,spread,real_volume\\n"
        ...     "2026-07-25T17:00,2350,2370,2345,2365.5,100,0,0\\n"
        ...     "2026-07-25T18:00,2365,2380,2355,2375,120,0,0\\n"
        ... )
        >>> bars = extract_ohlc_from_csv(csv)
        >>> len(bars)
        2
        >>> bars[0].open
        2350.0
    """
    rows: list[dict[str, Any]] = parse_csv_to_rows(csv_data)
    return [
        OHLCBar(
            time=row["time"],
            open=float(row["open"]),
            high=float(row["high"]),
            low=float(row["low"]),
            close=float(row["close"]),
        )
        for row in rows
    ]


def extract_ohlc_from_all_timeframes(csv_map: dict[str, str]) -> dict[str, list[OHLCBar]]:
    """Extract OHLC bars for all timeframes from a mapping of CSV strings.

    Args:
        csv_map: Dictionary keyed by timeframe string (e.g. ``"D1"``,
            ``"H4"``, ``"H1"``) with CSV data as values.

    Returns:
        Dictionary keyed by timeframe string with lists of
        :class:`OHLCBar` as values.

    Raises:
        ValueError: If any individual CSV is empty or contains no valid
            rows.
    """
    return {timeframe: extract_ohlc_from_csv(csv_data) for timeframe, csv_data in csv_map.items()}
