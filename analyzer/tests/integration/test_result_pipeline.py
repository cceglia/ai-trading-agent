"""End-to-end persistence tests for the canonical deterministic output."""

import json
from datetime import datetime
from pathlib import Path

from src.analysis.market_structure_engine.models import BiasLevel
from src.decision.models import DecisionAction, DecisionOutput, MarketContextSummary
from src.output.result_models import AnalysisResult, OHLCBar, SLTPOverlay
from src.output.result_writer import ResultWriter


def test_result_pipeline_writes_canonical_json(tmp_path: Path):
    now = datetime(2026, 7, 26, 8, 30)
    analysis_result = AnalysisResult(
        symbol="XAUUSD",
        run_id="XAUUSD-20260726083000",
        started_at=now,
        completed_at=now,
        status="success",
        sl_tp_overlay=SLTPOverlay(entry_price=1.101, stop_loss=1.098, take_profit=1.11),
        validation_status="VALID",
        setup_status="VALID",
        direction="BULLISH",
        entry_authorized=False,
    )
    result = {
        "market_context": MarketContextSummary(
            symbol="XAUUSD", bias=BiasLevel.BULLISH, confidence=75, reasoning="deterministic facts"
        ),
        "decision": DecisionOutput(
            symbol="XAUUSD", action=DecisionAction.NO_TRADE, reasoning="advisory context"
        ),
        "analysis_result": analysis_result,
        "errors": [],
        "fatal_error": None,
    }
    written = ResultWriter(tmp_path).write(
        "XAUUSD", result, {"D1": [OHLCBar(time="t", open=1, high=2, low=0, close=1)]}, now
    )
    data = json.loads(written.read_text())
    assert data["validation_status"] == "VALID"
    assert data["entry_authorized"] is False
    assert "review" not in data
    assert data["ohlc"]["D1"][0]["close"] == 1.0
