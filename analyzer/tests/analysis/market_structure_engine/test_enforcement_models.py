"""Model-level assertions for deterministic enforcement output."""

from src.analysis.market_structure_engine.models import (
    DecisionAction,
    EnforcementViolation,
    EnforcementViolationCode,
    ExecutionStatus,
    FinalDecisionState,
)


def test_enforcement_state_defaults_to_safe_action():
    state = FinalDecisionState()
    assert state.final_action == DecisionAction.NO_TRADE
    assert state.final_execution_status == ExecutionStatus.NOT_READY


def test_enforcement_state_serializes_violation_codes():
    state = FinalDecisionState(
        final_execution_status=ExecutionStatus.BLOCKED_BY_ENFORCEMENT,
        enforcement_violations=(
            EnforcementViolation(
                code=EnforcementViolationCode.INVALID_GEOMETRY,
                reason="geometry is unavailable",
            ),
        ),
    )
    assert state.model_dump(mode="json")["enforcement_violations"][0]["code"] == "INVALID_GEOMETRY"
