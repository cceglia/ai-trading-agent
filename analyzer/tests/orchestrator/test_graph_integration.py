"""Graph-level integration tests for the single-synthesizer routing.

TEST-010 / AC-010, TEST-011 / AC-011, TEST-012 / AC-012: these tests invoke
the *compiled* graph (``TradingGraph.run`` → ``self.graph.invoke``) with
injected mocks and assert LLM call counts plus the JSON outcome that a
downstream writer would consume.
"""

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from src.analysis.market_structure_engine.deterministic_validator import DeterministicValidation
from src.analysis.market_structure_engine.models import (
    DecisionAction,
    DeterministicSetupState,
    EnforcementViolation,
    EnforcementViolationCode,
    ExecutionPolicyState,
    ExecutionStatus,
    FinalDecisionState,
    GeometryStatus,
    RiskPolicyState,
    SetupClassificationStatus,
    SetupGrade,
    SetupLifecycleStatus,
    TradeDirection,
    TriggerStatus,
)
from src.decision.models import SynthesisResponse
from src.orchestrator.graph import TradingGraph
from src.output.result_writer import ResultWriter


def _setup_state() -> DeterministicSetupState:
    return DeterministicSetupState(
        setup_classification_status=SetupClassificationStatus.CLASSIFIED,
        setup_grade=SetupGrade.AAA,
        trade_direction=TradeDirection.BULLISH,
        setup_lifecycle_status=SetupLifecycleStatus.TRIGGERED,
        geometry_status=GeometryStatus.VALID,
        h1_trigger_status=TriggerStatus.CONFIRMED_TRIGGER,
        h1_setup_status="VALID_SETUP",
        current_price=1.1,
        entry_price=1.101,
        invalidation_price=1.098,
        target_price=1.11,
        estimated_reward_risk=3.0,
    )


def _risk_state() -> RiskPolicyState:
    return RiskPolicyState(
        base_risk_percentage=1.0,
        grade_risk_multiplier=1.0,
        minimum_reward_risk=2.0,
        estimated_reward_risk=3.0,
    )


def _policy_state() -> ExecutionPolicyState:
    return ExecutionPolicyState(trade_direction=TradeDirection.BULLISH)


def _validation(**overrides) -> DeterministicValidation:
    defaults = {
        "valid": True,
        "validation_status": "VALID",
        "setup_status": "READY",
        "direction": "LONG",
        "rr": 3.0,
        "calculated_rr": 3.0,
        "minimum_required_rr": 2.0,
        "rr_pass": True,
    }
    defaults.update(overrides)
    return DeterministicValidation(**defaults)


def _enforcement(
    action: DecisionAction = DecisionAction.BUY_SETUP,
    violations: tuple = (),
) -> FinalDecisionState:
    return FinalDecisionState(
        final_execution_status=(
            ExecutionStatus.ACTIONABLE
            if action in (DecisionAction.BUY_SETUP, DecisionAction.SELL_SETUP)
            else ExecutionStatus.BLOCKED_BY_ENFORCEMENT
        ),
        final_action=action,
        enforcement_violations=violations,
    )


def _tf() -> dict:
    """A minimal per-timeframe engine output that survives summarization."""
    return {
        "market_structure": {"primary_structure": "BULLISH"},
        "source_audit": {
            "candle_closure_verified": True,
            "latest_closed_candle_time": "2026-08-07T00:00:00",
        },
        "technical_context": {"close": 1.10},
        "analysis_context": {},
    }


def _structure_analysis() -> dict:
    return {
        "timeframes": {"D1": _tf(), "H4": _tf(), "H1": _tf()},
        "confluence": {},
    }


def _build_graph(
    monkeypatch,
    *,
    synthesizer: MagicMock,
    validation: DeterministicValidation,
    enforcement: FinalDecisionState,
    save_synthesis: MagicMock | None = None,
) -> TradingGraph:
    """Construct a TradingGraph with fully-mocked deterministic seams.

    The data provider, structure analyzer, calendar provider, and synthesizer
    are injected mocks; the deterministic engine functions (grade_setup,
    risk policy, execution policy), the validator, and the enforcement gate
    are patched so the compiled graph can run end-to-end deterministically.
    """
    graph = TradingGraph(
        data_provider=MagicMock(),
        structure_analyzer=MagicMock(),
        calendar_provider=MagicMock(),
        synthesizer=synthesizer,
    )

    # ── Data pipeline mocks ──────────────────────────────────────────────
    graph.data_provider.get_broker_time.return_value = datetime(2026, 8, 7, 12, 0, 0)
    graph.data_provider.get_candles.return_value = "time,open,high,low,close\n"
    graph.data_provider.get_positions.return_value = []
    graph.data_provider.get_pending_orders.return_value = []
    graph.data_provider.get_symbol_price.return_value = {"bid": 1.10, "ask": 1.11}
    graph.calendar_provider.fetch_events.return_value = []

    # Candle-cache seams: force a fresh fetch and no-op the writes.
    monkeypatch.setattr("src.orchestrator.graph.should_run_analysis", lambda *_: True)
    monkeypatch.setattr("src.orchestrator.graph.save_analysis", lambda *_: None)
    monkeypatch.setattr("src.orchestrator.graph.save_ohlc_cache", lambda *_: None)
    monkeypatch.setattr("src.orchestrator.graph.extract_ohlc_from_csv", lambda _: [])

    # Snapshot building is replaced so candle CSV is never parsed.
    graph._snapshot_builder = MagicMock()
    graph._snapshot_builder.build.return_value = {"timeframe": "D1"}

    # Structure analysis: canned multi-timeframe output.
    graph.structure_analyzer.analyze.return_value = _structure_analysis()

    # ── Deterministic engine seams ──────────────────────────────────────
    monkeypatch.setattr("src.orchestrator.graph.grade_setup", lambda *_, **__: _setup_state())
    monkeypatch.setattr("src.orchestrator.graph.build_risk_policy", lambda *_, **__: _risk_state())
    monkeypatch.setattr(
        "src.orchestrator.graph.evaluate_execution_policy", lambda *_, **__: _policy_state()
    )

    # ── Validator and enforcement gate ──────────────────────────────────
    monkeypatch.setattr(graph, "_deterministic_validator", MagicMock())
    graph._deterministic_validator.validate.return_value = validation
    monkeypatch.setattr(graph, "_enforcement_gate", MagicMock())
    graph._enforcement_gate.enforce.return_value = enforcement

    # ── Synthesizer cache seam ──────────────────────────────────────────
    monkeypatch.setattr("src.orchestrator.graph.should_run_synthesis", lambda *_: True)
    if save_synthesis is not None:
        monkeypatch.setattr("src.orchestrator.graph.save_synthesis", save_synthesis)

    return graph


def _invoke(graph: TradingGraph) -> dict:
    return graph.run("EURUSD")


# ===================================================================
# TEST-010 / AC-010 — invalid deterministic facts
# ===================================================================
def test_invalid_facts_zero_llm_calls_and_persist_partial(monkeypatch, tmp_path):
    synthesizer = MagicMock()
    save_synthesis = MagicMock()
    graph = _build_graph(
        monkeypatch,
        synthesizer=synthesizer,
        validation=_validation(
            valid=False,
            validation_status="INVALID",
            setup_status="INVALID",
            direction="NONE",
        ),
        enforcement=_enforcement(
            action=DecisionAction.NO_TRADE,
            violations=(
                EnforcementViolation(
                    code=EnforcementViolationCode.EXECUTION_NOT_ACTIONABLE,
                    reason="blocked by enforcement",
                ),
            ),
        ),
        save_synthesis=save_synthesis,
    )

    result = _invoke(graph)

    synthesizer.synthesize.assert_not_called()
    save_synthesis.assert_not_called()
    final_output = result["final_output"]
    assert final_output["status"] == "partial"
    assert final_output["validation_status"] == "INVALID"
    assert final_output["final_action"] == "no_trade"

    written = ResultWriter(tmp_path).write(
        "EURUSD",
        result,
        {},
        datetime(2026, 8, 7, 12, 0, 0),
    )
    assert written is not None
    import json

    data = json.loads(written.read_text())
    assert data["status"] == "partial"
    assert data["validation_status"] == "INVALID"


# ===================================================================
# TEST-011 / AC-011 — valid actionable facts, one successful call
# ===================================================================
def test_valid_facts_one_call_unchanged_action_success(monkeypatch):
    synthesizer = MagicMock()
    synthesizer.synthesize.return_value = SynthesisResponse(
        explanation="deterministic context is bullish",
        risks=["Calendar risk"],
        confluences=["Confirmed structure"],
    )
    save_synthesis = MagicMock()
    graph = _build_graph(
        monkeypatch,
        synthesizer=synthesizer,
        validation=_validation(),
        enforcement=_enforcement(),
        save_synthesis=save_synthesis,
    )

    result = _invoke(graph)

    synthesizer.synthesize.assert_called_once()
    save_synthesis.assert_called_once()
    final_output = result["final_output"]
    assert final_output["status"] == "success"
    assert final_output["validation_status"] == "VALID"
    assert final_output["final_action"] == "buy_setup"
    assert final_output["synthesis_status"] == "SUCCESS"
    assert final_output["synthesis_explanation"] == "deterministic context is bullish"


# ===================================================================
# TEST-012 / AC-012 — synthesis failure: degraded, unchanged, no retry/cache
# ===================================================================
def test_synthesis_failure_degraded_no_retry_no_cache_write(monkeypatch):
    synthesizer = MagicMock()
    synthesizer.synthesize.side_effect = TimeoutError("provider timeout")
    save_synthesis = MagicMock()
    graph = _build_graph(
        monkeypatch,
        synthesizer=synthesizer,
        validation=_validation(),
        enforcement=_enforcement(),
        save_synthesis=save_synthesis,
    )

    result = _invoke(graph)

    synthesizer.synthesize.assert_called_once()
    save_synthesis.assert_not_called()
    final_output = result["final_output"]
    assert final_output["status"] == "degraded"
    assert final_output["validation_status"] == "VALID"
    assert final_output["final_action"] == "buy_setup"
    assert final_output["synthesis_status"] == "FAILED"
    assert final_output["synthesis_error"] == "SYNTHESIS_UNAVAILABLE"


# ===================================================================
# TEST-021 / AC-021 — Synthesizer size/emptiness/duplicate violations
# ===================================================================
def _schema_boundary_payloads():
    """Each payload violates the SynthesisResponse presentation contract."""
    return [
        pytest.param(
            {"explanation": "x" * 4001, "risks": [], "confluences": []},
            id="explanation-over-4000",
        ),
        pytest.param(
            {"explanation": "ok", "risks": [f"risk {i}" for i in range(21)], "confluences": []},
            id="risks-over-20",
        ),
        pytest.param(
            {
                "explanation": "ok",
                "risks": [],
                "confluences": [f"confluence {i}" for i in range(21)],
            },
            id="confluences-over-20",
        ),
        pytest.param(
            {"explanation": "ok", "risks": ["   \t "], "confluences": []},
            id="whitespace-only-risk-item",
        ),
        pytest.param(
            {
                "explanation": "ok",
                "risks": [],
                "confluences": ["  "],
            },
            id="whitespace-only-confluence-item",
        ),
        pytest.param(
            {"explanation": "ok", "risks": ["dup", "dup"], "confluences": []},
            id="duplicate-risk-item",
        ),
        pytest.param(
            {"explanation": "   ", "risks": [], "confluences": []},
            id="whitespace-only-explanation",
        ),
    ]


@pytest.mark.parametrize("payload", _schema_boundary_payloads())
def test_schema_boundary_violation_routes_to_degraded_without_changing_action(monkeypatch, payload):
    """TEST-021: every presentation-contract violation degrades the run
    through the schema-failure path and never changes the deterministic
    action."""
    synthesizer = MagicMock()
    synthesizer.synthesize.return_value = payload
    save_synthesis = MagicMock()
    graph = _build_graph(
        monkeypatch,
        synthesizer=synthesizer,
        validation=_validation(),
        enforcement=_enforcement(),
        save_synthesis=save_synthesis,
    )

    result = _invoke(graph)

    synthesizer.synthesize.assert_called_once()
    save_synthesis.assert_not_called()
    final_output = result["final_output"]
    assert final_output["status"] == "degraded"
    assert final_output["final_action"] == "buy_setup"
    assert final_output["synthesis_status"] == "FAILED"
    assert final_output["synthesis_error"] == "SYNTHESIS_SCHEMA_INVALID"
