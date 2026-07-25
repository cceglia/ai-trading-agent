"""Tests for engine field rename (no _utc suffix)."""


def test_validation_accepts_new_field_names():
    """_ALLOWED_TOP_LEVEL must accept retrieved_at, not retrieved_at_utc."""
    from src.analysis.market_structure_engine.validation import _ALLOWED_TOP_LEVEL

    assert "retrieved_at" in _ALLOWED_TOP_LEVEL
    assert "retrieved_at_utc" not in _ALLOWED_TOP_LEVEL
    assert "latest_closed_candle_time" in _ALLOWED_TOP_LEVEL
    assert "latest_closed_candle_time_utc" not in _ALLOWED_TOP_LEVEL


def test_validation_accepts_open_time():
    """_ALLOWED_BAR must accept open_time, not open_time_utc."""
    from src.analysis.market_structure_engine.validation import _ALLOWED_BAR

    assert "open_time" in _ALLOWED_BAR
    assert "open_time_utc" not in _ALLOWED_BAR


def test_swing_no_timestamp_utc():
    """Swing dataclass must have timestamp, not timestamp_utc."""
    from src.analysis.market_structure_engine.swings import Swing

    swing = Swing(
        swing_id="test",
        index=0,
        timestamp="2024-01-01T00:00:00",
        side="HIGH",
        price=1.0,
        classification="MAJOR",
        prominence_atr=1.0,
        plateau_start_index=0,
        plateau_end_index=0,
    )
    assert hasattr(swing, "timestamp")
    assert not hasattr(swing, "timestamp_utc")
    d = swing.to_dict()
    assert "timestamp" in d
    assert "timestamp_utc" not in d


def test_engine_source_audit_no_utc():
    """Engine source_audit must use latest_closed_candle_time, not _utc."""
    from src.analysis.market_structure_engine.engine import analyze_snapshot

    snapshot = {
        "source": {"type": "TRADINGVIEW_MCP"},
        "market": {"symbol": "XAUUSD", "provider": "MCP"},
        "requested_timeframe": "D1",
        "returned_timeframe": "D1",
        "retrieved_at": "2026-07-21T14:00:00",
        "latest_closed_candle_time": "2024-01-03T00:00:00",
        "candle_closure_verified": True,
        "bars": [
            {
                "open_time": "2024-01-01T00:00:00",
                "open": 1.0,
                "high": 1.1,
                "low": 0.9,
                "close": 1.05,
                "closed": True,
            },
            {
                "open_time": "2024-01-02T00:00:00",
                "open": 1.05,
                "high": 1.15,
                "low": 1.0,
                "close": 1.1,
                "closed": True,
            },
            {
                "open_time": "2024-01-03T00:00:00",
                "open": 1.1,
                "high": 1.2,
                "low": 1.05,
                "close": 1.15,
                "closed": True,
            },
        ],
    }
    result = analyze_snapshot(snapshot, profile_overrides={"minimum_bars": 3})
    audit = result["source_audit"]
    assert "latest_closed_candle_time" in audit
    assert "latest_closed_candle_time_utc" not in audit
    assert audit["latest_closed_candle_time"] == "2024-01-03T00:00:00"


def test_engine_export_includes_latest_close():
    """Engine must export scoring.latest_close, matching technical_context.close.

    The canonical current price is the close of the latest verified-closed bar.
    It must be present in the exported scoring dict and equal the close already
    exposed via technical_context (the latest bar snapshot). For the 3-bar
    fixture the latest close is 1.15.
    """
    from src.analysis.market_structure_engine.engine import analyze_snapshot

    snapshot = {
        "source": {"type": "TRADINGVIEW_MCP"},
        "market": {"symbol": "XAUUSD", "provider": "MCP"},
        "requested_timeframe": "D1",
        "returned_timeframe": "D1",
        "retrieved_at": "2026-07-21T14:00:00",
        "latest_closed_candle_time": "2024-01-03T00:00:00",
        "candle_closure_verified": True,
        "bars": [
            {
                "open_time": "2024-01-01T00:00:00",
                "open": 1.0,
                "high": 1.1,
                "low": 0.9,
                "close": 1.05,
                "closed": True,
            },
            {
                "open_time": "2024-01-02T00:00:00",
                "open": 1.05,
                "high": 1.15,
                "low": 1.0,
                "close": 1.1,
                "closed": True,
            },
            {
                "open_time": "2024-01-03T00:00:00",
                "open": 1.1,
                "high": 1.2,
                "low": 1.05,
                "close": 1.15,
                "closed": True,
            },
        ],
    }
    result = analyze_snapshot(snapshot, profile_overrides={"minimum_bars": 3})

    assert "latest_close" in result["scoring"]
    assert result["scoring"]["latest_close"] == result["technical_context"]["close"]
    assert result["scoring"]["latest_close"] == 1.15
