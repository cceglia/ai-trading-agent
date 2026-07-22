"""Snapshot builder for converting MCP CSV data to normalized engine snapshots."""

import csv
import io
import logging
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)

_ENGINE_ALLOWED_TOP_LEVEL = {
    "schema_version",
    "source",
    "market",
    "timeframe",
    "requested_timeframe",
    "returned_timeframe",
    "retrieved_at_utc",
    "latest_closed_candle_time_utc",
    "candle_closure_verified",
    "bars",
}
_ENGINE_ALLOWED_BAR = {"open_time_utc", "open", "high", "low", "close", "closed"}


class SnapshotBuilder:
    """Builds normalized snapshots from MCP CSV data.

    Converts raw CSV candle data from the MCP server into the normalized
    snapshot format expected by the market structure engine.

    The MCP CSV columns are: time, open, high, low, close, tick_volume, spread, real_volume.
    The engine expects bars with: open_time_utc, open, high, low, close, closed.
    """

    def build(
        self,
        csv_data: str,
        symbol: str,
        timeframe: str,
        provider: str = "MCP",
    ) -> dict[str, Any]:
        """Convert CSV to normalized snapshot.

        Args:
            csv_data: CSV string from MCP server (columns: time, open, high, low, close, ...).
            symbol: Trading symbol (e.g., "EURUSD").
            timeframe: Timeframe (e.g., "D1", "H4", "H1").
            provider: Data provider name (default: "MCP").

        Returns:
            Normalized snapshot dict matching the engine schema.

        Raises:
            ValueError: If CSV parsing fails or validation errors occur.
        """
        logger.debug("Building snapshot for %s %s", symbol, timeframe)

        bars = self._parse_csv(csv_data)
        snapshot = self._build_snapshot(bars, symbol, timeframe, provider)
        self._validate_snapshot(snapshot)

        logger.info("Built snapshot with %d bars for %s %s", len(bars), symbol, timeframe)
        return snapshot

    def _parse_csv(self, csv_data: str) -> list[dict[str, Any]]:
        """Parse CSV string to list of bar dicts.

        Args:
            csv_data: Raw CSV string with OHLC columns.

        Returns:
            List of bar dicts with open_time_utc, open, high, low, close, closed.

        Raises:
            ValueError: If CSV is empty or contains no valid bars.
        """
        if not csv_data or not csv_data.strip():
            raise ValueError("Empty CSV data")

        reader = csv.DictReader(io.StringIO(csv_data))
        bars: list[dict[str, Any]] = []

        for row_num, row in enumerate(reader):
            try:
                time_str = row.get("time", "").strip()
                if not time_str:
                    logger.warning("Skipping row %d: missing time", row_num + 1)
                    continue

                open_val = float(row.get("open", 0))
                high_val = float(row.get("high", 0))
                low_val = float(row.get("low", 0))
                close_val = float(row.get("close", 0))

                if high_val < max(open_val, close_val, low_val):
                    logger.warning("Skipping row %d: high is inconsistent", row_num + 1)
                    continue
                if low_val > min(open_val, close_val, high_val):
                    logger.warning("Skipping row %d: low is inconsistent", row_num + 1)
                    continue

                bar = {
                    "open_time_utc": time_str,
                    "open": open_val,
                    "high": high_val,
                    "low": low_val,
                    "close": close_val,
                    "closed": True,
                }
                bars.append(bar)
            except (ValueError, KeyError) as e:
                logger.warning("Skipping malformed bar at row %d: %s", row_num + 1, e)
                continue

        if not bars:
            raise ValueError("No valid bars found in CSV")

        return bars

    def _build_snapshot(
        self,
        bars: list[dict[str, Any]],
        symbol: str,
        timeframe: str,
        provider: str,
    ) -> dict[str, Any]:
        """Build normalized snapshot from parsed bars.

        Args:
            bars: List of parsed bar dicts.
            symbol: Trading symbol.
            timeframe: Timeframe string.
            provider: Data provider name.

        Returns:
            Normalized snapshot dict matching the engine schema.
        """
        now_utc = datetime.now(UTC).isoformat()
        last_bar_time = bars[-1]["open_time_utc"] if bars else now_utc

        return {
            "source": {
                "type": "TRADINGVIEW_MCP",
            },
            "market": {
                "symbol": symbol,
                "provider": provider,
            },
            "requested_timeframe": timeframe.upper(),
            "returned_timeframe": timeframe.upper(),
            "retrieved_at_utc": now_utc,
            "latest_closed_candle_time_utc": last_bar_time,
            "candle_closure_verified": True,
            "bars": bars,
        }

    def _validate_snapshot(self, snapshot: dict[str, Any]) -> None:
        """Validate snapshot against engine schema.

        Args:
            snapshot: The normalized snapshot to validate.

        Raises:
            ValueError: If snapshot fails validation.
        """
        required_fields = {
            "source",
            "market",
            "requested_timeframe",
            "returned_timeframe",
            "retrieved_at_utc",
            "latest_closed_candle_time_utc",
            "candle_closure_verified",
            "bars",
        }
        missing = required_fields - set(snapshot)
        if missing:
            raise ValueError(f"Snapshot missing required field(s): {sorted(missing)}")

        source = snapshot.get("source", {})
        if not isinstance(source, dict) or source.get("type") != "TRADINGVIEW_MCP":
            raise ValueError("source.type must be TRADINGVIEW_MCP")

        market = snapshot.get("market", {})
        if not isinstance(market, dict):
            raise ValueError("market must be an object")
        if not str(market.get("symbol", "")).strip():
            raise ValueError("market.symbol is required")
        if not str(market.get("provider", "")).strip():
            raise ValueError("market.provider is required")

        timeframe = snapshot.get("requested_timeframe", "")
        if timeframe not in ("D1", "H4", "H1"):
            raise ValueError(f"Unsupported timeframe: {timeframe!r} (must be D1, H4, or H1)")

        if snapshot.get("candle_closure_verified") is not True:
            raise ValueError("candle_closure_verified must be true")

        bars = snapshot.get("bars", [])
        if not isinstance(bars, list) or len(bars) == 0:
            raise ValueError("Snapshot has no bars")

        for i, bar in enumerate(bars):
            if not isinstance(bar, dict):
                raise ValueError(f"Bar {i} must be an object")
            for field in ("open_time_utc", "open", "high", "low", "close", "closed"):
                if field not in bar:
                    raise ValueError(f"Bar {i} missing required field: {field}")
            if bar.get("closed") is not True:
                raise ValueError(f"Bar {i} must be closed")
            for field in ("open", "high", "low", "close"):
                val = bar.get(field)
                if not isinstance(val, int | float):
                    raise ValueError(f"Bar {i} field {field} must be a number")

        for i in range(1, len(bars)):
            prev_time = bars[i - 1].get("open_time_utc", "")
            curr_time = bars[i].get("open_time_utc", "")
            if prev_time >= curr_time:
                raise ValueError(
                    f"Bars must be strictly ordered oldest to newest (bar {i - 1} >= bar {i})"
                )
