"""Tests for Mt5DataProvider — MCP data provider with persistent event loop."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.data.mt5_data_provider import Mt5DataProvider

# Patch targets — the imports are local inside _connect_async, so we must
# patch at the source module, not at `src.data.mt5_data_provider`.
_SSE_CLIENT = "mcp.client.sse.sse_client"
_CLIENT_SESSION = "mcp.ClientSession"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_mcp_tool_result(text: str) -> MagicMock:
    """Create a mock MCP CallToolResult with a text content block."""
    content = MagicMock()
    content.text = text
    result = MagicMock()
    result.content = [content]
    return result


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_sse_context():
    """Mock ``mcp.client.sse.sse_client`` async context manager.

    Yields (read_stream, write_stream) when entered, and records enter/exit
    calls so tests can verify the session persists across tool calls.
    """
    read_stream = MagicMock(name="read_stream")
    write_stream = MagicMock(name="write_stream")

    ctx = AsyncMock()
    ctx.__aenter__ = AsyncMock(return_value=(read_stream, write_stream))
    ctx.__aexit__ = AsyncMock(return_value=None)
    ctx.enter_count = 0
    ctx.exit_count = 0

    original_aenter = ctx.__aenter__
    original_aexit = ctx.__aexit__

    async def _track_enter(*args, **kwargs):
        ctx.enter_count += 1
        return await original_aenter(*args, **kwargs)

    async def _track_exit(*args, **kwargs):
        ctx.exit_count += 1
        return await original_aexit(*args, **kwargs)

    ctx.__aenter__ = _track_enter
    ctx.__aexit__ = _track_exit

    return ctx, read_stream, write_stream


@pytest.fixture
def mock_client_session():
    """Mock ``mcp.ClientSession``."""
    client = AsyncMock()
    client.initialize = AsyncMock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)
    client.call_tool = AsyncMock()
    return client


@pytest.fixture
def provider():
    """Create an Mt5DataProvider with a known server URL."""
    return Mt5DataProvider(
        server_url="http://localhost:8082",
        max_retries=3,
        retry_delay=0.01,
    )


# ---------------------------------------------------------------------------
# Event loop persistence (the bug regression test)
# ---------------------------------------------------------------------------


class TestPersistentEventLoop:
    """Verify the background event loop persists across tool calls.

    The original bug: ``_call_tool`` called ``asyncio.run()`` per call, which
    creates a new event loop each time.  The ``sse_client`` async generator
    gets bound to that loop; when the loop is destroyed the generator tries
    to clean up via ``athrow()`` on a dead loop, producing:

        RuntimeError: generator didn't stop after athrow()

    The fix: a single background event loop in a daemon thread, scheduled via
    ``run_coroutine_threadsafe``.  These tests verify the fix works.
    """

    def test_event_loop_reused_across_calls(self, provider, mock_sse_context, mock_client_session):
        """Same event loop is used for every _call_tool invocation."""
        sse_ctx, _, _ = mock_sse_context

        with (
            patch(_SSE_CLIENT, return_value=sse_ctx),
            patch(_CLIENT_SESSION, return_value=mock_client_session),
        ):
            mock_client_session.call_tool.return_value = _make_mcp_tool_result('{"x":1}')

            provider._call_tool("tool_a")
            provider._call_tool("tool_b")
            provider._call_tool("tool_c")

            loop = provider._loop
            assert loop is not None
            assert loop.is_running()

            # SSE context entered exactly once — session persists
            assert sse_ctx.enter_count == 1

            # All three tool calls went through the same client
            assert mock_client_session.call_tool.call_count == 3

        provider.disconnect()

    def test_no_runtime_error_on_disconnect(self, provider, mock_sse_context, mock_client_session):
        """Disconnecting cleanly must NOT raise RuntimeError.

        This is the exact symptom of the original bug: the async generator
        couldn't stop after ``athrow()`` because its event loop was dead.
        """
        sse_ctx, _, _ = mock_sse_context

        with (
            patch(_SSE_CLIENT, return_value=sse_ctx),
            patch(_CLIENT_SESSION, return_value=mock_client_session),
        ):
            mock_client_session.call_tool.return_value = _make_mcp_tool_result("{}")

            provider._call_tool("tool_a")

            # This must not raise RuntimeError
            provider.disconnect()

            # SSE context was properly exited
            assert sse_ctx.exit_count == 1
            assert provider._client is None

    def test_background_loop_is_daemon_thread(self, provider):
        """The event loop thread must be a daemon so it won't block process exit."""
        provider._ensure_loop()
        thread = provider._loop_thread
        assert thread is not None
        assert thread.daemon is True
        provider.disconnect()

    def test_loop_stopped_after_disconnect(self, provider, mock_sse_context, mock_client_session):
        """After disconnect() the background loop must be stopped and references cleared."""
        sse_ctx, _, _ = mock_sse_context

        with (
            patch(_SSE_CLIENT, return_value=sse_ctx),
            patch(_CLIENT_SESSION, return_value=mock_client_session),
        ):
            mock_client_session.call_tool.return_value = _make_mcp_tool_result("{}")
            provider._call_tool("tool_a")

            provider.disconnect()

            assert provider._loop is None
            assert provider._loop_thread is None
            assert provider._client is None

    def test_reconnect_after_disconnect(self, provider, mock_sse_context, mock_client_session):
        """After disconnect, a new call_tool should reconnect on a fresh loop."""
        sse_ctx, _, _ = mock_sse_context

        with (
            patch(_SSE_CLIENT, return_value=sse_ctx),
            patch(_CLIENT_SESSION, return_value=mock_client_session),
        ):
            mock_client_session.call_tool.return_value = _make_mcp_tool_result("{}")

            provider._call_tool("tool_a")
            provider.disconnect()
            provider._call_tool("tool_b")

            # New loop created, SSE context entered again
            assert sse_ctx.enter_count == 2
            assert provider._loop is not None

        provider.disconnect()


# ---------------------------------------------------------------------------
# Connection lifecycle
# ---------------------------------------------------------------------------


class TestConnectionLifecycle:
    def test_connect_establishes_session(self, provider, mock_sse_context, mock_client_session):
        """connect() should enter the SSE context, create a ClientSession, and initialize."""
        sse_ctx, _, _ = mock_sse_context

        with (
            patch(_SSE_CLIENT, return_value=sse_ctx),
            patch(_CLIENT_SESSION, return_value=mock_client_session),
        ):
            provider.connect()

            # SSE context was entered (tracked via enter_count)
            assert sse_ctx.enter_count == 1
            mock_client_session.__aenter__.assert_awaited_once()
            mock_client_session.initialize.assert_awaited_once()
            assert provider._client is mock_client_session

        provider.disconnect()

    def test_disconnect_closes_session(self, provider, mock_sse_context, mock_client_session):
        """disconnect() should exit the ClientSession and SSE context."""
        sse_ctx, _, _ = mock_sse_context

        with (
            patch(_SSE_CLIENT, return_value=sse_ctx),
            patch(_CLIENT_SESSION, return_value=mock_client_session),
        ):
            provider.connect()
            provider.disconnect()

            mock_client_session.__aexit__.assert_awaited_once()
            # SSE context was exited (tracked via exit_count)
            assert sse_ctx.exit_count == 1
            assert provider._client is None

    def test_connect_failure_raises_connection_error(self, provider):
        """If the MCP server is unreachable, connect() raises ConnectionError."""
        with patch(_SSE_CLIENT) as mock_sse:
            mock_sse.side_effect = ConnectionRefusedError("refused")
            with pytest.raises(ConnectionError, match="Cannot connect to MCP server"):
                provider.connect()

    def test_connect_import_error_sets_client_none(self, provider):
        """If mcp is not installed, connect() logs warning and sets client to None."""
        with patch("builtins.__import__", side_effect=ImportError("no mcp")):
            provider.connect()
            assert provider._client is None


# ---------------------------------------------------------------------------
# _call_tool lazy connect
# ---------------------------------------------------------------------------


class TestCallToolLazyConnect:
    def test_call_tool_connects_if_client_none(
        self, provider, mock_sse_context, mock_client_session
    ):
        """_call_tool should auto-connect when _client is None."""
        sse_ctx, _, _ = mock_sse_context

        with (
            patch(_SSE_CLIENT, return_value=sse_ctx),
            patch(_CLIENT_SESSION, return_value=mock_client_session),
        ):
            assert provider._client is None
            mock_client_session.call_tool.return_value = _make_mcp_tool_result('{"ok":true}')

            provider._call_tool("get_candles_latest", {"symbol_name": "EURUSD"})

            mock_client_session.initialize.assert_awaited_once()

        provider.disconnect()

    def test_call_tool_passes_arguments(self, provider, mock_sse_context, mock_client_session):
        """_call_tool should forward tool_name and arguments to ClientSession.call_tool."""
        sse_ctx, _, _ = mock_sse_context

        with (
            patch(_SSE_CLIENT, return_value=sse_ctx),
            patch(_CLIENT_SESSION, return_value=mock_client_session),
        ):
            mock_client_session.call_tool.return_value = _make_mcp_tool_result("[]")

            provider._call_tool("get_all_positions", {"symbol": "EURUSD"})

            mock_client_session.call_tool.assert_awaited_once_with(
                "get_all_positions", {"symbol": "EURUSD"}
            )

        provider.disconnect()

    def test_call_tool_default_empty_arguments(
        self, provider, mock_sse_context, mock_client_session
    ):
        """_call_tool with no arguments should pass an empty dict."""
        sse_ctx, _, _ = mock_sse_context

        with (
            patch(_SSE_CLIENT, return_value=sse_ctx),
            patch(_CLIENT_SESSION, return_value=mock_client_session),
        ):
            mock_client_session.call_tool.return_value = _make_mcp_tool_result("[]")

            provider._call_tool("get_all_positions")

            mock_client_session.call_tool.assert_awaited_once_with("get_all_positions", {})

        provider.disconnect()


# ---------------------------------------------------------------------------
# Data fetching methods
# ---------------------------------------------------------------------------


class TestGetData:
    """Tests for get_candles, get_symbol_price, get_positions, get_pending_orders."""

    @pytest.fixture(autouse=True)
    def _connected_provider(self, provider, mock_sse_context, mock_client_session):
        """Provide a provider that's already connected (mocked)."""
        self.provider = provider
        self.mock_client = mock_client_session
        sse_ctx, _, _ = mock_sse_context

        self._patcher_sse = patch(_SSE_CLIENT, return_value=sse_ctx)
        self._patcher_session = patch(_CLIENT_SESSION, return_value=mock_client_session)
        self._patcher_sse.start()
        self._patcher_session.start()
        yield
        self._patcher_session.stop()
        self._patcher_sse.stop()
        provider.disconnect()

    def test_get_candles_returns_csv(self):
        csv = "time,open,high,low,close\n2024-01-01,1.085,1.090,1.080,1.0875\n"
        self.mock_client.call_tool.return_value = _make_mcp_tool_result(csv)

        result = self.provider.get_candles("EURUSD", "D1", 100)

        assert "time,open" in result
        assert "1.085" in result

    def test_get_candles_invalid_response_raises(self):
        """Invalid MCP response is retried and eventually wrapped as ConnectionError."""
        bad_result = MagicMock()
        bad_result.content = None
        self.mock_client.call_tool.return_value = bad_result

        with pytest.raises(ConnectionError, match="Failed to get_candles after 3 attempts"):
            self.provider.get_candles("EURUSD", "D1", 100)

    def test_get_symbol_price_returns_dict(self):
        data = {"bid": 1.0875, "ask": 1.0877, "last": 1.0876}
        self.mock_client.call_tool.return_value = _make_mcp_tool_result(json.dumps(data))

        result = self.provider.get_symbol_price("EURUSD")

        assert result["bid"] == 1.0875
        assert result["ask"] == 1.0877

    def test_get_positions_all(self):
        positions = [{"id": 1, "symbol": "EURUSD", "type": "BUY", "volume": 0.1}]
        self.mock_client.call_tool.return_value = _make_mcp_tool_result(json.dumps(positions))

        result = self.provider.get_positions()

        assert len(result) == 1
        assert result[0]["symbol"] == "EURUSD"
        self.mock_client.call_tool.assert_awaited_once_with("get_all_positions", {})

    def test_get_positions_by_symbol(self):
        positions = [{"id": 1, "symbol": "EURUSD"}]
        self.mock_client.call_tool.return_value = _make_mcp_tool_result(json.dumps(positions))

        self.provider.get_positions("EURUSD")

        self.mock_client.call_tool.assert_awaited_once_with(
            "get_positions_by_symbol", {"symbol": "EURUSD"}
        )

    def test_get_pending_orders_all(self):
        orders = [{"id": 10, "symbol": "EURUSD", "type": "BUY_LIMIT"}]
        self.mock_client.call_tool.return_value = _make_mcp_tool_result(json.dumps(orders))

        result = self.provider.get_pending_orders()

        assert len(result) == 1
        self.mock_client.call_tool.assert_awaited_once_with("get_all_pending_orders", {})

    def test_get_pending_orders_by_symbol(self):
        orders = [{"id": 10, "symbol": "EURUSD"}]
        self.mock_client.call_tool.return_value = _make_mcp_tool_result(json.dumps(orders))

        self.provider.get_pending_orders("EURUSD")

        self.mock_client.call_tool.assert_awaited_once_with(
            "get_pending_orders_by_symbol", {"symbol": "EURUSD"}
        )


# ---------------------------------------------------------------------------
# Retry logic
# ---------------------------------------------------------------------------


class TestRetryLogic:
    def test_retry_succeeds_on_second_attempt(self, provider):
        call_count = 0

        def _flaky():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise RuntimeError("transient error")
            return "ok"

        result = provider._retry_operation("flaky_op", _flaky)
        assert result == "ok"
        assert call_count == 2

    def test_retry_exhausted_raises_connection_error(self, provider):
        def _always_fails():
            raise RuntimeError("always fails")

        with pytest.raises(ConnectionError, match="Failed to flaky_op after 3 attempts"):
            provider._retry_operation("flaky_op", _always_fails)

    def test_retry_connection_error_immediately_reraised(self, provider):
        def _connection_error():
            raise ConnectionError("server down")

        with pytest.raises(ConnectionError, match="server down"):
            provider._retry_operation("op", _connection_error)


# ---------------------------------------------------------------------------
# CSV parsing
# ---------------------------------------------------------------------------


class TestParseCandlesCsv:
    def test_parse_valid_csv(self, provider):
        csv = (
            "time,open,high,low,close,tick_volume,spread,real_volume\n"
            "2024-01-01 00:00:00,1.0850,1.0900,1.0800,1.0875,1000,15,500\n"
            "2024-01-02 00:00:00,1.0875,1.0920,1.0850,1.0910,1200,12,600\n"
        )
        candles = provider.parse_candles_csv(csv)

        assert len(candles) == 2
        assert candles[0]["open"] == 1.085
        assert candles[1]["close"] == 1.091
        assert candles[0]["tick_volume"] == 1000

    def test_parse_single_bar(self, provider):
        csv = (
            "time,open,high,low,close,tick_volume,spread,real_volume\n"
            "2024-01-01,1.085,1.090,1.080,1.0875,100,5,50\n"
        )
        candles = provider.parse_candles_csv(csv)
        assert len(candles) == 1

    def test_parse_missing_fields_default_to_zero(self, provider):
        csv = "time,open,high,low,close\n2024-01-01,1.085,1.090,1.080,1.0875\n"
        candles = provider.parse_candles_csv(csv)
        assert candles[0]["tick_volume"] == 0


# ---------------------------------------------------------------------------
# Repr
# ---------------------------------------------------------------------------


class TestRepr:
    def test_repr_shows_server_url(self):
        p = Mt5DataProvider(server_url="http://my-server:9090")
        assert "http://my-server:9090" in repr(p)


# ---------------------------------------------------------------------------
# Server URL from env
# ---------------------------------------------------------------------------


class TestServerUrl:
    def test_default_server_url(self):
        p = Mt5DataProvider()
        assert p.server_url == "http://localhost:8082"

    def test_custom_server_url(self):
        p = Mt5DataProvider(server_url="http://custom:1234")
        assert p.server_url == "http://custom:1234"

    def test_env_var_fallback(self, monkeypatch):
        monkeypatch.setenv("MCP_SERVER_URL", "http://env-host:5555")
        p = Mt5DataProvider()
        assert p.server_url == "http://env-host:5555"
