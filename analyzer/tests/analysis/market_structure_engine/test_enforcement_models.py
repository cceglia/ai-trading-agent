"""Tests for enforcement logic and models (Section 16.6).

Tests the enforcement-related functions from models.py:
- EnforcementViolationCode coverage — every code is tested
- derive_execution_status() priority: CALENDAR > DATA_QUALITY > POLICY > ENFORCEMENT > REVIEW
- derive_allowed_actions() for ACTIONABLE vs blocked states
- Reviewer requires only for executable actions (ACTIONABLE status)
- Deterministic violations produce BLOCKED_BY_ENFORCEMENT
- Non-approved review without deterministic violations produces BLOCKED_BY_REVIEW
- Non-executable actions pass without reviewer
"""

from __future__ import annotations

import pytest

from src.analysis.market_structure_engine.models import (
    BlockerSeverity,
    DecisionAction,
    EnforcementViolation,
    EnforcementViolationCode,
    ExecutionBlocker,
    ExecutionBlockerCode,
    ExecutionBlockerType,
    ExecutionStatus,
    TradeDirection,
    derive_allowed_actions,
    derive_execution_status,
)

# ============================================================================
# derive_execution_status — priority order
# ============================================================================


class TestDeriveExecutionStatus:
    """Status derivation with priority: CALENDAR > DATA_QUALITY > POLICY > ENFORCEMENT > REVIEW."""

    def test_no_blockers_is_actionable(self) -> None:
        assert derive_execution_status(()) == ExecutionStatus.ACTIONABLE

    def test_calendar_highest_priority(self) -> None:
        blockers = (
            _blocker(
                ExecutionBlockerType.CALENDAR,
                ExecutionBlockerCode.CALENDAR_HIGH_IMPACT_SOON,
                BlockerSeverity.EXECUTION_ONLY,
            ),
            _blocker(
                ExecutionBlockerType.DATA_QUALITY,
                ExecutionBlockerCode.DATA_QUALITY_MISSING_D1_DATA,
                BlockerSeverity.INVALIDATES_GRADE,
            ),
            _blocker(
                ExecutionBlockerType.POLICY,
                ExecutionBlockerCode.POLICY_MAX_DAILY_TRADES,
                BlockerSeverity.EXECUTION_ONLY,
            ),
        )
        assert derive_execution_status(blockers) == ExecutionStatus.BLOCKED_BY_CALENDAR

    def test_data_quality_over_policy(self) -> None:
        blockers = (
            _blocker(
                ExecutionBlockerType.DATA_QUALITY,
                ExecutionBlockerCode.DATA_QUALITY_MISSING_D1_DATA,
                BlockerSeverity.INVALIDATES_GRADE,
            ),
            _blocker(
                ExecutionBlockerType.POLICY,
                ExecutionBlockerCode.POLICY_MAX_DAILY_TRADES,
                BlockerSeverity.EXECUTION_ONLY,
            ),
        )
        assert derive_execution_status(blockers) == ExecutionStatus.BLOCKED_BY_DATA_QUALITY

    def test_policy_over_enforcement(self) -> None:
        blockers = (
            _blocker(
                ExecutionBlockerType.POLICY,
                ExecutionBlockerCode.POLICY_MAX_DAILY_TRADES,
                BlockerSeverity.EXECUTION_ONLY,
            ),
            _blocker(
                ExecutionBlockerType.RISK_REWARD,
                ExecutionBlockerCode.RISK_REWARD_BELOW_MINIMUM,
                BlockerSeverity.INVALIDATES_GRADE,
            ),
        )
        assert derive_execution_status(blockers) == ExecutionStatus.BLOCKED_BY_POLICY

    def test_risk_reward_invalidates_grade_is_enforcement(self) -> None:
        blockers = (
            _blocker(
                ExecutionBlockerType.RISK_REWARD,
                ExecutionBlockerCode.RISK_REWARD_BELOW_MINIMUM,
                BlockerSeverity.INVALIDATES_GRADE,
            ),
        )
        assert derive_execution_status(blockers) == ExecutionStatus.BLOCKED_BY_ENFORCEMENT

    def test_risk_reward_execution_only_not_enforcement(self) -> None:
        blockers = (
            _blocker(
                ExecutionBlockerType.RISK_REWARD,
                ExecutionBlockerCode.RISK_REWARD_BELOW_MINIMUM,
                BlockerSeverity.EXECUTION_ONLY,
            ),
        )
        assert derive_execution_status(blockers) == ExecutionStatus.ACTIONABLE

    def test_geometry_invalidates_grade_is_enforcement(self) -> None:
        blockers = (
            _blocker(
                ExecutionBlockerType.GEOMETRY,
                ExecutionBlockerCode.GEOMETRY_INVALID,
                BlockerSeverity.INVALIDATES_GRADE,
            ),
        )
        assert derive_execution_status(blockers) == ExecutionStatus.BLOCKED_BY_ENFORCEMENT

    def test_geometry_execution_only_not_enforcement(self) -> None:
        blockers = (
            _blocker(
                ExecutionBlockerType.GEOMETRY,
                ExecutionBlockerCode.GEOMETRY_INVALID,
                BlockerSeverity.EXECUTION_ONLY,
            ),
        )
        assert derive_execution_status(blockers) == ExecutionStatus.ACTIONABLE

    def test_review_blocker(self) -> None:
        blockers = (
            _blocker(
                ExecutionBlockerType.REVIEW,
                ExecutionBlockerCode.REVIEW_PENDING,
                BlockerSeverity.EXECUTION_ONLY,
            ),
        )
        assert derive_execution_status(blockers) == ExecutionStatus.BLOCKED_BY_REVIEW

    def test_review_after_enforcement(self) -> None:
        """REVIEW lowest priority — enforcement blockers take precedence."""
        blockers = (
            _blocker(
                ExecutionBlockerType.RISK_REWARD,
                ExecutionBlockerCode.RISK_REWARD_BELOW_MINIMUM,
                BlockerSeverity.INVALIDATES_GRADE,
            ),
            _blocker(
                ExecutionBlockerType.REVIEW,
                ExecutionBlockerCode.REVIEW_PENDING,
                BlockerSeverity.EXECUTION_ONLY,
            ),
        )
        assert derive_execution_status(blockers) == ExecutionStatus.BLOCKED_BY_ENFORCEMENT


# ============================================================================
# derive_allowed_actions
# ============================================================================


class TestDeriveAllowedActions:
    """Allowed actions based on status and direction."""

    def test_actionable_bullish_buy(self) -> None:
        assert derive_allowed_actions(TradeDirection.BULLISH, ExecutionStatus.ACTIONABLE) == (
            DecisionAction.BUY_SETUP,
        )

    def test_actionable_bearish_sell(self) -> None:
        assert derive_allowed_actions(TradeDirection.BEARISH, ExecutionStatus.ACTIONABLE) == (
            DecisionAction.SELL_SETUP,
        )

    def test_actionable_neutral_no_trade(self) -> None:
        assert derive_allowed_actions(TradeDirection.NEUTRAL, ExecutionStatus.ACTIONABLE) == (
            DecisionAction.NO_TRADE,
        )

    def test_blocked_by_calendar_no_trade(self) -> None:
        for status in ExecutionStatus:
            if status == ExecutionStatus.ACTIONABLE:
                continue
            actions = derive_allowed_actions(TradeDirection.BULLISH, status)
            assert actions == (DecisionAction.NO_TRADE,), f"Expected NO_TRADE for {status}"


# ============================================================================
# EnforcementViolationCode — every code tested
# ============================================================================


class TestEnforcementViolationCodes:
    """Every EnforcementViolationCode can be instantiated in a violation."""

    @pytest.mark.parametrize(
        "code",
        [
            EnforcementViolationCode.INVALIDATION_ENTRY_AUTHORIZED,
            EnforcementViolationCode.INVALIDATION_GRADE_DOWNGRADED,
            EnforcementViolationCode.INVALIDATION_SETUP_EXPIRED,
            EnforcementViolationCode.INVALIDATION_TRIGGER_INVALIDATED,
            EnforcementViolationCode.INVALIDATION_POLICY_VIOLATION,
            EnforcementViolationCode.INVALIDATION_CALENDAR_BLOCK,
            EnforcementViolationCode.INVALIDATION_DATA_QUALITY,
            EnforcementViolationCode.INVALIDATION_REJECTED,
            EnforcementViolationCode.CANDIDATE_NOT_GENERATED,
            EnforcementViolationCode.EXECUTION_NOT_ACTIONABLE,
            EnforcementViolationCode.DIRECTION_MISMATCH,
            EnforcementViolationCode.INVALID_GEOMETRY,
            EnforcementViolationCode.ACTION_NOT_ALLOWED,
        ],
    )
    def test_violation_creation(self, code: EnforcementViolationCode) -> None:
        violation = EnforcementViolation(code=code, reason=f"Test {code.value}")
        assert violation.code == code
        assert violation.reason == f"Test {code.value}"
        assert isinstance(violation, EnforcementViolation)


# ============================================================================
# ExecutionBlockerCode — representative tests
# ============================================================================


class TestExecutionBlockerCodes:
    """Key blocker codes are creatable and have expected properties."""

    def test_policy_codes(self) -> None:
        for code in (
            ExecutionBlockerCode.POLICY_MAX_DAILY_TRADES,
            ExecutionBlockerCode.POLICY_MAX_DAILY_LOSS,
            ExecutionBlockerCode.POLICY_MAX_POSITION_SIZE,
            ExecutionBlockerCode.POLICY_BLACKOUT_HOUR,
            ExecutionBlockerCode.POLICY_REQUIRES_REVIEW,
            ExecutionBlockerCode.POLICY_COUNTERTREND_DISABLED,
        ):
            blocker = ExecutionBlocker(
                blocker_type=ExecutionBlockerType.POLICY,
                code=code,
                reason=f"Test {code.value}",
                severity=BlockerSeverity.INVALIDATES_GRADE,
            )
            assert blocker.code == code

    def test_calendar_codes(self) -> None:
        for code in (
            ExecutionBlockerCode.CALENDAR_HIGH_IMPACT_SOON,
            ExecutionBlockerCode.CALENDAR_MEDIUM_IMPACT_SOON,
            ExecutionBlockerCode.CALENDAR_INSIDE_EVENT_WINDOW,
        ):
            blocker = ExecutionBlocker(
                blocker_type=ExecutionBlockerType.CALENDAR,
                code=code,
                reason=f"Test {code.value}",
                severity=BlockerSeverity.EXECUTION_ONLY,
            )
            assert blocker.code == code

    def test_data_quality_codes(self) -> None:
        for code in (
            ExecutionBlockerCode.DATA_QUALITY_MISSING_BARS,
            ExecutionBlockerCode.DATA_QUALITY_STALE_DATA,
            ExecutionBlockerCode.DATA_QUALITY_LOW_CONFIDENCE,
            ExecutionBlockerCode.DATA_QUALITY_INSUFFICIENT_HISTORY,
            ExecutionBlockerCode.DATA_QUALITY_MISSING_D1_DATA,
            ExecutionBlockerCode.DATA_QUALITY_MISSING_H4_DATA,
            ExecutionBlockerCode.DATA_QUALITY_MISSING_H1_DATA,
        ):
            blocker = ExecutionBlocker(
                blocker_type=ExecutionBlockerType.DATA_QUALITY,
                code=code,
                reason=f"Test {code.value}",
                severity=BlockerSeverity.INVALIDATES_GRADE,
            )
            assert blocker.code == code

    def test_execution_mode_codes(self) -> None:
        for code in (
            ExecutionBlockerCode.EXECUTION_MODE_NOT_LIVE,
            ExecutionBlockerCode.EXECUTION_MODE_SHADOW_ONLY,
        ):
            blocker = ExecutionBlocker(
                blocker_type=ExecutionBlockerType.EXECUTION_MODE,
                code=code,
                reason=f"Test {code.value}",
                severity=BlockerSeverity.EXECUTION_ONLY,
            )
            assert blocker.code == code


# ============================================================================
# Enforcement violation consistency
# ============================================================================


class TestEnforcementConsistency:
    """Tests for enforcement reviewer logic patterns."""

    def test_deterministic_violation_produces_enforcement_status(self) -> None:
        """Deterministic violations (e.g., RISK_REWARD with INVALIDATES_GRADE)
        should produce BLOCKED_BY_ENFORCEMENT."""
        blockers = (
            _blocker(
                ExecutionBlockerType.RISK_REWARD,
                ExecutionBlockerCode.RISK_REWARD_BELOW_MINIMUM,
                BlockerSeverity.INVALIDATES_GRADE,
            ),
        )
        status = derive_execution_status(blockers)
        assert status == ExecutionStatus.BLOCKED_BY_ENFORCEMENT

    def test_non_approved_review_without_deterministic_violations(self) -> None:
        """A review that is not APPROVED but has no deterministic violations
        produces BLOCKED_BY_REVIEW (the review blocker)."""
        blockers = (
            _blocker(
                ExecutionBlockerType.REVIEW,
                ExecutionBlockerCode.REVIEW_PENDING,
                BlockerSeverity.EXECUTION_ONLY,
            ),
        )
        status = derive_execution_status(blockers)
        assert status == ExecutionStatus.BLOCKED_BY_REVIEW

    def test_non_executable_actions_pass_without_reviewer(self) -> None:
        """Non-executable actions (NO_TRADE, WAIT_FOR_SETUP) pass without
        needing a reviewer — they don't produce blockers on their own."""
        # For NO_TRADE, the allowed actions are always (NO_TRADE,) regardless
        # of blockers — review is not needed.
        allowed = derive_allowed_actions(TradeDirection.NEUTRAL, ExecutionStatus.ACTIONABLE)
        assert allowed == (DecisionAction.NO_TRADE,)

    def test_executable_actions_need_reviewer_approval(self) -> None:
        """For executable actions (BUY_SETUP/SELL_SETUP), if the status is
        ACTIONABLE, no reviewer is needed (no review blocker). If the review
        produces a REVIEW blocker, the status becomes BLOCKED_BY_REVIEW."""
        allowed = derive_allowed_actions(TradeDirection.BULLISH, ExecutionStatus.ACTIONABLE)
        assert allowed == (DecisionAction.BUY_SETUP,)

        # With a review blocker
        blockers = (
            _blocker(
                ExecutionBlockerType.REVIEW,
                ExecutionBlockerCode.REVIEW_PENDING,
                BlockerSeverity.EXECUTION_ONLY,
            ),
        )
        status = derive_execution_status(blockers)
        assert status == ExecutionStatus.BLOCKED_BY_REVIEW


# ============================================================================
# Helpers
# ============================================================================


def _blocker(
    blocker_type: ExecutionBlockerType,
    code: ExecutionBlockerCode,
    severity: BlockerSeverity,
) -> ExecutionBlocker:
    return ExecutionBlocker(
        blocker_type=blocker_type,
        code=code,
        reason=f"Test {code.value}",
        severity=severity,
    )
