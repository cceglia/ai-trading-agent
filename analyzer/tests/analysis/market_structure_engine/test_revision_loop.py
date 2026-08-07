"""Deterministic final-state behavior replaces the former approval loop."""

from src.analysis.market_structure_engine.models import (
    DecisionAction,
    EnforcementViolation,
    EnforcementViolationCode,
    ExecutionStatus,
    FinalDecisionState,
)


def test_final_state_defaults_to_safe_no_trade():
    state = FinalDecisionState()
    assert state.final_execution_status == ExecutionStatus.NOT_READY
    assert state.final_action == DecisionAction.NO_TRADE
    assert state.enforcement_violations == ()
    assert state.provider_retry_count == 0


def test_enforcement_violation_forces_no_trade():
    state = FinalDecisionState(
        final_execution_status=ExecutionStatus.BLOCKED_BY_ENFORCEMENT,
        final_action=DecisionAction.NO_TRADE,
        enforcement_violations=(
            EnforcementViolation(
                code=EnforcementViolationCode.CANDIDATE_NOT_GENERATED,
                reason="No deterministic candidate",
            ),
        ),
    )
    assert state.final_action == DecisionAction.NO_TRADE
    assert state.enforcement_violations[0].code == EnforcementViolationCode.CANDIDATE_NOT_GENERATED


def test_provider_retry_count_is_the_only_retry_state():
    state = FinalDecisionState(provider_retry_count=2)
    assert state.provider_retry_count == 2
