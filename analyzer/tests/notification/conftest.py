"""Fixtures for telegram notification tests."""

import pytest


@pytest.fixture
def sample_decision():
    return {
        "action": "buy_setup",
        "confidence": 0.85,
        "entry_price": 2400.0,
        "stop_loss": 2380.0,
        "take_profit": 2440.0,
        "risk_reward_ratio": 2.0,
    }


@pytest.fixture
def sample_context():
    return {"bias": "bullish", "current_price": 2400.0}


@pytest.fixture
def sample_review():
    return {"approved": True, "feedback": "Good setup"}
