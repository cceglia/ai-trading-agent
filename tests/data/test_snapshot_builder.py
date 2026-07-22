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
            "retrieved_at_utc",
            "latest_closed_candle_time_utc",
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
        times = [b["open_time_utc"] for b in snapshot["bars"]]
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
        csv = (
            "time,open,high,low,close\n"
            "2024-01-01T00:00:00,1.0900,1.0850,1.0800,1.0875\n"
        )
        builder = SnapshotBuilder()
        with pytest.raises(ValueError, match="No valid bars found"):
            builder.build(csv, "EURUSD", "H4")

    def test_low_inconsistent_with_ohlc_skips_bar(self):
        csv = (
            "time,open,high,low,close\n"
            "2024-01-01T00:00:00,1.0850,1.0900,1.0950,1.0875\n"
        )
        builder = SnapshotBuilder()
        with pytest.raises(ValueError, match="No valid bars found"):
            builder.build(csv, "EURUSD", "H4")
