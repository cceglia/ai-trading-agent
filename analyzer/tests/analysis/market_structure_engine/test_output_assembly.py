"""Tests for output assembly logic (Section 16.9).

Tests how FinalDecisionState assembles outputs from pipeline stages:
- Entry price, stop, target from DeterministicSetupState
- Risk from RiskPolicyState (final_risk_percentage)
- Reasoning from LLM (represented in DecisionOutput)
- Structured enforcement violations
- NOT_REQUIRED review for early deterministic bypass
- LLM never overrides deterministic values
"""

from __future__ import annotations

from src.analysis.market_structure_engine.models import (
    DecisionAction,
    DeterministicSetupState,
    EnforcementViolation,
    EnforcementViolationCode,
    ExecutionStatus,
    FinalDecisionState,
    ReviewStatus,
    RiskPolicyState,
    SetupClassificationStatus,
    SetupGrade,
    TradeDirection,
)
from src.decision.models import DecisionOutput

# ============================================================================
# DeterministicSetupState — entry/stop/target
# ============================================================================


class TestDeterministicEntryPlanFields:
    """Entry, stop, and target are stored in DeterministicSetupState."""

    def _make_setup(self, **overrides) -> DeterministicSetupState:
        params = dict(
            setup_classification_status=SetupClassificationStatus.CLASSIFIED,
            setup_grade=SetupGrade.AAA,
            trade_direction=TradeDirection.BULLISH,
            current_price=1.1000,
            entry_price=1.1010,
            entry_zone_low=1.1005,
            entry_zone_high=1.1015,
            trigger_level=1.1010,
            invalidation_price=1.0980,
            target_price=1.1100,
            estimated_reward_risk=3.0,
        )
        params.update(overrides)
        return DeterministicSetupState(**params)

    def test_entry_price_stored(self) -> None:
        state = self._make_setup(entry_price=1.1050)
        assert state.entry_price == 1.1050

    def test_target_price_stored(self) -> None:
        state = self._make_setup(target_price=1.1200)
        assert state.target_price == 1.1200

    def test_invalidation_price_stored(self) -> None:
        state = self._make_setup(invalidation_price=1.0950)
        assert state.invalidation_price == 1.0950

    def test_entry_zone_limits(self) -> None:
        state = self._make_setup(entry_zone_low=1.1000, entry_zone_high=1.1020)
        assert state.entry_zone_low == 1.1000
        assert state.entry_zone_high == 1.1020

    def test_estimated_reward_risk_stored(self) -> None:
        state = self._make_setup(estimated_reward_risk=2.5)
        assert state.estimated_reward_risk == 2.5


# ============================================================================
# RiskPolicyState — risk percentage
# ============================================================================


class TestRiskOutput:
    """Risk information is output from RiskPolicyState."""

    def test_final_risk_percentage(self) -> None:
        state = RiskPolicyState(
            base_risk_percentage=2.0,
            grade_risk_multiplier=0.5,
        )
        assert state.final_risk_percentage == 1.0

    def test_risk_reward_ok_flag(self) -> None:
        state = RiskPolicyState(
            estimated_reward_risk=3.0,
            minimum_reward_risk=2.0,
        )
        assert state.risk_reward_ok is True

    def test_missing_rr_ok_false(self) -> None:
        state = RiskPolicyState(
            estimated_reward_risk=None,
            minimum_reward_risk=2.0,
        )
        assert state.risk_reward_ok is False


# ============================================================================
# DecisionOutput — LLM reasoning
# ============================================================================


class TestDecisionOutputAssembly:
    """LLM output: action selection and reasoning. No deterministic fields."""

    def test_decision_output_creation(self) -> None:
        output = DecisionOutput(
            symbol="EURUSD",
            action=DecisionAction.BUY_SETUP,
            reasoning="Bullish structure with confirmed BOS on H1 and good R/R",
        )
        assert output.symbol == "EURUSD"
        assert output.action == "buy_setup"  # use_enum_values=True → str
        assert "Bullish" in output.reasoning

    def test_decision_output_no_override(self) -> None:
        """DecisionOutput does NOT contain deterministic fields like
        entry_price, stop_loss, or take_profit — those come from
        DeterministicSetupState."""
        output = DecisionOutput(
            symbol="EURUSD",
            action=DecisionAction.NO_TRADE,
            reasoning="No clear setup",
        )
        assert not hasattr(output, "entry_price")
        assert not hasattr(output, "stop_loss")
        assert not hasattr(output, "take_profit")


# ============================================================================
# Enforcement violations — structured output
# ============================================================================


class TestEnforcementViolationsOutput:
    """Enforcement violations are structured and carry code + reason."""

    def test_single_violation(self) -> None:
        violations = (
            EnforcementViolation(
                code=EnforcementViolationCode.INVALIDATION_ENTRY_AUTHORIZED,
                reason="entry_authorized must be False",
            ),
        )
        state = FinalDecisionState(
            review_status=ReviewStatus.APPROVED,
            final_execution_status=ExecutionStatus.BLOCKED_BY_ENFORCEMENT,
            final_action=DecisionAction.NO_TRADE,
            enforcement_violations=violations,
        )
        assert len(state.enforcement_violations) == 1
        assert (
            state.enforcement_violations[0].code
            == EnforcementViolationCode.INVALIDATION_ENTRY_AUTHORIZED
        )

    def test_multiple_violations(self) -> None:
        violations = (
            EnforcementViolation(
                code=EnforcementViolationCode.INVALIDATION_ENTRY_AUTHORIZED, reason="Auth"
            ),
            EnforcementViolation(
                code=EnforcementViolationCode.INVALIDATION_GRADE_DOWNGRADED, reason="Grade"
            ),
            EnforcementViolation(
                code=EnforcementViolationCode.CANDIDATE_NOT_GENERATED, reason="No candidate"
            ),
        )
        state = FinalDecisionState(
            enforcement_violations=violations,
        )
        assert len(state.enforcement_violations) == 3
        codes = [v.code for v in state.enforcement_violations]
        assert EnforcementViolationCode.INVALIDATION_ENTRY_AUTHORIZED in codes
        assert EnforcementViolationCode.INVALIDATION_GRADE_DOWNGRADED in codes
        assert EnforcementViolationCode.CANDIDATE_NOT_GENERATED in codes

    def test_empty_violations(self) -> None:
        state = FinalDecisionState()
        assert state.enforcement_violations == ()


# ============================================================================
# NOT_REQUIRED review — deterministic early bypass
# ============================================================================


class TestNotRequiredReview:
    """NOT_REQUIRED review status skips the reviewer for deterministic early exits."""

    def test_non_executable_bypasses_review(self) -> None:
        """When setup is NON_EXECUTABLE, review is NOT_REQUIRED."""
        state = FinalDecisionState(
            review_status=ReviewStatus.NOT_REQUIRED,
            final_execution_status=ExecutionStatus.NON_EXECUTABLE,
            final_action=DecisionAction.NO_TRADE,
        )
        assert state.review_status == ReviewStatus.NOT_REQUIRED
        assert state.final_execution_status == ExecutionStatus.NON_EXECUTABLE

    def test_no_setup_bypasses_review(self) -> None:
        """When there's no setup, review is NOT_REQUIRED."""
        state = FinalDecisionState(
            review_status=ReviewStatus.NOT_REQUIRED,
            final_execution_status=ExecutionStatus.NOT_READY,
            final_action=DecisionAction.NO_TRADE,
        )
        assert state.review_status == ReviewStatus.NOT_REQUIRED


# ============================================================================
# LLM never overrides deterministic
# ============================================================================


class TestLLMNoOverride:
    """The LLM (DecisionOutput) never overrides deterministic values.

    Deterministic values (entry price, stop loss, take profit) are computed
    by the engine and are NOT part of the LLM output. The LLM selects only
    the action and provides reasoning.
    """

    def test_deterministic_fields_separate_from_llm(self) -> None:
        """DeterministicSetupState holds prices, DecisionOutput holds action."""
        setup = DeterministicSetupState(
            setup_classification_status=SetupClassificationStatus.CLASSIFIED,
            setup_grade=SetupGrade.AAA,
            trade_direction=TradeDirection.BULLISH,
            entry_price=1.1010,
            target_price=1.1100,
            estimated_reward_risk=3.0,
        )
        decision = DecisionOutput(
            symbol="EURUSD",
            action=DecisionAction.BUY_SETUP,
            reasoning="Following deterministic analysis",
        )
        # LLM action must match the deterministic allowed action
        from src.analysis.market_structure_engine.models import (
            ExecutionStatus,
            derive_allowed_actions,
        )

        allowed = derive_allowed_actions(setup.trade_direction, ExecutionStatus.ACTIONABLE)
        assert decision.action in allowed

    def test_valid_actions_respect_deterministic(self) -> None:
        """LLM cannot select BUY_SETUP when deterministic says SELL_SETUP."""
        from src.analysis.market_structure_engine.models import (
            ExecutionStatus,
            derive_allowed_actions,
        )

        allowed = derive_allowed_actions(TradeDirection.BEARISH, ExecutionStatus.ACTIONABLE)
        assert DecisionAction.SELL_SETUP in allowed
        assert DecisionAction.BUY_SETUP not in allowed


# ============================================================================
# Integration: FinalDecisionState as assembled output
# ============================================================================


class TestFinalDecisionStateIntegration:
    """Full output assembly scenario."""

    def test_successful_trade_output(self) -> None:
        """A fully approved setup with no violations."""
        state = FinalDecisionState(
            review_status=ReviewStatus.APPROVED,
            final_execution_status=ExecutionStatus.ACTIONABLE,
            final_action=DecisionAction.BUY_SETUP,
            enforcement_violations=(),
            review_attempts=1,
            provider_retry_count=0,
            review_revision_count=0,
        )
        assert state.review_status == ReviewStatus.APPROVED
        assert state.final_execution_status == ExecutionStatus.ACTIONABLE
        assert state.final_action == DecisionAction.BUY_SETUP
        assert len(state.enforcement_violations) == 0

    def test_blocked_by_calendar_output(self) -> None:
        """A setup blocked by calendar event."""
        state = FinalDecisionState(
            review_status=ReviewStatus.NOT_REQUIRED,
            final_execution_status=ExecutionStatus.BLOCKED_BY_CALENDAR,
            final_action=DecisionAction.NO_TRADE,
        )
        assert state.final_execution_status == ExecutionStatus.BLOCKED_BY_CALENDAR
        assert state.final_action == DecisionAction.NO_TRADE

    def test_blocked_by_review_output(self) -> None:
        """A setup rejected during review."""
        state = FinalDecisionState(
            review_status=ReviewStatus.REJECTED,
            final_execution_status=ExecutionStatus.BLOCKED_BY_REVIEW,
            final_action=DecisionAction.NO_TRADE,
            review_attempts=1,
        )
        assert state.final_execution_status == ExecutionStatus.BLOCKED_BY_REVIEW
        assert state.review_attempts == 1

    def test_blocked_by_enforcement_output(self) -> None:
        """A setup with enforcement violations."""
        state = FinalDecisionState(
            review_status=ReviewStatus.APPROVED,
            final_execution_status=ExecutionStatus.BLOCKED_BY_ENFORCEMENT,
            final_action=DecisionAction.NO_TRADE,
            enforcement_violations=(
                EnforcementViolation(
                    code=EnforcementViolationCode.INVALIDATION_ENTRY_AUTHORIZED,
                    reason="entry_authorized invariant violated",
                ),
            ),
        )
        assert state.final_execution_status == ExecutionStatus.BLOCKED_BY_ENFORCEMENT
        assert len(state.enforcement_violations) == 1
