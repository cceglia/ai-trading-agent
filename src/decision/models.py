from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class BiasLevel(StrEnum):
    """Structural bias levels."""

    STRONG_BULLISH = "strong_bullish"
    BULLISH = "bullish"
    NEUTRAL_BULLISH = "neutral_bullish"
    NEUTRAL = "neutral"
    NEUTRAL_BEARISH = "neutral_bearish"
    BEARISH = "bearish"
    STRONG_BEARISH = "strong_bearish"


class MarketContextSummary(BaseModel):
    """Summary of market context from synthesizer agent."""

    symbol: str = Field(description="Trading symbol")
    bias: BiasLevel = Field(description="Structural bias level")
    confidence: float = Field(ge=0, le=100, description="Confidence score 0-100")
    reasoning: str = Field(description="Reasoning for the bias")
    key_levels: list[str] = Field(default_factory=list, description="Key support/resistance levels")
    structural_events: list[str] = Field(
        default_factory=list,
        description="Recent BOS/CHoCH events",
    )
    calendar_context: str = Field(default="", description="Calendar event context")

    model_config = {"use_enum_values": True}


class DecisionAction(StrEnum):
    """Decision actions."""

    NO_TRADE = "no_trade"
    WAIT_FOR_SETUP = "wait_for_setup"
    BUY_SETUP = "buy_setup"
    SELL_SETUP = "sell_setup"


class DecisionOutput(BaseModel):
    """Decision output from decider agent."""

    symbol: str = Field(description="Trading symbol")
    action: DecisionAction = Field(description="Decision action")
    entry_price: float | None = Field(default=None, description="Suggested entry price")
    stop_loss: float | None = Field(default=None, description="Suggested stop loss")
    take_profit: float | None = Field(default=None, description="Suggested take profit")
    reasoning: str = Field(description="Reasoning for the decision")
    risk_reward_ratio: float | None = Field(default=None, description="Risk/reward ratio")
    entry_authorized: bool = Field(default=False, description="Always false - advisory only")

    model_config = {"use_enum_values": True}


class ReviewVerdict(BaseModel):
    """Review verdict from reviewer agent."""

    approved: bool = Field(description="Whether decision is approved")
    reasoning: str = Field(description="Reasoning for the verdict")
    concerns: list[str] = Field(default_factory=list, description="List of concerns")
    suggested_improvements: str | None = Field(
        default=None,
        description="Suggested improvements",
    )
    risk_management_ok: bool = Field(default=True, description="Risk management compliance")
    htf_alignment_ok: bool = Field(default=True, description="Higher-timeframe alignment")
    calendar_clear: bool = Field(default=True, description="No blocking calendar events")
