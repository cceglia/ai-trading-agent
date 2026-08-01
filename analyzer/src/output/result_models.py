from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from src.decision.models import AdvisoryLevels, DecisionOutput, MarketContextSummary, ReviewVerdict


class OHLCBar(BaseModel):
    """Single OHLC bar for chart rendering."""

    time: str
    open: float
    high: float
    low: float
    close: float


class OHLCData(BaseModel):
    """OHLC data keyed by timeframe."""

    D1: list[OHLCBar] = Field(default_factory=list)
    H4: list[OHLCBar] = Field(default_factory=list)
    H1: list[OHLCBar] = Field(default_factory=list)


class SLTPOverlay(BaseModel):
    """Entry, stop-loss and take-profit overlay for charts."""

    entry_price: float | None = None
    stop_loss: float | None = None
    take_profit: float | None = None


class AnalysisResult(BaseModel):
    """Top-level pipeline output serialized to JSON for the web viewer.

    Fields are grouped by their provenance within the pipeline:

    * ``market_context``, ``decision``, ``review`` — LLM-derived (interpretive).
    * ``sl_tp_overlay``, and ``setup_*`` / ``trade_direction`` / ``estimated_reward_risk`` —
      deterministic engine values (authoritative).
    * ``risk_multiplier``, ``final_risk_percentage`` — risk policy evaluation.
    * ``execution_status``, ``execution_blockers`` — execution policy evaluation.
    * ``final_action``, ``enforcement_violations`` — enforcement gate resolution.
    """

    version: str = "1.0"
    symbol: str
    run_id: str
    started_at: datetime
    completed_at: datetime
    status: str  # "success" | "partial" | "error"
    errors: list[str] = Field(default_factory=list)
    fatal_error: str | None = None
    market_context: MarketContextSummary | None = None
    decision: DecisionOutput | None = None
    review: ReviewVerdict | None = None
    ohlc: OHLCData = Field(default_factory=OHLCData)
    sl_tp_overlay: SLTPOverlay = Field(default_factory=SLTPOverlay)
    advisory_levels: AdvisoryLevels | None = Field(
        default=None,
        description="Optional advisory levels from the decision; never authoritative",
    )
    review_advisory_levels: AdvisoryLevels | None = Field(
        default=None,
        description="Optional advisory levels from the review; never authoritative",
    )

    # ── Deterministic pipeline (authoritative) ─────────────────────────
    setup_grade: str | None = Field(
        default=None,
        description="Quality grade from deterministic grading (AAA, AA, COUNTERTREND)",
    )
    setup_classification_status: str | None = Field(
        default=None,
        description="Status of setup classification (CLASSIFIED, NO_SETUP, …)",
    )
    setup_lifecycle_status: str | None = Field(
        default=None,
        description="Lifecycle stage of the setup (PENDING, READY, …)",
    )
    trade_direction: str | None = Field(
        default=None,
        description="Deterministic trade direction (BULLISH, BEARISH, NEUTRAL)",
    )
    rejection_codes: list[str] = Field(
        default_factory=list,
        description="Structured rejection codes when setup is non-actionable",
    )
    estimated_reward_risk: float | None = Field(
        default=None,
        description="Reward-to-risk ratio from deterministic calculation",
    )
    order_type: str | None = Field(
        default=None,
        description="Direction-aware deterministic order type: MARKET, LIMIT, or STOP",
    )
    deterministic_setup_complete: bool = Field(
        default=False,
        description="Whether all canonical deterministic setup prices are available",
    )

    # ── Risk policy ────────────────────────────────────────────────────
    risk_multiplier: float | None = Field(
        default=None,
        description="Grade-based risk multiplier applied to base risk",
    )
    final_risk_percentage: float | None = Field(
        default=None,
        description="Final risk percentage after multiplier applied",
    )

    # ── Execution policy ───────────────────────────────────────────────
    execution_status: str | None = Field(
        default=None,
        description="Final execution status (ACTIONABLE, BLOCKED_BY_*, …)",
    )
    execution_blockers: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Active execution blockers with type, code, reason, severity",
    )

    # ── Enforcement gate ───────────────────────────────────────────────
    final_action: str | None = Field(
        default=None,
        description="Final resolved decision action after enforcement",
    )
    enforcement_violations: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Enforcement violations detected by the gate",
    )
