from datetime import UTC, datetime
from unittest.mock import patch

import pytest

from src.data.snapshot_builder import SnapshotBuilder

VALID_CSV = (
    "time,open,high,low,close,tick_volume,spread,real_volume\n"
    "2024-01-01T00:00:00,1.0850,1.0900,1.0800,1.0875,1000,1,500\n"
    "2024-01-02T00:00:00,1.0875,1.0950,1.0850,1.0920,1200,1,600\n"
    "2024-01-03T00:00:00,1.0920,1.0960,1.0880,1.0940,1100,1,550\n"
)


class TestSnapshotBuilderParsing:
    def test_build_valid_csv(self):
        builder = SnapshotBuilder()
        snapshot = builder.build(VALID_CSV, "EURUSD", "H4")
        assert snapshot["market"]["symbol"] == "EURUSD"
        assert snapshot["requested_timeframe"] == "H4"
        assert snapshot["returned_timeframe"] == "H4"
        assert len(snapshot["bars"]) == 3

    def test_build_single_bar(self):
        csv = "time,open,high,low,close\n2024-01-01T00:00:00,1.0850,1.0900,1.0800,1.0875\n"
        builder = SnapshotBuilder()
        snapshot = builder.build(csv, "EURUSD", "D1")
        assert len(snapshot["bars"]) == 1
        assert snapshot["bars"][0]["open"] == 1.0850
        assert snapshot["bars"][0]["high"] == 1.0900
        assert snapshot["bars"][0]["low"] == 1.0800
        assert snapshot["bars"][0]["close"] == 1.0875

    def test_build_empty_csv_raises(self):
        builder = SnapshotBuilder()
        with pytest.raises(ValueError, match="Empty CSV data"):
            builder.build("", "EURUSD", "H4")

    def test_build_whitespace_only_csv_raises(self):
        builder = SnapshotBuilder()
        with pytest.raises(ValueError, match="Empty CSV data"):
            builder.build("   \n  ", "EURUSD", "H4")

    def test_build_no_valid_bars_raises(self):
        csv = "time,open,high,low,close\n,1.0850,1.0900,1.0800,1.0875\n"
        builder = SnapshotBuilder()
        with pytest.raises(ValueError, match="No valid bars found"):
            builder.build(csv, "EURUSD", "H4")


class TestSnapshotBuilderStructure:
    def test_snapshot_has_required_fields(self):
        builder = SnapshotBuilder()
        snapshot = builder.build(VALID_CSV, "EURUSD", "H4")
        required = {
            "source",
            "market",
            "requested_timeframe",
            "returned_timeframe",
            "retrieved_at",
            "latest_closed_candle_time",
            "candle_closure_verified",
            "bars",
        }
        assert required.issubset(set(snapshot.keys()))

    def test_source_type_is_tradingview_mcp(self):
        builder = SnapshotBuilder()
        snapshot = builder.build(VALID_CSV, "EURUSD", "H4")
        assert snapshot["source"]["type"] == "TRADINGVIEW_MCP"

    def test_market_contains_symbol_and_provider(self):
        builder = SnapshotBuilder()
        snapshot = builder.build(VALID_CSV, "XAUUSD", "H1")
        assert snapshot["market"]["symbol"] == "XAUUSD"
        assert snapshot["market"]["provider"] == "MCP"

    def test_custom_provider(self):
        builder = SnapshotBuilder()
        snapshot = builder.build(VALID_CSV, "EURUSD", "H4", provider="CUSTOM")
        assert snapshot["market"]["provider"] == "CUSTOM"

    def test_candle_closure_verified_true(self):
        builder = SnapshotBuilder()
        snapshot = builder.build(VALID_CSV, "EURUSD", "H4")
        assert snapshot["candle_closure_verified"] is True

    def test_bars_are_closed(self):
        builder = SnapshotBuilder()
        snapshot = builder.build(VALID_CSV, "EURUSD", "H4")
        for bar in snapshot["bars"]:
            assert bar["closed"] is True

    def test_bar_times_are_ordered(self):
        builder = SnapshotBuilder()
        snapshot = builder.build(VALID_CSV, "EURUSD", "H4")
        times = [b["open_time"] for b in snapshot["bars"]]
        assert times == sorted(times)


class TestSnapshotBuilderValidation:
    def test_unsupported_timeframe_raises(self):
        csv = "time,open,high,low,close\n2024-01-01T00:00:00,1.0850,1.0900,1.0800,1.0875\n"
        builder = SnapshotBuilder()
        with pytest.raises(ValueError, match="Unsupported timeframe"):
            builder.build(csv, "EURUSD", "M15")

    def test_empty_symbol_raises(self):
        csv = "time,open,high,low,close\n2024-01-01T00:00:00,1.0850,1.0900,1.0800,1.0875\n"
        builder = SnapshotBuilder()
        with pytest.raises(ValueError, match="market.symbol is required"):
            builder.build(csv, "", "H4")

    def test_high_inconsistent_with_ohlc_skips_bar(self):
        csv = "time,open,high,low,close\n2024-01-01T00:00:00,1.0900,1.0850,1.0800,1.0875\n"
        builder = SnapshotBuilder()
        with pytest.raises(ValueError, match="No valid bars found"):
            builder.build(csv, "EURUSD", "H4")

    def test_low_inconsistent_with_ohlc_skips_bar(self):
        csv = "time,open,high,low,close\n2024-01-01T00:00:00,1.0850,1.0900,1.0950,1.0875\n"
        builder = SnapshotBuilder()
        with pytest.raises(ValueError, match="No valid bars found"):
            builder.build(csv, "EURUSD", "H4")


# ── Feature-02: SnapshotBuilder broker_time + field rename ──────────────


def test_snapshot_builder_accepts_broker_time():
    """build() must accept optional broker_now parameter."""
    builder = SnapshotBuilder()
    broker_now = datetime(2026, 7, 21, 14, 30, 0)
    snapshot = builder.build(VALID_CSV, "EURUSD", "H4", broker_now=broker_now)
    assert snapshot["retrieved_at"] == "2026-07-21T14:30:00"


def test_snapshot_builder_falls_back_to_utc():
    """Without broker_now, build() uses datetime.now(UTC)."""
    builder = SnapshotBuilder()
    frozen = datetime(2026, 7, 21, 14, 30, 0, tzinfo=UTC)
    with patch("src.data.snapshot_builder.datetime") as mock_dt:
        mock_dt.now.return_value = frozen
        snapshot = builder.build(VALID_CSV, "EURUSD", "H4")
    assert snapshot["retrieved_at"] == "2026-07-21T14:30:00+00:00"


def test_snapshot_fields_no_utc_suffix():
    """Snapshot top-level fields must not have _utc suffix."""
    builder = SnapshotBuilder()
    broker_now = datetime(2026, 7, 21, 14, 30, 0)
    snapshot = builder.build(VALID_CSV, "EURUSD", "H4", broker_now=broker_now)
    assert "retrieved_at_utc" not in snapshot
    assert "retrieved_at" in snapshot
    assert "latest_closed_candle_time_utc" not in snapshot
    assert "latest_closed_candle_time" in snapshot


def test_bar_fields_no_utc_suffix():
    """Bar fields must not have _utc suffix."""
    builder = SnapshotBuilder()
    broker_now = datetime(2026, 7, 21, 14, 30, 0)
    snapshot = builder.build(VALID_CSV, "EURUSD", "H4", broker_now=broker_now)
    for bar in snapshot["bars"]:
        assert "open_time_utc" not in bar
        assert "open_time" in bar


def test_latest_closed_candle_time_matches_last_bar():
    """latest_closed_candle_time must equal the final bar open_time."""
    builder = SnapshotBuilder()
    snapshot = builder.build(VALID_CSV, "EURUSD", "H4", broker_now=datetime(2026, 7, 21, 14, 0))
    last_time = snapshot["bars"][-1]["open_time"]
    assert snapshot["latest_closed_candle_time"] == last_time


def test_no_dead_constants():
    """_ENGINE_ALLOWED_TOP_LEVEL and _ENGINE_ALLOWED_BAR must not exist (will be removed)."""
    import pytest

    import src.data.snapshot_builder as sb

    with pytest.raises(AttributeError):
        _ = sb._ENGINE_ALLOWED_TOP_LEVEL
    with pytest.raises(AttributeError):
        _ = sb._ENGINE_ALLOWED_BAR
