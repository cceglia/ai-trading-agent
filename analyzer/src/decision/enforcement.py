"""Deterministic enforcement gate for the trading pipeline.

This module implements :class:`DeterministicEnforcementGate` as specified
in Section 12 of the multi-timeframe pipeline redesign plan. The gate
sits between the deterministic pipeline output and the final decision,
verifying that every executable action satisfies invariants before it
reaches the output stage.

The gate is purely deterministic — no LLM calls, no I/O, no external
dependencies beyond the engine models for type definitions.

Violation checks performed:

    CANDIDATE_NOT_GENERATED
        An executable action (BUY_SETUP / SELL_SETUP) was selected
        without a classified candidate from the deterministic pipeline.

    EXECUTION_NOT_ACTIONABLE
        An executable action was selected while the pre-review execution
        status is not ACTIONABLE (i.e. execution blockers are active).

    DIRECTION_MISMATCH
        The decision action contradicts the deterministic trade direction
        derived from the setup.

    INVALID_GEOMETRY
        An executable action was selected while the deterministic entry
        geometry status is not VALID.

    ACTION_NOT_ALLOWED
        The decision action is not in the set of allowed actions derived
        from the trade direction and execution status.
"""

from __future__ import annotations

import logging

from config.settings import Settings
from src.analysis.market_structure_engine.models import (
    DecisionAction,
    DeterministicSetupState,
    EnforcementViolation,
    EnforcementViolationCode,
    ExecutionPolicyState,
    ExecutionStatus,
    FinalDecisionState,
    GeometryStatus,
    RiskPolicyState,
    TradeDirection,
)
from src.decision.models import DecisionOutput, ReviewVerdict

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Actions considered "executable" (require a classified candidate)
#
# String values are used instead of DecisionAction enums because
# DecisionOutput has use_enum_values=True, which stores the action as
# a plain string rather than a StrEnum member.  Comparing directly
# against the enum would fail at runtime.
# ---------------------------------------------------------------------------
_EXECUTABLE_ACTION_VALUES: frozenset[str] = frozenset({"buy_setup", "sell_setup"})


# ---------------------------------------------------------------------------
# Gate
# ---------------------------------------------------------------------------


class DeterministicEnforcementGate:
    """Enforces deterministic invariants before a decision is finalised.

    The gate inspects the full pipeline state and collects any violations
    of deterministic invariants.  If violations are found, the final
    status is set to ``BLOCKED_BY_ENFORCEMENT`` and the action is forced
    to ``NO_TRADE``.  If the review has not approved an executable action,
    the status is ``BLOCKED_BY_REVIEW``.  Otherwise the pre-review
    execution status and decision action are passed through unchanged.

    The class follows SOLID principles:

    * **SRP** — single responsibility: enforce deterministic invariants.
    * **OCP** — new violation checks can be added as new private methods
      without modifying existing logic.
    * **ISP** — focused solely on enforcement; does not perform review,
      grading, or execution-mode logic.
    * **DIP** — depends only on engine model abstractions, never on
      concrete implementations.
    """

    def enforce(
        self,
        *,
        setup: DeterministicSetupState,
        policy: ExecutionPolicyState,
        risk: RiskPolicyState,
        decision: DecisionOutput,
        review: ReviewVerdict,
        settings: Settings,
        provider_retry_count: int = 0,
        review_revision_count: int = 0,
    ) -> FinalDecisionState:
        """Evaluate all enforcement checks and produce a final decision state.

        Args:
            setup: Classified setup from the deterministic grading stage.
            policy: Execution policy derived from the setup and blockers.
            risk: Risk policy derived from the setup grade.
            decision: LLM decision output (action + reasoning).
            review: Review verdict from the reviewer agent.
            settings: Runtime settings (reserved for future policy knobs).
            provider_retry_count: Number of LLM provider retries so far.
            review_revision_count: Number of review revision cycles so far.

        Returns:
            An immutable :class:`FinalDecisionState` with the resolved
            execution status, final action, and any violations detected.
        """
        violations: list[EnforcementViolation] = []

        self._check_candidate_generated(setup, decision, violations)
        self._check_execution_actionable(policy, decision, violations)
        self._check_direction_mismatch(setup, decision, violations)
        self._check_invalid_geometry(setup, decision, violations)
        self._check_action_not_allowed(policy, decision, violations)

        # ── Resolve final status ────────────────────────────────────────
        violations_tuple = tuple(violations)

        if violations:
            # Any violation forces a hard block.
            final_status = ExecutionStatus.BLOCKED_BY_ENFORCEMENT
            final_action = DecisionAction.NO_TRADE
            logger.info(
                "Enforcement gate: BLOCKED — %d violation(s) detected",
                len(violations),
            )
            for v in violations:
                logger.info(
                    "  violation: %s — %s",
                    v.code.value,
                    v.reason,
                )
        elif decision.action in _EXECUTABLE_ACTION_VALUES and not review.approved:
            # Executable action requires an approved review.
            final_status = ExecutionStatus.BLOCKED_BY_REVIEW
            final_action = DecisionAction.NO_TRADE
            logger.info(
                "Enforcement gate: BLOCKED_BY_REVIEW — action %s not approved",
                decision.action,
            )
        else:
            # Pass through the deterministic execution status and decision action.
            final_status = policy.pre_review_execution_status
            final_action = decision.action

        return FinalDecisionState(
            review_status=review.status,
            final_execution_status=final_status,
            final_action=final_action,
            enforcement_violations=violations_tuple,
            review_attempts=0,
            provider_retry_count=provider_retry_count,
            review_revision_count=review_revision_count,
        )

    # ------------------------------------------------------------------
    # Violation checks (each appends to the violations list)
    # ------------------------------------------------------------------

    @staticmethod
    def _check_candidate_generated(
        setup: DeterministicSetupState,
        decision: DecisionOutput,
        violations: list[EnforcementViolation],
    ) -> None:
        """CANDIDATE_NOT_GENERATED: executable action without classified candidate."""
        if decision.action in _EXECUTABLE_ACTION_VALUES and not setup.candidate_generated:
            violations.append(
                EnforcementViolation(
                    code=EnforcementViolationCode.CANDIDATE_NOT_GENERATED,
                    reason=(
                        f"Action {decision.action} requires a classified candidate "
                        f"but setup classification is "
                        f"{setup.setup_classification_status.value}"
                    ),
                )
            )

    @staticmethod
    def _check_execution_actionable(
        policy: ExecutionPolicyState,
        decision: DecisionOutput,
        violations: list[EnforcementViolation],
    ) -> None:
        """EXECUTION_NOT_ACTIONABLE: executable action while not ACTIONABLE."""
        if decision.action in _EXECUTABLE_ACTION_VALUES:
            if policy.pre_review_execution_status != ExecutionStatus.ACTIONABLE:
                violations.append(
                    EnforcementViolation(
                        code=EnforcementViolationCode.EXECUTION_NOT_ACTIONABLE,
                        reason=(
                            f"Action {decision.action} requires ACTIONABLE status "
                            f"but current status is "
                            f"{policy.pre_review_execution_status.value}"
                        ),
                    )
                )

    @staticmethod
    def _check_direction_mismatch(
        setup: DeterministicSetupState,
        decision: DecisionOutput,
        violations: list[EnforcementViolation],
    ) -> None:
        """DIRECTION_MISMATCH: decision contradicts deterministic direction."""
        if decision.action not in _EXECUTABLE_ACTION_VALUES:
            return

        # Map decision action → expected trade direction
        expected_direction: TradeDirection | None
        if decision.action == DecisionAction.BUY_SETUP:
            expected_direction = TradeDirection.BULLISH
        elif decision.action == DecisionAction.SELL_SETUP:
            expected_direction = TradeDirection.BEARISH
        else:
            expected_direction = None

        if expected_direction is None:
            return

        if (
            setup.trade_direction != TradeDirection.NEUTRAL
            and setup.trade_direction != expected_direction
        ):
            violations.append(
                EnforcementViolation(
                    code=EnforcementViolationCode.DIRECTION_MISMATCH,
                    reason=(
                        f"Action {decision.action} implies {expected_direction.value} "
                        f"direction but deterministic setup is "
                        f"{setup.trade_direction.value}"
                    ),
                )
            )

    @staticmethod
    def _check_invalid_geometry(
        setup: DeterministicSetupState,
        decision: DecisionOutput,
        violations: list[EnforcementViolation],
    ) -> None:
        """INVALID_GEOMETRY: executable action with non-VALID geometry."""
        if decision.action in _EXECUTABLE_ACTION_VALUES:
            if setup.geometry_status != GeometryStatus.VALID:
                violations.append(
                    EnforcementViolation(
                        code=EnforcementViolationCode.INVALID_GEOMETRY,
                        reason=(
                            f"Action {decision.action} requires VALID geometry "
                            f"but geometry status is "
                            f"{setup.geometry_status.value}"
                        ),
                    )
                )

    @staticmethod
    def _check_action_not_allowed(
        policy: ExecutionPolicyState,
        decision: DecisionOutput,
        violations: list[EnforcementViolation],
    ) -> None:
        """ACTION_NOT_ALLOWED: decision action not in derived allowed actions."""
        if decision.action not in policy.allowed_actions:
            allowed_str = ", ".join(a.value for a in policy.allowed_actions)
            violations.append(
                EnforcementViolation(
                    code=EnforcementViolationCode.ACTION_NOT_ALLOWED,
                    reason=(f"Action {decision.action} is not in the allowed set: [{allowed_str}]"),
                )
            )
