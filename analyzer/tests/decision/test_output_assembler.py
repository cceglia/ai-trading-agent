"""Final output maps deterministic facts and validation ahead of LLM prose."""

from src.analysis.market_structure_engine.deterministic_validator import DeterministicValidation
from src.analysis.market_structure_engine.models import (
    DecisionAction,
    DeterministicSetupState,
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
from src.decision.models import AdvisoryLevels, DecisionOutput
from src.decision.output_assembler import FinalOutputAssembler


def _setup():
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


def _risk():
    return RiskPolicyState(
        base_risk_percentage=1.0,
        grade_risk_multiplier=1.0,
        minimum_reward_risk=2.0,
        estimated_reward_risk=3.0,
    )


def test_deterministic_prices_survive_assembly():
    decision = DecisionOutput(
        symbol="EURUSD",
        action=DecisionAction.BUY_SETUP,
        reasoning="explanation",
        advisory_levels=AdvisoryLevels(entry_price=9.0),
    )
    result = FinalOutputAssembler().assemble(
        setup=_setup(),
        policy=ExecutionPolicyState(trade_direction=TradeDirection.BULLISH),
        risk=_risk(),
        decision=decision,
        enforcement=FinalDecisionState(
            final_execution_status=ExecutionStatus.ACTIONABLE,
            final_action=DecisionAction.BUY_SETUP,
        ),
        validation=DeterministicValidation(
            valid=True,
            validation_status="VALID",
            setup_status="VALID",
            direction="BULLISH",
            rr=3.0,
            calculated_rr=3.0,
            minimum_required_rr=2.0,
            rr_pass=True,
        ),
    )
    assert result.sl_tp_overlay.entry_price == 1.101
    assert result.sl_tp_overlay.stop_loss == 1.098
    assert result.sl_tp_overlay.take_profit == 1.11
    assert result.advisory_levels.entry_price == 9.0
    assert result.entry_authorized is False


def test_invalid_deterministic_validation_marks_partial_and_no_trade():
    result = FinalOutputAssembler().assemble(
        setup=_setup(),
        policy=ExecutionPolicyState(trade_direction=TradeDirection.BULLISH),
        risk=_risk(),
        decision=DecisionOutput(
            symbol="EURUSD", action=DecisionAction.NO_TRADE, reasoning="invalid"
        ),
        enforcement=FinalDecisionState(
            final_execution_status=ExecutionStatus.BLOCKED_BY_ENFORCEMENT,
            final_action=DecisionAction.NO_TRADE,
        ),
        validation=DeterministicValidation(
            valid=False,
            validation_status="INVALID",
            validation_errors=("bad facts",),
            setup_status="INVALID",
            direction="NONE",
        ),
    )
    assert result.status == "partial"
    assert result.validation_errors == ["bad facts"]
    assert result.entry_authorized is False
