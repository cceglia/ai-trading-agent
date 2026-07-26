"""End-to-end integration test for the result JSON pipeline."""

import json
from datetime import datetime
from pathlib import Path

from src.decision.models import (
    BiasLevel,
    DecisionAction,
    DecisionOutput,
    MarketContextSummary,
    ReviewVerdict,
)
from src.output.result_models import OHLCBar
from src.output.result_writer import ResultWriter


def test_result_pipeline_writes_json(tmp_path: Path):
    """Full pipeline simulation writes valid JSON result."""
    from src.output.result_writer import ResultWriter

    symbol = "XAUUSD"
    broker_now = datetime(2026, 7, 26, 8, 30)

    # Create a realistic pipeline result dict (simulating TradingGraph.run() output)
    result = {
        "market_context": MarketContextSummary(
            symbol=symbol,
            bias=BiasLevel.BULLISH,
            confidence=75.0,
            reasoning="Bullish BOS on D1, HTF alignment supports longs.",
            key_levels=["2350.00", "2400.00"],
            structural_events=["Bullish BOS at 2350"],
            calendar_context="NFP next week — monitor volatility",
            current_price=2365.50,
            current_price_time="2026-07-26T08:29:00",
        ),
        "decision": DecisionOutput(
            symbol=symbol,
            action=DecisionAction.BUY_SETUP,
            entry_price=2368.00,
            stop_loss=2350.00,
            take_profit=2400.00,
            reasoning="Price at support with bullish confirmation.",
            risk_reward_ratio=1.78,
            entry_authorized=False,
        ),
        "review": ReviewVerdict(
            approved=True,
            reasoning="All checks pass.",
            concerns=[],
            suggested_improvements=None,
            risk_management_ok=True,
            htf_alignment_ok=True,
            calendar_clear=True,
        ),
        "errors": [],
        "fatal_error": None,
    }

    # Simulate OHLC data that would come from the OHLC cache/extractor
    ohlc = {
        "D1": [
            OHLCBar(time="2026-07-25T17:00", open=2350.0, high=2370.0, low=2345.0, close=2365.5),
        ],
        "H4": [
            OHLCBar(time="2026-07-25T16:00", open=2345.0, high=2365.0, low=2340.0, close=2360.0),
        ],
        "H1": [
            OHLCBar(time="2026-07-26T07:00", open=2360.0, high=2375.0, low=2358.0, close=2365.5),
            OHLCBar(time="2026-07-26T08:00", open=2365.5, high=2380.0, low=2363.0, close=2378.0),
        ],
    }

    # Write the result
    writer = ResultWriter(tmp_path)
    written = writer.write(symbol, result, ohlc, broker_now)

    # Verify
    assert written.exists(), "Result file was not written"
    assert written.is_file(), "Result path is not a file"

    with open(written) as f:
        data = json.load(f)

    # Check structure
    assert data["version"] == "1.0"
    assert data["symbol"] == "XAUUSD"
    assert data["status"] == "success"
    assert data["errors"] == []
    assert data["fatal_error"] is None

    # Check market_context
    assert data["market_context"]["bias"] == "bullish"
    assert data["market_context"]["confidence"] == 75.0
    assert data["market_context"]["current_price"] == 2365.5

    # Check decision
    assert data["decision"]["action"] == "buy_setup"
    assert data["decision"]["entry_price"] == 2368.0
    assert data["decision"]["stop_loss"] == 2350.0
    assert data["decision"]["take_profit"] == 2400.0
    assert data["decision"]["entry_authorized"] is False  # Critical invariant

    # Check review
    assert data["review"]["approved"] is True
    assert data["review"]["concerns"] == []

    # Check OHLC
    assert "ohlc" in data
    assert len(data["ohlc"]["D1"]) == 1
    assert len(data["ohlc"]["H4"]) == 1
    assert len(data["ohlc"]["H1"]) == 2
    assert data["ohlc"]["D1"][0]["open"] == 2350.0
    assert data["ohlc"]["D1"][0]["close"] == 2365.5

    # Check SL/TP overlay
    assert data["sl_tp_overlay"]["entry_price"] == 2368.0
    assert data["sl_tp_overlay"]["stop_loss"] == 2350.0
    assert data["sl_tp_overlay"]["take_profit"] == 2400.0

    # Check entry_authorized invariant via AnalysisResult model
    from src.output.result_models import AnalysisResult

    parsed = AnalysisResult.model_validate(data)
    assert parsed.decision is not None
    assert parsed.decision.entry_authorized is False


def test_result_with_fatal_error(tmp_path: Path):
    """Pipeline with fatal error produces valid error result."""
    writer = ResultWriter(tmp_path)
    symbol = "XAUUSD"
    broker_now = datetime(2026, 7, 26, 8, 30)

    result = {
        "errors": ["Data fetch failed for H1", "Calendar unavailable"],
        "fatal_error": "Cannot get broker time",
    }
    ohlc = {}

    written = writer.write(symbol, result, ohlc, broker_now)
    with open(written) as f:
        data = json.load(f)

    assert data["symbol"] == "XAUUSD"
    assert data["status"] == "error"
    assert data["fatal_error"] == "Cannot get broker time"
    assert len(data["errors"]) == 2
    assert data["decision"] is None
    assert data["market_context"] is None
    assert data["review"] is None


def test_empty_ohlc_defaults(tmp_path: Path):
    """Result with no OHLC data produces empty arrays."""
    writer = ResultWriter(tmp_path)
    symbol = "EURUSD"
    broker_now = datetime(2026, 7, 26, 10, 0)

    result = {
        "market_context": MarketContextSummary(
            symbol=symbol, bias=BiasLevel.NEUTRAL, confidence=50.0, reasoning="test"
        ),
        "decision": DecisionOutput(symbol=symbol, action=DecisionAction.NO_TRADE, reasoning="test"),
        "errors": [],
        "fatal_error": None,
    }
    ohlc = {"D1": [], "H4": [], "H1": []}

    written = writer.write(symbol, result, ohlc, broker_now)
    with open(written) as f:
        data = json.load(f)

    assert data["ohlc"]["D1"] == []
    assert data["ohlc"]["H4"] == []
    assert data["ohlc"]["H1"] == []
