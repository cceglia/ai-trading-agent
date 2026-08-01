"""Tests for ResultWriter."""

import json
from datetime import datetime
from pathlib import Path

import pytest

from src.analysis.market_structure_engine.models import ReviewStatus
from src.decision.models import (
    BiasLevel,
    DecisionAction,
    DecisionOutput,
    MarketContextSummary,
    ReviewVerdict,
)
from src.output.result_models import AnalysisResult, OHLCBar, SLTPOverlay
from src.output.result_writer import ResultWriter, ResultWriterContractError


def _make_analysis_result(
    symbol: str = "XAUUSD",
    sl_tp_overlay: SLTPOverlay | None = None,
) -> AnalysisResult:
    """Create a minimal AnalysisResult for test result dicts."""
    return AnalysisResult(
        symbol=symbol,
        run_id=f"{symbol}-20260726083000",
        started_at=datetime(2026, 7, 26, 8, 30),
        completed_at=datetime(2026, 7, 26, 8, 31),
        status="success",
        sl_tp_overlay=sl_tp_overlay or SLTPOverlay(),
    )


class TestResultWriter:
    def test_path_construction(self, tmp_path: Path):
        writer = ResultWriter(tmp_path)
        path = writer._build_path("XAUUSD", datetime(2026, 7, 26, 8, 30))
        assert "XAUUSD" in str(path)
        assert "result-08.json" in str(path)

    def test_path_construction_has_dated_hierarchy(self, tmp_path: Path):
        writer = ResultWriter(tmp_path)
        path = writer._build_path("XAUUSD", datetime(2026, 7, 26, 8, 30))
        relative = path.relative_to(tmp_path)
        parts = relative.parts
        assert parts[0] == "2026"
        assert parts[1] == "07"
        assert parts[2] == "26"
        assert parts[3] == "XAUUSD"
        assert parts[4] == "result-08.json"

    def test_write_creates_directory_tree(self, tmp_path: Path):
        writer = ResultWriter(tmp_path)
        symbol = "XAUUSD"
        broker_now = datetime(2026, 7, 26, 8, 30)
        result: dict = {
            "market_context": MarketContextSummary(
                symbol="XAUUSD", bias=BiasLevel.BULLISH, confidence=75.0, reasoning="test"
            ),
            "decision": DecisionOutput(
                symbol="XAUUSD", action=DecisionAction.BUY_SETUP, reasoning="test"
            ),
            "review": ReviewVerdict(status=ReviewStatus.APPROVED, reasoning="test"),
            "analysis_result": _make_analysis_result(),
            "errors": [],
            "fatal_error": None,
        }
        ohlc: dict = {
            "D1": [
                OHLCBar(
                    time="2026-07-25T17:00",
                    open=2350.0,
                    high=2370.0,
                    low=2345.0,
                    close=2365.5,
                )
            ],
        }
        written = writer.write(symbol, result, ohlc, broker_now)
        assert written.exists()
        assert written.is_file()

    def test_write_produces_valid_json(self, tmp_path: Path):
        writer = ResultWriter(tmp_path)
        symbol = "XAUUSD"
        broker_now = datetime(2026, 7, 26, 8, 30)
        result: dict = {
            "market_context": MarketContextSummary(
                symbol="XAUUSD", bias=BiasLevel.BULLISH, confidence=75.0, reasoning="test"
            ),
            "decision": DecisionOutput(
                symbol="XAUUSD", action=DecisionAction.BUY_SETUP, reasoning="test"
            ),
            "review": ReviewVerdict(status=ReviewStatus.APPROVED, reasoning="test"),
            "analysis_result": _make_analysis_result(),
            "errors": [],
            "fatal_error": None,
        }
        ohlc: dict = {"D1": []}
        written = writer.write(symbol, result, ohlc, broker_now)
        with open(written) as f:
            data = json.load(f)
        assert data["symbol"] == "XAUUSD"
        assert data["version"] == "1.0"
        assert data["status"] == "success"

    def test_with_fatal_error_is_not_persisted(self, tmp_path: Path):
        writer = ResultWriter(tmp_path)
        symbol = "XAUUSD"
        broker_now = datetime(2026, 7, 26, 8, 30)
        result: dict = {
            "analysis_result": _make_analysis_result(),
            "errors": ["Something failed"],
            "fatal_error": "Critical failure",
        }
        ohlc: dict = {}
        written = writer.write(symbol, result, ohlc, broker_now)

        assert written is None
        assert not (tmp_path / "2026" / "07" / "26" / "XAUUSD").exists()

    def test_status_partial_with_errors(self, tmp_path: Path):
        """When there are errors but no fatal_error, status should be 'partial'."""
        writer = ResultWriter(tmp_path)
        symbol = "XAUUSD"
        broker_now = datetime(2026, 7, 26, 8, 30)
        result: dict = {
            "analysis_result": _make_analysis_result(),
            "errors": ["Non-fatal warning"],
            "fatal_error": None,
        }
        ohlc: dict = {}
        written = writer.write(symbol, result, ohlc, broker_now)
        with open(written) as f:
            data = json.load(f)
        assert data["status"] == "partial"
        assert data["fatal_error"] is None
        assert len(data["errors"]) == 1

    def test_ohlc_data_in_output(self, tmp_path: Path):
        """OHLC bars appear in the output JSON under 'ohlc'."""
        writer = ResultWriter(tmp_path)
        symbol = "XAUUSD"
        broker_now = datetime(2026, 7, 26, 8, 30)
        bar = OHLCBar(time="2026-07-25T17:00", open=2350.0, high=2370.0, low=2345.0, close=2365.5)
        result: dict = {
            "analysis_result": _make_analysis_result(),
            "errors": [],
            "fatal_error": None,
        }
        ohlc: dict = {"D1": [bar], "H4": [bar], "H1": []}
        written = writer.write(symbol, result, ohlc, broker_now)
        with open(written) as f:
            data = json.load(f)
        assert len(data["ohlc"]["D1"]) == 1
        assert len(data["ohlc"]["H4"]) == 1
        assert len(data["ohlc"]["H1"]) == 0
        assert data["ohlc"]["D1"][0]["open"] == 2350.0

    def test_raises_when_no_analysis_result(self, tmp_path: Path):
        """ResultWriterContractError when analysis_result is missing."""
        writer = ResultWriter(tmp_path)
        symbol = "XAUUSD"
        broker_now = datetime(2026, 7, 26, 8, 30)
        result: dict = {"errors": [], "fatal_error": None}
        ohlc: dict = {}
        with pytest.raises(ResultWriterContractError, match="AnalysisResult is required"):
            writer.write(symbol, result, ohlc, broker_now)

    def test_sl_tp_overlay_none_when_analysis_result_has_empty_overlay(self, tmp_path: Path):
        """SL/TP overlay fields are None when analysis_result has default SLTPOverlay."""
        writer = ResultWriter(tmp_path)
        symbol = "XAUUSD"
        broker_now = datetime(2026, 7, 26, 8, 30)
        result: dict = {
            "decision": DecisionOutput(
                symbol="XAUUSD",
                action=DecisionAction.BUY_SETUP,
                reasoning="test",
            ),
            "analysis_result": _make_analysis_result(),
            "errors": [],
            "fatal_error": None,
        }
        ohlc: dict = {}
        written = writer.write(symbol, result, ohlc, broker_now)
        with open(written) as f:
            data = json.load(f)
        assert data["sl_tp_overlay"]["entry_price"] is None
        assert data["sl_tp_overlay"]["stop_loss"] is None
        assert data["sl_tp_overlay"]["take_profit"] is None

    def test_sl_tp_overlay_from_analysis_result(self, tmp_path: Path):
        """SL/TP overlay values come from analysis_result.sl_tp_overlay."""
        writer = ResultWriter(tmp_path)
        symbol = "XAUUSD"
        broker_now = datetime(2026, 7, 26, 8, 30)
        overlay = SLTPOverlay(entry_price=1.1050, stop_loss=1.0950, take_profit=1.1200)
        result: dict = {
            "analysis_result": _make_analysis_result(sl_tp_overlay=overlay),
            "errors": [],
            "fatal_error": None,
        }
        ohlc: dict = {}
        written = writer.write(symbol, result, ohlc, broker_now)
        with open(written) as f:
            data = json.load(f)
        assert data["sl_tp_overlay"]["entry_price"] == 1.1050
        assert data["sl_tp_overlay"]["stop_loss"] == 1.0950
        assert data["sl_tp_overlay"]["take_profit"] == 1.1200

    def test_run_id_format(self, tmp_path: Path):
        """run_id should be formatted as YYYY-MM-DDTHH:MM:SS."""
        writer = ResultWriter(tmp_path)
        symbol = "XAUUSD"
        broker_now = datetime(2026, 7, 26, 8, 30)
        result: dict = {
            "analysis_result": _make_analysis_result(),
            "errors": [],
            "fatal_error": None,
        }
        ohlc: dict = {}
        written = writer.write(symbol, result, ohlc, broker_now)
        with open(written) as f:
            data = json.load(f)
        assert data["run_id"] == "2026-07-26T08:30:00"

    def test_review_status_in_json(self, tmp_path: Path):
        """Review verdict serializes status field (not approved boolean)."""
        writer = ResultWriter(tmp_path)
        symbol = "XAUUSD"
        broker_now = datetime(2026, 7, 26, 8, 30)
        result: dict = {
            "review": ReviewVerdict(
                status=ReviewStatus.APPROVED,
                reasoning="All checks pass",
                concerns=(),
            ),
            "analysis_result": _make_analysis_result(),
            "errors": [],
            "fatal_error": None,
        }
        ohlc: dict = {}
        written = writer.write(symbol, result, ohlc, broker_now)
        with open(written) as f:
            data = json.load(f)
        assert data["review"]["status"] == "APPROVED"
        assert data["review"]["reasoning"] == "All checks pass"
