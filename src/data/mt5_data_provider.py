"""MetaTrader 5 data provider via MCP server."""

import csv
import io
import logging
import os
import time
from typing import Any, cast

logger = logging.getLogger(__name__)


class Mt5DataProvider:
    """MetaTrader 5 data provider via MCP server.

    Implements the DataSource protocol for fetching market data
    from MetaTrader 5 through an MCP (Model Context Protocol) server.
    """

    def __init__(
        self,
        server_url: str | None = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """Initialize MT5 data provider.

        Args:
            server_url: MCP server URL (defaults to MCP_SERVER_URL env var)
            max_retries: Maximum retry attempts for failed operations
            retry_delay: Base delay between retries in seconds (exponential backoff)
        """
        self.server_url = server_url or os.getenv("MCP_SERVER_URL", "http://localhost:8082")
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._client: Any = None

    async def connect(self) -> None:
        """Establish connection to MCP server."""
        try:
            from mcp import ClientSession
            from mcp.client.sse import sse_client

            self._sse_context = sse_client(self.server_url or "http://localhost:8082")
            self._transport = await self._sse_context.__aenter__()
            self._client = ClientSession(self._transport[0], self._transport[1])
            await self._client.__aenter__()
            await self._client.initialize()
            logger.info("Connected to MCP server at %s", self.server_url)
        except ImportError:
            logger.warning("MCP library not installed, using direct HTTP fallback")
            self._client = None
        except Exception as e:
            logger.error("Failed to connect to MCP server: %s", e)
            raise ConnectionError(f"Cannot connect to MCP server at {self.server_url}") from e

    async def disconnect(self) -> None:
        """Disconnect from MCP server."""
        if self._client:
            try:
                await self._client.__aexit__(None, None, None)
                if hasattr(self, "_sse_context"):
                    await self._sse_context.__aexit__(None, None, None)
            except Exception as e:
                logger.warning("Error during disconnect: %s", e)
            finally:
                self._client = None

    def _retry_operation(self, operation: str, func: Any, *args: Any, **kwargs: Any) -> Any:
        """Execute operation with retry logic and exponential backoff.

        Args:
            operation: Name of operation for logging
            func: Function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result of func execution

        Raises:
            ConnectionError: If all retry attempts fail
        """
        last_error = None
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except ConnectionError:
                raise
            except Exception as e:
                last_error = e
                logger.warning(
                    "Attempt %d/%d for %s failed: %s",
                    attempt + 1,
                    self.max_retries,
                    operation,
                    e,
                )
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2**attempt)
                    logger.debug("Retrying in %.1f seconds...", delay)
                    time.sleep(delay)
        raise ConnectionError(
            f"Failed to {operation} after {self.max_retries} attempts: {last_error}"
        )

    def _call_tool(self, tool_name: str, arguments: dict[str, Any] | None = None) -> Any:
        """Call an MCP tool synchronously.

        Args:
            tool_name: Name of the MCP tool to call
            arguments: Arguments to pass to the tool

        Returns:
            Tool result
        """
        import asyncio

        async def _async_call() -> Any:
            if self._client is None:
                await self.connect()
            result = await self._client.call_tool(tool_name, arguments or {})
            return result

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, _async_call())
                    return future.result(timeout=30)
            else:
                return loop.run_until_complete(_async_call())
        except RuntimeError:
            return asyncio.run(_async_call())

    def get_candles(self, symbol: str, timeframe: str, count: int) -> str:
        """Fetch OHLC candles as CSV string.

        Args:
            symbol: Trading symbol (e.g., "EURUSD")
            timeframe: Timeframe (e.g., "D1", "H4", "H1")
            count: Number of candles to fetch

        Returns:
            CSV string with OHLC data containing columns:
            time, open, high, low, close, tick_volume, spread, real_volume
        """
        logger.info("Fetching candles for %s %s count=%d", symbol, timeframe, count)

        def _fetch() -> str:
            result = self._call_tool(
                "get_candles_latest",
                {"symbol_name": symbol, "timeframe": timeframe, "count": count},
            )
            if result and hasattr(result, "content"):
                for content in result.content:
                    if hasattr(content, "text"):
                        text: str = content.text
                        return text
            raise ValueError("Invalid response format from MCP server")

        return cast(str, self._retry_operation("get_candles", _fetch))

    def get_symbol_price(self, symbol: str) -> dict[str, Any]:
        """Get latest price info for a symbol.

        Args:
            symbol: Trading symbol

        Returns:
            Dictionary with price data including bid, ask, last, volume, etc.
        """
        logger.info("Fetching price for %s", symbol)

        def _fetch() -> dict[str, Any]:
            result = self._call_tool("get_symbol_price", {"symbol_name": symbol})
            if result and hasattr(result, "content"):
                for content in result.content:
                    if hasattr(content, "text"):
                        import json

                        parsed: dict[str, Any] = json.loads(content.text)
                        return parsed
            raise ValueError("Invalid response format from MCP server")

        return cast(dict[str, Any], self._retry_operation("get_symbol_price", _fetch))

    def get_positions(self, symbol: str | None = None) -> list[dict[str, Any]]:
        """Get open positions.

        Args:
            symbol: Optional symbol filter. If None, returns all positions.

        Returns:
            List of position dictionaries with keys like:
            id, symbol, type, volume, price_open, sl, tp, profit, etc.
        """
        logger.info("Fetching positions for %s", symbol or "all")

        def _fetch() -> list[dict[str, Any]]:
            if symbol:
                result = self._call_tool("get_positions_by_symbol", {"symbol": symbol})
            else:
                result = self._call_tool("get_all_positions")

            if result and hasattr(result, "content"):
                for content in result.content:
                    if hasattr(content, "text"):
                        import json

                        parsed: list[dict[str, Any]] = json.loads(content.text)
                        return parsed
            raise ValueError("Invalid response format from MCP server")

        return cast(list[dict[str, Any]], self._retry_operation("get_positions", _fetch))

    def get_pending_orders(self, symbol: str | None = None) -> list[dict[str, Any]]:
        """Get pending orders.

        Args:
            symbol: Optional symbol filter. If None, returns all pending orders.

        Returns:
            List of pending order dictionaries with keys like:
            id, symbol, type, volume, price, sl, tp, status, etc.
        """
        logger.info("Fetching pending orders for %s", symbol or "all")

        def _fetch() -> list[dict[str, Any]]:
            if symbol:
                result = self._call_tool("get_pending_orders_by_symbol", {"symbol": symbol})
            else:
                result = self._call_tool("get_all_pending_orders")

            if result and hasattr(result, "content"):
                for content in result.content:
                    if hasattr(content, "text"):
                        import json

                        parsed: list[dict[str, Any]] = json.loads(content.text)
                        return parsed
            raise ValueError("Invalid response format from MCP server")

        return cast(list[dict[str, Any]], self._retry_operation("get_pending_orders", _fetch))

    def parse_candles_csv(self, csv_data: str) -> list[dict[str, Any]]:
        """Parse CSV candle data into list of dictionaries.

        Args:
            csv_data: CSV string from get_candles

        Returns:
            List of candle dictionaries with parsed values
        """
        reader = csv.DictReader(io.StringIO(csv_data))
        candles = []
        for row in reader:
            candle = {
                "time": row.get("time", ""),
                "open": float(row.get("open", 0)),
                "high": float(row.get("high", 0)),
                "low": float(row.get("low", 0)),
                "close": float(row.get("close", 0)),
                "tick_volume": int(row.get("tick_volume", 0)),
                "spread": int(row.get("spread", 0)),
                "real_volume": int(row.get("real_volume", 0)),
            }
            candles.append(candle)
        return candles

    def __repr__(self) -> str:
        """Return string representation."""
        return f"Mt5DataProvider(server_url={self.server_url!r})"
