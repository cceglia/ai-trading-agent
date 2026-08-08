from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from src.analysis.market_structure_engine.models import (
    BiasLevel,
    DecisionAction,
)

# Re-export engine enums for backward compatibility — consumers can continue
# to import BiasLevel, DecisionAction from this module.
__all__ = [
    "BiasLevel",
    "DecisionAction",
    "MarketContextSummary",
    "AdvisoryLevels",
    "DecisionOutput",
    "SynthesisResponse",
]


class SynthesisResponse(BaseModel):
    """Presentation-only output from the single Synthesizer call."""

    explanation: str = Field(min_length=1, max_length=4000)
    risks: list[str] = Field(default_factory=list, max_length=20)
    confluences: list[str] = Field(default_factory=list, max_length=20)

    model_config = {"extra": "forbid"}

    @field_validator("explanation")
    @classmethod
    def normalize_explanation(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("explanation must contain non-whitespace characters")
        return normalized

    @field_validator("risks", "confluences")
    @classmethod
    def validate_items(cls, values: list[str]) -> list[str]:
        if any(not item.strip() or len(item) > 500 for item in values):
            raise ValueError("presentation list items must be non-empty and at most 500 chars")
        if len(values) != len(set(values)):
            raise ValueError("presentation lists must not contain exact duplicates")
        return values


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
    current_price: float | None = Field(default=None, description="Canonical current price")
    current_price_time: str | None = Field(
        default=None,
        description="ISO timestamp of the canonical current price",
    )

    model_config = {"use_enum_values": True}


class AdvisoryLevels(BaseModel):
    """Optional LLM-proposed levels, never used for execution or chart overlays."""

    entry_price: float | None = Field(default=None, description="Advisory entry price")
    stop_loss: float | None = Field(default=None, description="Advisory stop-loss price")
    take_profit: float | None = Field(default=None, description="Advisory take-profit price")


class DecisionOutput(BaseModel):
    """Deterministic decision projection used by the existing output seam."""

    symbol: str = Field(description="Trading symbol")
    action: DecisionAction = Field(description="Decision action")
    reasoning: str = Field(description="Reasoning for the decision")
    advisory_levels: AdvisoryLevels | None = Field(
        default=None,
        description="Optional advisory levels; deterministic levels remain authoritative",
    )

    model_config = {"use_enum_values": True}
