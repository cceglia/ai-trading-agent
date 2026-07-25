"""Tests for TerminalDataProvider — MCP Streamable HTTP data provider."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from config.settings import Settings
from src.data.terminal_data_provider import TerminalDataProvider

# ---------------------------------------------------------------------------
# Settings descriptions
# ---------------------------------------------------------------------------


class TestSettingsDescriptions:
    """Settings field descriptions should refer to broker time, not UTC."""

    def test_settings_d1_close_time_description_says_broker_time(self):
        desc = Settings.model_fields["d1_close_time"].description
        assert "broker time" in desc.lower()

    def test_settings_h4_close_time_description_says_broker_time(self):
        desc = Settings.model_fields["h4_close_time"].description
        assert "broker time" in desc.lower()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_mcp_result(text: str, is_error: bool = False) -> MagicMock:
    """Create a mock object mimicking mcp.types.CallToolResult.

    Matches the real shape: .content[0].text and .isError
    """
    result = MagicMock()
    content_item = MagicMock()
    content_item.type = "text"
    content_item.text = text
    result.content = [content_item]
    result.isError = is_error
    return result


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def provider():
    return TerminalDataProvider(
        server_url="http://localhost:8082/jsonrpc",
        api_key="test-key-123",
        max_retries=2,
        retry_delay=0.01,
    )


GOLDEN_XAUUSD_H1 = json.dumps(
    {
        "symbol": "XAUUSD",
        "period": "H1",
        "history": [
            {
                "time": "2026.07.23 01:00:00",
                "open": 4120.67,
                "high": 4129.52,
                "low": 4119.81,
                "close": 4121.57,
                "tick_volume": 7444,
                "spread": 53,
            },
            {
                "time": "2026.07.23 02:00:00",
                "open": 4121.82,
                "high": 4134.01,
                "low": 4116.54,
                "close": 4133.24,
                "tick_volume": 7626,
                "spread": 40,
            },
        ],
    }
)

EURUSD_NO_SPREAD = json.dumps(
    {
        "symbol": "EURUSD",
        "period": "H1",
        "history": [
            {
                "time": "2026.07.23 09:00:00",
                "open": 1.14296,
                "high": 1.14330,
                "low": 1.14237,
                "close": 1.14254,
                "tick_volume": 2594,
            },
        ],
    }
)

EMPTY_HISTORY = json.dumps({"symbol": "XAUUSD", "period": "H1", "history": []})

PRICE_RESPONSE = json.dumps({"symbols": [{"symbol": "XAUUSD", "bid": 1.0875, "ask": 1.0877}]})

POSITIONS_RESPONSE = json.dumps(
    {"positions": [{"id": 1, "symbol": "XAUUSD", "type": "buy", "volume": 0.1}], "orders": []}
)

ORDERS_RESPONSE = json.dumps(
    {
        "positions": [],
        "orders": [
            {"id": 42, "symbol": "XAUUSD", "type": "buy_limit", "volume": 0.1, "price": 4100.0}
        ],
    }
)


# ---------------------------------------------------------------------------
# CSV output
# ---------------------------------------------------------------------------


class TestGetCandlesCsv:
    """Verify get_candles returns correctly formatted CSV."""

    def test_get_candles_returns_csv_with_header(self, provider):
        mock_result = _make_mcp_result(GOLDEN_XAUUSD_H1)
        frozen = datetime(2026, 7, 23, 12, 0, 0, tzinfo=UTC)

        with (
            patch.object(provider, "_call_tool", return_value=mock_result) as mock_call,
            patch("datetime.datetime", wraps=datetime) as mock_dt,
        ):
            mock_dt.now.return_value = frozen
            result = provider.get_candles("XAUUSD", "H1", 2)

        assert isinstance(result, str)
        lines = result.strip().split("\n")
        assert lines[0] == "time,open,high,low,close,tick_volume,spread,real_volume"
        assert "4120.67" in result
        assert "4121.57" in result
        assert "4129.52" in result
        assert "7444" in result
        assert "53" in result
        assert "0" in result

        mock_call.assert_called_once_with(
            "get_chart_history",
            {
                "symbol": "XAUUSD",
                "period": "H1",
                "datetime_from": "2026-07-23T09:00:00",
                "datetime_to": "2026-07-23T12:00:00",
                "limit": 2,
            },
        )

    def test_csv_column_order(self, provider):
        mock_result = _make_mcp_result(GOLDEN_XAUUSD_H1)
        frozen = datetime(2026, 7, 23, 12, 0, 0, tzinfo=UTC)

        with (
            patch.object(provider, "_call_tool", return_value=mock_result),
            patch("datetime.datetime", wraps=datetime) as mock_dt,
        ):
            mock_dt.now.return_value = frozen
            result = provider.get_candles("XAUUSD", "H1", 2)

        header = result.strip().split("\n")[0]
        columns = header.split(",")
        assert columns == [
            "time",
            "open",
            "high",
            "low",
            "close",
            "tick_volume",
            "spread",
            "real_volume",
        ]

    def test_missing_spread_defaults_to_zero(self, provider):
        mock_result = _make_mcp_result(EURUSD_NO_SPREAD)
        frozen = datetime(2026, 7, 23, 12, 0, 0, tzinfo=UTC)

        with (
            patch.object(provider, "_call_tool", return_value=mock_result),
            patch("datetime.datetime", wraps=datetime) as mock_dt,
        ):
            mock_dt.now.return_value = frozen
            result = provider.get_candles("EURUSD", "H1", 1)

        header, data = result.strip().split("\n")
        columns = header.split(",")
        values = data.split(",")
        spread_idx = columns.index("spread")
        assert values[spread_idx] == "0"

    def test_missing_real_volume_defaults_to_zero(self, provider):
        mock_result = _make_mcp_result(GOLDEN_XAUUSD_H1)
        frozen = datetime(2026, 7, 23, 12, 0, 0, tzinfo=UTC)

        with (
            patch.object(provider, "_call_tool", return_value=mock_result),
            patch("datetime.datetime", wraps=datetime) as mock_dt,
        ):
            mock_dt.now.return_value = frozen
            result = provider.get_candles("XAUUSD", "H1", 2)

        header = result.strip().split("\n")[0]
        columns = header.split(",")
        real_vol_idx = columns.index("real_volume")
        for line in result.strip().split("\n")[1:]:
            values = line.split(",")
            assert values[real_vol_idx] == "0"

    def test_empty_history_returns_header_only(self, provider):
        mock_result = _make_mcp_result(EMPTY_HISTORY)
        frozen = datetime(2026, 7, 23, 12, 0, 0, tzinfo=UTC)

        with (
            patch.object(provider, "_call_tool", return_value=mock_result),
            patch("datetime.datetime", wraps=datetime) as mock_dt,
        ):
            mock_dt.now.return_value = frozen
            result = provider.get_candles("XAUUSD", "H1", 10)

        lines = result.strip().split("\n")
        assert len(lines) == 1
        assert lines[0] == "time,open,high,low,close,tick_volume,spread,real_volume"


# ---------------------------------------------------------------------------
# Broker now param
# ---------------------------------------------------------------------------


class TestGetCandlesBrokerNow:
    """get_candles must accept a broker_now parameter for broker-local time."""

    def test_get_candles_uses_broker_time_param(self, provider):
        """get_candles must use broker_now for lookback when provided."""
        mock_result = _make_mcp_result(GOLDEN_XAUUSD_H1)
        frozen = datetime(2026, 7, 23, 14, 0, 0)  # naive broker time

        with patch.object(provider, "_call_tool", return_value=mock_result) as mock_call:
            result = provider.get_candles("XAUUSD", "H1", 2, broker_now=frozen)

        assert isinstance(result, str)
        mock_call.assert_called_once_with(
            "get_chart_history",
            {
                "symbol": "XAUUSD",
                "period": "H1",
                "datetime_from": "2026-07-23T11:00:00",
                "datetime_to": "2026-07-23T14:00:00",
                "limit": 2,
            },
        )

    def test_get_candles_falls_back_to_utc_when_no_broker_now(self, provider):
        """Without broker_now, get_candles uses datetime.now(UTC)."""
        mock_result = _make_mcp_result(GOLDEN_XAUUSD_H1)
        frozen = datetime(2026, 7, 23, 12, 0, 0, tzinfo=UTC)

        with (
            patch.object(provider, "_call_tool", return_value=mock_result) as mock_call,
            patch("datetime.datetime", wraps=datetime) as mock_dt,
        ):
            mock_dt.now.return_value = frozen
            result = provider.get_candles("XAUUSD", "H1", 2)

        assert isinstance(result, str)
        mock_call.assert_called_once()

    def test_get_candles_explicit_none_falls_back_to_utc(self, provider):
        """Explicit broker_now=None must use datetime.now(UTC)."""
        mock_result = _make_mcp_result(GOLDEN_XAUUSD_H1)
        frozen = datetime(2026, 7, 23, 12, 0, 0, tzinfo=UTC)

        with (
            patch.object(provider, "_call_tool", return_value=mock_result) as mock_call,
            patch("datetime.datetime", wraps=datetime) as mock_dt,
        ):
            mock_dt.now.return_value = frozen
            result = provider.get_candles("XAUUSD", "H1", 2, broker_now=None)

        assert isinstance(result, str)
        mock_call.assert_called_once()

    def test_get_candles_rejects_aware_datetime(self, provider):
        """get_candles must raise ValueError when broker_now has tzinfo."""
        aware = datetime(2026, 7, 23, 14, 0, 0, tzinfo=UTC)
        with pytest.raises(ValueError, match="naive datetime"):
            provider.get_candles("XAUUSD", "H1", 2, broker_now=aware)


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


class TestErrorHandling:
    """Verify error conditions are surfaced as the right exception types."""

    def test_raises_runtime_error_on_mcp_is_error(self, provider):
        mock_result = _make_mcp_result("something went wrong", is_error=True)

        with patch.object(provider, "_call_tool", return_value=mock_result):
            with pytest.raises(RuntimeError, match="returned error"):
                provider.get_candles("XAUUSD", "H1", 2)

    def test_raises_connection_error_on_timeout(self, provider):
        with patch.object(provider, "_call_tool", side_effect=ConnectionError("timed out")):
            with pytest.raises(ConnectionError):
                provider.get_candles("XAUUSD", "H1", 2)

    def test_raises_value_error_on_malformed_inner_json(self, provider):
        mock_result = _make_mcp_result("not valid json{{{")

        with patch.object(provider, "_call_tool", return_value=mock_result):
            with pytest.raises(ValueError):
                provider.get_candles("XAUUSD", "H1", 2)


# ---------------------------------------------------------------------------
# Retry logic
# ---------------------------------------------------------------------------


class TestRetryLogic:
    """Verify retry behaviour via _call_with_retry."""

    def test_call_with_retry_succeeds_on_first_try(self, provider):
        mock_result = _make_mcp_result(EMPTY_HISTORY)
        extractor = MagicMock(return_value="ok")

        with patch.object(provider, "_call_tool", return_value=mock_result) as mock_call:
            result = provider._call_with_retry("test_tool", {}, "test_method", extractor)

        assert result == "ok"
        mock_call.assert_called_once_with("test_tool", {})
        extractor.assert_called_once_with(mock_result)

    def test_call_with_retry_retries_on_transient_failure(self, provider):
        mock_result = _make_mcp_result(EMPTY_HISTORY)
        mock_call = MagicMock()
        mock_call.side_effect = [RuntimeError("transient"), mock_result]
        extractor = MagicMock(return_value="ok")

        with patch.object(provider, "_call_tool", mock_call):
            result = provider._call_with_retry("test_tool", {}, "test_method", extractor)

        assert result == "ok"
        assert mock_call.call_count == 2
        extractor.assert_called_once_with(mock_result)

    def test_call_with_retry_exhausted_raises_connection_error(self, provider):
        mock_call = MagicMock(side_effect=RuntimeError("persistent"))
        extractor = MagicMock()

        with patch.object(provider, "_call_tool", mock_call):
            with pytest.raises(ConnectionError, match="Failed to test_method after"):
                provider._call_with_retry("test_tool", {}, "test_method", extractor)

        assert mock_call.call_count == provider.max_retries + 1
        extractor.assert_not_called()

    def test_call_with_retry_terminal_api_error_not_retried(self, provider):
        from src.data.terminal_data_provider import TerminalApiError

        mock_call = MagicMock(side_effect=TerminalApiError("auth failed"))
        extractor = MagicMock()

        with patch.object(provider, "_call_tool", mock_call):
            with pytest.raises(TerminalApiError, match="auth failed"):
                provider._call_with_retry("test_tool", {}, "test_method", extractor)

        mock_call.assert_called_once()
        extractor.assert_not_called()

    def test_call_with_retry_connection_error_not_retried(self, provider):
        mock_call = MagicMock(side_effect=ConnectionError("refused"))
        extractor = MagicMock()

        with patch.object(provider, "_call_tool", mock_call):
            with pytest.raises(ConnectionError, match="refused"):
                provider._call_with_retry("test_tool", {}, "test_method", extractor)

        mock_call.assert_called_once()
        extractor.assert_not_called()

    def test_call_with_retry_value_error_not_retried(self, provider):
        mock_call = MagicMock(side_effect=ValueError("bad data"))
        extractor = MagicMock()

        with patch.object(provider, "_call_tool", mock_call):
            with pytest.raises(ValueError, match="bad data"):
                provider._call_with_retry("test_tool", {}, "test_method", extractor)

        mock_call.assert_called_once()
        extractor.assert_not_called()

    def test_get_candles_retry_still_works(self, provider):
        ok_result = _make_mcp_result(GOLDEN_XAUUSD_H1)
        mock_call = MagicMock()
        mock_call.side_effect = [RuntimeError("transient"), ok_result]
        frozen = datetime(2026, 7, 23, 12, 0, 0, tzinfo=UTC)

        with (
            patch.object(provider, "_call_tool", mock_call),
            patch("datetime.datetime", wraps=datetime) as mock_dt,
        ):
            mock_dt.now.return_value = frozen
            result = provider.get_candles("XAUUSD", "H1", 2)

        assert isinstance(result, str)
        assert "4120.67" in result
        assert mock_call.call_count == 2


# ---------------------------------------------------------------------------
# Symbol price
# ---------------------------------------------------------------------------


class TestGetSymbolPrice:
    """Verify get_symbol_price returns price dict and sends correct request."""

    def test_get_symbol_price_returns_dict(self, provider):
        mock_result = _make_mcp_result(PRICE_RESPONSE)

        with patch.object(provider, "_call_tool", return_value=mock_result) as mock_call:
            result = provider.get_symbol_price("XAUUSD")

        assert isinstance(result, dict)
        assert result == {"symbol": "XAUUSD", "bid": 1.0875, "ask": 1.0877}
        mock_call.assert_called_once_with(
            "get_marketwatch_symbols",
            {"symbol": "XAUUSD"},
        )

    def test_get_symbol_price_sends_correct_request(self, provider):
        mock_result = _make_mcp_result(PRICE_RESPONSE)

        with patch.object(provider, "_call_tool", return_value=mock_result) as mock_call:
            provider.get_symbol_price("XAUUSD")

        mock_call.assert_called_once_with(
            "get_marketwatch_symbols",
            {"symbol": "XAUUSD"},
        )

    def test_get_symbol_price_handles_empty_response(self, provider):
        mock_result = _make_mcp_result(json.dumps({"symbols": []}))

        with patch.object(provider, "_call_tool", return_value=mock_result):
            result = provider.get_symbol_price("XAUUSD")

        assert result == {}


# ---------------------------------------------------------------------------
# Positions
# ---------------------------------------------------------------------------


class TestGetPositions:
    """Verify get_positions returns list of positions and sends correct request."""

    def test_get_positions_all(self, provider):
        mock_result = _make_mcp_result(POSITIONS_RESPONSE)

        with patch.object(provider, "_call_tool", return_value=mock_result) as mock_call:
            result = provider.get_positions()

        mock_call.assert_called_once_with("get_trading_open_positions", {})
        assert result == [{"id": 1, "symbol": "XAUUSD", "type": "buy", "volume": 0.1}]

    def test_get_positions_by_symbol(self, provider):
        response = json.dumps(
            {
                "positions": [
                    {"id": 1, "symbol": "EURUSD", "volume": 0.2},
                    {"id": 2, "symbol": "XAUUSD", "volume": 0.1},
                ],
                "orders": [],
            }
        )
        mock_result = _make_mcp_result(response)

        with patch.object(provider, "_call_tool", return_value=mock_result) as mock_call:
            result = provider.get_positions("XAUUSD")

        mock_call.assert_called_once_with("get_trading_open_positions", {})
        assert result == [{"id": 2, "symbol": "XAUUSD", "volume": 0.1}]

    def test_get_positions_returns_list(self, provider):
        mock_result = _make_mcp_result(POSITIONS_RESPONSE)

        with patch.object(provider, "_call_tool", return_value=mock_result):
            result = provider.get_positions()

        assert isinstance(result, list)
        assert result == [{"id": 1, "symbol": "XAUUSD", "type": "buy", "volume": 0.1}]

    def test_get_positions_empty(self, provider):
        mock_result = _make_mcp_result(json.dumps({"positions": [], "orders": []}))

        with patch.object(provider, "_call_tool", return_value=mock_result):
            result = provider.get_positions()

        assert result == []


# ---------------------------------------------------------------------------
# Pending orders
# ---------------------------------------------------------------------------


class TestGetPendingOrders:
    """Verify get_pending_orders returns list of orders and sends correct request."""

    def test_get_pending_orders_all(self, provider):
        mock_result = _make_mcp_result(ORDERS_RESPONSE)

        with patch.object(provider, "_call_tool", return_value=mock_result) as mock_call:
            result = provider.get_pending_orders()

        mock_call.assert_called_once_with("get_trading_open_positions", {})
        assert result == [
            {"id": 42, "symbol": "XAUUSD", "type": "buy_limit", "volume": 0.1, "price": 4100.0}
        ]

    def test_get_pending_orders_by_symbol(self, provider):
        response = json.dumps(
            {
                "positions": [],
                "orders": [
                    {"id": 1, "symbol": "EURUSD", "price": 1.05},
                    {"id": 42, "symbol": "XAUUSD", "price": 4100.0},
                ],
            }
        )
        mock_result = _make_mcp_result(response)

        with patch.object(provider, "_call_tool", return_value=mock_result) as mock_call:
            result = provider.get_pending_orders("XAUUSD")

        mock_call.assert_called_once_with("get_trading_open_positions", {})
        assert result == [{"id": 42, "symbol": "XAUUSD", "price": 4100.0}]

    def test_get_pending_orders_returns_list(self, provider):
        mock_result = _make_mcp_result(ORDERS_RESPONSE)

        with patch.object(provider, "_call_tool", return_value=mock_result):
            result = provider.get_pending_orders()

        assert isinstance(result, list)
        assert result == [
            {"id": 42, "symbol": "XAUUSD", "type": "buy_limit", "volume": 0.1, "price": 4100.0}
        ]

    def test_get_pending_orders_empty(self, provider):
        mock_result = _make_mcp_result(json.dumps({"positions": [], "orders": []}))

        with patch.object(provider, "_call_tool", return_value=mock_result):
            result = provider.get_pending_orders()

        assert result == []


# ---------------------------------------------------------------------------
# Broker time
# ---------------------------------------------------------------------------

TIME_INFO_RESPONSE = json.dumps(
    {
        "utc_time": "2026-07-23T18:08:54Z",
        "local_time": "2026-07-23T20:08:54Z",
        "local_utc_offset_minutes": 120,
        "daylight_saving_time": True,
        "trade_server_last_known_time": "2026-07-23T21:08:54Z",
    }
)


class TestGetBrokerTime:
    """Verify get_broker_time returns naive datetime and sends correct request."""

    def test_returns_naive_datetime(self, provider):
        mock_result = _make_mcp_result(TIME_INFO_RESPONSE)

        with patch.object(provider, "_call_tool", return_value=mock_result):
            result = provider.get_broker_time()

        assert isinstance(result, datetime)
        assert result.tzinfo is None

    def test_parses_correct_time(self, provider):
        mock_result = _make_mcp_result(TIME_INFO_RESPONSE)

        with patch.object(provider, "_call_tool", return_value=mock_result):
            result = provider.get_broker_time()

        assert result == datetime(2026, 7, 23, 21, 8, 54)

    def test_calls_time_information_with_no_args(self, provider):
        mock_result = _make_mcp_result(TIME_INFO_RESPONSE)

        with patch.object(provider, "_call_tool", return_value=mock_result) as mock_call:
            provider.get_broker_time()

        mock_call.assert_called_once_with("get_time_information", {})

    def test_raises_value_error_on_missing_field(self, provider):
        mock_result = _make_mcp_result(json.dumps({"utc_time": "2026-07-23T18:08:54Z"}))

        with patch.object(provider, "_call_tool", return_value=mock_result):
            with pytest.raises(ValueError, match="trade_server_last_known_time"):
                provider.get_broker_time()

    def test_raises_value_error_on_malformed_json(self, provider):
        mock_result = _make_mcp_result("{{{bad json")

        with patch.object(provider, "_call_tool", return_value=mock_result):
            with pytest.raises(ValueError, match="Failed to parse"):
                provider.get_broker_time()

    def test_raises_terminal_api_error_on_mcp_error(self, provider):
        mock_result = _make_mcp_result("server error", is_error=True)

        with patch.object(provider, "_call_tool", return_value=mock_result):
            with pytest.raises(RuntimeError, match="returned error"):
                provider.get_broker_time()

    def test_raises_connection_error_on_timeout(self, provider):
        with patch.object(provider, "_call_tool", side_effect=ConnectionError("timed out")):
            with pytest.raises(ConnectionError):
                provider.get_broker_time()


# ---------------------------------------------------------------------------
# Structural checks — inline imports
# ---------------------------------------------------------------------------


def test_no_inline_imports():
    """Verify terminal_data_provider.py has no imports inside function bodies.

    All imports must be at module level. Inline imports inside method bodies
    add unnecessary overhead and hurt readability.
    """
    import ast
    from pathlib import Path

    source = (
        Path(__file__).resolve().parent.parent.parent / "src" / "data" / "terminal_data_provider.py"
    )
    tree = ast.parse(source.read_text(encoding="utf-8"))

    violations: list[tuple[str, int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            for child in ast.walk(node):
                if child is node:
                    continue
                if isinstance(child, ast.Import | ast.ImportFrom):
                    violations.append((node.name, child.lineno, ast.dump(child)))

    assert not violations, (
        f"Found {len(violations)} inline import(s) in function bodies:\n"
        + "\n".join(f"  {name}:{lineno} -> {dump}" for name, lineno, dump in violations)
    )
