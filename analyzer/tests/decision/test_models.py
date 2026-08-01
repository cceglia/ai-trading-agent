import pytest

from src.analysis.market_structure_engine.models import ReviewStatus
from src.decision.models import (
    AdvisoryLevels,
    BiasLevel,
    DecisionAction,
    DecisionOutput,
    MarketContextSummary,
    ReviewVerdict,
)


class TestMarketContextSummary:
    def test_creation(self, sample_market_context):
        assert sample_market_context.symbol == "EURUSD"
        assert sample_market_context.bias == BiasLevel.BULLISH.value
        assert sample_market_context.confidence == 75.0
        assert sample_market_context.reasoning == "Primary structure bullish with recent BOS"
        assert sample_market_context.key_levels == ["1.0850", "1.0900"]
        assert sample_market_context.structural_events == ["Bullish BOS at 1.0850"]
        assert sample_market_context.calendar_context == ""

    def test_bias_values_are_strings(self, sample_market_context):
        assert isinstance(sample_market_context.bias, str)

    def test_confidence_bounds(self):
        with pytest.raises(Exception):
            MarketContextSummary(
                symbol="EURUSD",
                bias=BiasLevel.BULLISH,
                confidence=101,
                reasoning="test",
            )

    def test_all_bias_levels(self):
        for level in BiasLevel:
            ctx = MarketContextSummary(
                symbol="EURUSD",
                bias=level,
                confidence=50,
                reasoning="test",
            )
            assert ctx.bias == level.value

    def test_defaults(self):
        ctx = MarketContextSummary(
            symbol="EURUSD",
            bias=BiasLevel.NEUTRAL,
            confidence=50,
            reasoning="test",
        )
        assert ctx.key_levels == []
        assert ctx.structural_events == []
        assert ctx.calendar_context == ""

    def test_market_context_summary_current_price_defaults_none(self):
        ctx = MarketContextSummary(
            symbol="EURUSD",
            bias=BiasLevel.NEUTRAL,
            confidence=50,
            reasoning="x",
        )
        assert ctx.current_price is None
        assert ctx.current_price_time is None

    def test_market_context_summary_accepts_current_price(self):
        ctx = MarketContextSummary(
            symbol="EURUSD",
            bias=BiasLevel.NEUTRAL,
            confidence=50,
            reasoning="x",
            current_price=1.0875,
            current_price_time="2024-01-03T00:00:00",
        )
        assert ctx.current_price == 1.0875
        assert ctx.current_price_time == "2024-01-03T00:00:00"


class TestDecisionOutput:
    def test_creation(self, sample_decision):
        assert sample_decision.symbol == "EURUSD"
        assert sample_decision.action == DecisionAction.BUY_SETUP.value
        assert sample_decision.reasoning == "Bullish structure with good R/R"

    def test_action_values_are_strings(self, sample_decision):
        assert isinstance(sample_decision.action, str)

    def test_all_actions(self):
        for action in DecisionAction:
            decision = DecisionOutput(
                symbol="EURUSD",
                action=action,
                reasoning="test",
            )
            assert decision.action == action.value

    def test_advisory_levels_are_optional_and_structured(self):
        """Advisory prices are explicit fields and are absent by default."""
        decision = DecisionOutput(
            symbol="EURUSD",
            action=DecisionAction.NO_TRADE,
            reasoning="No setup available",
            advisory_levels=AdvisoryLevels(entry_price=1.08, stop_loss=1.07),
        )
        assert decision.advisory_levels is not None
        assert decision.advisory_levels.entry_price == 1.08
        assert decision.advisory_levels.take_profit is None

    def test_only_decision_fields_are_structured(self):
        """DecisionOutput has no free-form price fields."""
        DecisionOutput(
            symbol="EURUSD",
            action=DecisionAction.NO_TRADE,
            reasoning="No setup available",
        )
        fields = set(DecisionOutput.model_fields.keys())
        assert fields == {"symbol", "action", "reasoning", "advisory_levels"}


class TestReviewVerdict:
    def test_creation(self, sample_review):
        assert sample_review.approved is True
        assert sample_review.status == ReviewStatus.APPROVED.value
        assert sample_review.reasoning == "All criteria met"
        assert sample_review.concerns == ()
        assert sample_review.suggested_improvements is None

    def test_approved_property(self):
        verdict = ReviewVerdict(status=ReviewStatus.APPROVED, reasoning="OK")
        assert verdict.approved is True

    def test_rejected_property(self):
        verdict = ReviewVerdict(status=ReviewStatus.REJECTED, reasoning="Bad")
        assert verdict.approved is False

    def test_defaults(self):
        verdict = ReviewVerdict(status=ReviewStatus.REJECTED, reasoning="Rejected")
        assert verdict.concerns == ()
        assert verdict.suggested_improvements is None
        assert verdict.risk_management_ok is True
        assert verdict.htf_alignment_ok is True
        assert verdict.calendar_clear is True
        assert verdict.deterministic_compliance_ok is True
        assert verdict.grade_violation_detected is False
        assert verdict.blocker_violation_detected is False
        assert verdict.geometry_violation_detected is False

    def test_rejection_with_concerns(self):
        verdict = ReviewVerdict(
            status=ReviewStatus.REJECTED,
            reasoning="Risk too high",
            concerns=("R/R below 2:1", "High-impact event pending"),
            suggested_improvements="Widen stop loss",
        )
        assert verdict.approved is False
        assert len(verdict.concerns) == 2
        assert verdict.suggested_improvements == "Widen stop loss"

    def test_concerns_is_tuple(self):
        verdict = ReviewVerdict(
            status=ReviewStatus.APPROVED,
            reasoning="Good",
            concerns=("Minor concern",),
        )
        assert isinstance(verdict.concerns, tuple)

    def test_new_violation_fields(self):
        verdict = ReviewVerdict(
            status=ReviewStatus.REJECTED,
            reasoning="Violations detected",
            grade_violation_detected=True,
            blocker_violation_detected=True,
            geometry_violation_detected=False,
        )
        assert verdict.grade_violation_detected is True
        assert verdict.blocker_violation_detected is True
        assert verdict.geometry_violation_detected is False

    def test_review_verdict_serializes_approved(self):
        """approved must appear in model_dump() via @computed_field."""
        verdict = ReviewVerdict(status=ReviewStatus.APPROVED, reasoning="ok")
        payload = verdict.model_dump(mode="json")
        assert payload["approved"] is True
        assert payload["status"] == "APPROVED"

    def test_review_verdict_rejected_serializes_approved_false(self):
        verdict = ReviewVerdict(status=ReviewStatus.REJECTED, reasoning="no")
        payload = verdict.model_dump(mode="json")
        assert payload["approved"] is False
        assert payload["status"] == "REJECTED"
