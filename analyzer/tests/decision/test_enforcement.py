"""Deterministic enforcement assertions; no approval or retry stage exists."""

from src.analysis.market_structure_engine.models import (
    BlockerSeverity,
    DecisionAction,
    DeterministicSetupState,
    EnforcementViolationCode,
    ExecutionBlocker,
    ExecutionBlockerCode,
    ExecutionBlockerType,
    ExecutionPolicyState,
    ExecutionStatus,
    GeometryStatus,
    SetupClassificationStatus,
    SetupGrade,
    SetupLifecycleStatus,
    TradeDirection,
    TriggerStatus,
)
from src.decision.enforcement import DeterministicEnforcementGate
from src.decision.models import DecisionOutput


def _setup(**overrides):
    values = dict(
        setup_classification_status=SetupClassificationStatus.CLASSIFIED,
        setup_grade=SetupGrade.AAA,
        trade_direction=TradeDirection.BULLISH,
        setup_lifecycle_status=SetupLifecycleStatus.TRIGGERED,
        geometry_status=GeometryStatus.VALID,
        h1_trigger_status=TriggerStatus.CONFIRMED_TRIGGER,
        h1_setup_status="VALID_SETUP",
        current_price=1.1,
        entry_price=1.101,
        entry_zone_low=1.1,
        entry_zone_high=1.102,
        trigger_level=1.101,
        invalidation_price=1.098,
        target_price=1.11,
        estimated_reward_risk=3.0,
    )
    values.update(overrides)
    return DeterministicSetupState(**values)


def _policy(direction=TradeDirection.BULLISH, blockers=()):
    return ExecutionPolicyState(trade_direction=direction, execution_blockers=blockers)


def _decision(action=DecisionAction.BUY_SETUP):
    return DecisionOutput(symbol="EURUSD", action=action, reasoning="deterministic test")


def _enforce(setup=None, policy=None, decision=None):
    return DeterministicEnforcementGate().enforce(
        setup=setup or _setup(),
        policy=policy or _policy(),
        decision=decision or _decision(),
    )


def test_actionable_deterministic_policy_passes():
    result = _enforce()
    assert result.final_execution_status == ExecutionStatus.ACTIONABLE
    assert result.final_action == DecisionAction.BUY_SETUP
    assert result.enforcement_violations == ()


def test_missing_candidate_is_blocked_by_enforcement():
    result = _enforce(
        setup=_setup(
            setup_classification_status=SetupClassificationStatus.NO_SETUP, setup_grade=None
        )
    )
    assert result.final_execution_status == ExecutionStatus.BLOCKED_BY_ENFORCEMENT
    assert result.final_action == DecisionAction.NO_TRADE
    assert any(
        v.code == EnforcementViolationCode.CANDIDATE_NOT_GENERATED
        for v in result.enforcement_violations
    )


def test_policy_blocker_is_enforced_without_second_llm_decision():
    blocker = ExecutionBlocker(
        blocker_type=ExecutionBlockerType.POLICY,
        code=ExecutionBlockerCode.POLICY_COUNTERTREND_DISABLED,
        reason="policy",
        severity=BlockerSeverity.INVALIDATES_GRADE,
    )
    result = _enforce(policy=_policy(blockers=(blocker,)))
    assert result.final_execution_status == ExecutionStatus.BLOCKED_BY_ENFORCEMENT
    assert result.final_action == DecisionAction.NO_TRADE
