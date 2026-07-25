import pytest

from src.decision.models import (
    BiasLevel,
    DecisionAction,
    DecisionOutput,
    MarketContextSummary,
    ReviewVerdict,
)


@pytest.fixture(autouse=True)
def reset_candle_cache_settings():
    """Reset the _settings sentinel in candle_cache before each test.

    Tests use monkeypatch to set env vars (TRADING_D1_CLOSE_TIME, etc.)
    and expect _get_settings() to pick up those changes. Without resetting
    the module-level sentinel, the cached Settings instance from a prior
    test would shadow monkeypatched env vars.
    """
    import src.analysis.candle_cache

    src.analysis.candle_cache._settings = None
    yield
    src.analysis.candle_cache._settings = None


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
