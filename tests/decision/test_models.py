import pytest

from src.decision.models import (
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


class TestDecisionOutput:
    def test_creation(self, sample_decision):
        assert sample_decision.symbol == "EURUSD"
        assert sample_decision.action == DecisionAction.BUY_SETUP.value
        assert sample_decision.entry_price == 1.0875
        assert sample_decision.stop_loss == 1.0825
        assert sample_decision.take_profit == 1.0975
        assert sample_decision.risk_reward_ratio == 2.0
        assert sample_decision.entry_authorized is False

    def test_action_values_are_strings(self, sample_decision):
        assert isinstance(sample_decision.action, str)

    def test_entry_authorized_always_false(self):
        for action in DecisionAction:
            decision = DecisionOutput(
                symbol="EURUSD",
                action=action,
                reasoning="test",
                entry_authorized=True,
            )
            assert decision.entry_authorized is False

    def test_optional_fields_default_none(self):
        decision = DecisionOutput(
            symbol="EURUSD",
            action=DecisionAction.NO_TRADE,
            reasoning="No setup",
        )
        assert decision.entry_price is None
        assert decision.stop_loss is None
        assert decision.take_profit is None
        assert decision.risk_reward_ratio is None

    def test_all_actions(self):
        for action in DecisionAction:
            decision = DecisionOutput(
                symbol="EURUSD",
                action=action,
                reasoning="test",
            )
            assert decision.action == action.value


class TestReviewVerdict:
    def test_creation(self, sample_review):
        assert sample_review.approved is True
        assert sample_review.reasoning == "All criteria met"
        assert sample_review.concerns == []
        assert sample_review.suggested_improvements is None

    def test_defaults(self):
        verdict = ReviewVerdict(approved=False, reasoning="Rejected")
        assert verdict.concerns == []
        assert verdict.suggested_improvements is None
        assert verdict.risk_management_ok is True
        assert verdict.htf_alignment_ok is True
        assert verdict.calendar_clear is True

    def test_rejection_with_concerns(self):
        verdict = ReviewVerdict(
            approved=False,
            reasoning="Risk too high",
            concerns=["R/R below 2:1", "High-impact event pending"],
            suggested_improvements="Widen stop loss",
        )
        assert verdict.approved is False
        assert len(verdict.concerns) == 2
        assert verdict.suggested_improvements == "Widen stop loss"
