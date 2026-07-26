"""Snapshot builder for converting MCP CSV data to normalized engine snapshots."""

import logging
from datetime import UTC, datetime
from typing import Any

from src.data.csv_parser import parse_csv_to_rows

logger = logging.getLogger(__name__)


class SnapshotBuilder:
    """Builds normalized snapshots from MCP CSV data.

    Converts raw CSV candle data from the MCP server into the normalized
    snapshot format expected by the market structure engine.

    The MCP CSV columns are: time, open, high, low, close, tick_volume, spread, real_volume.
    The engine expects bars with: open_time, open, high, low, close, closed.
    """

    def build(
        self,
        csv_data: str,
        symbol: str,
        timeframe: str,
        provider: str = "MCP",
        broker_now: datetime | None = None,
    ) -> dict[str, Any]:
        """Convert CSV to normalized snapshot.

        Args:
            csv_data: CSV string from MCP server (columns: time, open, high, low, close, ...).
            symbol: Trading symbol (e.g., "EURUSD").
            timeframe: Timeframe (e.g., "D1", "H4", "H1").
            provider: Data provider name (default: "MCP").
            broker_now: Broker local time as a naive datetime. If None, UTC is used.

        Returns:
            Normalized snapshot dict matching the engine schema.

        Raises:
            ValueError: If CSV parsing fails or validation errors occur.
        """
        logger.debug("Building snapshot for %s %s", symbol, timeframe)

        bars = self._parse_csv(csv_data)
        snapshot = self._build_snapshot(bars, symbol, timeframe, provider, broker_now)
        self._validate_snapshot(snapshot)

        logger.info("Built snapshot with %d bars for %s %s", len(bars), symbol, timeframe)
        return snapshot

    def _parse_csv(self, csv_data: str) -> list[dict[str, Any]]:
        """Parse CSV string to list of bar dicts.

        Delegates to the shared :func:`parse_csv_to_rows` utility and
        maps the raw row format (``time``, ``open``, ``high``, ``low``,
        ``close``) into the engine snapshot format (``open_time``,
        ``open``, ``high``, ``low``, ``close``, ``closed``).

        Args:
            csv_data: Raw CSV string with OHLC columns.

        Returns:
            List of bar dicts with open_time, open, high, low, close, closed.

        Raises:
            ValueError: If CSV is empty or contains no valid bars.
        """
        rows = parse_csv_to_rows(csv_data)
        bars = [
            {
                "open_time": row["time"],
                "open": row["open"],
                "high": row["high"],
                "low": row["low"],
                "close": row["close"],
                "closed": True,
            }
            for row in rows
        ]
        return bars

    def _build_snapshot(
        self,
        bars: list[dict[str, Any]],
        symbol: str,
        timeframe: str,
        provider: str,
        broker_now: datetime | None,
    ) -> dict[str, Any]:
        """Build normalized snapshot from parsed bars.

        Args:
            bars: List of parsed bar dicts.
            symbol: Trading symbol.
            timeframe: Timeframe string.
            provider: Data provider name.
            broker_now: Broker local time. If None, UTC is used.

        Returns:
            Normalized snapshot dict matching the engine schema.
        """
        now = (broker_now or datetime.now(UTC)).isoformat()
        last_bar_time = bars[-1]["open_time"] if bars else now

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
            "retrieved_at": now,
            "latest_closed_candle_time": last_bar_time,
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
            "retrieved_at",
            "latest_closed_candle_time",
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
            for field in ("open_time", "open", "high", "low", "close", "closed"):
                if field not in bar:
                    raise ValueError(f"Bar {i} missing required field: {field}")
            if bar.get("closed") is not True:
                raise ValueError(f"Bar {i} must be closed")
            for field in ("open", "high", "low", "close"):
                val = bar.get(field)
                if not isinstance(val, int | float):
                    raise ValueError(f"Bar {i} field {field} must be a number")

        for i in range(1, len(bars)):
            prev_time = bars[i - 1].get("open_time", "")
            curr_time = bars[i].get("open_time", "")
            if prev_time >= curr_time:
                raise ValueError(
                    f"Bars must be strictly ordered oldest to newest (bar {i - 1} >= bar {i})"
                )
