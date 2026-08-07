from __future__ import annotations

from src.analysis.market_structure_engine.deterministic_validator import DeterministicValidator
from src.analysis.market_structure_engine.models import (
    BlockerSeverity,
    DeterministicSetupState,
    EntryType,
    ExecutionBlocker,
    ExecutionBlockerCode,
    ExecutionBlockerType,
    ExecutionPolicyState,
    GeometryStatus,
    SetupClassificationStatus,
    SetupLifecycleStatus,
    TradeDirection,
)


def _setup(**overrides: object) -> DeterministicSetupState:
    values: dict[str, object] = {
        "setup_classification_status": SetupClassificationStatus.CLASSIFIED,
        "setup_lifecycle_status": SetupLifecycleStatus.TRIGGERED,
        "trade_direction": TradeDirection.BULLISH,
        "geometry_status": GeometryStatus.VALID,
        "current_price": 100.0,
        "entry_price": 101.0,
        "invalidation_price": 99.0,
        "target_price": 105.0,
        "estimated_reward_risk": 2.0,
        "entry_type": EntryType.STOP,
    }
    values.update(overrides)
    return DeterministicSetupState(**values)


def test_validator_exposes_canonical_long_contract() -> None:
    result = DeterministicValidator().validate(
        setup=_setup(),
        policy=ExecutionPolicyState(),
        action="buy_setup",
    )

    assert result.validation_status == "VALID"
    assert result.direction == "LONG"
    assert result.setup_status == "READY"
    assert result.calculated_rr == 2.0
    assert result.minimum_required_rr == 2.0
    assert result.rr_pass is True
    assert result.entry_authorized is False


def test_validator_rejects_action_direction_and_geometry() -> None:
    result = DeterministicValidator().validate(
        setup=_setup(target_price=98.0),
        policy=ExecutionPolicyState(),
        action="sell_setup",
    )

    assert result.validation_status == "INVALID"
    assert "ACTION_DIRECTION_MISMATCH" in result.reason_codes
    assert result.rr_pass is False


def test_ready_setup_with_blocker_is_invalid() -> None:
    blocker = ExecutionBlocker(
        blocker_type=ExecutionBlockerType.GEOMETRY,
        code=ExecutionBlockerCode.GEOMETRY_INVALID,
        reason="bad geometry",
        severity=BlockerSeverity.INVALIDATES_GRADE,
    )
    result = DeterministicValidator().validate(
        setup=_setup(),
        policy=ExecutionPolicyState(execution_blockers=(blocker,)),
    )

    assert result.validation_status == "INVALID"
    assert "READY_HAS_BLOCKERS" in result.reason_codes
