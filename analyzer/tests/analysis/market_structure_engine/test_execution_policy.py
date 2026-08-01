"""Tests for deterministic execution policy evaluation (Section 16.2).

Tests the evaluate_execution_policy() function and its helpers:
- Each blocker type (POLICY, CALENDAR, RISK_REWARD, REVIEW, DATA_QUALITY, GEOMETRY)
- Status derivation priority order
- Allowed actions derivation for ACTIONABLE vs blocked states
- Factory construction via ExecutionPolicyState.create()
"""

from __future__ import annotations

from src.analysis.market_structure_engine.execution_policy import (
    PolicySettings,
    evaluate_execution_policy,
)
from src.analysis.market_structure_engine.models import (
    BlockerSeverity,
    DecisionAction,
    DeterministicSetupState,
    ExecutionBlocker,
    ExecutionBlockerCode,
    ExecutionBlockerType,
    ExecutionMode,
    ExecutionPolicyState,
    ExecutionStatus,
    GeometryStatus,
    RiskPolicyState,
    SetupClassificationStatus,
    SetupGrade,
    SetupLifecycleStatus,
    TradeDirection,
    TriggerStatus,
)


def _make_setup(
    *,
    grade: SetupGrade | None = SetupGrade.AAA,
    trade_direction: TradeDirection = TradeDirection.BULLISH,
    classification: SetupClassificationStatus = SetupClassificationStatus.CLASSIFIED,
    lifecycle: SetupLifecycleStatus = SetupLifecycleStatus.TRIGGERED,
    geometry: GeometryStatus = GeometryStatus.VALID,
    trigger_status: TriggerStatus = TriggerStatus.CONFIRMED_TRIGGER,
    d1_directional: bool = True,
    d1_structure: str = "BULLISH",
    h4_alignment: str = "ALIGNED_CONTINUATION",
    h4_structure: str = "BULLISH",
    h1_setup: str = "VALID_SETUP",
) -> DeterministicSetupState:
    return DeterministicSetupState(
        setup_classification_status=classification,
        setup_grade=grade,
        trade_direction=trade_direction,
        setup_lifecycle_status=lifecycle,
        geometry_status=geometry,
        confirmed_at="2026-07-21T14:00:00",
        confirmed_bar_index=100,
        expires_after_h1_bars=24,
        d1_bias="BULLISH",
        d1_direction=trade_direction,
        d1_is_directional=d1_directional,
        d1_structure_status=d1_structure,
        d1_regime="BULLISH_TREND",
        h4_bias="BULLISH",
        h4_direction=TradeDirection.BULLISH,
        h4_alignment_status=h4_alignment,
        h4_structure_status=h4_structure,
        h4_pullback_status="CONTINUATION",
        h1_bias="BULLISH",
        h1_direction=TradeDirection.BULLISH,
        h1_trigger_type="BULLISH_BOS",
        h1_trigger_status=trigger_status,
        h1_setup_status=h1_setup,
        current_price=1.1000,
        entry_price=1.1010,
        entry_zone_low=1.1005,
        entry_zone_high=1.1015,
        trigger_level=1.1010,
        invalidation_price=1.0980,
        target_price=1.1100,
        estimated_reward_risk=2.5,
    )


def _make_risk_policy(
    *,
    base_risk: float = 1.0,
    multiplier: float = 1.0,
    min_rr: float = 2.0,
    estimated_rr: float | None = 2.5,
) -> RiskPolicyState:
    return RiskPolicyState(
        base_risk_percentage=base_risk,
        grade_risk_multiplier=multiplier,
        minimum_reward_risk=min_rr,
        estimated_reward_risk=estimated_rr,
    )


# ============================================================================
# Blocker types
# ============================================================================


class TestPolicyBlocker:
    """Policy blocker for countertrend disabled."""

    def test_countertrend_disabled_blocks(self) -> None:
        setup = _make_setup(grade=SetupGrade.COUNTERTREND)
        policy = _make_risk_policy()
        settings = PolicySettings(countertrend_enabled=False)

        state = evaluate_execution_policy(setup=setup, risk_policy=policy, settings=settings)
        assert len(state.execution_blockers) == 1
        blocker = state.execution_blockers[0]
        assert blocker.blocker_type == ExecutionBlockerType.POLICY
        assert blocker.code == ExecutionBlockerCode.POLICY_COUNTERTREND_DISABLED
        assert blocker.severity == BlockerSeverity.INVALIDATES_GRADE

    def test_countertrend_enabled_passes(self) -> None:
        setup = _make_setup(grade=SetupGrade.COUNTERTREND)
        policy = _make_risk_policy()
        settings = PolicySettings(countertrend_enabled=True)

        state = evaluate_execution_policy(setup=setup, risk_policy=policy, settings=settings)
        assert not any(
            b.blocker_type == ExecutionBlockerType.POLICY for b in state.execution_blockers
        )


class TestCalendarBlocker:
    """Calendar blocker for high-impact events."""

    def test_high_impact_blocks_when_enabled(self) -> None:
        setup = _make_setup()
        policy = _make_risk_policy()
        settings = PolicySettings(high_impact_calendar_block=True)

        state = evaluate_execution_policy(
            setup=setup, risk_policy=policy, has_high_impact_event=True, settings=settings
        )
        assert any(
            b.blocker_type == ExecutionBlockerType.CALENDAR for b in state.execution_blockers
        )

    def test_high_impact_skipped_when_disabled(self) -> None:
        setup = _make_setup()
        policy = _make_risk_policy()
        settings = PolicySettings(high_impact_calendar_block=False)

        state = evaluate_execution_policy(
            setup=setup, risk_policy=policy, has_high_impact_event=True, settings=settings
        )
        assert not any(
            b.blocker_type == ExecutionBlockerType.CALENDAR for b in state.execution_blockers
        )

    def test_no_high_impact_no_blocker(self) -> None:
        setup = _make_setup()
        policy = _make_risk_policy()

        state = evaluate_execution_policy(
            setup=setup, risk_policy=policy, has_high_impact_event=False
        )
        assert not any(
            b.blocker_type == ExecutionBlockerType.CALENDAR for b in state.execution_blockers
        )


class TestRiskRewardBlocker:
    """Risk/reward blockers."""

    def test_missing_rr_blocks(self) -> None:
        setup = _make_setup()
        policy = _make_risk_policy(estimated_rr=None)

        state = evaluate_execution_policy(setup=setup, risk_policy=policy)
        assert any(
            b.code == ExecutionBlockerCode.RISK_REWARD_CALCULATION_FAILED
            for b in state.execution_blockers
        )

    def test_below_minimum_rr_blocks(self) -> None:
        setup = _make_setup()
        policy = _make_risk_policy(estimated_rr=1.5, min_rr=2.0)

        state = evaluate_execution_policy(setup=setup, risk_policy=policy)
        assert any(
            b.code == ExecutionBlockerCode.RISK_REWARD_BELOW_MINIMUM
            for b in state.execution_blockers
        )

    def test_adequate_rr_passes(self) -> None:
        setup = _make_setup()
        policy = _make_risk_policy(estimated_rr=3.0, min_rr=2.0)

        state = evaluate_execution_policy(setup=setup, risk_policy=policy)
        assert not any(
            b.blocker_type == ExecutionBlockerType.RISK_REWARD for b in state.execution_blockers
        )


class TestTriggerBlocker:
    """Review blocker for unconfirmed trigger."""

    def test_unconfirmed_trigger_blocks(self) -> None:
        setup = _make_setup(trigger_status=TriggerStatus.PENDING_CONFIRMATION)
        policy = _make_risk_policy()
        settings = PolicySettings(require_confirmed_trigger=True)

        state = evaluate_execution_policy(setup=setup, risk_policy=policy, settings=settings)
        assert any(
            b.code == ExecutionBlockerCode.REVIEW_TRIGGER_NOT_CONFIRMED
            for b in state.execution_blockers
        )

    def test_confirmed_trigger_passes(self) -> None:
        setup = _make_setup(trigger_status=TriggerStatus.CONFIRMED_TRIGGER)
        policy = _make_risk_policy()
        settings = PolicySettings(require_confirmed_trigger=True)

        state = evaluate_execution_policy(setup=setup, risk_policy=policy, settings=settings)
        assert not any(
            b.code == ExecutionBlockerCode.REVIEW_TRIGGER_NOT_CONFIRMED
            for b in state.execution_blockers
        )


class TestDataQualityBlocker:
    """Data quality blockers for missing timeframe data."""

    def test_missing_d1_data(self) -> None:
        setup = _make_setup(d1_directional=False, d1_structure="UNKNOWN")
        policy = _make_risk_policy()

        state = evaluate_execution_policy(setup=setup, risk_policy=policy)
        assert any(
            b.code == ExecutionBlockerCode.DATA_QUALITY_MISSING_D1_DATA
            for b in state.execution_blockers
        )

    def test_missing_h4_data(self) -> None:
        setup = _make_setup(h4_alignment="UNKNOWN", h4_structure="UNKNOWN")
        policy = _make_risk_policy()

        state = evaluate_execution_policy(setup=setup, risk_policy=policy)
        assert any(
            b.code == ExecutionBlockerCode.DATA_QUALITY_MISSING_H4_DATA
            for b in state.execution_blockers
        )

    def test_missing_h1_data(self) -> None:
        setup = _make_setup(h1_setup="UNKNOWN")
        policy = _make_risk_policy()

        state = evaluate_execution_policy(setup=setup, risk_policy=policy)
        assert any(
            b.code == ExecutionBlockerCode.DATA_QUALITY_MISSING_H1_DATA
            for b in state.execution_blockers
        )

    def test_all_data_present_no_blocker(self) -> None:
        setup = _make_setup()
        policy = _make_risk_policy()

        state = evaluate_execution_policy(setup=setup, risk_policy=policy)
        assert not any(
            b.blocker_type == ExecutionBlockerType.DATA_QUALITY for b in state.execution_blockers
        )


class TestGeometryBlocker:
    """Geometry blocker for invalid entry geometry."""

    def test_invalid_geometry_blocks_when_required(self) -> None:
        setup = _make_setup(geometry=GeometryStatus.TEMPORARILY_UNAVAILABLE)
        policy = _make_risk_policy()
        settings = PolicySettings(require_valid_geometry=True)

        state = evaluate_execution_policy(setup=setup, risk_policy=policy, settings=settings)
        assert any(
            b.code == ExecutionBlockerCode.GEOMETRY_INVALID for b in state.execution_blockers
        )

    def test_valid_geometry_passes(self) -> None:
        setup = _make_setup(geometry=GeometryStatus.VALID)
        policy = _make_risk_policy()
        settings = PolicySettings(require_valid_geometry=True)

        state = evaluate_execution_policy(setup=setup, risk_policy=policy, settings=settings)
        assert not any(
            b.blocker_type == ExecutionBlockerType.GEOMETRY for b in state.execution_blockers
        )

    def test_invalid_geometry_skipped_when_not_required(self) -> None:
        setup = _make_setup(geometry=GeometryStatus.TEMPORARILY_UNAVAILABLE)
        policy = _make_risk_policy()
        settings = PolicySettings(require_valid_geometry=False)

        state = evaluate_execution_policy(setup=setup, risk_policy=policy, settings=settings)
        assert not any(
            b.blocker_type == ExecutionBlockerType.GEOMETRY for b in state.execution_blockers
        )


# ============================================================================
# Status derivation priority
# ============================================================================


class TestStatusDerivation:
    """Status derivation priority order from models.py derive_execution_status()."""

    def test_calendar_overrides_data_quality(self) -> None:
        """Calendar has highest priority among non-execution blockers."""
        setup = _make_setup(d1_directional=False, d1_structure="UNKNOWN")
        policy = _make_risk_policy()

        state = evaluate_execution_policy(
            setup=setup, risk_policy=policy, has_high_impact_event=True
        )
        assert state.pre_review_execution_status == ExecutionStatus.BLOCKED_BY_CALENDAR

    def test_actionable_when_no_blockers(self) -> None:
        setup = _make_setup()
        policy = _make_risk_policy()

        state = evaluate_execution_policy(setup=setup, risk_policy=policy)
        assert state.pre_review_execution_status == ExecutionStatus.ACTIONABLE

    def test_incomplete_deterministic_plan_is_blocked(self) -> None:
        setup = _make_setup().model_copy(update={"entry_price": None})
        policy = evaluate_execution_policy(
            setup=setup,
            risk_policy=RiskPolicyState(estimated_reward_risk=2.0),
            settings=PolicySettings(require_confirmed_trigger=False),
        )

        assert policy.pre_review_execution_status == ExecutionStatus.BLOCKED_BY_DATA_QUALITY
        assert policy.allowed_actions == (DecisionAction.NO_TRADE,)
        assert any(
            blocker.code == ExecutionBlockerCode.DATA_QUALITY_INCOMPLETE_SETUP
            for blocker in policy.execution_blockers
        )

    def test_multiple_blockers_use_highest_priority(self) -> None:
        """When multiple blocker types present, status uses the highest priority."""
        setup = _make_setup(
            d1_directional=False,
            d1_structure="UNKNOWN",
            geometry=GeometryStatus.TEMPORARILY_UNAVAILABLE,
        )
        policy = _make_risk_policy(estimated_rr=None)

        state = evaluate_execution_policy(setup=setup, risk_policy=policy)
        # Should have DATA_QUALITY (missing D1), RISK_REWARD (missing rr), GEOMETRY (invalid)
        # DATA_QUALITY has higher priority than both RISK_REWARD and GEOMETRY
        assert state.pre_review_execution_status == ExecutionStatus.BLOCKED_BY_DATA_QUALITY


# ============================================================================
# Allowed actions derivation
# ============================================================================


class TestAllowedActions:
    """Allowed actions based on status and direction."""

    def test_actionable_bullish(self) -> None:
        setup = _make_setup(trade_direction=TradeDirection.BULLISH)
        policy = _make_risk_policy()
        state = evaluate_execution_policy(setup=setup, risk_policy=policy)
        assert state.allowed_actions == (DecisionAction.BUY_SETUP,)

    def test_actionable_bearish(self) -> None:
        setup = _make_setup(trade_direction=TradeDirection.BEARISH)
        policy = _make_risk_policy()
        state = evaluate_execution_policy(setup=setup, risk_policy=policy)
        assert state.allowed_actions == (DecisionAction.SELL_SETUP,)

    def test_actionable_neutral(self) -> None:
        setup = _make_setup(trade_direction=TradeDirection.NEUTRAL)
        policy = _make_risk_policy()
        state = evaluate_execution_policy(setup=setup, risk_policy=policy)
        assert state.allowed_actions == (DecisionAction.NO_TRADE,)

    def test_blocked_yields_no_trade(self) -> None:
        setup = _make_setup(trade_direction=TradeDirection.BULLISH)
        policy = _make_risk_policy(estimated_rr=None)  # Causes RISK_REWARD blocker
        state = evaluate_execution_policy(setup=setup, risk_policy=policy)
        assert state.allowed_actions == (DecisionAction.NO_TRADE,)


# ============================================================================
# Factory construction
# ============================================================================


class TestExecutionPolicyStateCreate:
    """ExecutionPolicyState.create() factory method."""

    def test_creates_from_setup(self) -> None:
        setup = _make_setup(trade_direction=TradeDirection.BULLISH)
        blockers = (
            ExecutionBlocker(
                blocker_type=ExecutionBlockerType.POLICY,
                code=ExecutionBlockerCode.POLICY_MAX_DAILY_TRADES,
                reason="Max daily trades reached",
                severity=BlockerSeverity.EXECUTION_ONLY,
            ),
        )
        state = ExecutionPolicyState.create(setup=setup, execution_blockers=blockers)
        assert state.trade_direction == TradeDirection.BULLISH
        assert len(state.execution_blockers) == 1
        assert state.pre_review_execution_status == ExecutionStatus.BLOCKED_BY_POLICY
        assert state.allowed_actions == (DecisionAction.NO_TRADE,)

    def test_creates_with_empty_blockers(self) -> None:
        setup = _make_setup(trade_direction=TradeDirection.BEARISH)
        state = ExecutionPolicyState.create(setup=setup)
        assert state.trade_direction == TradeDirection.BEARISH
        assert state.execution_blockers == ()


# ============================================================================
# Edge cases
# ============================================================================


class TestExecutionPolicyEdgeCases:
    """Edge cases for execution policy evaluation."""

    def test_default_settings_are_safe(self) -> None:
        """Default PolicySettings should have conservative defaults."""
        settings = PolicySettings()
        assert settings.countertrend_enabled is False
        assert settings.high_impact_calendar_block is True
        assert settings.require_confirmed_trigger is True
        assert settings.require_valid_geometry is True

    def test_multiple_blockers_accumulate(self) -> None:
        """Multiple blocker conditions create multiple blockers, not just the first."""
        setup = _make_setup(
            grade=SetupGrade.COUNTERTREND,
            d1_directional=False,
            d1_structure="UNKNOWN",
            geometry=GeometryStatus.PERMANENTLY_INVALID,
        )
        policy = _make_risk_policy(estimated_rr=None)
        settings = PolicySettings(countertrend_enabled=False)

        state = evaluate_execution_policy(
            setup=setup, risk_policy=policy, has_high_impact_event=True, settings=settings
        )
        # Expected blockers: POLICY (countertrend), CALENDAR, RISK_REWARD (missing),
        # DATA_QUALITY (D1), GEOMETRY
        assert len(state.execution_blockers) >= 4

    def test_execution_mode_parameter_accepted(self) -> None:
        """execution_mode parameter is accepted even if not used in current logic."""
        setup = _make_setup()
        policy = _make_risk_policy()
        state = evaluate_execution_policy(
            setup=setup, risk_policy=policy, execution_mode=ExecutionMode.LIVE
        )
        assert state is not None
