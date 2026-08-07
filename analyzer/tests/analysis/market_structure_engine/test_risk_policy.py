"""Tests for deterministic risk policy creation (Section 16.3).

Tests the build_risk_policy() function and RiskPolicyState computed fields:
- Multiplier calculation for each grade (AAA=1.0, AA=0.5, COUNTERTREND=0.25)
- Computed final_risk_percentage
- Computed risk_reward_ok check (True when estimated_rr >= min_rr)
- Missing R/R → risk_reward_ok=False
- Reject invalid negative base_risk_percentage
"""

from __future__ import annotations

import pytest

from src.analysis.market_structure_engine.models import RiskPolicyState, SetupGrade
from src.analysis.market_structure_engine.risk_policy import GRADE_RISK_TABLE, build_risk_policy

# ============================================================================
# build_risk_policy
# ============================================================================


class TestBuildRiskPolicy:
    """build_risk_policy() creates correct RiskPolicyState for each grade."""

    def test_aaa_grade_multiplier(self) -> None:
        result = build_risk_policy(
            setup_grade=SetupGrade.AAA,
            base_risk_percentage=1.0,
            estimated_reward_risk=3.0,
        )
        assert result.grade_risk_multiplier == 1.0
        assert result.minimum_reward_risk == 2.0

    def test_aa_grade_multiplier(self) -> None:
        result = build_risk_policy(
            setup_grade=SetupGrade.AA,
            base_risk_percentage=1.0,
            estimated_reward_risk=3.0,
        )
        assert result.grade_risk_multiplier == 0.5
        assert result.minimum_reward_risk == 2.0

    def test_countertrend_grade_multiplier(self) -> None:
        result = build_risk_policy(
            setup_grade=SetupGrade.COUNTERTREND,
            base_risk_percentage=1.0,
            estimated_reward_risk=3.0,
        )
        assert result.grade_risk_multiplier == 0.25
        assert result.minimum_reward_risk == 2.0

    def test_none_grade_zero_multiplier(self) -> None:
        """A setup without a grade (NO_SETUP) must not fabricate a multiplier.

        Regression test for result-23.json (US100.cash, 2026-08-04): a NO_SETUP
        previously fell back to the AA table entry via `or SetupGrade.AA` in the
        graph node, producing an apparently-valid risk allocation of 0.5.
        """
        result = build_risk_policy(
            setup_grade=None,
            base_risk_percentage=1.0,
            estimated_reward_risk=None,
        )
        assert result.grade_risk_multiplier == 0.0
        assert result.final_risk_percentage == 0.0
        assert result.risk_reward_ok is False


class TestGRADERiskTable:
    """GRADE_RISK_TABLE must contain expected entries."""

    def test_aaa_entry(self) -> None:
        assert SetupGrade.AAA in GRADE_RISK_TABLE
        assert GRADE_RISK_TABLE[SetupGrade.AAA] == (2.0, 1.0)

    def test_aa_entry(self) -> None:
        assert SetupGrade.AA in GRADE_RISK_TABLE
        assert GRADE_RISK_TABLE[SetupGrade.AA] == (2.0, 0.5)

    def test_countertrend_entry(self) -> None:
        assert SetupGrade.COUNTERTREND in GRADE_RISK_TABLE
        assert GRADE_RISK_TABLE[SetupGrade.COUNTERTREND] == (2.0, 0.25)


# ============================================================================
# Computed fields
# ============================================================================


class TestFinalRiskPercentage:
    """RiskPolicyState.final_risk_percentage computation."""

    def test_base_multiplied_by_grade(self) -> None:
        state = RiskPolicyState(
            base_risk_percentage=2.0,
            grade_risk_multiplier=0.5,
        )
        assert state.final_risk_percentage == 1.0

    def test_zero_base(self) -> None:
        state = RiskPolicyState(
            base_risk_percentage=0.0,
            grade_risk_multiplier=1.0,
        )
        assert state.final_risk_percentage == 0.0

    def test_zero_multiplier(self) -> None:
        state = RiskPolicyState(
            base_risk_percentage=2.0,
            grade_risk_multiplier=0.0,
        )
        assert state.final_risk_percentage == 0.0

    def test_aaa_full_multiplier(self) -> None:
        state = RiskPolicyState(
            base_risk_percentage=1.0,
            grade_risk_multiplier=1.0,
        )
        assert state.final_risk_percentage == 1.0

    def test_aa_half_multiplier(self) -> None:
        state = RiskPolicyState(
            base_risk_percentage=1.0,
            grade_risk_multiplier=0.5,
        )
        assert state.final_risk_percentage == 0.5


class TestRiskRewardOk:
    """RiskPolicyState.risk_reward_ok computation."""

    def test_rr_meets_minimum(self) -> None:
        state = RiskPolicyState(
            estimated_reward_risk=3.0,
            minimum_reward_risk=2.0,
        )
        assert state.risk_reward_ok is True

    def test_rr_exceeds_minimum(self) -> None:
        state = RiskPolicyState(
            estimated_reward_risk=5.0,
            minimum_reward_risk=2.0,
        )
        assert state.risk_reward_ok is True

    def test_rr_equals_minimum(self) -> None:
        state = RiskPolicyState(
            estimated_reward_risk=2.0,
            minimum_reward_risk=2.0,
        )
        assert state.risk_reward_ok is True

    def test_rr_below_minimum(self) -> None:
        state = RiskPolicyState(
            estimated_reward_risk=1.5,
            minimum_reward_risk=2.0,
        )
        assert state.risk_reward_ok is False

    def test_rr_is_none(self) -> None:
        state = RiskPolicyState(
            estimated_reward_risk=None,
            minimum_reward_risk=2.0,
        )
        assert state.risk_reward_ok is False

    def test_rr_is_zero_rejected_by_model(self) -> None:
        """R/R of 0.0 is rejected by the model's gt=0 constraint."""
        with pytest.raises(Exception):
            RiskPolicyState(
                estimated_reward_risk=0.0,
                minimum_reward_risk=2.0,
            )


# ============================================================================
# build_risk_policy computed fields integration
# ============================================================================


class TestBuildRiskPolicyComputedFields:
    """build_risk_policy computed fields work end-to-end."""

    def test_aaa_final_risk(self) -> None:
        result = build_risk_policy(
            setup_grade=SetupGrade.AAA,
            base_risk_percentage=2.0,
            estimated_reward_risk=3.0,
        )
        assert result.final_risk_percentage == 2.0  # multiplier 1.0
        assert result.risk_reward_ok is True  # 3.0 >= 2.0

    def test_aa_final_risk(self) -> None:
        result = build_risk_policy(
            setup_grade=SetupGrade.AA,
            base_risk_percentage=2.0,
            estimated_reward_risk=1.5,
        )
        assert result.final_risk_percentage == 1.0  # multiplier 0.5
        assert result.risk_reward_ok is False  # 1.5 < 2.0

    def test_countertrend_final_risk(self) -> None:
        result = build_risk_policy(
            setup_grade=SetupGrade.COUNTERTREND,
            base_risk_percentage=2.0,
            estimated_reward_risk=3.0,
        )
        assert result.final_risk_percentage == 0.5  # multiplier 0.25
        assert result.risk_reward_ok is True  # 3.0 >= 2.0

    def test_missing_rr_risk_reward_ok_false(self) -> None:
        """Missing R/R leads to risk_reward_ok=False even if minimum is technically met."""
        result = build_risk_policy(
            setup_grade=SetupGrade.AAA,
            base_risk_percentage=1.0,
            estimated_reward_risk=None,
        )
        assert result.risk_reward_ok is False


# ============================================================================
# Validation
# ============================================================================


class TestBuildRiskPolicyValidation:
    """Input validation for build_risk_policy."""

    def test_rejects_negative_base_risk(self) -> None:
        with pytest.raises(ValueError, match="base_risk_percentage must be non-negative"):
            build_risk_policy(
                setup_grade=SetupGrade.AAA,
                base_risk_percentage=-1.0,
                estimated_reward_risk=3.0,
            )

    def test_zero_base_risk_allowed(self) -> None:
        result = build_risk_policy(
            setup_grade=SetupGrade.AAA,
            base_risk_percentage=0.0,
            estimated_reward_risk=3.0,
        )
        assert result.base_risk_percentage == 0.0

    def test_rejects_negative_estimated_rr_in_model(self) -> None:
        """RiskPolicyState model validates estimated_reward_risk > 0 via gt=0 constraint."""
        with pytest.raises(Exception):
            RiskPolicyState(
                base_risk_percentage=1.0,
                estimated_reward_risk=-1.0,
            )


# ============================================================================
# Edge cases
# ============================================================================


class TestRiskPolicyEdgeCases:
    """Edge cases for risk policy creation."""

    def test_large_base_risk(self) -> None:
        result = build_risk_policy(
            setup_grade=SetupGrade.AAA,
            base_risk_percentage=100.0,
            estimated_reward_risk=3.0,
        )
        assert result.final_risk_percentage == 100.0

    def test_large_estimated_reward_risk(self) -> None:
        result = build_risk_policy(
            setup_grade=SetupGrade.AAA,
            base_risk_percentage=1.0,
            estimated_reward_risk=100.0,
        )
        assert result.estimated_reward_risk == 100.0
        assert result.risk_reward_ok is True
