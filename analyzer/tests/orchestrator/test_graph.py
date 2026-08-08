from unittest.mock import MagicMock

from src.analysis.market_structure_engine.deterministic_validator import DeterministicValidation
from src.analysis.market_structure_engine.models import (
    DecisionAction,
    DeterministicSetupState,
    EnforcementViolation,
    EnforcementViolationCode,
    ExecutionBlockerType,
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
from src.decision.models import DecisionOutput, SynthesisResponse
from src.orchestrator.graph import TradingGraph, _summarize_timeframe


def _graph(synthesizer=None):
    return TradingGraph(
        data_provider=MagicMock(),
        structure_analyzer=MagicMock(),
        calendar_provider=MagicMock(),
        synthesizer=synthesizer or MagicMock(),
    )


def test_graph_has_no_secondary_llm_nodes():
    graph = _graph()
    nodes = set(graph.graph.get_graph().nodes)
    assert "decide" not in nodes
    assert "review" not in nodes
    assert "deterministic_decision" in nodes
    assert "pre_llm_validation" in nodes


def test_deterministic_decision_uses_policy_action_without_llm():
    graph = _graph()
    policy = MagicMock()
    policy.allowed_actions = (DecisionAction.SELL_SETUP,)
    policy.execution_blockers = ()
    state = {
        "symbol": "EURUSD",
        "execution_policy": policy,
        "calendar_events": [],
        "fatal_error": None,
    }

    result = graph._deterministic_decision(state)

    assert result["decision"].action == DecisionAction.SELL_SETUP
    assert result["deterministic_validation"] is None
    graph.synthesizer.synthesize.assert_not_called()


def test_deterministic_decision_defaults_to_no_trade_when_policy_blocks():
    graph = _graph()
    policy = MagicMock()
    policy.allowed_actions = ()
    policy.execution_blockers = (MagicMock(blocker_type=ExecutionBlockerType.CANDIDATE),)

    result = graph._deterministic_decision(
        {
            "symbol": "EURUSD",
            "execution_policy": policy,
            "calendar_events": [],
            "fatal_error": None,
        }
    )

    assert result["decision"].action == DecisionAction.NO_TRADE


def test_synthesis_receives_deterministic_facts(monkeypatch):
    monkeypatch.setenv("TRADING_SYNTHESIZER_CACHE_ENABLED", "false")
    synthesizer = MagicMock()
    synthesizer.synthesize.return_value = SynthesisResponse(
        explanation="facts", risks=[], confluences=[]
    )
    graph = _graph(synthesizer)
    monkeypatch.setattr("src.orchestrator.graph.should_run_synthesis", lambda *_: True)
    setup = MagicMock()
    risk = MagicMock()
    policy = MagicMock()
    result = graph._synthesize_context(
        {
            "symbol": "EURUSD",
            "structure_analysis": {"timeframes": {}},
            "calendar_events": [],
            "broker_now": None,
            "deterministic_setup": setup,
            "risk_policy": risk,
            "execution_policy": policy,
            "fatal_error": None,
        }
    )

    assert result["synthesis_status"] == "SUCCESS"
    call = synthesizer.synthesize.call_args.kwargs
    assert call["deterministic_setup"] is setup
    assert call["risk_policy"] is risk
    assert call["execution_policy"] is policy


def test_synthesizer_structure_summary_preserves_event_and_liquidity_histories():
    timeframe = {
        "source_audit": {},
        "market_structure": {"primary_structure": "RANGE"},
        "events": {
            "event_history": [{"event_index": 1}],
            "failed_breakouts": [{"event_index": 2}],
            "primary_events": [{"event_index": 3}],
            "internal_events": [{"event_index": 4}],
            "latest_material_event": {"event_index": 4},
            "latest_primary_event": {"event_index": 3},
            "latest_internal_event": {"event_index": 4},
        },
        "liquidity": {
            "event_history": [{"event_index": 5}],
            "current_state": {"pool-1": "RECLAIMED"},
            "latest_event": {"event_index": 5},
        },
    }

    summary = _summarize_timeframe(timeframe)

    assert summary["events"] == timeframe["events"]
    assert summary["liquidity"] == timeframe["liquidity"]


def test_synthesizer_structure_summary_preserves_selected_level_lifecycle_and_blocker():
    selected_support = {
        "price": 99.0,
        "eligible_for_invalidation": True,
        "current_status": "TESTED",
        "freshness": "TESTED",
        "age_bars": 4,
        "touch_count": 2,
        "break_count": 0,
        "reclaim_count": 0,
        "accepted_beyond_count": 0,
        "accepted_beyond": False,
    }
    selected_resistance = {"price": 101.0, "eligible_for_invalidation": True}
    timeframe = {
        "market_structure": {"primary_structure": "RANGE"},
        "levels": {
            "nearest_support": {"price": 98.0},
            "nearest_resistance": {"price": 102.0},
            "nearest_eligible_support": selected_support,
            "nearest_eligible_resistance": selected_resistance,
            "invalidation_blocker": None,
            "support_levels": [{"price": 98.0}],
            "resistance_levels": [{"price": 102.0}],
        },
    }

    summary = _summarize_timeframe(timeframe)

    assert summary["levels"]["nearest_eligible_support"] == selected_support
    assert summary["levels"]["nearest_eligible_resistance"] == selected_resistance
    assert summary["levels"]["invalidation_blocker"] is None


def test_synthesizer_structure_summary_preserves_invalidation_blocker():
    summary = _summarize_timeframe(
        {
            "market_structure": {"primary_structure": "RANGE"},
            "levels": {"invalidation_blocker": "NO_ELIGIBLE_INVALIDATION_LEVEL"},
        }
    )

    assert summary["levels"] == {"invalidation_blocker": "NO_ELIGIBLE_INVALIDATION_LEVEL"}


# ===================================================================
# Degraded-status routing (SYNTH-009)
# ===================================================================
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


def _assembled(graph, *, action, validation, violations=()):
    state = {
        "symbol": "EURUSD",
        "deterministic_setup": _setup_state(),
        "risk_policy": _risk_state(),
        "execution_policy": _policy_state(),
        "decision": DecisionOutput(symbol="EURUSD", action=action, reasoning="explanation"),
        "final_decision": _enforcement(action, violations),
        "deterministic_validation": validation,
        "synthesis_status": "FAILED",
        "synthesis_error": "SYNTHESIS_UNAVAILABLE",
        "fatal_error": None,
        "errors": [],
    }
    return graph._assemble_output(state)


def test_synthesis_failure_with_actionable_facts_marks_degraded():
    graph = _graph()
    result = _assembled(graph, action=DecisionAction.BUY_SETUP, validation=_validation())
    assert result["analysis_result"].status == "degraded"


def test_synthesis_failure_with_enforcement_blocked_is_not_degraded():
    graph = _graph()
    violation = EnforcementViolation(
        code=EnforcementViolationCode.EXECUTION_NOT_ACTIONABLE,
        reason="blocked by enforcement",
    )
    result = _assembled(
        graph,
        action=DecisionAction.NO_TRADE,
        validation=_validation(),
        violations=(violation,),
    )
    assert result["analysis_result"].status == "partial"
    assert result["analysis_result"].status != "degraded"


def test_synthesis_failure_with_invalid_facts_is_not_degraded():
    graph = _graph()
    result = _assembled(
        graph,
        action=DecisionAction.NO_TRADE,
        validation=_validation(
            valid=False,
            validation_status="INVALID",
            setup_status="INVALID",
            direction="NONE",
        ),
    )
    assert result["analysis_result"].status == "partial"
    assert result["analysis_result"].status != "degraded"
