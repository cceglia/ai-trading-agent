"""Tests for output result models."""

import json
from datetime import datetime

import pytest
from pydantic import ValidationError

from src.decision.models import (
    BiasLevel,
    DecisionAction,
    DecisionOutput,
    MarketContextSummary,
)
from src.output.result_models import (
    AnalysisEnvelope,
    AnalysisResult,
    DecisionBlock,
    DeterministicFacts,
    OHLCBar,
    OHLCData,
    SLTPOverlay,
    SynthesisBlock,
)


class TestOHLCBar:
    def test_create(self):
        bar = OHLCBar(time="2026-07-25T17:00", open=2350.0, high=2370.0, low=2345.0, close=2365.5)
        assert bar.time == "2026-07-25T17:00"
        assert bar.open == 2350.0
        assert bar.high == 2370.0
        assert bar.low == 2345.0
        assert bar.close == 2365.5

    def test_float_coercion(self):
        """ints passed to float fields are promoted to float."""
        bar = OHLCBar(time="t", open=1, high=2, low=3, close=4)
        assert isinstance(bar.open, float)
        assert bar.open == 1.0


class TestOHLCData:
    def test_default_empty_lists(self):
        data = OHLCData()
        assert data.D1 == []
        assert data.H4 == []
        assert data.H1 == []

    def test_with_bars(self):
        bar = OHLCBar(time="2026-07-25T17:00", open=2350.0, high=2370.0, low=2345.0, close=2365.5)
        data = OHLCData(D1=[bar])
        assert len(data.D1) == 1
        assert data.H4 == []
        assert data.H1 == []


class TestSLTPOverlay:
    def test_default_nulls(self):
        overlay = SLTPOverlay()
        assert overlay.entry_price is None
        assert overlay.stop_loss is None
        assert overlay.take_profit is None

    def test_with_values(self):
        overlay = SLTPOverlay(entry_price=2350.0, stop_loss=2340.0, take_profit=2380.0)
        assert overlay.entry_price == 2350.0
        assert overlay.stop_loss == 2340.0
        assert overlay.take_profit == 2380.0


class TestAnalysisResult:
    def test_version_default(self):
        result = AnalysisResult(
            symbol="XAUUSD",
            run_id="test",
            started_at=datetime.now(),
            completed_at=datetime.now(),
            status="success",
        )
        assert result.version == "2.0"

    def test_with_market_context(self):
        ctx = MarketContextSummary(
            symbol="XAUUSD", bias=BiasLevel.BULLISH, confidence=75.0, reasoning="test"
        )
        result = AnalysisResult(
            symbol="XAUUSD",
            run_id="test",
            started_at=datetime.now(),
            completed_at=datetime.now(),
            status="success",
            market_context=ctx,
        )
        assert result.market_context is not None
        assert result.market_context.bias == "BULLISH"

    def test_with_decision(self):
        dec = DecisionOutput(symbol="XAUUSD", action=DecisionAction.BUY_SETUP, reasoning="test")
        result = AnalysisResult(
            symbol="XAUUSD",
            run_id="test",
            started_at=datetime.now(),
            completed_at=datetime.now(),
            status="success",
            decision=dec,
        )
        assert result.decision is not None
        assert result.decision.action == "buy_setup"

    def test_deterministic_validation_defaults_are_safe(self):
        result = AnalysisResult(
            symbol="XAUUSD",
            run_id="test",
            started_at=datetime.now(),
            completed_at=datetime.now(),
            status="success",
        )
        assert result.validation_status == "INVALID"
        assert result.entry_authorized is False

    def test_serialization_roundtrip(self):
        ctx = MarketContextSummary(
            symbol="XAUUSD", bias=BiasLevel.BULLISH, confidence=75.0, reasoning="test"
        )
        result = AnalysisResult(
            symbol="XAUUSD",
            run_id="test",
            started_at=datetime.now(),
            completed_at=datetime.now(),
            status="success",
            market_context=ctx,
        )
        serialized = result.model_dump(mode="json")
        deserialized = AnalysisResult.model_validate(serialized)
        assert deserialized.symbol == "XAUUSD"
        assert deserialized.version == "2.0"
        assert deserialized.market_context is not None

    def test_status_enum_values(self):
        result = AnalysisResult(
            symbol="XAUUSD",
            run_id="test",
            started_at=datetime.now(),
            completed_at=datetime.now(),
            status="success",
        )
        assert result.status == "success"

    def test_fatal_error_and_errors(self):
        result = AnalysisResult(
            symbol="XAUUSD",
            run_id="test",
            started_at=datetime.now(),
            completed_at=datetime.now(),
            status="error",
            errors=["Something went wrong"],
            fatal_error="Critical failure",
        )
        assert len(result.errors) == 1
        assert result.fatal_error == "Critical failure"

    def test_ohlc_and_sl_tp_defaults(self):
        result = AnalysisResult(
            symbol="XAUUSD",
            run_id="test",
            started_at=datetime.now(),
            completed_at=datetime.now(),
            status="success",
        )
        assert result.ohlc.D1 == []
        assert result.ohlc.H4 == []
        assert result.ohlc.H1 == []
        assert result.sl_tp_overlay.entry_price is None

    def test_all_fields_populated(self):
        """Full-featured AnalysisResult with all optional fields set."""
        now = datetime.now()
        ctx = MarketContextSummary(
            symbol="XAUUSD", bias=BiasLevel.BULLISH, confidence=80.0, reasoning="Strong trend"
        )
        dec = DecisionOutput(
            symbol="XAUUSD",
            action=DecisionAction.BUY_SETUP,
            reasoning="Good R/R",
        )
        ohlc = OHLCData(
            D1=[
                OHLCBar(time="2026-07-25T17:00", open=2350.0, high=2370.0, low=2345.0, close=2365.5)
            ],
        )
        sltp = SLTPOverlay(entry_price=2350.0, stop_loss=2320.0, take_profit=2410.0)

        result = AnalysisResult(
            version="2.0",
            symbol="XAUUSD",
            run_id="full-test",
            started_at=now,
            completed_at=now,
            status="success",
            errors=[],
            fatal_error=None,
            market_context=ctx,
            decision=dec,
            ohlc=ohlc,
            sl_tp_overlay=sltp,
        )

        assert result.version == "2.0"
        assert result.market_context.bias == "BULLISH"
        assert result.decision.action == "buy_setup"
        assert result.entry_authorized is False
        assert len(result.ohlc.D1) == 1
        assert result.sl_tp_overlay.entry_price == 2350.0


class TestRejectionCodes:
    """rejection_codes must survive model_dump() round-trip."""

    def test_rejection_codes_in_serialized_output(self):
        result = AnalysisResult(
            symbol="EURUSD",
            run_id="test-001",
            started_at=datetime.now(),
            completed_at=datetime.now(),
            status="success",
            rejection_codes=["INVALID_TRADE_DIRECTION"],
        )
        payload = result.model_dump(mode="json")
        assert payload["rejection_codes"] == ["INVALID_TRADE_DIRECTION"]

    def test_rejection_codes_defaults_to_empty_list(self):
        result = AnalysisResult(
            symbol="EURUSD",
            run_id="test-002",
            started_at=datetime.now(),
            completed_at=datetime.now(),
            status="success",
        )
        payload = result.model_dump(mode="json")
        assert payload["rejection_codes"] == []

    def test_rejection_codes_round_trip(self):
        result = AnalysisResult(
            symbol="EURUSD",
            run_id="test-003",
            started_at=datetime.now(),
            completed_at=datetime.now(),
            status="success",
            rejection_codes=["INVALID_TRADE_DIRECTION", "INSUFFICIENT_DATA"],
        )
        payload = result.model_dump(mode="json")
        restored = AnalysisResult.model_validate(payload)
        assert restored.rejection_codes == ["INVALID_TRADE_DIRECTION", "INSUFFICIENT_DATA"]


class TestV2Envelope:
    """Nested schema-v2 envelope contract (TEST-013 / AC-013, INV-015)."""

    def _minimal_env(self, **overrides) -> AnalysisEnvelope:
        data = dict(
            symbol="XAUUSD",
            run_id="2026-08-07T13:00:00",
            started_at=datetime(2026, 8, 7, 13, 0),
            completed_at=datetime(2026, 8, 7, 13, 1),
            status="degraded",
            deterministic_facts=DeterministicFacts(symbol="XAUUSD"),
            decision=DecisionBlock(action="buy_setup"),
            synthesis=SynthesisBlock(
                status="FAILED",
                explanation=None,
                error="SYNTHESIS_UNAVAILABLE",
            ),
        )
        data.update(overrides)
        return AnalysisEnvelope(**data)

    def test_serializes_nested_v2_shape(self):
        raw = self._minimal_env().model_dump(mode="json")
        assert raw["schema_version"] == "2"
        assert set(raw) == {
            "schema_version",
            "symbol",
            "run_id",
            "started_at",
            "completed_at",
            "status",
            "errors",
            "fatal_error",
            "deterministic_facts",
            "decision",
            "synthesis",
            "ohlc",
        }
        assert raw["deterministic_facts"]["entry_authorized"] is False
        assert raw["decision"]["action"] == "buy_setup"
        assert raw["synthesis"]["status"] == "FAILED"
        assert raw["ohlc"] == {"D1": [], "H4": [], "H1": []}

    def test_serialized_output_has_no_review_fields(self):
        raw = self._minimal_env().model_dump(mode="json")
        dumped = json.dumps(raw)
        assert "review" not in dumped
        assert "reviewer" not in dumped
        assert "decider" not in dumped
        assert "BLOCKED_BY_REVIEW" not in dumped

    def test_envelope_rejects_review_extra_field(self):
        with pytest.raises(ValidationError):
            AnalysisEnvelope.model_validate(
                {
                    **self._minimal_env().model_dump(mode="python"),
                    "review": {"status": "APPROVED"},
                }
            )

    def test_envelope_rejects_non_v2_schema_version(self):
        with pytest.raises(ValidationError):
            AnalysisEnvelope.model_validate(
                {
                    **self._minimal_env().model_dump(mode="python"),
                    "schema_version": "1.0",
                }
            )

    def test_envelope_rejects_unknown_decision_action(self):
        with pytest.raises(ValidationError):
            DecisionBlock(action="wait_for_setup")

    def test_envelope_rejects_unknown_status(self):
        with pytest.raises(ValidationError):
            self._minimal_env(status="completed")

    def test_envelope_roundtrip(self):
        env = self._minimal_env(
            status="success",
            deterministic_facts=DeterministicFacts(
                symbol="XAUUSD",
                setup_status="READY",
                direction="LONG",
                trade_direction="BULLISH",
                validation_status="VALID",
                operational=True,
                entry_authorized=False,
            ),
            decision=DecisionBlock(action="sell_setup"),
            synthesis=SynthesisBlock(
                status="SUCCESS",
                explanation="presentation only",
                risks=["Calendar risk"],
                confluences=["Confirmed structure"],
            ),
        )
        raw = env.model_dump(mode="json")
        restored = AnalysisEnvelope.model_validate(raw)
        assert restored.schema_version == "2"
        assert restored.deterministic_facts.setup_status == "READY"
        assert restored.deterministic_facts.operational is True
        assert restored.deterministic_facts.entry_authorized is False
        assert restored.decision.action == "sell_setup"
        assert restored.synthesis.status == "SUCCESS"

    def test_invalid_run_persists_as_no_trade_non_operational_partial(self):
        """INV-011 / FR-023: INVALID maps to no_trade + non-operational partial."""
        env = self._minimal_env(
            status="partial",
            deterministic_facts=DeterministicFacts(
                symbol="XAUUSD",
                setup_status="INVALID",
                direction="NONE",
                trade_direction="NEUTRAL",
                validation_status="INVALID",
                validation_errors=["INVARIANT_VIOLATION"],
                operational=False,
                entry_authorized=False,
            ),
            decision=DecisionBlock(action="no_trade"),
        )
        raw = env.model_dump(mode="json")
        assert raw["status"] == "partial"
        assert raw["deterministic_facts"]["validation_status"] == "INVALID"
        assert raw["deterministic_facts"]["setup_status"] == "INVALID"
        assert raw["deterministic_facts"]["operational"] is False
        assert raw["decision"]["action"] == "no_trade"

    def test_deterministic_facts_policy_and_rr(self):
        facts = DeterministicFacts(
            symbol="XAUUSD",
            validation_status="VALID",
            rr={"calculated_rr": 2.34, "minimum_required_rr": 2.0, "rr_pass": True},
            policy={
                "execution_status": "ACTIONABLE",
                "actionable": True,
                "blockers": [],
                "reason_codes": ["VALID_SETUP"],
            },
        )
        raw = facts.model_dump(mode="json")
        assert raw["rr"]["calculated_rr"] == 2.34
        assert raw["rr"]["minimum_required_rr"] == 2.0
        assert raw["rr"]["rr_pass"] is True
        assert raw["policy"]["actionable"] is True

    def test_entry_authorized_always_false_in_facts(self):
        """INV-003: entry_authorized cannot be set true through the envelope."""
        with pytest.raises(ValidationError):
            DeterministicFacts(symbol="XAUUSD", entry_authorized=True)
