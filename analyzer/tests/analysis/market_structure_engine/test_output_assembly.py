"""Output state tests for deterministic validation and enforcement."""

from src.analysis.market_structure_engine.models import (
    DecisionAction,
    EnforcementViolation,
    EnforcementViolationCode,
    ExecutionStatus,
    FinalDecisionState,
)


def test_final_decision_state_has_no_approval_fields():
    state = FinalDecisionState(final_action=DecisionAction.NO_TRADE)
    assert state.final_execution_status == ExecutionStatus.NOT_READY
    assert set(state.model_fields_set) == {"final_action"}


def test_enforcement_violations_are_retained_for_output():
    violation = EnforcementViolation(
        code=EnforcementViolationCode.CANDIDATE_NOT_GENERATED,
        reason="missing candidate",
    )
    state = FinalDecisionState(
        final_execution_status=ExecutionStatus.BLOCKED_BY_ENFORCEMENT,
        final_action=DecisionAction.NO_TRADE,
        enforcement_violations=(violation,),
    )
    assert state.enforcement_violations == (violation,)
