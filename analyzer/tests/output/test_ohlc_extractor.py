"""Tests for OHLC extractor."""

import pytest

from src.output.ohlc_extractor import extract_ohlc_from_all_timeframes, extract_ohlc_from_csv

VALID_CSV = """time,open,high,low,close,tick_volume,spread,real_volume
2026-07-25T17:00,2350.0,2370.0,2345.0,2365.5,100,0,0
2026-07-25T18:00,2365.0,2380.0,2355.0,2375.0,120,0,0
2026-07-25T19:00,2375.0,2390.0,2360.0,2385.0,110,0,0
"""


class TestExtractOhlcFromCsv:
    def test_parses_three_bars(self):
        bars = extract_ohlc_from_csv(VALID_CSV)
        assert len(bars) == 3
        assert bars[0].open == 2350.0
        assert bars[0].close == 2365.5
        assert bars[2].high == 2390.0

    def test_empty_csv_raises(self):
        with pytest.raises(ValueError, match="Empty CSV"):
            extract_ohlc_from_csv("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError, match="Empty CSV"):
            extract_ohlc_from_csv("   \n\n  ")

    def test_header_only_raises(self):
        with pytest.raises(ValueError, match="No valid bars found in CSV"):
            extract_ohlc_from_csv("time,open,high,low,close,tick_volume,spread,real_volume\n")

    def test_malformed_rows_skipped(self):
        csv_data = """time,open,high,low,close,tick_volume,spread,real_volume
2026-07-25T17:00,2350.0,2370.0,2345.0,2365.5,100,0,0
missing,data,here
2026-07-25T19:00,2375.0,2390.0,2360.0,2385.0,110,0,0
"""
        bars = extract_ohlc_from_csv(csv_data)
        assert len(bars) == 2  # middle row skipped

    def test_inconsistent_high_skipped(self):
        """Row where high < max(open, close, low) is skipped."""
        csv_data = """time,open,high,low,close,tick_volume,spread,real_volume
2026-07-25T17:00,2350.0,2300.0,2345.0,2365.5,100,0,0
2026-07-25T18:00,2365.0,2380.0,2355.0,2375.0,120,0,0
"""
        bars = extract_ohlc_from_csv(csv_data)
        assert len(bars) == 1  # first row has high < open

    def test_inconsistent_low_skipped(self):
        """Row where low > min(open, close, high) is skipped."""
        csv_data = """time,open,high,low,close,tick_volume,spread,real_volume
2026-07-25T17:00,2350.0,2370.0,2400.0,2365.5,100,0,0
2026-07-25T18:00,2365.0,2380.0,2355.0,2375.0,120,0,0
"""
        bars = extract_ohlc_from_csv(csv_data)
        assert len(bars) == 1  # first row has low > high

    def test_terminal_date_format(self):
        """Terminal date format YYYY.MM.DD HH:MM:SS is normalised to ISO-8601."""
        csv_data = """time,open,high,low,close,tick_volume,spread,real_volume
2026.07.25 17:00,2350.0,2370.0,2345.0,2365.5,100,0,0
"""
        bars = extract_ohlc_from_csv(csv_data)
        assert len(bars) == 1
        assert bars[0].time == "2026-07-25T17:00"

    def test_negative_values_float(self):
        """Negative OHLC values are valid floats."""
        csv_data = """time,open,high,low,close,tick_volume,spread,real_volume
2026-07-25T17:00,-2350.0,-2340.0,-2370.0,-2365.5,100,0,0
"""
        bars = extract_ohlc_from_csv(csv_data)
        assert len(bars) == 1
        assert bars[0].open == -2350.0

    def test_missing_time_skipped(self):
        """Row with missing time column is skipped."""
        csv_data = """time,open,high,low,close,tick_volume,spread,real_volume
,2350.0,2370.0,2345.0,2365.5,100,0,0
2026-07-25T18:00,2365.0,2380.0,2355.0,2375.0,120,0,0
"""
        bars = extract_ohlc_from_csv(csv_data)
        assert len(bars) == 1


class TestExtractOhlcFromAllTimeframes:
    def test_returns_dict_keyed_by_timeframe(self):
        csv_map = {
            "D1": VALID_CSV,
            "H4": VALID_CSV,
            "H1": VALID_CSV,
        }
        result = extract_ohlc_from_all_timeframes(csv_map)
        assert set(result.keys()) == {"D1", "H4", "H1"}
        assert len(result["D1"]) == 3
        assert len(result["H4"]) == 3
        assert len(result["H1"]) == 3

    def test_empty_timeframe_map(self):
        result = extract_ohlc_from_all_timeframes({})
        assert result == {}

    def test_one_timeframe(self):
        csv_map = {"H1": VALID_CSV}
        result = extract_ohlc_from_all_timeframes(csv_map)
        assert list(result.keys()) == ["H1"]
        assert len(result["H1"]) == 3

    def test_propagates_parse_errors(self):
        """An empty CSV in any timeframe propagates ValueError."""
        csv_map = {
            "D1": VALID_CSV,
            "H4": "",
        }
        with pytest.raises(ValueError, match="Empty CSV"):
            extract_ohlc_from_all_timeframes(csv_map)
