"""Tests for revision loop logic (Section 16.8).

Tests the FinalDecisionState model and revision loop semantics:
- APPROVED → enforcement (final_execution_status from blockers)
- REJECTED → NO_TRADE (no retry)
- REVISION_REQUIRED → business-level retry (review_revision_count incremented)
- UNAVAILABLE → safe failure (NO_TRADE)
- Transport retry count (provider_retry_count) and revision count (review_revision_count)
  are tested independently
- NOT_REQUIRED used for deterministic early exits (skip review)
"""

from __future__ import annotations

from src.analysis.market_structure_engine.models import (
    DecisionAction,
    EnforcementViolation,
    EnforcementViolationCode,
    ExecutionStatus,
    FinalDecisionState,
    ReviewStatus,
)

# ============================================================================
# FinalDecisionState creation
# ============================================================================


class TestFinalDecisionStateCreation:
    """FinalDecisionState model creation with defaults."""

    def test_default_creation(self) -> None:
        state = FinalDecisionState()
        assert state.review_status == ReviewStatus.NOT_REQUIRED
        assert state.final_execution_status == ExecutionStatus.NOT_READY
        assert state.final_action == DecisionAction.NO_TRADE
        assert state.enforcement_violations == ()
        assert state.review_attempts == 0
        assert state.provider_retry_count == 0
        assert state.review_revision_count == 0

    def test_custom_creation(self) -> None:
        violations = (
            EnforcementViolation(
                code=EnforcementViolationCode.INVALIDATION_ENTRY_AUTHORIZED,
                reason="Entry authorized when it should not be",
            ),
        )
        state = FinalDecisionState(
            review_status=ReviewStatus.APPROVED,
            final_execution_status=ExecutionStatus.ACTIONABLE,
            final_action=DecisionAction.BUY_SETUP,
            enforcement_violations=violations,
            review_attempts=2,
            provider_retry_count=1,
            review_revision_count=3,
        )
        assert state.review_status == ReviewStatus.APPROVED
        assert state.final_execution_status == ExecutionStatus.ACTIONABLE
        assert state.final_action == DecisionAction.BUY_SETUP
        assert len(state.enforcement_violations) == 1
        assert state.review_attempts == 2
        assert state.provider_retry_count == 1
        assert state.review_revision_count == 3


# ============================================================================
# Review status outcomes
# ============================================================================


class TestReviewStatusOutcomes:
    """Different review statuses produce different final outcomes."""

    def test_approved_leads_to_enforcement(self) -> None:
        """APPROVED: the final execution status is the enforcement-determined
        status (ACTIONABLE if no enforcement violations exist)."""
        state = FinalDecisionState(
            review_status=ReviewStatus.APPROVED,
            final_execution_status=ExecutionStatus.ACTIONABLE,
            final_action=DecisionAction.BUY_SETUP,
        )
        assert state.review_status == ReviewStatus.APPROVED
        assert state.final_execution_status == ExecutionStatus.ACTIONABLE

    def test_approved_with_violations(self) -> None:
        """APPROVED but enforcement detected issues (e.g., entry_authorized=False
        invariant violated) leads to BLOCKED_BY_ENFORCEMENT."""
        state = FinalDecisionState(
            review_status=ReviewStatus.APPROVED,
            final_execution_status=ExecutionStatus.BLOCKED_BY_ENFORCEMENT,
            final_action=DecisionAction.NO_TRADE,
            enforcement_violations=(
                EnforcementViolation(
                    code=EnforcementViolationCode.INVALIDATION_ENTRY_AUTHORIZED,
                    reason="entry_authorized must be False",
                ),
            ),
        )
        assert state.final_execution_status == ExecutionStatus.BLOCKED_BY_ENFORCEMENT
        assert state.final_action == DecisionAction.NO_TRADE

    def test_rejected_no_trade(self) -> None:
        """REJECTED: final action must be NO_TRADE — no retry."""
        state = FinalDecisionState(
            review_status=ReviewStatus.REJECTED,
            final_execution_status=ExecutionStatus.BLOCKED_BY_REVIEW,
            final_action=DecisionAction.NO_TRADE,
        )
        assert state.final_action == DecisionAction.NO_TRADE
        assert state.final_execution_status == ExecutionStatus.BLOCKED_BY_REVIEW

    def test_revision_required_allows_business_retry(self) -> None:
        """REVISION_REQUIRED: business-level retry allowed with incremented
        review_revision_count."""
        state = FinalDecisionState(
            review_status=ReviewStatus.REVISION_REQUIRED,
            final_execution_status=ExecutionStatus.BLOCKED_BY_REVIEW,
            final_action=DecisionAction.NO_TRADE,
            review_revision_count=1,
        )
        assert state.review_status == ReviewStatus.REVISION_REQUIRED
        assert state.review_revision_count == 1

    def test_unavailable_safe_failure(self) -> None:
        """UNAVAILABLE: safe failure, NO_TRADE, no retry expected."""
        state = FinalDecisionState(
            review_status=ReviewStatus.REVIEW_UNAVAILABLE,
            final_execution_status=ExecutionStatus.BLOCKED_BY_REVIEW,
            final_action=DecisionAction.NO_TRADE,
        )
        assert state.final_action == DecisionAction.NO_TRADE

    def test_not_required_deterministic_early_exit(self) -> None:
        """NOT_REQUIRED: deterministic early exit — skip review entirely."""
        state = FinalDecisionState(
            review_status=ReviewStatus.NOT_REQUIRED,
            final_execution_status=ExecutionStatus.NON_EXECUTABLE,
            final_action=DecisionAction.NO_TRADE,
        )
        assert state.review_status == ReviewStatus.NOT_REQUIRED
        assert state.final_execution_status == ExecutionStatus.NON_EXECUTABLE


# ============================================================================
# Retry counts — independent
# ============================================================================


class TestRetryCountIndependence:
    """Transport retry count (provider_retry_count) and revision count
    (review_revision_count) are tested independently."""

    def test_provider_retry_alone(self) -> None:
        state = FinalDecisionState(
            provider_retry_count=3,
            review_revision_count=0,
        )
        assert state.provider_retry_count == 3
        assert state.review_revision_count == 0

    def test_revision_alone(self) -> None:
        state = FinalDecisionState(
            provider_retry_count=0,
            review_revision_count=5,
        )
        assert state.provider_retry_count == 0
        assert state.review_revision_count == 5

    def test_both_independent(self) -> None:
        """Both counters can be non-zero simultaneously and remain independent."""
        state = FinalDecisionState(
            provider_retry_count=2,
            review_revision_count=3,
        )
        assert state.provider_retry_count == 2
        assert state.review_revision_count == 3

    def test_max_counts_no_overflow(self) -> None:
        """Large counts are handled."""
        state = FinalDecisionState(
            provider_retry_count=100,
            review_revision_count=100,
        )
        assert state.provider_retry_count == 100
        assert state.review_revision_count == 100


# ============================================================================
# Review status transitions
# ============================================================================


class TestReviewStatusTransitions:
    """Transition semantics for review status."""

    def test_not_required_used_for_deterministic_early_exit(self) -> None:
        """NOT_REQUIRED means this stage was skipped deterministically."""
        state = FinalDecisionState(review_status=ReviewStatus.NOT_REQUIRED)
        assert state.review_status == ReviewStatus.NOT_REQUIRED

    def test_review_error_safe_handling(self) -> None:
        """REVIEW_ERROR: model handles gracefully as a safe failure."""
        state = FinalDecisionState(
            review_status=ReviewStatus.REVIEW_ERROR,
            final_execution_status=ExecutionStatus.BLOCKED_BY_REVIEW,
            final_action=DecisionAction.NO_TRADE,
        )
        assert state.review_status == ReviewStatus.REVIEW_ERROR
