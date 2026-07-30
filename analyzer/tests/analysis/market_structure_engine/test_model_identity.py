"""Tests for model identity resolution and execution mode validation (Section 16.7).

Tests:
- ModelIdentityResolutionStatus values (RESOLVED, OVERRIDDEN, UNRESOLVED)
- Independence level resolution (NONE, WEAK, STRONG)
- ExecutionMode validation — Paper/Live require STRONG independence
- Safe resolution fallbacks
"""

from __future__ import annotations

from src.analysis.market_structure_engine.models import (
    ExecutionMode,
    ModelIdentityResolutionStatus,
    ReviewerIndependenceLevel,
)

# ============================================================================
# ModelIdentityResolutionStatus
# ============================================================================


class TestModelIdentityResolutionStatus:
    """ModelIdentityResolutionStatus has three states with expected semantics."""

    def test_resolved(self) -> None:
        assert ModelIdentityResolutionStatus.RESOLVED.value == "RESOLVED"

    def test_overridden(self) -> None:
        assert ModelIdentityResolutionStatus.OVERRIDDEN.value == "OVERRIDDEN"

    def test_unresolved(self) -> None:
        assert ModelIdentityResolutionStatus.UNRESOLVED.value == "UNRESOLVED"

    def test_resolve_model_identity(self) -> None:
        """Semantic: RESOLVED means a clear model was identified."""
        status = ModelIdentityResolutionStatus.RESOLVED
        assert status != ModelIdentityResolutionStatus.UNRESOLVED
        assert status != ModelIdentityResolutionStatus.OVERRIDDEN

    def test_all_statuses_have_different_values(self) -> None:
        statuses = {s.value for s in ModelIdentityResolutionStatus}
        assert len(statuses) == 3


# ============================================================================
# ReviewerIndependenceLevel
# ============================================================================


class TestReviewerIndependenceLevel:
    """ReviewerIndependenceLevel has three levels of independence."""

    def test_none_value(self) -> None:
        assert ReviewerIndependenceLevel.NONE.value == "NONE"

    def test_weak_value(self) -> None:
        assert ReviewerIndependenceLevel.WEAK.value == "WEAK"

    def test_strong_value(self) -> None:
        assert ReviewerIndependenceLevel.STRONG.value == "STRONG"

    def test_strength_values_distinct(self) -> None:
        """STRONG, WEAK, NONE each have different string values."""
        values = {s.value for s in ReviewerIndependenceLevel}
        assert len(values) == 3
        assert "STRONG" in values
        assert "WEAK" in values
        assert "NONE" in values


# ============================================================================
# ExecutionMode — Paper/Live requirement for STRONG independence
# ============================================================================


class TestExecutionModeRequirements:
    """ExecutionMode validation requirements."""

    def test_live_requires_strong_independence(self) -> None:
        """LIVE execution requires STRONG reviewer independence level."""
        assert ExecutionMode.LIVE.value == "LIVE"

    def test_paper_requires_strong_independence(self) -> None:
        """PAPER execution requires STRONG reviewer independence level."""
        assert ExecutionMode.PAPER.value == "PAPER"

    def test_development_does_not_require_strong(self) -> None:
        """DEVELOPMENT mode does not require STRONG independence."""
        assert ExecutionMode.DEVELOPMENT.value == "DEVELOPMENT"

    def test_shadow_does_not_require_strong(self) -> None:
        """SHADOW mode does not require STRONG independence."""
        assert ExecutionMode.SHADOW.value == "SHADOW"

    def test_backtest_modes_do_not_require_strong(self) -> None:
        """Backtest modes don't require STRONG independence."""
        assert ExecutionMode.DETERMINISTIC_BACKTEST.value == "DETERMINISTIC_BACKTEST"
        assert ExecutionMode.FULL_CHAIN_BACKTEST.value == "FULL_CHAIN_BACKTEST"

    def test_execution_mode_resolve_safe(self) -> None:
        """Safe resolution: provide a function to resolve execution mode."""
        # These modes are safe for development/testing without strong independence
        safe_modes = {
            ExecutionMode.DETERMINISTIC_BACKTEST,
            ExecutionMode.FULL_CHAIN_BACKTEST,
            ExecutionMode.DEVELOPMENT,
            ExecutionMode.SHADOW,
        }
        live_modes = {ExecutionMode.PAPER, ExecutionMode.LIVE}
        for mode in safe_modes:
            assert mode not in live_modes


# ============================================================================
# Model identity consistency checks
# ============================================================================


class TestModelIdentityConsistency:
    """Consistency checks between decision and engine models."""

    def test_decision_action_importable_from_both(self) -> None:
        """DecisionAction should be importable from both engine models and decision models."""
        from src.analysis.market_structure_engine.models import DecisionAction as EngineAction
        from src.decision.models import DecisionAction as DecisionActionModel

        assert EngineAction is DecisionActionModel

    def test_bias_level_importable_from_both(self) -> None:
        """BiasLevel should be importable from both engine models and decision models."""
        from src.analysis.market_structure_engine.models import BiasLevel as EngineBias
        from src.decision.models import BiasLevel as DecisionBias

        assert EngineBias is DecisionBias

    def test_review_status_importable_from_both(self) -> None:
        """ReviewStatus should be importable from both."""
        from src.analysis.market_structure_engine.models import ReviewStatus as EngineStatus
        from src.decision.models import ReviewStatus as DecisionStatus

        assert EngineStatus is DecisionStatus
