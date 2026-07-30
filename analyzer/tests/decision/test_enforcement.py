"""Tests for deterministic enforcement gate (Section 16.6).

Tests the DeterministicEnforcementGate class from decision/enforcement.py:

- Each EnforcementViolationCode: CANDIDATE_NOT_GENERATED, EXECUTION_NOT_ACTIONABLE,
  DIRECTION_MISMATCH, INVALID_GEOMETRY, ACTION_NOT_ALLOWED
- Violation → BLOCKED_BY_ENFORCEMENT
- Non-approved review for executable → BLOCKED_BY_REVIEW
- Non-executable action passes without reviewer
- ReviewStatus.NOT_REQUIRED for deterministic bypass

NOTE: DecisionOutput has use_enum_values=True, so action is serialised as a str.
The enforcement gate now uses _EXECUTABLE_ACTION_VALUES (frozenset[str]) to
compare against plain string values, making the comparison robust.
We still use model_construct() in tests to exercise the same code paths.
"""

from __future__ import annotations

from config.settings import Settings
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
    RiskPolicyState,
    SetupClassificationStatus,
    SetupGrade,
    SetupLifecycleStatus,
    TradeDirection,
    TriggerStatus,
)
from src.decision.enforcement import _EXECUTABLE_ACTION_VALUES, DeterministicEnforcementGate
from src.decision.models import DecisionOutput, ReviewStatus, ReviewVerdict

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_setup(
    *,
    classification: SetupClassificationStatus = SetupClassificationStatus.CLASSIFIED,
    grade: SetupGrade | None = SetupGrade.AAA,
    trade_direction: TradeDirection = TradeDirection.BULLISH,
    geometry: GeometryStatus = GeometryStatus.VALID,
    lifecycle: SetupLifecycleStatus = SetupLifecycleStatus.TRIGGERED,
    trigger_status: TriggerStatus = TriggerStatus.CONFIRMED_TRIGGER,
    entry_price: float | None = 1.1010,
    target_price: float | None = 1.1100,
    invalidation_price: float | None = 1.0980,
    estimated_rr: float | None = 3.0,
    **kwargs,
) -> DeterministicSetupState:
    params = dict(
        setup_classification_status=classification,
        setup_grade=grade,
        trade_direction=trade_direction,
        setup_lifecycle_status=lifecycle,
        geometry_status=geometry,
        h1_trigger_status=trigger_status,
        h1_setup_status="VALID_SETUP",
        current_price=1.1000,
        entry_price=entry_price,
        entry_zone_low=1.1005,
        entry_zone_high=1.1015,
        trigger_level=1.1010,
        invalidation_price=invalidation_price,
        target_price=target_price,
        estimated_reward_risk=estimated_rr,
    )
    params.update(kwargs)
    return DeterministicSetupState(**params)


def _make_policy(
    *,
    trade_direction: TradeDirection = TradeDirection.BULLISH,
    execution_blockers: tuple[ExecutionBlocker, ...] = (),
) -> ExecutionPolicyState:
    """Create an ExecutionPolicyState with the given blockers.

    The computed fields pre_review_execution_status and allowed_actions
    are derived automatically from execution_blockers and trade_direction.
    """
    return ExecutionPolicyState(
        trade_direction=trade_direction,
        execution_blockers=execution_blockers,
    )


def _make_risk_policy(
    *,
    base_risk: float = 1.0,
    multiplier: float = 1.0,
    min_rr: float = 2.0,
    estimated_rr: float | None = 3.0,
) -> RiskPolicyState:
    return RiskPolicyState(
        base_risk_percentage=base_risk,
        grade_risk_multiplier=multiplier,
        minimum_reward_risk=min_rr,
        estimated_reward_risk=estimated_rr,
    )


def _make_decision(
    *,
    action: DecisionAction = DecisionAction.BUY_SETUP,
    symbol: str = "EURUSD",
    reasoning: str = "Test reasoning",
) -> DecisionOutput:
    """Create DecisionOutput with enum action preserved.

    Uses model_construct to bypass use_enum_values=True serialization,
    so that enforcement code can safely call .value on the action attribute.
    """
    return DecisionOutput.model_construct(
        symbol=symbol,
        action=action,
        reasoning=reasoning,
    )


def _make_review(
    *,
    status: ReviewStatus = ReviewStatus.APPROVED,
    reasoning: str = "Approved",
    approved: bool = True,
) -> ReviewVerdict:
    return ReviewVerdict(status=status, reasoning=reasoning)


def _policy_blocker() -> ExecutionBlocker:
    return ExecutionBlocker(
        blocker_type=ExecutionBlockerType.POLICY,
        code=ExecutionBlockerCode.POLICY_COUNTERTREND_DISABLED,
        reason="Countertrend disabled",
        severity=BlockerSeverity.INVALIDATES_GRADE,
    )


def _calendar_blocker() -> ExecutionBlocker:
    return ExecutionBlocker(
        blocker_type=ExecutionBlockerType.CALENDAR,
        code=ExecutionBlockerCode.CALENDAR_HIGH_IMPACT_SOON,
        reason="High-impact event imminent",
        severity=BlockerSeverity.EXECUTION_ONLY,
    )


# ============================================================================
# EnforcementViolationCode coverage — each code tested
# ============================================================================


class TestEnforcementViolationCodes:
    """Every EnforcementViolationCode from the enforcement gate can be produced."""

    def test_candidate_not_generated(self) -> None:
        """CANDIDATE_NOT_GENERATED: executable action without classified candidate."""
        setup = _make_setup(
            classification=SetupClassificationStatus.NO_SETUP,
            grade=None,
        )
        policy = _make_policy()
        risk = _make_risk_policy()
        decision = _make_decision(action=DecisionAction.BUY_SETUP)
        review = _make_review()
        settings = Settings()

        gate = DeterministicEnforcementGate()
        result = gate.enforce(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            settings=settings,
        )
        assert result.final_execution_status == ExecutionStatus.BLOCKED_BY_ENFORCEMENT
        assert result.final_action == DecisionAction.NO_TRADE
        codes = {v.code for v in result.enforcement_violations}
        assert EnforcementViolationCode.CANDIDATE_NOT_GENERATED in codes

    def test_execution_not_actionable(self) -> None:
        """EXECUTION_NOT_ACTIONABLE: executable action while status is not ACTIONABLE."""
        setup = _make_setup()
        # POLICY blocker produces BLOCKED_BY_POLICY status
        policy = _make_policy(execution_blockers=(_policy_blocker(),))
        risk = _make_risk_policy()
        decision = _make_decision(action=DecisionAction.BUY_SETUP)
        review = _make_review()
        settings = Settings()

        gate = DeterministicEnforcementGate()
        result = gate.enforce(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            settings=settings,
        )
        assert result.final_execution_status == ExecutionStatus.BLOCKED_BY_ENFORCEMENT
        codes = {v.code for v in result.enforcement_violations}
        assert EnforcementViolationCode.EXECUTION_NOT_ACTIONABLE in codes

    def test_direction_mismatch(self) -> None:
        """DIRECTION_MISMATCH: decision contradicts deterministic direction."""
        setup = _make_setup(trade_direction=TradeDirection.BEARISH)
        policy = _make_policy(trade_direction=TradeDirection.BEARISH)
        risk = _make_risk_policy()
        # BUY_SETUP implies BULLISH but setup direction is BEARISH
        decision = _make_decision(action=DecisionAction.BUY_SETUP)
        review = _make_review()
        settings = Settings()

        gate = DeterministicEnforcementGate()
        result = gate.enforce(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            settings=settings,
        )
        assert result.final_execution_status == ExecutionStatus.BLOCKED_BY_ENFORCEMENT
        codes = {v.code for v in result.enforcement_violations}
        assert EnforcementViolationCode.DIRECTION_MISMATCH in codes

    def test_invalid_geometry(self) -> None:
        """INVALID_GEOMETRY: executable action with non-VALID geometry."""
        setup = _make_setup(geometry=GeometryStatus.TEMPORARILY_UNAVAILABLE)
        policy = _make_policy()
        risk = _make_risk_policy()
        decision = _make_decision(action=DecisionAction.BUY_SETUP)
        review = _make_review()
        settings = Settings()

        gate = DeterministicEnforcementGate()
        result = gate.enforce(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            settings=settings,
        )
        assert result.final_execution_status == ExecutionStatus.BLOCKED_BY_ENFORCEMENT
        codes = {v.code for v in result.enforcement_violations}
        assert EnforcementViolationCode.INVALID_GEOMETRY in codes

    def test_action_not_allowed(self) -> None:
        """ACTION_NOT_ALLOWED: decision action not in allowed set.

        The strategy: use NEUTRAL trade direction so that allowed_actions
        is (NO_TRADE,) while avoiding DIRECTION_MISMATCH (which only
        triggers for non-NEUTRAL directions).
        """
        setup = _make_setup(trade_direction=TradeDirection.NEUTRAL)
        policy = _make_policy(trade_direction=TradeDirection.NEUTRAL)
        risk = _make_risk_policy()
        # SELL_SETUP is executable but not in (NO_TRADE,)
        decision = _make_decision(action=DecisionAction.SELL_SETUP)
        review = _make_review()
        settings = Settings()

        gate = DeterministicEnforcementGate()
        result = gate.enforce(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            settings=settings,
        )
        assert result.final_execution_status == ExecutionStatus.BLOCKED_BY_ENFORCEMENT
        codes = {v.code for v in result.enforcement_violations}
        assert EnforcementViolationCode.ACTION_NOT_ALLOWED in codes

    def test_multiple_violations_in_one_call(self) -> None:
        """Multiple violation types can fire in the same enforce() call."""
        # NO_SETUP → candidate_not_generated
        # NEUTRAL direction → DIRECTION_MISMATCH is skipped, but...
        # SELL_SETUP not in (NO_TRADE,) allowed_actions → ACTION_NOT_ALLOWED
        setup = _make_setup(
            classification=SetupClassificationStatus.NO_SETUP,
            grade=None,
            trade_direction=TradeDirection.NEUTRAL,
        )
        policy = _make_policy(trade_direction=TradeDirection.NEUTRAL)
        risk = _make_risk_policy()
        decision = _make_decision(action=DecisionAction.SELL_SETUP)
        review = _make_review()
        settings = Settings()

        gate = DeterministicEnforcementGate()
        result = gate.enforce(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            settings=settings,
        )
        codes = {v.code for v in result.enforcement_violations}
        assert EnforcementViolationCode.CANDIDATE_NOT_GENERATED in codes
        assert EnforcementViolationCode.ACTION_NOT_ALLOWED in codes


# ============================================================================
# Violation → BLOCKED_BY_ENFORCEMENT
# ============================================================================


class TestViolationLeadsToBlockedByEnforcement:
    """Any violation forces BLOCKED_BY_ENFORCEMENT + NO_TRADE."""

    def test_single_violation_blocks(self) -> None:
        setup = _make_setup(geometry=GeometryStatus.TEMPORARILY_UNAVAILABLE)
        policy = _make_policy()
        risk = _make_risk_policy()
        decision = _make_decision(action=DecisionAction.BUY_SETUP)
        review = _make_review()
        settings = Settings()

        gate = DeterministicEnforcementGate()
        result = gate.enforce(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            settings=settings,
        )
        assert result.final_execution_status == ExecutionStatus.BLOCKED_BY_ENFORCEMENT
        assert result.final_action == DecisionAction.NO_TRADE
        assert len(result.enforcement_violations) >= 1

    def test_multiple_violations_accumulate(self) -> None:
        """Multiple violations are accumulated, not just the first."""
        setup = _make_setup(
            classification=SetupClassificationStatus.NO_SETUP,
            grade=None,
            trade_direction=TradeDirection.NEUTRAL,
            geometry=GeometryStatus.TEMPORARILY_UNAVAILABLE,
            entry_price=None,
            target_price=None,
            invalidation_price=None,
        )
        policy = _make_policy(trade_direction=TradeDirection.NEUTRAL)
        risk = _make_risk_policy()
        decision = _make_decision(action=DecisionAction.SELL_SETUP)
        review = _make_review()
        settings = Settings()

        gate = DeterministicEnforcementGate()
        result = gate.enforce(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            settings=settings,
        )
        # Should have: CANDIDATE_NOT_GENERATED, ACTION_NOT_ALLOWED (INVALID_GEOMETRY
        # would fire IF it were an executable action, but SELL_SETUP → geometry check
        # also fires since SELL_SETUP is in _EXECUTABLE_ACTION_VALUES)
        assert len(result.enforcement_violations) >= 2
        assert result.final_execution_status == ExecutionStatus.BLOCKED_BY_ENFORCEMENT
        assert result.final_action == DecisionAction.NO_TRADE

    def test_violations_recorded_in_output(self) -> None:
        setup = _make_setup(classification=SetupClassificationStatus.NO_SETUP, grade=None)
        policy = _make_policy()
        risk = _make_risk_policy()
        decision = _make_decision(action=DecisionAction.BUY_SETUP)
        review = _make_review()
        settings = Settings()

        gate = DeterministicEnforcementGate()
        result = gate.enforce(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            settings=settings,
        )
        assert len(result.enforcement_violations) > 0
        violation = result.enforcement_violations[0]
        assert hasattr(violation, "code")
        assert hasattr(violation, "reason")
        assert violation.code == EnforcementViolationCode.CANDIDATE_NOT_GENERATED


# ============================================================================
# Non-approved review for executable → BLOCKED_BY_REVIEW
# ============================================================================


class TestBlockedByReview:
    """Executable action without approved review → BLOCKED_BY_REVIEW."""

    def test_unapproved_review_blocks_executable(self) -> None:
        setup = _make_setup()
        policy = _make_policy()
        risk = _make_risk_policy()
        decision = _make_decision(action=DecisionAction.BUY_SETUP)
        review = _make_review(status=ReviewStatus.REJECTED, approved=False)
        settings = Settings()

        gate = DeterministicEnforcementGate()
        result = gate.enforce(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            settings=settings,
        )
        assert result.final_execution_status == ExecutionStatus.BLOCKED_BY_REVIEW
        assert result.final_action == DecisionAction.NO_TRADE
        assert len(result.enforcement_violations) == 0

    def test_revision_required_blocks_executable(self) -> None:
        setup = _make_setup()
        policy = _make_policy()
        risk = _make_risk_policy()
        decision = _make_decision(action=DecisionAction.BUY_SETUP)
        review = _make_review(status=ReviewStatus.REVISION_REQUIRED, approved=False)
        settings = Settings()

        gate = DeterministicEnforcementGate()
        result = gate.enforce(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            settings=settings,
        )
        assert result.final_execution_status == ExecutionStatus.BLOCKED_BY_REVIEW

    def test_approved_review_passes_for_executable(self) -> None:
        setup = _make_setup()
        policy = _make_policy()
        risk = _make_risk_policy()
        decision = _make_decision(action=DecisionAction.BUY_SETUP)
        review = _make_review(status=ReviewStatus.APPROVED, approved=True)
        settings = Settings()

        gate = DeterministicEnforcementGate()
        result = gate.enforce(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            settings=settings,
        )
        assert result.final_execution_status == ExecutionStatus.ACTIONABLE
        assert result.final_action == DecisionAction.BUY_SETUP
        assert len(result.enforcement_violations) == 0


# ============================================================================
# Non-executable action passes without reviewer
# ============================================================================


class TestNonExecutableActions:
    """Non-executable actions (NO_TRADE, WAIT_FOR_SETUP) pass regardless of review."""

    def test_no_trade_passes_without_approval(self) -> None:
        """NO_TRADE is non-executable and is in allowed_actions for NEUTRAL direction,
        so it passes the enforcement gate without violations or review."""
        setup = _make_setup(trade_direction=TradeDirection.NEUTRAL)
        policy = _make_policy(trade_direction=TradeDirection.NEUTRAL)
        risk = _make_risk_policy()
        decision = _make_decision(action=DecisionAction.NO_TRADE)
        review = _make_review(status=ReviewStatus.REJECTED, approved=False)
        settings = Settings()

        gate = DeterministicEnforcementGate()
        result = gate.enforce(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            settings=settings,
        )
        # Non-executable action: no enforcement violations, review check bypassed
        assert result.final_execution_status == ExecutionStatus.ACTIONABLE
        assert result.final_action == DecisionAction.NO_TRADE
        assert len(result.enforcement_violations) == 0

    def test_wait_for_setup_triggers_action_not_allowed(self) -> None:
        """WAIT_FOR_SETUP is never returned by derive_allowed_actions, so it
        always triggers ACTION_NOT_ALLOWED. However, it IS non-executable so
        the review check is bypassed. The violation comes from allowed_actions,
        not from needing a reviewer."""
        setup = _make_setup()
        policy = _make_policy()
        risk = _make_risk_policy()
        decision = _make_decision(action=DecisionAction.WAIT_FOR_SETUP)
        review = _make_review(status=ReviewStatus.REVIEW_UNAVAILABLE, approved=False)
        settings = Settings()

        gate = DeterministicEnforcementGate()
        result = gate.enforce(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            settings=settings,
        )
        # WAIT_FOR_SETUP triggers ACTION_NOT_ALLOWED (not in allowed_actions)
        assert result.final_execution_status == ExecutionStatus.BLOCKED_BY_ENFORCEMENT
        codes = {v.code for v in result.enforcement_violations}
        assert EnforcementViolationCode.ACTION_NOT_ALLOWED in codes


# ============================================================================
# ReviewStatus.NOT_REQUIRED for deterministic bypass
# ============================================================================


class TestNotRequiredReview:
    """NOT_REQUIRED review status interaction with enforcement gate."""

    def test_not_required_blocks_executable(self) -> None:
        """NOT_REQUIRED is not APPROVED, so executable actions are blocked."""
        setup = _make_setup()
        policy = _make_policy()
        risk = _make_risk_policy()
        decision = _make_decision(action=DecisionAction.BUY_SETUP)
        review = _make_review(status=ReviewStatus.NOT_REQUIRED, approved=False)
        settings = Settings()

        gate = DeterministicEnforcementGate()
        result = gate.enforce(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            settings=settings,
        )
        # NOT_REQUIRED is not approved (approved property checks == APPROVED)
        # So executable actions are BLOCKED_BY_REVIEW
        assert result.final_execution_status == ExecutionStatus.BLOCKED_BY_REVIEW
        assert result.final_action == DecisionAction.NO_TRADE

    def test_not_required_with_non_executable_passes(self) -> None:
        """Non-executable actions bypass the review check regardless of approval.
        Using NEUTRAL direction so NO_TRADE is in allowed_actions."""
        setup = _make_setup(trade_direction=TradeDirection.NEUTRAL)
        policy = _make_policy(trade_direction=TradeDirection.NEUTRAL)
        risk = _make_risk_policy()
        decision = _make_decision(action=DecisionAction.NO_TRADE)
        review = _make_review(status=ReviewStatus.NOT_REQUIRED, approved=False)
        settings = Settings()

        gate = DeterministicEnforcementGate()
        result = gate.enforce(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            settings=settings,
        )
        # NO_TRADE is non-executable, bypasses review check
        assert result.final_action == DecisionAction.NO_TRADE
        assert len(result.enforcement_violations) == 0


# ============================================================================
# Pass-through: no violations + approved review
# ============================================================================


class TestPassThrough:
    """When no violations and review is approved, status/action pass through."""

    def test_actionable_passes_through(self) -> None:
        setup = _make_setup()
        policy = _make_policy()
        risk = _make_risk_policy()
        decision = _make_decision(action=DecisionAction.BUY_SETUP)
        review = _make_review()
        settings = Settings()

        gate = DeterministicEnforcementGate()
        result = gate.enforce(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            settings=settings,
        )
        assert result.final_execution_status == ExecutionStatus.ACTIONABLE
        assert result.final_action == DecisionAction.BUY_SETUP
        assert len(result.enforcement_violations) == 0

    def test_blocked_by_calendar_passes_through(self) -> None:
        """Non-ACTIONABLE status passes through when no violations and action is non-executable."""
        setup = _make_setup()
        policy = _make_policy(execution_blockers=(_calendar_blocker(),))
        risk = _make_risk_policy()
        decision = _make_decision(action=DecisionAction.NO_TRADE)
        review = _make_review()
        settings = Settings()

        gate = DeterministicEnforcementGate()
        result = gate.enforce(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            settings=settings,
        )
        assert result.final_execution_status == ExecutionStatus.BLOCKED_BY_CALENDAR
        assert result.final_action == DecisionAction.NO_TRADE

    def test_enforcement_violations_empty_when_no_issues(self) -> None:
        setup = _make_setup()
        policy = _make_policy()
        risk = _make_risk_policy()
        decision = _make_decision(action=DecisionAction.BUY_SETUP)
        review = _make_review()
        settings = Settings()

        gate = DeterministicEnforcementGate()
        result = gate.enforce(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            settings=settings,
        )
        assert len(result.enforcement_violations) == 0


# ============================================================================
# Edge cases
# ============================================================================


class TestEnforcementGateEdgeCases:
    """Edge cases for the enforcement gate."""

    def test_direction_mismatch_not_raised_for_non_executable(self) -> None:
        """DIRECTION_MISMATCH is only checked for executable actions.
        Using a CALENDAR blocker so status is not ACTIONABLE, making
        allowed_actions = (NO_TRADE,) which includes the NO_TRADE action."""
        setup = _make_setup(trade_direction=TradeDirection.BEARISH)
        policy = _make_policy(
            trade_direction=TradeDirection.BEARISH,
            execution_blockers=(_calendar_blocker(),),
        )
        risk = _make_risk_policy()
        decision = _make_decision(action=DecisionAction.NO_TRADE)
        review = _make_review()
        settings = Settings()

        gate = DeterministicEnforcementGate()
        result = gate.enforce(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            settings=settings,
        )
        assert len(result.enforcement_violations) == 0

    def test_executable_actions_set_is_correct(self) -> None:
        assert DecisionAction.BUY_SETUP in _EXECUTABLE_ACTION_VALUES
        assert DecisionAction.SELL_SETUP in _EXECUTABLE_ACTION_VALUES
        assert DecisionAction.NO_TRADE not in _EXECUTABLE_ACTION_VALUES
        assert DecisionAction.WAIT_FOR_SETUP not in _EXECUTABLE_ACTION_VALUES

    def test_provider_and_review_counts_in_output(self) -> None:
        setup = _make_setup()
        policy = _make_policy()
        risk = _make_risk_policy()
        decision = _make_decision(action=DecisionAction.BUY_SETUP)
        review = _make_review()
        settings = Settings()

        gate = DeterministicEnforcementGate()
        result = gate.enforce(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            settings=settings,
            provider_retry_count=2,
            review_revision_count=1,
        )
        assert result.provider_retry_count == 2
        assert result.review_revision_count == 1

    def test_empty_setup_no_candidate(self) -> None:
        """An empty/minimal setup should still produce violations correctly."""
        setup = _make_setup(
            classification=SetupClassificationStatus.NO_SETUP,
            grade=None,
            trade_direction=TradeDirection.NEUTRAL,
            geometry=GeometryStatus.TEMPORARILY_UNAVAILABLE,
            entry_price=None,
            target_price=None,
            invalidation_price=None,
        )
        policy = _make_policy(trade_direction=TradeDirection.NEUTRAL)
        risk = _make_risk_policy()
        decision = _make_decision(action=DecisionAction.BUY_SETUP)
        review = _make_review()
        settings = Settings()

        gate = DeterministicEnforcementGate()
        result = gate.enforce(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            settings=settings,
        )
        assert result.final_execution_status == ExecutionStatus.BLOCKED_BY_ENFORCEMENT
        assert result.final_action == DecisionAction.NO_TRADE

    def test_approved_review_with_calendar_blocker_passes_through(self) -> None:
        """Approved review with calendar blocker passes through the calendar status
        (not BLOCKED_BY_ENFORCEMENT) because there are no enforcement violations.
        NO_TRADE is non-executable so review is not enforced."""
        setup = _make_setup()
        policy = _make_policy(execution_blockers=(_calendar_blocker(),))
        risk = _make_risk_policy()
        decision = _make_decision(action=DecisionAction.NO_TRADE)
        review = _make_review(status=ReviewStatus.APPROVED, approved=True)
        settings = Settings()

        gate = DeterministicEnforcementGate()
        result = gate.enforce(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            settings=settings,
        )
        assert result.final_execution_status == ExecutionStatus.BLOCKED_BY_CALENDAR
        assert result.final_action == DecisionAction.NO_TRADE
        assert len(result.enforcement_violations) == 0
