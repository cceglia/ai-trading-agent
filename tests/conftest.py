import pytest

from src.decision.models import (
    BiasLevel,
    DecisionAction,
    DecisionOutput,
    MarketContextSummary,
    ReviewVerdict,
)


@pytest.fixture
def sample_market_context():
    return MarketContextSummary(
        symbol="EURUSD",
        bias=BiasLevel.BULLISH,
        confidence=75.0,
        reasoning="Primary structure bullish with recent BOS",
        key_levels=["1.0850", "1.0900"],
        structural_events=["Bullish BOS at 1.0850"],
    )


@pytest.fixture
def sample_decision():
    return DecisionOutput(
        symbol="EURUSD",
        action=DecisionAction.BUY_SETUP,
        entry_price=1.0875,
        stop_loss=1.0825,
        take_profit=1.0975,
        reasoning="Bullish structure with good R/R",
        risk_reward_ratio=2.0,
        entry_authorized=False,
    )


@pytest.fixture
def sample_review():
    return ReviewVerdict(
        approved=True,
        reasoning="All criteria met",
        concerns=[],
        suggested_improvements=None,
    )
