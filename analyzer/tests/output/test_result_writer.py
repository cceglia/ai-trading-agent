"""Tests for ResultWriter (schema-v2 nested envelope persistence)."""

import json
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.decision.models import (
    BiasLevel,
    DecisionAction,
    DecisionOutput,
    MarketContextSummary,
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


def _write(writer: ResultWriter, result: dict, ohlc: dict | None = None, **kw):
    """Convenience wrapper around ResultWriter.write."""
    broker_now = kw.pop("broker_now", datetime(2026, 7, 26, 8, 30))
    return writer.write(result.pop("_symbol", "XAUUSD"), result, ohlc or {}, broker_now)


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

    def test_write_produces_nested_v2_json(self, tmp_path: Path):
        """TEST-013 / AC-013: persisted output is a nested schema-v2 envelope
        with no review fields."""
        writer = ResultWriter(tmp_path)
        result: dict = {
            "market_context": MarketContextSummary(
                symbol="XAUUSD", bias=BiasLevel.BULLISH, confidence=75.0, reasoning="test"
            ),
            "decision": DecisionOutput(
                symbol="XAUUSD", action=DecisionAction.BUY_SETUP, reasoning="test"
            ),
            "analysis_result": _make_analysis_result(),
            "errors": [],
            "fatal_error": None,
        }
        written = writer.write("XAUUSD", result, {"D1": []}, datetime(2026, 7, 26, 8, 30))
        with open(written) as f:
            data = json.load(f)
        assert data["schema_version"] == "2"
        assert data["status"] == "partial"
        assert "deterministic_facts" in data
        assert "decision" in data
        assert "synthesis" in data
        assert "review" not in data
        assert "reviewer" not in json.dumps(data)

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

    def test_preserves_degraded_status_when_errors_empty(self, tmp_path: Path):
        """A degraded analysis (synthesis failure, valid facts) must not be
        rewritten as 'success' just because the errors list is empty."""
        degraded = AnalysisResult(
            symbol="XAUUSD",
            run_id="XAUUSD-20260726083000",
            started_at=datetime(2026, 7, 26, 8, 30),
            completed_at=datetime(2026, 7, 26, 8, 31),
            status="degraded",
            validation_status="VALID",
            setup_status="READY",
            operational=True,
            synthesis_status="FAILED",
            synthesis_error="SYNTHESIS_UNAVAILABLE",
            sl_tp_overlay=SLTPOverlay(),
        )
        written = ResultWriter(tmp_path).write(
            "XAUUSD",
            {"analysis_result": degraded, "errors": [], "fatal_error": None},
            {},
            datetime(2026, 7, 26, 8, 30),
        )
        data = json.loads(written.read_text())
        assert data["status"] == "degraded"
        assert data["synthesis"]["status"] == "FAILED"
        assert data["synthesis"]["error"] == "SYNTHESIS_UNAVAILABLE"
        assert data["synthesis"]["explanation"] is None

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

    def test_entry_plan_none_when_analysis_result_has_empty_overlay(self, tmp_path: Path):
        """Entry-plan fields are None when analysis_result has default SLTPOverlay."""
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
        entry_plan = data["deterministic_facts"]["entry_plan"]
        assert entry_plan["entry_price"] is None
        assert entry_plan["invalidation_price"] is None
        assert entry_plan["target_price"] is None

    def test_entry_plan_from_analysis_result(self, tmp_path: Path):
        """Entry-plan values come from analysis_result.sl_tp_overlay."""
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
        entry_plan = data["deterministic_facts"]["entry_plan"]
        assert entry_plan["entry_price"] == 1.1050
        assert entry_plan["invalidation_price"] == 1.0950
        assert entry_plan["target_price"] == 1.1200

    def test_preserves_complete_deterministic_contract(self, tmp_path: Path):
        analysis_result = AnalysisResult(
            symbol="XAUUSD",
            run_id="run",
            started_at=datetime(2026, 7, 26, 8, 30),
            completed_at=datetime(2026, 7, 26, 8, 31),
            status="success",
            sl_tp_overlay=SLTPOverlay(entry_price=2400.0, stop_loss=2380.0, take_profit=2440.0),
            setup_grade="AAA",
            setup_classification_status="CLASSIFIED",
            setup_lifecycle_status="TRIGGERED",
            trade_direction="BULLISH",
            estimated_reward_risk=2.0,
            order_type="STOP",
            risk_multiplier=1.0,
            final_risk_percentage=1.0,
            execution_status="ACTIONABLE",
            final_action="buy_setup",
            validation_status="VALID",
            setup_status="READY",
            direction="LONG",
            operational=True,
            reason_codes=["VALID_SETUP"],
        )
        written = ResultWriter(tmp_path).write(
            "XAUUSD",
            {"analysis_result": analysis_result, "errors": [], "fatal_error": None},
            {},
            datetime(2026, 7, 26, 8, 30),
        )
        data = json.loads(written.read_text())
        facts = data["deterministic_facts"]
        assert facts["entry_plan"]["entry_type"] == "STOP"
        assert facts["entry_plan"]["estimated_reward_risk"] == 2.0
        assert facts["policy"]["execution_status"] == "ACTIONABLE"
        assert facts["policy"]["actionable"] is True
        assert facts["policy"]["reason_codes"] == ["VALID_SETUP"]
        assert facts["setup_grade"] == "AAA"
        assert facts["setup_classification_status"] == "CLASSIFIED"
        assert facts["setup_lifecycle_status"] == "TRIGGERED"
        assert facts["trade_direction"] == "BULLISH"
        assert data["decision"]["action"] == "buy_setup"

    @pytest.mark.parametrize("as_object", [False, True])
    def test_preserves_dict_and_object_analysis_results(
        self, tmp_path: Path, as_object: bool
    ) -> None:
        source = _make_analysis_result().model_copy(
            update={
                "setup_grade": "AAA",
                "order_type": "STOP",
                "execution_status": "BLOCKED_BY_DATA_QUALITY",
                "final_action": "no_trade",
                "deterministic_setup_complete": False,
            }
        )
        raw = source.model_dump(mode="json")
        analysis_result: object = SimpleNamespace(**raw) if as_object else raw

        written = ResultWriter(tmp_path).write(
            "XAUUSD",
            {"analysis_result": analysis_result, "errors": [], "fatal_error": None},
            {},
            datetime(2026, 7, 26, 8, 30),
        )
        data = json.loads(written.read_text())
        facts = data["deterministic_facts"]
        assert facts["setup_grade"] == "AAA"
        assert facts["entry_plan"]["entry_type"] == "STOP"
        assert facts["policy"]["execution_status"] == "BLOCKED_BY_DATA_QUALITY"
        assert data["decision"]["action"] == "no_trade"
        assert facts["setup_classification_status"] == "NO_SETUP"

    def test_invalid_analysis_result_fails_without_creating_output(self, tmp_path: Path) -> None:
        with pytest.raises(ResultWriterContractError, match="does not satisfy"):
            ResultWriter(tmp_path).write(
                "XAUUSD",
                {"analysis_result": {"setup_grade": "AAA"}, "errors": [], "fatal_error": None},
                {},
                datetime(2026, 7, 26, 8, 30),
            )
        assert not list(tmp_path.iterdir())

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

    def test_deterministic_validation_fields_are_persisted(self, tmp_path: Path):
        result = _make_analysis_result().model_copy(
            update={
                "validation_status": "VALID",
                "entry_authorized": False,
                "reason_codes": ["VALID_SETUP"],
            }
        )
        written = ResultWriter(tmp_path).write(
            "XAUUSD",
            {"analysis_result": result, "errors": [], "fatal_error": None},
            {},
            datetime(2026, 7, 26, 8, 30),
        )
        data = json.loads(written.read_text())
        facts = data["deterministic_facts"]
        assert facts["validation_status"] == "VALID"
        assert facts["entry_authorized"] is False


class TestInvalidPersistence:
    """FR-031 / INV-011: INVALID persists as partial; fatal does not."""

    def test_invalid_run_persists_partial_no_trade_non_operational(self, tmp_path: Path):
        invalid = _make_analysis_result().model_copy(
            update={
                "validation_status": "INVALID",
                "setup_status": "INVALID",
                "direction": "NONE",
                "operational": False,
                "final_action": "no_trade",
                "status": "partial",
                "validation_errors": ["INVARIANT_VIOLATION"],
            }
        )
        written = ResultWriter(tmp_path).write(
            "XAUUSD",
            {"analysis_result": invalid, "errors": [], "fatal_error": None},
            {},
            datetime(2026, 7, 26, 8, 30),
        )
        assert written is not None
        data = json.loads(written.read_text())
        assert data["status"] == "partial"
        facts = data["deterministic_facts"]
        assert facts["validation_status"] == "INVALID"
        assert facts["setup_status"] == "INVALID"
        assert facts["operational"] is False
        assert facts["entry_authorized"] is False
        assert data["decision"]["action"] == "no_trade"
        assert facts["validation_errors"] == ["INVARIANT_VIOLATION"]

    def test_fatal_run_leaves_no_file_and_no_temp(self, tmp_path: Path):
        written = ResultWriter(tmp_path).write(
            "XAUUSD",
            {
                "analysis_result": _make_analysis_result(),
                "errors": ["terminal"],
                "fatal_error": "FATAL_DATA_FETCH",
            },
            {},
            datetime(2026, 7, 26, 8, 30),
        )
        assert written is None
        assert not (tmp_path / "2026").exists()
        assert list(tmp_path.iterdir()) == []

    def test_envelope_validation_failure_persists_nothing(self, tmp_path: Path):
        """A decision action outside the v2 enum must be rejected before any
        file (or temp file) is created."""
        bad = _make_analysis_result().model_copy(
            update={"final_action": "frobnicate", "status": "success"}
        )
        with pytest.raises(ResultWriterContractError, match="decision action"):
            ResultWriter(tmp_path).write(
                "XAUUSD",
                {"analysis_result": bad, "errors": [], "fatal_error": None},
                {},
                datetime(2026, 7, 26, 8, 30),
            )
        assert not list(tmp_path.iterdir())


class TestAtomicWrite:
    """FR-031 / Section 13: temp-file + atomic replace + cleanup."""

    def test_failed_replace_leaves_no_final_or_temp_file(self, tmp_path: Path, monkeypatch):
        writer = ResultWriter(tmp_path)

        import src.output.result_writer as writer_mod

        def _boom(*args, **kwargs):
            raise OSError("disk full")

        monkeypatch.setattr(writer_mod.os, "replace", _boom)
        with pytest.raises(ResultWriterContractError, match="persist"):
            writer.write(
                "XAUUSD",
                {"analysis_result": _make_analysis_result(), "errors": [], "fatal_error": None},
                {},
                datetime(2026, 7, 26, 8, 30),
            )
        # No final file and no leftover temp files anywhere under base_dir.
        assert list(tmp_path.rglob("*.json")) == []
        assert list(tmp_path.rglob("*.tmp")) == []
        assert list(tmp_path.rglob(".*.tmp")) == []

    def test_success_leaves_no_temp_files(self, tmp_path: Path):
        written = ResultWriter(tmp_path).write(
            "XAUUSD",
            {"analysis_result": _make_analysis_result(), "errors": [], "fatal_error": None},
            {},
            datetime(2026, 7, 26, 8, 30),
        )
        assert written.exists()
        assert list(tmp_path.rglob("*.tmp")) == []
        assert list(tmp_path.rglob(".*.tmp")) == []

    def test_same_hour_overwrite_is_atomic(self, tmp_path: Path):
        """Overwriting an existing same-hour file replaces it atomically."""
        writer = ResultWriter(tmp_path)
        now = datetime(2026, 7, 26, 8, 30)
        writer.write(
            "XAUUSD",
            {"analysis_result": _make_analysis_result(), "errors": [], "fatal_error": None},
            {},
            now,
        )
        first = (tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08.json").read_text()
        newer = _make_analysis_result().model_copy(
            update={"run_id": "XAUUSD-2", "status": "success", "validation_status": "VALID"}
        )
        writer.write(
            "XAUUSD",
            {"analysis_result": newer, "errors": [], "fatal_error": None},
            {},
            datetime(2026, 7, 26, 8, 45),
        )
        path = tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08.json"
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["run_id"] == "2026-07-26T08:45:00"
        assert data["deterministic_facts"]["validation_status"] == "VALID"
        assert json.loads(first)["run_id"] == "2026-07-26T08:30:00"


class TestCompactFacts:
    """Deterministic facts derived from structure_analysis stay compact and
    bounded (NFR-003 / FR-010 / FR-011)."""

    def _structure(self) -> dict:
        events = [{"event_id": f"e{i}", "type": "BULLISH_BOS", "event_index": i} for i in range(60)]
        liquidity = [{"pool_id": f"p{i}", "state": "INTACT", "event_index": i} for i in range(60)]
        return {
            "_full_multi_timeframe": {
                "timeframes": {
                    "D1": {"market_structure": {"regime": "RANGE"}},
                    "H4": {},
                    "H1": {
                        "source_audit": {"latest_closed_candle_time": "2026-07-26T08:00:00"},
                        "scoring": {"confidence_score": 72.0, "confidence_components": {}},
                        "market_structure": {"regime": "BULLISH"},
                        "events": {
                            "latest_material_event": {"type": "BULLISH_BOS", "event_index": 59},
                            "event_history": events,
                            "failed_breakouts": [],
                        },
                        "liquidity": {
                            "current_state": {"pool_id": "p3", "state": "SWEPT"},
                            "event_history": liquidity,
                        },
                        "levels": {"nearest_support": {"price": 1.1}},
                        "swings": [{"huge": "payload"}],
                    },
                }
            }
        }

    def test_compact_facts_are_bounded_and_skip_swings(self, tmp_path: Path):
        result: dict = {
            "analysis_result": _make_analysis_result(),
            "errors": [],
            "fatal_error": None,
            "structure_analysis": self._structure(),
        }
        written = ResultWriter(tmp_path).write("XAUUSD", result, {}, datetime(2026, 7, 26, 8, 30))
        data = json.loads(written.read_text())
        facts = data["deterministic_facts"]

        assert set(facts["timeframes"]) == {"D1", "H4", "H1"}
        # Raw swings must never be persisted (DEC-011).
        assert "swings" not in json.dumps(facts["timeframes"])

        h1 = facts["timeframes"]["H1"]
        assert h1["scoring"]["confidence_score"] == 72.0
        assert h1["market_structure"]["regime"] == "BULLISH"
        # Bounded event/liquidity history (NFR-003).
        assert len(h1["events"]["event_history"]) == 50
        assert len(h1["liquidity"]["event_history"]) == 50

        assert facts["latest_structural_events"]["H1"]["event_index"] == 59
        assert facts["latest_liquidity_states"]["H1"]["state"] == "SWEPT"
        assert facts["event_history"]["H1"][-1]["event_index"] == 59
        assert facts["liquidity_history"]["H1"][-1]["event_index"] == 59
        assert facts["selected_levels"]["H1"]["nearest_support"]["price"] == 1.1
        # Deterministic confidence projected from H1 scoring.
        assert facts["confidence"] == 72.0
        assert facts["bias"] == "NEUTRAL"

    def test_no_structure_analysis_yields_empty_timeframes(self, tmp_path: Path):
        result: dict = {
            "analysis_result": _make_analysis_result(),
            "errors": [],
            "fatal_error": None,
        }
        written = ResultWriter(tmp_path).write("XAUUSD", result, {}, datetime(2026, 7, 26, 8, 30))
        data = json.loads(written.read_text())
        facts = data["deterministic_facts"]
        assert facts["timeframes"] == {}
        assert facts["confidence_components"] == {}
        assert facts["event_history"] == {}


class TestCompletionLog:
    """The completion log carries required diagnostic fields without secrets."""

    def test_completion_log_includes_required_diagnostics(self, tmp_path: Path, caplog):
        import logging

        result: dict = {
            "analysis_result": _make_analysis_result(),
            "errors": [],
            "fatal_error": None,
        }
        with caplog.at_level(logging.INFO, logger="src.output.result_writer"):
            ResultWriter(tmp_path).write("XAUUSD", result, {"D1": []}, datetime(2026, 7, 26, 8, 30))
        matches = [
            record
            for record in caplog.records
            if record.getMessage().startswith("Wrote analysis result for")
        ]
        assert matches
        line = matches[0].getMessage()
        # Required diagnostic fields (NFR §18): symbol, run_id, schema version,
        # validation/setup status, action, synthesis/execution status, and a
        # stable error-code slot.
        assert "XAUUSD" in line
        assert "schema_version=2" in line
        assert "validation_status=" in line
        assert "setup_status=" in line
        assert "action=" in line
        assert "synthesis_status=" in line
        assert "execution_status=" in line
        assert "error_codes=" in line
        assert "run_id=" in line

    def test_error_codes_slot_is_bounded_and_empty_for_success(self, tmp_path: Path, caplog):
        import logging

        result: dict = {
            "analysis_result": _make_analysis_result(),
            "errors": [],
            "fatal_error": None,
        }
        with caplog.at_level(logging.INFO, logger="src.output.result_writer"):
            ResultWriter(tmp_path).write("XAUUSD", result, {"D1": []}, datetime(2026, 7, 26, 8, 30))
        line = [
            record.getMessage()
            for record in caplog.records
            if record.getMessage().startswith("Wrote analysis result for")
        ][0]
        assert "error_codes=-" in line
