"""Shared domain enums and data models for the market structure engine.

This module contains all domain enums as specified in Section 4.1 of the
multi-timeframe pipeline redesign plan. It serves as the foundation for
the entire engine, providing type-safe definitions for:

- Setup grading and classification
- Execution status and blockers
- Trigger and entry types
- Decision and bias levels
- Review and enforcement status
- Model identity resolution

This module has no external dependencies beyond pydantic and the standard library,
making it the foundation for the multi-timeframe pipeline.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Self

from pydantic import BaseModel, Field, computed_field

# ---------------------------------------------------------------------------
# Setup Enums
# ---------------------------------------------------------------------------


class SetupGrade(StrEnum):
    """Quality grade assigned to a trading setup."""

    AAA = "AAA"
    AA = "AA"
    COUNTERTREND = "COUNTERTREND"


class SetupClassificationStatus(StrEnum):
    """Status of the setup classification process."""

    CLASSIFIED = "CLASSIFIED"
    NO_SETUP = "NO_SETUP"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class SetupLifecycleStatus(StrEnum):
    """Lifecycle status of a classified setup."""

    PENDING = "PENDING"
    READY = "READY"
    TRIGGERED = "TRIGGERED"
    EXPIRED = "EXPIRED"
    INVALIDATED = "INVALIDATED"


# ---------------------------------------------------------------------------
# Execution Enums
# ---------------------------------------------------------------------------


class ExecutionStatus(StrEnum):
    """Status of the execution pipeline for a setup."""

    ACTIONABLE = "ACTIONABLE"
    BLOCKED_BY_CALENDAR = "BLOCKED_BY_CALENDAR"
    BLOCKED_BY_POLICY = "BLOCKED_BY_POLICY"
    BLOCKED_BY_ENFORCEMENT = "BLOCKED_BY_ENFORCEMENT"
    BLOCKED_BY_REVIEW = "BLOCKED_BY_REVIEW"
    BLOCKED_BY_DATA_QUALITY = "BLOCKED_BY_DATA_QUALITY"
    NOT_READY = "NOT_READY"
    NON_EXECUTABLE = "NON_EXECUTABLE"


class BlockerSeverity(StrEnum):
    """Severity level of an execution blocker."""

    EXECUTION_ONLY = "EXECUTION_ONLY"
    INVALIDATES_GRADE = "INVALIDATES_GRADE"


class ExecutionBlockerType(StrEnum):
    """Type of execution blocker."""

    POLICY = "POLICY"
    CALENDAR = "CALENDAR"
    DATA_QUALITY = "DATA_QUALITY"
    REVIEW = "REVIEW"
    EXECUTION_MODE = "EXECUTION_MODE"
    RISK_REWARD = "RISK_REWARD"
    GEOMETRY = "GEOMETRY"


class ExecutionBlockerCode(StrEnum):
    """Specific code identifying an execution blocker."""

    # Policy blockers
    POLICY_MAX_DAILY_TRADES = "POLICY_MAX_DAILY_TRADES"
    POLICY_MAX_DAILY_LOSS = "POLICY_MAX_DAILY_LOSS"
    POLICY_MAX_POSITION_SIZE = "POLICY_MAX_POSITION_SIZE"
    POLICY_BLACKOUT_HOUR = "POLICY_BLACKOUT_HOUR"
    POLICY_REQUIRES_REVIEW = "POLICY_REQUIRES_REVIEW"
    POLICY_COUNTERTREND_DISABLED = "POLICY_COUNTERTREND_DISABLED"

    # Calendar blockers
    CALENDAR_HIGH_IMPACT_SOON = "CALENDAR_HIGH_IMPACT_SOON"
    CALENDAR_MEDIUM_IMPACT_SOON = "CALENDAR_MEDIUM_IMPACT_SOON"
    CALENDAR_INSIDE_EVENT_WINDOW = "CALENDAR_INSIDE_EVENT_WINDOW"

    # Data quality blockers
    DATA_QUALITY_MISSING_BARS = "DATA_QUALITY_MISSING_BARS"
    DATA_QUALITY_STALE_DATA = "DATA_QUALITY_STALE_DATA"
    DATA_QUALITY_LOW_CONFIDENCE = "DATA_QUALITY_LOW_CONFIDENCE"
    DATA_QUALITY_INSUFFICIENT_HISTORY = "DATA_QUALITY_INSUFFICIENT_HISTORY"
    DATA_QUALITY_MISSING_D1_DATA = "DATA_QUALITY_MISSING_D1_DATA"
    DATA_QUALITY_MISSING_H4_DATA = "DATA_QUALITY_MISSING_H4_DATA"
    DATA_QUALITY_MISSING_H1_DATA = "DATA_QUALITY_MISSING_H1_DATA"
    DATA_QUALITY_INCOMPLETE_SETUP = "DATA_QUALITY_INCOMPLETE_SETUP"

    # Review blockers
    REVIEW_PENDING = "REVIEW_PENDING"
    REVIEW_REJECTED = "REVIEW_REJECTED"
    REVIEW_REVISION_REQUIRED = "REVIEW_REVISION_REQUIRED"
    REVIEW_UNAVAILABLE = "REVIEW_UNAVAILABLE"
    REVIEW_TRIGGER_NOT_CONFIRMED = "REVIEW_TRIGGER_NOT_CONFIRMED"

    # Execution mode blockers
    EXECUTION_MODE_NOT_LIVE = "EXECUTION_MODE_NOT_LIVE"
    EXECUTION_MODE_SHADOW_ONLY = "EXECUTION_MODE_SHADOW_ONLY"

    # Risk/reward blockers
    RISK_REWARD_BELOW_MINIMUM = "RISK_REWARD_BELOW_MINIMUM"
    RISK_REWARD_CALCULATION_FAILED = "RISK_REWARD_CALCULATION_FAILED"

    # Geometry blockers
    GEOMETRY_INVALID = "GEOMETRY_INVALID"
    GEOMETRY_TEMPORARILY_UNAVAILABLE = "GEOMETRY_TEMPORARILY_UNAVAILABLE"


class EnforcementViolationCode(StrEnum):
    """Code identifying an enforcement violation in the setup."""

    INVALIDATION_ENTRY_AUTHORIZED = "INVALIDATION_ENTRY_AUTHORIZED"
    INVALIDATION_GRADE_DOWNGRADED = "INVALIDATION_GRADE_DOWNGRADED"
    INVALIDATION_SETUP_EXPIRED = "INVALIDATION_SETUP_EXPIRED"
    INVALIDATION_TRIGGER_INVALIDATED = "INVALIDATION_TRIGGER_INVALIDATED"
    INVALIDATION_POLICY_VIOLATION = "INVALIDATION_POLICY_VIOLATION"
    INVALIDATION_CALENDAR_BLOCK = "INVALIDATION_CALENDAR_BLOCK"
    INVALIDATION_DATA_QUALITY = "INVALIDATION_DATA_QUALITY"
    INVALIDATION_REJECTED = "INVALIDATION_REJECTED"

    # Enforcement gate violations (Section 12)
    CANDIDATE_NOT_GENERATED = "CANDIDATE_NOT_GENERATED"
    EXECUTION_NOT_ACTIONABLE = "EXECUTION_NOT_ACTIONABLE"
    DIRECTION_MISMATCH = "DIRECTION_MISMATCH"
    INVALID_GEOMETRY = "INVALID_GEOMETRY"
    ACTION_NOT_ALLOWED = "ACTION_NOT_ALLOWED"


class InvalidationReason(StrEnum):
    """Reason a setup was invalidated."""

    ENTRY_AUTHORIZED = "ENTRY_AUTHORIZED"
    GRADE_DOWNGRADED = "GRADE_DOWNGRADED"
    SETUP_EXPIRED = "SETUP_EXPIRED"
    TRIGGER_INVALIDATED = "TRIGGER_INVALIDATED"
    POLICY_VIOLATION = "POLICY_VIOLATION"
    CALENDAR_BLOCK = "CALENDAR_BLOCK"
    DATA_QUALITY = "DATA_QUALITY"
    REVIEW_REJECTED = "REVIEW_REJECTED"


class GeometryStatus(StrEnum):
    """Status of the geometric validation for a setup."""

    VALID = "VALID"
    TEMPORARILY_UNAVAILABLE = "TEMPORARILY_UNAVAILABLE"
    PERMANENTLY_INVALID = "PERMANENTLY_INVALID"


# ---------------------------------------------------------------------------
# Trigger Enums
# ---------------------------------------------------------------------------


class TriggerType(StrEnum):
    """Type of price action trigger for a setup."""

    NONE = "NONE"
    BULLISH_BOS = "BULLISH_BOS"
    BEARISH_BOS = "BEARISH_BOS"
    BULLISH_CHOCH = "BULLISH_CHOCH"
    BEARISH_CHOCH = "BEARISH_CHOCH"
    RECLAIM = "RECLAIM"
    RETEST = "RETEST"


class TriggerStatus(StrEnum):
    """Status of the trigger confirmation process."""

    NO_TRIGGER = "NO_TRIGGER"
    EARLY_TRANSITION = "EARLY_TRANSITION"
    PENDING_CONFIRMATION = "PENDING_CONFIRMATION"
    CONFIRMED_TRIGGER = "CONFIRMED_TRIGGER"
    INVALIDATED_TRIGGER = "INVALIDATED_TRIGGER"


# ---------------------------------------------------------------------------
# Entry Enums
# ---------------------------------------------------------------------------


class EntryType(StrEnum):
    """Type of entry order for a trade setup."""

    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    WAIT_FOR_CLOSE = "WAIT_FOR_CLOSE"
    WAIT_FOR_RETEST = "WAIT_FOR_RETEST"
    WAIT_FOR_ZONE = "WAIT_FOR_ZONE"


# ---------------------------------------------------------------------------
# Decision Enums
# ---------------------------------------------------------------------------


class DecisionAction(StrEnum):
    """Decision action taken by the decision agent."""

    NO_TRADE = "no_trade"
    WAIT_FOR_SETUP = "wait_for_setup"
    BUY_SETUP = "buy_setup"
    SELL_SETUP = "sell_setup"


class BiasLevel(StrEnum):
    """Structural bias levels."""

    STRONG_BULLISH = "STRONG_BULLISH"
    BULLISH = "BULLISH"
    NEUTRAL_BULLISH = "NEUTRAL_BULLISH"
    NEUTRAL = "NEUTRAL"
    NEUTRAL_BEARISH = "NEUTRAL_BEARISH"
    BEARISH = "BEARISH"
    STRONG_BEARISH = "STRONG_BEARISH"


class TradeDirection(StrEnum):
    """Trade direction based on bias."""

    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


# ---------------------------------------------------------------------------
# Review Enums
# ---------------------------------------------------------------------------


class ReviewStatus(StrEnum):
    """Status of the review process."""

    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    REVISION_REQUIRED = "REVISION_REQUIRED"
    REVIEW_UNAVAILABLE = "REVIEW_UNAVAILABLE"
    REVIEW_ERROR = "REVIEW_ERROR"
    NOT_REQUIRED = "NOT_REQUIRED"


class ReviewerIndependenceLevel(StrEnum):
    """Independence level of the reviewer."""

    NONE = "NONE"
    WEAK = "WEAK"
    STRONG = "STRONG"


# ---------------------------------------------------------------------------
# Execution Mode Enums
# ---------------------------------------------------------------------------


class ExecutionMode(StrEnum):
    """Execution mode of the trading system."""

    DETERMINISTIC_BACKTEST = "DETERMINISTIC_BACKTEST"
    FULL_CHAIN_BACKTEST = "FULL_CHAIN_BACKTEST"
    DEVELOPMENT = "DEVELOPMENT"
    SHADOW = "SHADOW"
    PAPER = "PAPER"
    LIVE = "LIVE"


# ---------------------------------------------------------------------------
# Model Identity Enums
# ---------------------------------------------------------------------------


class ModelIdentityResolutionStatus(StrEnum):
    """Status of model identity resolution."""

    RESOLVED = "RESOLVED"
    OVERRIDDEN = "OVERRIDDEN"
    UNRESOLVED = "UNRESOLVED"


# ---------------------------------------------------------------------------
# Pydantic Data Models
# ---------------------------------------------------------------------------


class ExecutionBlocker(BaseModel, frozen=True):
    """An execution blocker that prevents or delays trade execution.

    Attributes:
        blocker_type: The category of blocker (e.g., POLICY, CALENDAR).
        code: Specific code identifying the blocker reason.
        reason: Human-readable explanation of the blocker.
        severity: Severity level determining impact on setup grade.
    """

    blocker_type: ExecutionBlockerType
    code: ExecutionBlockerCode
    reason: str
    severity: BlockerSeverity


class EnforcementViolation(BaseModel, frozen=True):
    """An enforcement violation detected during setup validation.

    Attributes:
        code: Specific code identifying the violation type.
        reason: Human-readable explanation of the violation.
    """

    code: EnforcementViolationCode
    reason: str


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------


def derive_execution_status(blockers: tuple[ExecutionBlocker, ...]) -> ExecutionStatus:
    """Derive the execution status from a set of blockers.

    Priority order (highest priority checked across ALL blockers first):
    1. Any CALENDAR blocker → BLOCKED_BY_CALENDAR
    2. Any DATA_QUALITY blocker → BLOCKED_BY_DATA_QUALITY
    3. Any POLICY blocker → BLOCKED_BY_POLICY
    4. Any RISK_REWARD blocker with INVALIDATES_GRADE severity → BLOCKED_BY_ENFORCEMENT
    5. Any GEOMETRY blocker with INVALIDATES_GRADE severity → BLOCKED_BY_ENFORCEMENT
    6. Any REVIEW blocker → BLOCKED_BY_REVIEW
    7. No blockers → ACTIONABLE
    """
    types = {b.blocker_type for b in blockers}
    if ExecutionBlockerType.CALENDAR in types:
        return ExecutionStatus.BLOCKED_BY_CALENDAR
    if ExecutionBlockerType.DATA_QUALITY in types:
        return ExecutionStatus.BLOCKED_BY_DATA_QUALITY
    if ExecutionBlockerType.POLICY in types:
        return ExecutionStatus.BLOCKED_BY_POLICY
    if any(
        b.blocker_type == ExecutionBlockerType.RISK_REWARD
        and b.severity == BlockerSeverity.INVALIDATES_GRADE
        for b in blockers
    ):
        return ExecutionStatus.BLOCKED_BY_ENFORCEMENT
    if any(
        b.blocker_type == ExecutionBlockerType.GEOMETRY
        and b.severity == BlockerSeverity.INVALIDATES_GRADE
        for b in blockers
    ):
        return ExecutionStatus.BLOCKED_BY_ENFORCEMENT
    if ExecutionBlockerType.REVIEW in types:
        return ExecutionStatus.BLOCKED_BY_REVIEW
    return ExecutionStatus.ACTIONABLE


def derive_allowed_actions(
    trade_direction: TradeDirection,
    execution_status: ExecutionStatus,
) -> tuple[DecisionAction, ...]:
    """Derive the allowed actions based on trade direction and execution status.

    Rules:
    - ACTIONABLE + BULLISH → (BUY_SETUP,)
    - ACTIONABLE + BEARISH → (SELL_SETUP,)
    - ACTIONABLE + NEUTRAL → (NO_TRADE,)
    - Any non-ACTIONABLE status → (NO_TRADE,)
    """
    if execution_status != ExecutionStatus.ACTIONABLE:
        return (DecisionAction.NO_TRADE,)

    if trade_direction == TradeDirection.BULLISH:
        return (DecisionAction.BUY_SETUP,)
    if trade_direction == TradeDirection.BEARISH:
        return (DecisionAction.SELL_SETUP,)
    return (DecisionAction.NO_TRADE,)


# ---------------------------------------------------------------------------
# Rejection Codes
# ---------------------------------------------------------------------------


class SetupRejectionCode(StrEnum):
    """Structured rejection codes for deterministic setup classification."""

    INVALID_TRADE_DIRECTION = "INVALID_TRADE_DIRECTION"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


# ---------------------------------------------------------------------------
# State Models
# ---------------------------------------------------------------------------


class DeterministicSetupState(BaseModel, frozen=True):
    """Immutable state representing a classified trading setup.

    Captures the full lifecycle of a setup from classification through
    entry plan generation. Fields are populated progressively by the
    deterministic pipeline stages.

    Attributes:
        # Classification
        setup_classification_status: Whether a setup was classified.
        setup_grade: Quality grade (AAA, AA, COUNTERTREND).
        trade_direction: Direction of the trade.

        # Lifecycle
        setup_lifecycle_status: Current lifecycle stage.
        geometry_status: Geometric validation status.
        confirmed_at: ISO timestamp when setup was confirmed.
        confirmed_bar_index: Bar index at confirmation.
        expires_after_h1_bars: Number of H1 bars before expiry.
        invalidation_reason: Why the setup was invalidated, if applicable.

        # D1 timeframe data
        d1_bias: Daily structural bias.
        d1_direction: Daily directional bias.
        d1_is_directional: Whether D1 shows clear direction.
        d1_structure_status: D1 market structure status.
        d1_regime: D1 market regime.
        d1_invalidation_status: D1 invalidation status.

        # H4 timeframe data
        h4_bias: H4 structural bias.
        h4_direction: H4 directional bias.
        h4_alignment_status: H4 alignment with D1.
        h4_structure_status: H4 market structure status.
        h4_pullback_status: H4 pullback status.

        # H1 timeframe data
        h1_bias: H1 structural bias.
        h1_direction: H1 directional bias.
        h1_trigger_type: Type of H1 trigger.
        h1_trigger_status: Confirmation status of the trigger.
        h1_setup_status: H1 setup validation status.

        # Entry plan
        current_price: Current market price.
        entry_type: Type of entry order.
        entry_price: Target entry price.
        entry_zone_low: Lower bound of entry zone.
        entry_zone_high: Upper bound of entry zone.
        trigger_level: Price level for trigger.
        invalidation_price: Price that invalidates the setup.
        target_price: Target take-profit price.
        estimated_reward_risk: Calculated reward-to-risk ratio.
    """

    # Classification
    setup_classification_status: SetupClassificationStatus = Field(
        default=SetupClassificationStatus.NO_SETUP,
        description="Whether a setup was classified",
    )
    setup_grade: SetupGrade | None = Field(
        default=None,
        description="Quality grade (AAA, AA, COUNTERTREND)",
    )
    trade_direction: TradeDirection = Field(
        default=TradeDirection.NEUTRAL,
        description="Direction of the trade",
    )
    rejection_codes: tuple[SetupRejectionCode, ...] = Field(
        default=(),
        description="Structured rejection codes for this setup",
    )

    # Lifecycle
    setup_lifecycle_status: SetupLifecycleStatus = Field(
        default=SetupLifecycleStatus.PENDING,
        description="Current lifecycle stage",
    )
    geometry_status: GeometryStatus = Field(
        default=GeometryStatus.TEMPORARILY_UNAVAILABLE,
        description="Geometric validation status",
    )
    confirmed_at: str | None = Field(
        default=None,
        description="ISO timestamp when setup was confirmed",
    )
    confirmed_bar_index: int | None = Field(
        default=None,
        description="Bar index at confirmation",
    )
    expires_after_h1_bars: int | None = Field(
        default=None,
        description="Number of H1 bars before expiry",
    )
    invalidation_reason: InvalidationReason | None = Field(
        default=None,
        description="Why the setup was invalidated, if applicable",
    )

    # D1 timeframe data
    d1_bias: BiasLevel = Field(
        default=BiasLevel.NEUTRAL,
        description="Daily structural bias",
    )
    d1_direction: TradeDirection = Field(
        default=TradeDirection.NEUTRAL,
        description="Daily directional bias",
    )
    d1_is_directional: bool = Field(
        default=False,
        description="Whether D1 shows clear direction",
    )
    d1_structure_status: str = Field(
        default="UNKNOWN",
        description="D1 market structure status",
    )
    d1_regime: str = Field(
        default="UNKNOWN",
        description="D1 market regime",
    )
    d1_invalidation_status: str | None = Field(
        default=None,
        description="D1 invalidation status",
    )

    # H4 timeframe data
    h4_bias: BiasLevel = Field(
        default=BiasLevel.NEUTRAL,
        description="H4 structural bias",
    )
    h4_direction: TradeDirection = Field(
        default=TradeDirection.NEUTRAL,
        description="H4 directional bias",
    )
    h4_alignment_status: str = Field(
        default="UNKNOWN",
        description="H4 alignment with D1",
    )
    h4_structure_status: str = Field(
        default="UNKNOWN",
        description="H4 market structure status",
    )
    h4_pullback_status: str = Field(
        default="UNKNOWN",
        description="H4 pullback status",
    )

    # H1 timeframe data
    h1_bias: BiasLevel = Field(
        default=BiasLevel.NEUTRAL,
        description="H1 structural bias",
    )
    h1_direction: TradeDirection = Field(
        default=TradeDirection.NEUTRAL,
        description="H1 directional bias",
    )
    h1_trigger_type: TriggerType = Field(
        default=TriggerType.NONE,
        description="Type of H1 trigger",
    )
    h1_trigger_status: TriggerStatus = Field(
        default=TriggerStatus.NO_TRIGGER,
        description="Confirmation status of the trigger",
    )
    h1_setup_status: str = Field(
        default="UNKNOWN",
        description="H1 setup validation status",
    )

    # Entry plan
    current_price: float | None = Field(
        default=None,
        description="Current market price",
    )
    entry_type: EntryType | None = Field(
        default=None,
        description="Type of entry order",
    )
    entry_price: float | None = Field(
        default=None,
        description="Target entry price",
    )
    entry_zone_low: float | None = Field(
        default=None,
        description="Lower bound of entry zone",
    )
    entry_zone_high: float | None = Field(
        default=None,
        description="Upper bound of entry zone",
    )
    trigger_level: float | None = Field(
        default=None,
        description="Price level for trigger",
    )
    invalidation_price: float | None = Field(
        default=None,
        description="Price that invalidates the setup",
    )
    target_price: float | None = Field(
        default=None,
        description="Target take-profit price",
    )
    estimated_reward_risk: float | None = Field(
        default=None,
        description="Calculated reward-to-risk ratio",
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def candidate_generated(self) -> bool:
        """Whether this setup qualifies as a candidate for decision.

        A setup is a candidate when classification is CLASSIFIED and
        a grade has been assigned. Price completeness is checked separately
        by ``deterministic_plan_complete``.
        """
        return (
            self.setup_classification_status == SetupClassificationStatus.CLASSIFIED
            and self.setup_grade is not None
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def deterministic_plan_complete(self) -> bool:
        """Whether all canonical deterministic setup prices are available."""
        return all(
            price is not None
            for price in (
                self.current_price,
                self.entry_price,
                self.invalidation_price,
                self.target_price,
            )
        )


class RiskPolicyState(BaseModel, frozen=True):
    """Immutable state for risk management policy evaluation.

    Attributes:
        base_risk_percentage: Base risk per trade as a percentage.
        grade_risk_multiplier: Multiplier applied based on setup grade.
        minimum_reward_risk: Minimum acceptable reward-to-risk ratio.
        estimated_reward_risk: Calculated reward-to-risk ratio, if available.
    """

    base_risk_percentage: float = Field(
        default=0.0,
        ge=0,
        description="Base risk per trade as a percentage",
    )
    grade_risk_multiplier: float = Field(
        default=1.0,
        ge=0,
        description="Multiplier applied based on setup grade",
    )
    minimum_reward_risk: float = Field(
        default=1.0,
        gt=0,
        description="Minimum acceptable reward-to-risk ratio",
    )
    estimated_reward_risk: float | None = Field(
        default=None,
        gt=0,
        description="Calculated reward-to-risk ratio, if available",
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def final_risk_percentage(self) -> float:
        """Final risk percentage after grade multiplier is applied."""
        return self.base_risk_percentage * self.grade_risk_multiplier

    @computed_field  # type: ignore[prop-decorator]
    @property
    def risk_reward_ok(self) -> bool:
        """Whether the estimated reward-to-risk meets the minimum threshold."""
        return (
            self.estimated_reward_risk is not None
            and self.estimated_reward_risk >= self.minimum_reward_risk
        )


class ExecutionPolicyState(BaseModel, frozen=True):
    """Immutable state for execution policy evaluation.

    Attributes:
        trade_direction: Direction of the trade.
        execution_blockers: Tuple of active execution blockers.
    """

    trade_direction: TradeDirection = Field(
        default=TradeDirection.NEUTRAL,
        description="Direction of the trade",
    )
    execution_blockers: tuple[ExecutionBlocker, ...] = Field(
        default=(),
        description="Tuple of active execution blockers",
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def pre_review_execution_status(self) -> ExecutionStatus:
        """Derive execution status from blockers before review stage."""
        return derive_execution_status(self.execution_blockers)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def allowed_actions(self) -> tuple[DecisionAction, ...]:
        """Derive allowed actions from direction and execution status."""
        return derive_allowed_actions(self.trade_direction, self.pre_review_execution_status)

    @classmethod
    def create(
        cls,
        setup: DeterministicSetupState,
        execution_blockers: tuple[ExecutionBlocker, ...] = (),
    ) -> Self:
        """Create an ExecutionPolicyState from a setup and blockers.

        Extracts the trade direction from the setup and combines it
        with the provided blockers.

        Args:
            setup: The classified setup state.
            execution_blockers: Active execution blockers.

        Returns:
            Configured ExecutionPolicyState instance.
        """
        return cls(
            trade_direction=setup.trade_direction,
            execution_blockers=execution_blockers,
        )


class FinalDecisionState(BaseModel, frozen=True):
    """Immutable state representing the final decision outcome.

    Attributes:
        review_status: Status of the review process.
        final_execution_status: Final execution status after all stages.
        final_action: Decision action taken.
        enforcement_violations: Tuple of enforcement violations detected.
        review_attempts: Number of review attempts made.
        provider_retry_count: Number of provider retries.
        review_revision_count: Number of review revisions.
    """

    review_status: ReviewStatus = Field(
        default=ReviewStatus.NOT_REQUIRED,
        description="Status of the review process",
    )
    final_execution_status: ExecutionStatus = Field(
        default=ExecutionStatus.NOT_READY,
        description="Final execution status after all stages",
    )
    final_action: DecisionAction = Field(
        default=DecisionAction.NO_TRADE,
        description="Decision action taken",
    )
    enforcement_violations: tuple[EnforcementViolation, ...] = Field(
        default=(),
        description="Tuple of enforcement violations detected",
    )
    review_attempts: int = Field(
        default=0,
        description="Number of review attempts made",
    )
    provider_retry_count: int = Field(
        default=0,
        description="Number of provider retries",
    )
    review_revision_count: int = Field(
        default=0,
        description="Number of review revisions",
    )
