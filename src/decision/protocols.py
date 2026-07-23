from datetime import datetime
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class DataSource(Protocol):
    """Read-only market data provider."""

    def get_candles(self, symbol: str, timeframe: str, count: int) -> str:
        """Fetch OHLC candles as CSV string.

        Args:
            symbol: Trading symbol (e.g., "EURUSD")
            timeframe: Timeframe (e.g., "D1", "H4", "H1")
            count: Number of candles to fetch

        Returns:
            CSV string with OHLC data
        """
        ...

    def get_symbol_price(self, symbol: str) -> dict[str, Any]:
        """Get latest price info for a symbol.

        Args:
            symbol: Trading symbol

        Returns:
            Dictionary with price data
        """
        ...

    def get_positions(self, symbol: str | None = None) -> list[dict[str, Any]]:
        """Get open positions.

        Args:
            symbol: Optional symbol filter

        Returns:
            List of position dictionaries
        """
        ...

    def get_pending_orders(self, symbol: str | None = None) -> list[dict[str, Any]]:
        """Get pending orders.

        Args:
            symbol: Optional symbol filter

        Returns:
            List of order dictionaries
        """
        ...

    def get_broker_time(self) -> datetime:
        """Get current broker/server time from the data provider.

        Returns a naive datetime (no timezone) representing the broker's
        local time, as reported by the trade server. This is used for
        cache file naming that must align with candle close times.

        Returns:
            Naive datetime in broker-local time.

        Raises:
            ConnectionError: If the server cannot be reached.
            TerminalApiError: If the server returns an error.
            ValueError: If the response is malformed.
        """
        ...


@runtime_checkable
class CalendarProvider(Protocol):
    """Economic calendar data provider."""

    def fetch_events(self) -> list[dict[str, Any]]:
        """Fetch upcoming economic calendar events.

        Returns:
            List of event dictionaries with:
            - time: ISO timestamp
            - currency: Currency code (e.g., "USD")
            - impact: "high", "medium", "low"
            - title: Event name
        """
        ...


@runtime_checkable
class StructureAnalyzer(Protocol):
    """Market structure analysis provider."""

    def analyze(
        self, snapshots: dict[str, Any], profile_overrides: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Analyze market structure from snapshots.

        Args:
            snapshots: Dictionary of timeframe snapshots
            profile_overrides: Optional profile overrides

        Returns:
            Analysis result dictionary
        """
        ...
