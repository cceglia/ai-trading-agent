import logging
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)


class Evaluator:
    """Evaluates calendar events for trading symbols."""

    TIMEFRAME_WINDOWS = {
        "D1": 48,  # hours
        "H4": 24,
        "H1": 12,
    }

    SYMBOL_MAPPINGS = {
        # Forex pairs
        "EURUSD": ["EUR", "USD"],
        "GBPUSD": ["GBP", "USD"],
        "USDJPY": ["USD", "JPY"],
        "USDCHF": ["USD", "CHF"],
        "AUDUSD": ["AUD", "USD"],
        "NZDUSD": ["NZD", "USD"],
        "USDCAD": ["USD", "CAD"],
        # Commodities
        "XAUUSD": ["XAU", "USD"],  # Gold
        "XTIUSD": ["XTI", "USD"],  # Oil
        # Indices
        "US30": ["USD"],
        "US500": ["USD"],
        "NASDAQ100": ["USD"],
    }

    def _is_within_window(
        self,
        event_time_str: str,
        window_hours: int,
        now: datetime | None = None,
    ) -> bool:
        """Check if an event falls within the time window from now.

        Returns False for missing/unparseable times (fail-safe).
        """
        if not event_time_str:
            return False
        try:
            # Handle both ISO format and naive datetimes
            event_time = datetime.fromisoformat(event_time_str.replace("Z", "+00:00"))
            if event_time.tzinfo is None:
                event_time = event_time.replace(tzinfo=now.tzinfo if now else None)
            if now is None:
                now = datetime.now(UTC)
            if now.tzinfo is None:
                now = now.replace(tzinfo=event_time.tzinfo)
            diff = abs((now - event_time).total_seconds() / 3600)
            return diff <= window_hours
        except (ValueError, TypeError, AttributeError):
            return False

    def evaluate_for_symbol(
        self,
        events: list[dict[str, Any]],
        symbol: str,
        timeframe: str = "H4",
        now: datetime | None = None,
    ) -> dict[str, Any]:
        """Evaluate events for symbol with timeframe-dependent window.

        Args:
            events: List of calendar events
            symbol: Trading symbol
            timeframe: Analysis timeframe

        Returns:
            Dictionary with:
            - blocking: List of blocking events
            - warning: List of warning events
            - safe: Whether trading is safe
            - window_hours: Window used
            - currencies: Currencies considered
        """
        window_hours = self.TIMEFRAME_WINDOWS.get(timeframe, 24)
        currencies = self.SYMBOL_MAPPINGS.get(symbol, [])

        logger.debug(
            "Evaluating %s with %dh window, currencies: %s",
            symbol,
            window_hours,
            currencies,
        )

        blocking: list[dict[str, Any]] = []
        warning: list[dict[str, Any]] = []

        for event in events:
            if event.get("currency") not in currencies:
                continue

            event_time = event.get("time", "")
            if not self._is_within_window(event_time, window_hours, now):
                continue

            if event.get("impact") == "high":
                blocking.append(event)
            elif event.get("impact") == "medium":
                warning.append(event)

        return {
            "blocking": blocking,
            "warning": warning,
            "safe": len(blocking) == 0,
            "window_hours": window_hours,
            "currencies": currencies,
        }
