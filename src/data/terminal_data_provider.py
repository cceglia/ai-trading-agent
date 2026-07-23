"""Terminal MCP data provider via MCP Streamable HTTP protocol."""

import asyncio
import csv
import io
import json
import logging
import threading
from collections.abc import Callable
from datetime import datetime
from typing import Any, TypeVar, cast

logger = logging.getLogger(__name__)

T = TypeVar("T")


class TerminalApiError(RuntimeError):
    """Non-retryable server-side error from the terminal MCP server."""


class TerminalDataProvider:
    """Data provider using terminal MCP server via MCP Streamable HTTP protocol.

    Fetches OHLC candle data and other market information from the terminal MCP
    server using the MCP library with Streamable HTTP transport. Maintains a
    persistent session in a background event loop thread.
    """

    def __init__(
        self,
        server_url: str | None = None,
        api_key: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """Initialize TerminalDataProvider.

        Args:
            server_url: Terminal MCP server URL (default from settings/env).
            api_key: Bearer token for authentication.
            timeout: HTTP request timeout in seconds.
            max_retries: Maximum retry attempts on transient failures.
            retry_delay: Base delay in seconds for exponential backoff.
        """
        self.server_url = server_url or "http://127.0.0.1:22346/mcp"
        self.api_key = api_key or ""
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        # Background event loop state
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None
        # MCP session state (set by _connect_async)
        self._client: Any = None
        self._transport_context: Any = None
        self._http_client: Any = None

    # ------------------------------------------------------------------
    # Background event loop
    # ------------------------------------------------------------------

    def _ensure_loop(self) -> asyncio.AbstractEventLoop:
        """Start background event loop thread if not already running."""
        if self._loop is None or self._loop.is_closed():
            loop = asyncio.new_event_loop()
            thread = threading.Thread(
                target=loop.run_forever,
                daemon=True,
                name="mcp-event-loop",
            )
            thread.start()
            self._loop = loop
            self._thread = thread
        return self._loop

    def _run_async(self, coro: Any) -> Any:
        """Run a coroutine in the background event loop and return its result."""
        loop = self._ensure_loop()
        future = asyncio.run_coroutine_threadsafe(coro, loop)
        try:
            return future.result(timeout=self.timeout + 5.0)
        except TimeoutError:
            raise ConnectionError("MCP operation timed out") from None

    # ------------------------------------------------------------------
    # MCP connection lifecycle
    # ------------------------------------------------------------------

    async def _connect_async(self) -> None:
        """Establish MCP session via Streamable HTTP."""
        from mcp import ClientSession
        from mcp.client.streamable_http import streamable_http_client

        headers: dict[str, str] = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        http_client = __import__("httpx").AsyncClient(
            headers=headers,
            timeout=__import__("httpx").Timeout(self.timeout),
        )

        try:
            self._transport_context = streamable_http_client(
                self.server_url,
                http_client=http_client,
            )
            streams = await self._transport_context.__aenter__()
            read_stream, write_stream, _get_session_id = streams
            self._client = ClientSession(read_stream, write_stream)
            await self._client.__aenter__()
            await self._client.initialize()
            self._http_client = http_client
            logger.info("MCP session initialized at %s", self.server_url)
        except Exception as e:
            await http_client.aclose()
            raise ConnectionError(f"Cannot connect to MCP server at {self.server_url}: {e}") from e

    async def _disconnect_async(self) -> None:
        """Tear down MCP session."""
        if self._client is not None:
            try:
                await self._client.__aexit__(None, None, None)
            except Exception:
                pass
            self._client = None
        if self._transport_context is not None:
            try:
                await self._transport_context.__aexit__(None, None, None)
            except Exception:
                pass
            self._transport_context = None
        if self._http_client is not None:
            try:
                await self._http_client.aclose()
            except Exception:
                pass
            self._http_client = None

    # ------------------------------------------------------------------
    # Tool calling
    # ------------------------------------------------------------------

    def _call_tool(self, tool_name: str, arguments: dict[str, Any] | None = None) -> Any:
        """Call an MCP tool via the persistent session.

        Returns:
            CallToolResult from the mcp library (has .content, .isError).

        Raises:
            ConnectionError: Cannot reach server or timeout.
            TerminalApiError: Server returned an error result.
            ValueError: Response is malformed.
        """

        async def _async_call() -> Any:
            if self._client is None:
                await self._connect_async()
            try:
                return await self._client.call_tool(tool_name, arguments or {})
            except Exception as e:
                raise TerminalApiError(str(e)) from e

        try:
            return self._run_async(_async_call())
        except ConnectionError:
            raise
        except TerminalApiError:
            raise
        except Exception as e:
            raise TerminalApiError(str(e)) from e

    # ------------------------------------------------------------------
    # Retry logic
    # ------------------------------------------------------------------

    def _call_with_retry(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        method_name: str,
        extractor: Callable[[Any], T],
    ) -> T:
        """Call an MCP tool with retry on transient failures.

        Args:
            tool_name: MCP tool name.
            arguments: Tool arguments dict.
            method_name: Human-readable name for logging.
            extractor: Callable that transforms the raw MCP result into T.

        Returns:
            Extracted value of type T.

        Raises:
            ConnectionError: All retries exhausted or server unreachable.
            TerminalApiError: Non-retryable server error.
            ValueError: Malformed response.
        """
        import time

        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                result = self._call_tool(tool_name, arguments)
                return extractor(result)
            except (TerminalApiError, ConnectionError, ValueError):
                raise
            except Exception as e:
                last_error = e
                logger.warning(
                    "Attempt %d/%d for %s failed: %s",
                    attempt + 1,
                    self.max_retries + 1,
                    method_name,
                    e,
                )
                if attempt < self.max_retries:
                    delay = self.retry_delay * (2**attempt)
                    logger.debug("Retrying in %.1f seconds...", delay)
                    time.sleep(delay)
        raise ConnectionError(
            f"Failed to {method_name} after {self.max_retries + 1} attempts: {last_error}"
        )

    # ------------------------------------------------------------------
    # Response extraction helpers
    # ------------------------------------------------------------------

    def _extract_text(self, result: Any) -> str:
        """Extract text from CallToolResult.content[0].text."""
        if getattr(result, "isError", False):
            error_text = "unknown error"
            try:
                error_text = result.content[0].text
            except Exception:
                pass
            raise TerminalApiError(f"Terminal MCP server returned error: {error_text}")
        try:
            return cast(str, result.content[0].text)
        except (KeyError, IndexError, TypeError, AttributeError):
            raise ValueError("MCP response missing result.content[0].text")

    def _extract_history(self, result: Any) -> list[dict[str, Any]]:
        """Extract candle history from CallToolResult.

        The text payload is a JSON object with a 'history' list.
        """
        inner_text = self._extract_text(result)
        try:
            inner = json.loads(inner_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse inner JSON from MCP response: {e}") from e
        history = inner.get("history")
        if history is None:
            raise ValueError("MCP response missing 'history' field in inner JSON")
        if not isinstance(history, list):
            raise ValueError("MCP 'history' field is not a list")
        return history

    def _normalize_to_csv(self, candles: list[dict[str, Any]]) -> str:
        """Convert terminal candle list to CSV string.

        CSV columns: time,open,high,low,close,tick_volume,spread,real_volume
        """
        output = io.StringIO()
        writer = csv.writer(output, lineterminator="\n")
        writer.writerow(
            [
                "time",
                "open",
                "high",
                "low",
                "close",
                "tick_volume",
                "spread",
                "real_volume",
            ]
        )
        for candle in candles:
            writer.writerow(
                [
                    candle.get("time", ""),
                    float(candle.get("open", 0)),
                    float(candle.get("high", 0)),
                    float(candle.get("low", 0)),
                    float(candle.get("close", 0)),
                    int(candle.get("tick_volume", 0)),
                    int(candle.get("spread", 0)),
                    0,
                ]
            )
        return output.getvalue()

    def _extract_candles_csv(self, result: Any) -> str:
        """Extract candle history from MCP result and normalize to CSV."""
        history = self._extract_history(result)
        return self._normalize_to_csv(history)

    def _extract_price(self, result: Any) -> dict[str, Any]:
        """Extract first symbol price from MCP result.

        The response format is: {"symbols": [{"symbol":"XAUUSD","bid":...,"ask":...}]}
        """
        data = json.loads(self._extract_text(result))
        symbols = data.get("symbols", [])
        if symbols:
            return cast(dict[str, Any], symbols[0])
        return {}

    def _extract_positions(self, result: Any, symbol: str | None) -> list[dict[str, Any]]:
        """Extract positions list from MCP result, optionally filtering by symbol."""
        data = json.loads(self._extract_text(result))
        positions = data.get("positions", [])
        if symbol and positions:
            return [p for p in positions if p.get("symbol", "").upper() == symbol.upper()]
        return cast(list[dict[str, Any]], positions)

    def _extract_orders(self, result: Any, symbol: str | None) -> list[dict[str, Any]]:
        """Extract orders list from MCP result, optionally filtering by symbol."""
        data = json.loads(self._extract_text(result))
        orders = data.get("orders", [])
        if symbol and orders:
            return [o for o in orders if o.get("symbol", "").upper() == symbol.upper()]
        return cast(list[dict[str, Any]], orders)

    # ------------------------------------------------------------------
    # Public API (DataSource protocol)
    # ------------------------------------------------------------------

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        count: int,
        broker_now: datetime | None = None,
    ) -> str:
        """Fetch OHLC candles from terminal MCP server.

        Args:
            symbol: Trading symbol (e.g., "XAUUSD").
            timeframe: Timeframe string (e.g., "H1", "D1", "H4").
            count: Number of candles to fetch.
            broker_now: Naive datetime in broker-local time to use as
                the reference point for lookback calculations. When
                omitted (None), UTC now is used.

        Returns:
            CSV string with columns:
            time,open,high,low,close,tick_volume,spread,real_volume

        Raises:
            ConnectionError: Server unreachable or max retries exceeded.
            TerminalApiError: Server-side error (auth, HTTP error).
            ValueError: Malformed response or missing required fields,
                or broker_now is timezone-aware (must be naive).
        """
        from datetime import UTC, datetime, timedelta

        if broker_now is not None and broker_now.tzinfo is not None:
            raise ValueError(
                f"broker_now must be a naive datetime, got timezone-aware: {broker_now.tzinfo}"
            )

        now = broker_now if broker_now is not None else datetime.now(UTC)
        period_hours = {
            "M1": 1 / 60,
            "M5": 5 / 60,
            "M15": 15 / 60,
            "M30": 0.5,
            "H1": 1,
            "H2": 2,
            "H3": 3,
            "H4": 4,
            "H6": 6,
            "H8": 8,
            "H12": 12,
            "D1": 24,
            "W1": 168,
            "MN1": 720,
        }
        hours = period_hours.get(timeframe, 1)
        # Weekend buffer: markets trade ~5/7 days, so multiply the lookback
        # by 1.5 to ensure we get the requested number of bars.
        # Without this, D1 at 500 bars would only return ~357 bars.
        weekend_buffer = 1.5
        dt_from = now - timedelta(hours=int(hours * count * weekend_buffer))

        return self._call_with_retry(
            "get_chart_history",
            {
                "symbol": symbol,
                "period": timeframe,
                "datetime_from": dt_from.strftime("%Y-%m-%dT%H:%M:%S"),
                "datetime_to": now.strftime("%Y-%m-%dT%H:%M:%S"),
                "limit": count,
            },
            "get_candles",
            self._extract_candles_csv,
        )

    def get_symbol_price(self, symbol: str) -> dict[str, Any]:
        """Fetch current symbol price from terminal MCP server."""
        return self._call_with_retry(
            "get_marketwatch_symbols",
            {"symbol": symbol},
            "get_symbol_price",
            lambda r: self._extract_price(r),
        )

    def get_positions(self, symbol: str | None = None) -> list[dict[str, Any]]:
        """Fetch open positions from terminal MCP server."""
        return self._call_with_retry(
            "get_trading_open_positions",
            {},
            "get_positions",
            lambda r: self._extract_positions(r, symbol),
        )

    def get_pending_orders(self, symbol: str | None = None) -> list[dict[str, Any]]:
        """Fetch pending orders from terminal MCP server."""
        return self._call_with_retry(
            "get_trading_open_positions",
            {},
            "get_pending_orders",
            lambda r: self._extract_orders(r, symbol),
        )

    def get_broker_time(self) -> datetime:
        """Fetch current broker server time from terminal MCP server.

        Returns:
            Naive datetime in broker-local time.

        Raises:
            ConnectionError: Server unreachable or max retries exceeded.
            TerminalApiError: Server-side error (auth, HTTP error).
            ValueError: Malformed response or missing required fields.
        """
        return self._call_with_retry(
            "get_time_information",
            {},
            "get_broker_time",
            self._extract_broker_time,
        )

    def _extract_broker_time(self, result: Any) -> datetime:
        """Extract broker time from get_time_information response.

        Expects JSON with a 'trade_server_last_known_time' field
        containing an ISO string like '2026-07-23T21:08:54Z'.
        """
        from datetime import datetime

        try:
            data = json.loads(self._extract_text(result))
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse inner JSON from MCP response: {e}") from e
        time_str = data.get("trade_server_last_known_time")
        if not time_str:
            raise ValueError("MCP response missing 'trade_server_last_known_time' field")
        return datetime.fromisoformat(time_str.rstrip("Z"))

    def __repr__(self) -> str:
        url = self.server_url
        masked_key = self.api_key[:4] + "..." if self.api_key else "(none)"
        return f"TerminalDataProvider(server_url={url!r}, api_key={masked_key!r})"
