import pytest

from src.analysis.market_structure_engine.models import BiasLevel, DecisionAction
from src.decision.models import AdvisoryLevels, DecisionOutput, MarketContextSummary


class TestMarketContextSummary:
    def test_creation(self, sample_market_context):
        assert sample_market_context.symbol == "EURUSD"
        assert sample_market_context.bias == BiasLevel.BULLISH.value
        assert sample_market_context.confidence == 75.0
        assert sample_market_context.current_price is None

    def test_confidence_bounds(self):
        with pytest.raises(Exception):
            MarketContextSummary(
                symbol="EURUSD", bias=BiasLevel.BULLISH, confidence=101, reasoning="x"
            )


class TestDecisionOutput:
    def test_advisory_levels_are_optional(self):
        decision = DecisionOutput(
            symbol="EURUSD",
            action=DecisionAction.NO_TRADE,
            reasoning="No deterministic setup",
            advisory_levels=AdvisoryLevels(entry_price=1.08),
        )
        assert decision.action == DecisionAction.NO_TRADE.value
        assert decision.advisory_levels.entry_price == 1.08

    def test_schema_contains_only_current_decision_fields(self):
        assert set(DecisionOutput.model_fields) == {
            "symbol",
            "action",
            "reasoning",
            "advisory_levels",
        }
