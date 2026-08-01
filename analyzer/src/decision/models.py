from __future__ import annotations

import logging

from pydantic import BaseModel, Field, computed_field

from src.analysis.market_structure_engine.models import (
    BiasLevel,
    DecisionAction,
    ReviewStatus,
)

logger = logging.getLogger(__name__)

# Re-export engine enums for backward compatibility — consumers can continue
# to import BiasLevel, DecisionAction from this module.
__all__ = [
    "BiasLevel",
    "DecisionAction",
    "MarketContextSummary",
    "AdvisoryLevels",
    "DecisionOutput",
    "ReviewVerdict",
    "ReviewStatus",
]


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
    """Decision output from decider agent.

    The LLM selects an action and explains its reasoning.  Deterministic
    values (entry price, stop-loss, take-profit) are computed by the
    engine and are **not** part of the LLM output.
    """

    symbol: str = Field(description="Trading symbol")
    action: DecisionAction = Field(description="Decision action")
    reasoning: str = Field(description="Reasoning for the decision")
    advisory_levels: AdvisoryLevels | None = Field(
        default=None,
        description="Optional advisory levels; deterministic levels remain authoritative",
    )

    model_config = {"use_enum_values": True}


class ReviewVerdict(BaseModel):
    """Review verdict from reviewer agent.

    The ``approved`` property derives from ``status`` so that existing
    code checking ``verdict.approved`` continues to work.
    """

    status: ReviewStatus = Field(description="Review status")
    reasoning: str = Field(description="Reasoning for the verdict")
    concerns: tuple[str, ...] = Field(
        default=(),
        description="Tuple of concerns",
    )
    suggested_improvements: str | None = Field(
        default=None,
        description="Suggested improvements",
    )
    deterministic_compliance_ok: bool = Field(
        default=True,
        description="Deterministic compliance check passed",
    )
    risk_management_ok: bool = Field(default=True, description="Risk management compliance")
    htf_alignment_ok: bool = Field(default=True, description="Higher-timeframe alignment")
    calendar_clear: bool = Field(default=True, description="No blocking calendar events")
    grade_violation_detected: bool = Field(
        default=False,
        description="Grade violation detected during review",
    )
    blocker_violation_detected: bool = Field(
        default=False,
        description="Blocker violation detected during review",
    )
    geometry_violation_detected: bool = Field(
        default=False,
        description="Geometry violation detected during review",
    )
    advisory_levels: AdvisoryLevels | None = Field(
        default=None,
        description="Optional advisory levels; deterministic levels remain authoritative",
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def approved(self) -> bool:
        """Compatibility field — canonical source is ``status``."""
        return self.status == ReviewStatus.APPROVED

    model_config = {"use_enum_values": True}
