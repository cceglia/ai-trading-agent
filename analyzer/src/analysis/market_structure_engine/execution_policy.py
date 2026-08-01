"""Deterministic execution policy evaluation for the multi-timeframe pipeline.

This module implements ``evaluate_execution_policy()`` as specified in Section 5.3
of the multi-timeframe pipeline redesign plan. It consumes a classified setup
state and risk policy, applies execution rules, and constructs an immutable
:class:`ExecutionPolicyState` populated with any active blockers.

The module is purely deterministic — no LLM calls, no I/O, no external
dependencies beyond the models module for type definitions.

Blocker conditions evaluated:
    - COUNTERTREND_DISABLED: Setup grade is COUNTERTREND but countertrend is disabled
    - HIGH_IMPACT_EVENT: Calendar has a high-impact event imminent
    - RISK_REWARD_MISSING: Estimated reward-to-risk ratio is not available
    - RISK_REWARD_BELOW_MINIMUM: Reward-to-risk ratio below minimum threshold
    - TRIGGER_NOT_CONFIRMED: H1 trigger status is not CONFIRMED
    - MISSING_D1_DATA / MISSING_H4_DATA / MISSING_H1_DATA: Timeframe data absent
    - INVALID_ENTRY_GEOMETRY: Entry geometry status is not VALID

The computed fields ``pre_review_execution_status`` and ``allowed_actions`` on
the returned :class:`ExecutionPolicyState` are derived automatically from the
blockers via ``derive_execution_status()`` and ``derive_allowed_actions()``.
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import (
    BlockerSeverity,
    DeterministicSetupState,
    ExecutionBlocker,
    ExecutionBlockerCode,
    ExecutionBlockerType,
    ExecutionMode,
    ExecutionPolicyState,
    GeometryStatus,
    RiskPolicyState,
    SetupGrade,
    TriggerStatus,
)

# ---------------------------------------------------------------------------
# Policy Settings
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PolicySettings:
    """Configuration for execution policy evaluation.

    Attributes:
        countertrend_enabled: Whether countertrend setups are allowed.
        high_impact_calendar_block: Whether high-impact calendar events block execution.
        minimum_reward_risk: Minimum acceptable reward-to-risk ratio (used for
            validation; the actual threshold lives in RiskPolicyState).
        require_confirmed_trigger: Whether a confirmed trigger is required.
        require_valid_geometry: Whether valid entry geometry is required.
    """

    countertrend_enabled: bool = False
    high_impact_calendar_block: bool = True
    minimum_reward_risk: float = 1.0
    require_confirmed_trigger: bool = True
    require_valid_geometry: bool = True


# ---------------------------------------------------------------------------
# Helper: build blockers
# ---------------------------------------------------------------------------


def _build_blockers(
    setup: DeterministicSetupState,
    risk_policy: RiskPolicyState,
    has_high_impact_event: bool,
    settings: PolicySettings,
) -> list[ExecutionBlocker]:
    """Evaluate all blocker conditions and return the active blockers.

    This is an internal helper; callers use :func:`evaluate_execution_policy`.
    """
    blockers: list[ExecutionBlocker] = []

    # ── Policy: countertrend disabled ──────────────────────────────────
    if setup.setup_grade == SetupGrade.COUNTERTREND and not settings.countertrend_enabled:
        blockers.append(
            ExecutionBlocker(
                blocker_type=ExecutionBlockerType.POLICY,
                code=ExecutionBlockerCode.POLICY_COUNTERTREND_DISABLED,
                reason="Countertrend setup is disabled by policy",
                severity=BlockerSeverity.INVALIDATES_GRADE,
            )
        )

    # ── Calendar: high-impact event ────────────────────────────────────
    if has_high_impact_event and settings.high_impact_calendar_block:
        blockers.append(
            ExecutionBlocker(
                blocker_type=ExecutionBlockerType.CALENDAR,
                code=ExecutionBlockerCode.CALENDAR_HIGH_IMPACT_SOON,
                reason="High-impact calendar event imminent",
                severity=BlockerSeverity.EXECUTION_ONLY,
            )
        )

    # ── Risk/reward: missing ───────────────────────────────────────────
    if risk_policy.estimated_reward_risk is None:
        blockers.append(
            ExecutionBlocker(
                blocker_type=ExecutionBlockerType.RISK_REWARD,
                code=ExecutionBlockerCode.RISK_REWARD_CALCULATION_FAILED,
                reason="Reward-to-risk ratio could not be calculated",
                severity=BlockerSeverity.INVALIDATES_GRADE,
            )
        )
    # ── Risk/reward: below minimum ─────────────────────────────────────
    elif not risk_policy.risk_reward_ok:
        blockers.append(
            ExecutionBlocker(
                blocker_type=ExecutionBlockerType.RISK_REWARD,
                code=ExecutionBlockerCode.RISK_REWARD_BELOW_MINIMUM,
                reason=(
                    f"Reward-to-risk {risk_policy.estimated_reward_risk:.2f} "
                    f"below minimum {risk_policy.minimum_reward_risk:.2f}"
                ),
                severity=BlockerSeverity.INVALIDATES_GRADE,
            )
        )

    # ── Trigger: not confirmed ─────────────────────────────────────────
    if settings.require_confirmed_trigger and setup.h1_trigger_status not in (
        TriggerStatus.CONFIRMED_TRIGGER,
    ):
        blockers.append(
            ExecutionBlocker(
                blocker_type=ExecutionBlockerType.REVIEW,
                code=ExecutionBlockerCode.REVIEW_TRIGGER_NOT_CONFIRMED,
                reason=(f"Trigger status {setup.h1_trigger_status.value} is not CONFIRMED"),
                severity=BlockerSeverity.EXECUTION_ONLY,
            )
        )

    # ── Data quality: missing timeframe data ───────────────────────────
    if not setup.d1_is_directional and setup.d1_structure_status == "UNKNOWN":
        blockers.append(
            ExecutionBlocker(
                blocker_type=ExecutionBlockerType.DATA_QUALITY,
                code=ExecutionBlockerCode.DATA_QUALITY_MISSING_D1_DATA,
                reason="D1 timeframe data is missing or unanalyzed",
                severity=BlockerSeverity.INVALIDATES_GRADE,
            )
        )

    if setup.h4_alignment_status == "UNKNOWN" and setup.h4_structure_status == "UNKNOWN":
        blockers.append(
            ExecutionBlocker(
                blocker_type=ExecutionBlockerType.DATA_QUALITY,
                code=ExecutionBlockerCode.DATA_QUALITY_MISSING_H4_DATA,
                reason="H4 timeframe data is missing or unanalyzed",
                severity=BlockerSeverity.INVALIDATES_GRADE,
            )
        )

    if setup.h1_setup_status == "UNKNOWN":
        blockers.append(
            ExecutionBlocker(
                blocker_type=ExecutionBlockerType.DATA_QUALITY,
                code=ExecutionBlockerCode.DATA_QUALITY_MISSING_H1_DATA,
                reason="H1 timeframe data is missing or unanalyzed",
                severity=BlockerSeverity.INVALIDATES_GRADE,
            )
        )

    # ── Geometry: invalid ──────────────────────────────────────────────
    if settings.require_valid_geometry and setup.geometry_status != GeometryStatus.VALID:
        blockers.append(
            ExecutionBlocker(
                blocker_type=ExecutionBlockerType.GEOMETRY,
                code=ExecutionBlockerCode.GEOMETRY_INVALID,
                reason=(f"Entry geometry status {setup.geometry_status.value} is not VALID"),
                severity=BlockerSeverity.INVALIDATES_GRADE,
            )
        )

    # ── Deterministic plan: incomplete ─────────────────────────────────
    if not setup.deterministic_plan_complete:
        blockers.append(
            ExecutionBlocker(
                blocker_type=ExecutionBlockerType.DATA_QUALITY,
                code=ExecutionBlockerCode.DATA_QUALITY_INCOMPLETE_SETUP,
                reason=(
                    "Deterministic setup is incomplete: canonical current price, "
                    "entry, stop loss, and take profit are all required"
                ),
                severity=BlockerSeverity.INVALIDATES_GRADE,
            )
        )

    return blockers


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def evaluate_execution_policy(
    *,
    setup: DeterministicSetupState,
    risk_policy: RiskPolicyState,
    has_high_impact_event: bool = False,
    execution_mode: ExecutionMode = ExecutionMode.DEVELOPMENT,
    settings: PolicySettings | None = None,
) -> ExecutionPolicyState:
    """Evaluate execution policy and return an :class:`ExecutionPolicyState`.

    Consumes a classified setup and risk policy, applies all execution rules
    (policy, calendar, risk/reward, trigger, data quality, geometry), and
    constructs an immutable state with the resulting blockers.

    The computed fields ``pre_review_execution_status`` and ``allowed_actions``
    are derived automatically from the blockers via ``derive_execution_status()``
    and ``derive_allowed_actions()``.

    Args:
        setup: The classified setup state from the grading stage.
        risk_policy: The risk policy state from the risk policy stage.
        has_high_impact_event: Whether a high-impact calendar event is imminent.
        execution_mode: Current execution mode (DEVELOPMENT, SHADOW, LIVE, etc.).
            **Reserved for future use.**  The parameter is accepted for API
            consistency but is not yet evaluated; all execution policies are
            currently treated the same regardless of mode.
        settings: Optional policy settings override. Uses defaults when ``None``.

    Returns:
        An immutable ``ExecutionPolicyState`` with all active blockers and
        derived status/actions.

    Example::

        >>> state = evaluate_execution_policy(
        ...     setup=my_setup,
        ...     risk_policy=my_risk_policy,
        ...     has_high_impact_event=True,
        ... )
        >>> state.pre_review_execution_status
        <ExecutionStatus.BLOCKED_BY_CALENDAR: 'BLOCKED_BY_CALENDAR'>
        >>> state.allowed_actions
        (<DecisionAction.NO_TRADE: 'no_trade'>,)
    """
    resolved_settings = settings or PolicySettings()

    blockers = _build_blockers(
        setup=setup,
        risk_policy=risk_policy,
        has_high_impact_event=has_high_impact_event,
        settings=resolved_settings,
    )

    return ExecutionPolicyState.create(
        setup=setup,
        execution_blockers=tuple(blockers),
    )
