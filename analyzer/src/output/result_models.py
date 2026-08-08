from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field

from src.analysis.market_structure_engine.config import MIN_RR
from src.analysis.market_structure_engine.models import (
    SetupClassificationStatus,
    SetupGrade,
    SetupLifecycleStatus,
    TradeDirection,
)
from src.decision.models import AdvisoryLevels, DecisionOutput, MarketContextSummary


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

    * ``market_context`` and ``decision.reasoning`` — LLM-derived (interpretive).
    * ``sl_tp_overlay``, and ``setup_*`` / ``trade_direction`` / ``estimated_reward_risk`` —
      deterministic engine values (authoritative).
    * ``risk_multiplier``, ``final_risk_percentage`` — risk policy evaluation.
    * ``execution_status``, ``execution_blockers`` — execution policy evaluation.
    * ``final_action``, ``enforcement_violations`` — enforcement gate resolution.
    """

    version: str = "2.0"
    symbol: str
    run_id: str
    started_at: datetime
    completed_at: datetime
    status: str  # "success" | "partial" | "degraded" | "error"
    errors: list[str] = Field(default_factory=list)
    fatal_error: str | None = None
    synthesis_status: str = "SKIPPED"
    synthesis_explanation: str | None = None
    synthesis_risks: list[str] = Field(default_factory=list)
    synthesis_confluences: list[str] = Field(default_factory=list)
    synthesis_error: str | None = None
    market_context: MarketContextSummary | None = None
    decision: DecisionOutput | None = None
    ohlc: OHLCData = Field(default_factory=OHLCData)
    sl_tp_overlay: SLTPOverlay = Field(default_factory=SLTPOverlay)
    advisory_levels: AdvisoryLevels | None = Field(
        default=None,
        description="Optional advisory levels from the decision; never authoritative",
    )

    # ── Canonical deterministic contract ───────────────────────────────
    validation_status: str = "INVALID"
    validation_errors: list[str] = Field(default_factory=list)
    rr: float | None = None
    calculated_rr: float | None = None
    minimum_required_rr: float = MIN_RR
    rr_pass: bool = False
    deterministic_blockers: list[dict[str, Any]] = Field(default_factory=list)
    reason_codes: list[str] = Field(default_factory=list)
    setup_status: str = "INVALID"
    direction: str = "NONE"
    operational: bool = False
    entry_authorized: bool = False

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


# =====================================================================
# Schema-v2 envelope (canonical persisted/API contract)
# =====================================================================
#
# These models define the normative nested v2 envelope that the writer
# persists and the server reads (FR-029, DEC-006). They intentionally carry
# no review-process state of any kind (INV-015) and hardcode
# ``entry_authorized=False`` (INV-003). The flat ``AnalysisResult`` above
# remains the internal pipeline seam; this envelope is the public persisted
# shape.


class V2Status(StrEnum):
    """Top-level run status persisted for v2 envelopes."""

    SUCCESS = "success"
    DEGRADED = "degraded"
    PARTIAL = "partial"
    ERROR = "error"


class V2DecisionAction(StrEnum):
    """Canonical deterministic action values (DEC-002)."""

    BUY_SETUP = "buy_setup"
    SELL_SETUP = "sell_setup"
    NO_TRADE = "no_trade"


class SetupStatusV2(StrEnum):
    """Deterministic setup classification for the v2 contract."""

    READY = "READY"
    NO_SETUP = "NO_SETUP"
    INVALID = "INVALID"


class DirectionV2(StrEnum):
    """Canonical human-facing direction for the v2 contract."""

    LONG = "LONG"
    SHORT = "SHORT"
    NONE = "NONE"


class ValidationStatusV2(StrEnum):
    """Deterministic invariant validity for the v2 contract."""

    VALID = "VALID"
    INVALID = "INVALID"


class SynthesisStatusV2(StrEnum):
    """Presentation status of the single Synthesizer call.

    ``SUCCESS``/``FAILED`` describe an attempted call; ``SKIPPED`` is the
    deterministic no-LLM path (invalid runs) where no call was made.
    """

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class RRInfo(BaseModel):
    """Calculated reward-to-risk values (FR-017/018)."""

    calculated_rr: float | None = None
    minimum_required_rr: float = MIN_RR
    rr_pass: bool = False


class EntryPlan(BaseModel):
    """Deterministic entry plan prices and metadata."""

    current_price: float | None = None
    entry_type: str | None = None
    entry_price: float | None = None
    entry_zone_low: float | None = None
    entry_zone_high: float | None = None
    trigger_level: float | None = None
    invalidation_level_id: str | None = None
    invalidation_timeframe: str | None = None
    invalidation_price: float | None = None
    target_price: float | None = None
    estimated_reward_risk: float | None = None


class PolicyFacts(BaseModel):
    """Execution policy projection for the v2 contract."""

    execution_status: str | None = None
    actionable: bool = False
    blockers: list[dict[str, Any]] = Field(default_factory=list)
    reason_codes: list[str] = Field(default_factory=list)


class DeterministicFacts(BaseModel):
    """Immutable deterministic facts for one symbol/run (Section 12.1).

    ``bias`` and ``confidence`` are summary projections derived from the
    deterministic engine's per-timeframe scoring (falling back to the
    interpretive market context only when no deterministic score exists);
    they exist so the server run-summary contract has deterministic values.
    """

    symbol: str
    timeframes: dict[str, Any] = Field(
        default_factory=dict,
        description="Compact D1/H4/H1 facts with bounded history (NFR-003)",
    )
    setup_status: SetupStatusV2 = SetupStatusV2.NO_SETUP
    direction: DirectionV2 = DirectionV2.NONE
    trade_direction: TradeDirection = TradeDirection.NEUTRAL
    setup_grade: SetupGrade | None = None
    setup_classification_status: SetupClassificationStatus = SetupClassificationStatus.NO_SETUP
    setup_lifecycle_status: SetupLifecycleStatus = SetupLifecycleStatus.PENDING
    entry_plan: EntryPlan = Field(default_factory=EntryPlan)
    rr: RRInfo = Field(default_factory=RRInfo)
    confidence_components: dict[str, Any] = Field(default_factory=dict)
    policy: PolicyFacts = Field(default_factory=PolicyFacts)
    selected_levels: dict[str, Any] = Field(default_factory=dict)
    latest_structural_events: dict[str, Any] = Field(default_factory=dict)
    latest_liquidity_states: dict[str, Any] = Field(default_factory=dict)
    event_history: dict[str, Any] = Field(default_factory=dict)
    liquidity_history: dict[str, Any] = Field(default_factory=dict)
    validation_status: ValidationStatusV2 = ValidationStatusV2.INVALID
    validation_errors: list[str] = Field(default_factory=list)
    operational: bool = False
    entry_authorized: Literal[False] = Field(default=False)
    bias: str | None = None
    confidence: float | None = None


class DecisionBlock(BaseModel):
    """Deterministic decision projection — action only (FR-021)."""

    action: V2DecisionAction

    model_config = {"extra": "forbid"}


class SynthesisBlock(BaseModel):
    """Presentation-only output of the single Synthesizer call."""

    status: SynthesisStatusV2 = SynthesisStatusV2.SKIPPED
    explanation: str | None = None
    risks: list[str] = Field(default_factory=list)
    confluences: list[str] = Field(default_factory=list)
    error: str | None = None

    model_config = {"extra": "forbid"}


class AnalysisEnvelope(BaseModel):
    """Top-level schema-v2 persisted/API object (Section 12.1)."""

    schema_version: Literal["2"] = "2"
    symbol: str
    run_id: str
    started_at: datetime
    completed_at: datetime
    status: V2Status
    errors: list[str] = Field(default_factory=list)
    fatal_error: str | None = None
    deterministic_facts: DeterministicFacts
    decision: DecisionBlock
    synthesis: SynthesisBlock = Field(default_factory=SynthesisBlock)
    ohlc: OHLCData = Field(default_factory=OHLCData)

    model_config = {"extra": "forbid"}
