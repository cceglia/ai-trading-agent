"""Integration tests for the full pipeline: enforcement gate + output assembler.

Tests the interplay of DeterministicSetupState, ExecutionPolicyState,
RiskPolicyState, DecisionOutput, ReviewVerdict through the enforcement gate
and output assembler, covering the 7 scenarios from Section 17 of the plan.

NOTE: DecisionOutput has use_enum_values=True, so constructing it normally
serialises action to a str. We use model_construct() to keep the action as a
DecisionAction enum because the enforcement gate calls .value on it.
"""

from __future__ import annotations

from config.settings import Settings
from src.analysis.market_structure_engine.models import (
    BlockerSeverity,
    DecisionAction,
    DeterministicSetupState,
    EnforcementViolationCode,
    ExecutionBlocker,
    ExecutionBlockerCode,
    ExecutionBlockerType,
    ExecutionPolicyState,
    ExecutionStatus,
    GeometryStatus,
    ReviewStatus,
    RiskPolicyState,
    SetupClassificationStatus,
    SetupGrade,
    SetupLifecycleStatus,
    TradeDirection,
    TriggerStatus,
)
from src.decision.enforcement import DeterministicEnforcementGate
from src.decision.models import DecisionOutput, ReviewVerdict
from src.decision.output_assembler import FinalOutputAssembler

# ---------------------------------------------------------------------------
# Helpers (following conventions from tests/decision/test_enforcement.py)
# ---------------------------------------------------------------------------


def _make_setup(
    *,
    classification: SetupClassificationStatus = SetupClassificationStatus.CLASSIFIED,
    grade: SetupGrade | None = SetupGrade.AAA,
    trade_direction: TradeDirection = TradeDirection.BULLISH,
    geometry: GeometryStatus = GeometryStatus.VALID,
    lifecycle: SetupLifecycleStatus = SetupLifecycleStatus.READY,
    estimated_rr: float | None = 3.5,
    **kwargs,
) -> DeterministicSetupState:
    """Build a deterministic setup state with sensible defaults."""
    params: dict = {
        "setup_classification_status": classification,
        "setup_grade": grade,
        "trade_direction": trade_direction,
        "setup_lifecycle_status": lifecycle,
        "geometry_status": geometry,
        "h1_trigger_status": TriggerStatus.CONFIRMED_TRIGGER,
        "h1_setup_status": "VALID_SETUP",
        "d1_is_directional": True,
        "d1_structure_status": "DIRECTIONAL",
        "h4_alignment_status": "ALIGNED",
        "h4_structure_status": "TRENDING",
        "current_price": 2365.50,
        "entry_price": 2360.00,
        "entry_zone_low": 2358.00,
        "entry_zone_high": 2362.00,
        "trigger_level": 2360.00,
        "invalidation_price": 2345.00,
        "target_price": 2410.00,
        "estimated_reward_risk": estimated_rr,
    }
    params.update(kwargs)
    return DeterministicSetupState(**params)


def _make_policy(
    *,
    trade_direction: TradeDirection = TradeDirection.BULLISH,
    execution_blockers: tuple[ExecutionBlocker, ...] = (),
) -> ExecutionPolicyState:
    """Create an ExecutionPolicyState.

    Computed fields (pre_review_execution_status, allowed_actions) are
    derived automatically from blockers and trade direction.
    """
    return ExecutionPolicyState(
        trade_direction=trade_direction,
        execution_blockers=execution_blockers,
    )


def _make_risk_policy(
    *,
    base_risk: float = 1.0,
    multiplier: float = 1.5,
    min_rr: float = 1.5,
    estimated_rr: float | None = 3.5,
) -> RiskPolicyState:
    """Create a RiskPolicyState with sensible defaults."""
    return RiskPolicyState(
        base_risk_percentage=base_risk,
        grade_risk_multiplier=multiplier,
        minimum_reward_risk=min_rr,
        estimated_reward_risk=estimated_rr,
    )


def _make_decision(
    *,
    action: DecisionAction = DecisionAction.BUY_SETUP,
    symbol: str = "XAUUSD",
    reasoning: str = "Test reasoning",
) -> DecisionOutput:
    """Create DecisionOutput with enum action preserved.

    Uses model_construct to bypass use_enum_values=True serialisation,
    so that enforcement code can safely call .value on the action attribute.
    """
    return DecisionOutput.model_construct(
        symbol=symbol,
        action=action,
        reasoning=reasoning,
    )


def _make_review(
    *,
    status: ReviewStatus = ReviewStatus.APPROVED,
    reasoning: str = "Approved by reviewer",
) -> ReviewVerdict:
    """Create a ReviewVerdict."""
    return ReviewVerdict(status=status, reasoning=reasoning)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_settings = Settings()


def _run_pipeline(
    *,
    setup: DeterministicSetupState,
    policy: ExecutionPolicyState,
    risk: RiskPolicyState,
    decision: DecisionOutput,
    review: ReviewVerdict,
) -> tuple:
    """Run the enforcement gate and output assembler, return both results.

    Returns (FinalDecisionState, AnalysisResult).
    """
    gate = DeterministicEnforcementGate()
    enforcement = gate.enforce(
        setup=setup,
        policy=policy,
        risk=risk,
        decision=decision,
        review=review,
        settings=_settings,
    )
    assembler = FinalOutputAssembler()
    result = assembler.assemble(
        setup=setup,
        policy=policy,
        risk=risk,
        decision=decision,
        review=review,
        enforcement=enforcement,
    )
    return enforcement, result


# ============================================================================
# Section 17 Scenarios
# ============================================================================


class TestValidAAAPipeline:
    """Scenario 1: Valid AAA pipeline with all stages green."""

    def test_enforcement_passes_without_violations(self) -> None:
        setup = _make_setup()
        policy = _make_policy()
        risk = _make_risk_policy()
        decision = _make_decision(action=DecisionAction.BUY_SETUP)
        review = _make_review()

        enforcement, result = _run_pipeline(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
        )

        # ── Enforcement gate ─────────────────────────────────────────────
        assert len(enforcement.enforcement_violations) == 0
        assert enforcement.final_execution_status == ExecutionStatus.ACTIONABLE
        assert enforcement.final_action == DecisionAction.BUY_SETUP

        # ── Output assembler ─────────────────────────────────────────────
        assert result.setup_grade == "AAA"
        assert result.final_action == "buy_setup"
        assert result.execution_status == "ACTIONABLE"
        assert result.status == "success"


class TestReviewerRejection:
    """Scenario 2: Reviewer rejects a BUY_SETUP decision."""

    def test_reviewer_rejection_blocks_execution(self) -> None:
        setup = _make_setup()
        policy = _make_policy()
        risk = _make_risk_policy()
        decision = _make_decision(action=DecisionAction.BUY_SETUP)
        review = _make_review(status=ReviewStatus.REJECTED, reasoning="Risky setup")

        enforcement, result = _run_pipeline(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
        )

        # ── Enforcement gate ─────────────────────────────────────────────
        # No deterministic violations (setup is valid) but review blocked the
        # executable action → BLOCKED_BY_REVIEW
        assert len(enforcement.enforcement_violations) == 0
        assert enforcement.final_execution_status == ExecutionStatus.BLOCKED_BY_REVIEW
        assert enforcement.final_action == DecisionAction.NO_TRADE

        # ── Output assembler ─────────────────────────────────────────────
        assert result.final_action == "no_trade"


class TestReviewerUnavailableNoTrade:
    """Scenario 3: Reviewer unavailable with NO_TRADE decision.

    NO_TRADE is non-executable so the review check is bypassed —
    the action passes through unchanged.
    """

    def test_non_executable_action_bypasses_review_check(self) -> None:
        # Use NEUTRAL trade direction so that allowed_actions = (NO_TRADE,)
        # when execution status is ACTIONABLE.  NO_TRADE is non-executable
        # and should pass through regardless of review availability.
        setup = _make_setup(trade_direction=TradeDirection.NEUTRAL)
        policy = _make_policy(trade_direction=TradeDirection.NEUTRAL)
        risk = _make_risk_policy()
        decision = _make_decision(action=DecisionAction.NO_TRADE, reasoning="Wait for better setup")
        review = _make_review(status=ReviewStatus.REVIEW_UNAVAILABLE, reasoning="Reviewer offline")

        enforcement, result = _run_pipeline(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
        )

        # ── Enforcement gate ─────────────────────────────────────────────
        # NO_TRADE is not in _EXECUTABLE_ACTION_VALUES → all executable checks skip,
        # review check is also skipped → passes through policy status
        assert len(enforcement.enforcement_violations) == 0
        assert enforcement.final_execution_status == ExecutionStatus.ACTIONABLE
        assert enforcement.final_action == DecisionAction.NO_TRADE

        # ── Output assembler ─────────────────────────────────────────────
        assert result.final_action == "no_trade"


class TestReviewerUnavailableBuySetup:
    """Scenario 4: Reviewer unavailable with BUY_SETUP decision.

    BUY_SETUP is executable but the review is not APPROVED →
    blocked by review.
    """

    def test_executable_action_blocked_by_unavailable_review(self) -> None:
        setup = _make_setup()
        policy = _make_policy()
        risk = _make_risk_policy()
        decision = _make_decision(action=DecisionAction.BUY_SETUP, reasoning="Bullish structure")
        review = _make_review(
            status=ReviewStatus.REVIEW_UNAVAILABLE,
            reasoning="Reviewer unavailable",
        )

        enforcement, result = _run_pipeline(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
        )

        # ── Enforcement gate ─────────────────────────────────────────────
        # No deterministic violations (setup is valid) but the review is not
        # APPROVED and the action is executable → BLOCKED_BY_REVIEW
        assert len(enforcement.enforcement_violations) == 0
        assert enforcement.final_execution_status == ExecutionStatus.BLOCKED_BY_REVIEW
        assert enforcement.final_action == DecisionAction.NO_TRADE

        # ── Output assembler ─────────────────────────────────────────────
        assert result.final_action == "no_trade"


class TestGradePreservedWithCalendarBlock:
    """Scenario 5: Grade preserved when calendar blocks execution.

    The deterministic grade (AAA) must survive into the output even when
    BLOCKED_BY_CALENDAR prevents execution. The action is NO_TRADE because
    allowed_actions excludes BUY_SETUP when blocked.
    """

    def test_grade_preserved_with_calendar_block(self) -> None:
        setup = _make_setup(grade=SetupGrade.AAA)
        calendar_blocker = ExecutionBlocker(
            blocker_type=ExecutionBlockerType.CALENDAR,
            code=ExecutionBlockerCode.CALENDAR_HIGH_IMPACT_SOON,
            reason="High-impact NFP event within 2 hours",
            severity=BlockerSeverity.EXECUTION_ONLY,
        )
        policy = _make_policy(
            trade_direction=TradeDirection.BULLISH,
            execution_blockers=(calendar_blocker,),
        )
        risk = _make_risk_policy()
        decision = _make_decision(
            action=DecisionAction.NO_TRADE,
            reasoning="Calendar block — no trade",
        )
        review = _make_review(status=ReviewStatus.APPROVED)

        enforcement, result = _run_pipeline(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
        )

        # ── Enforcement gate ─────────────────────────────────────────────
        # NO_TRADE is not executable → passes through policy status
        assert len(enforcement.enforcement_violations) == 0
        assert enforcement.final_execution_status == ExecutionStatus.BLOCKED_BY_CALENDAR
        assert enforcement.final_action == DecisionAction.NO_TRADE

        # ── Output assembler ─────────────────────────────────────────────
        # Grade is determined by setup, not by execution status
        assert result.setup_grade == "AAA"
        assert result.execution_status == "BLOCKED_BY_CALENDAR"
        assert result.final_action == "no_trade"

        # Calendar blocker is preserved
        assert len(result.execution_blockers) == 1
        blocker = result.execution_blockers[0]
        assert blocker["blocker_type"] == "CALENDAR"
        assert blocker["code"] == "CALENDAR_HIGH_IMPACT_SOON"


class TestMultipleBlockers:
    """Scenario 6: Multiple blockers from different categories.

    When COUNTERTREND is disabled, calendar has a high-impact event, and
    the R/R ratio is below minimum, all blockers are preserved and the
    pre-review execution status reflects the highest-priority blocker.
    """

    def test_multiple_blockers_all_preserved(self) -> None:
        setup = _make_setup(
            grade=SetupGrade.COUNTERTREND,
            trade_direction=TradeDirection.BULLISH,
        )
        policy_blocker = ExecutionBlocker(
            blocker_type=ExecutionBlockerType.POLICY,
            code=ExecutionBlockerCode.POLICY_COUNTERTREND_DISABLED,
            reason="Countertrend setup is disabled by policy",
            severity=BlockerSeverity.INVALIDATES_GRADE,
        )
        rr_blocker = ExecutionBlocker(
            blocker_type=ExecutionBlockerType.RISK_REWARD,
            code=ExecutionBlockerCode.RISK_REWARD_BELOW_MINIMUM,
            reason="Reward-to-risk 1.20 below minimum 2.00",
            severity=BlockerSeverity.INVALIDATES_GRADE,
        )
        # POLICY has higher priority than RISK_REWARD in derive_execution_status
        policy = _make_policy(
            trade_direction=TradeDirection.BULLISH,
            execution_blockers=(policy_blocker, rr_blocker),
        )
        risk = _make_risk_policy(
            multiplier=0.25,
            estimated_rr=1.2,
            min_rr=2.0,
        )
        decision = _make_decision(
            action=DecisionAction.NO_TRADE,
            reasoning="Multiple blockers prevent trade",
        )
        review = _make_review(status=ReviewStatus.NOT_REQUIRED)

        enforcement, result = _run_pipeline(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
        )

        # ── Enforcement gate ─────────────────────────────────────────────
        # NO_TRADE is non-executable → passes through policy status
        assert len(enforcement.enforcement_violations) == 0
        assert enforcement.final_execution_status == ExecutionStatus.BLOCKED_BY_POLICY
        assert enforcement.final_action == DecisionAction.NO_TRADE

        # ── Output assembler ─────────────────────────────────────────────
        assert result.final_action == "no_trade"
        assert result.execution_status == "BLOCKED_BY_POLICY"

        # All blockers are preserved in the output
        assert len(result.execution_blockers) == 2
        codes = {b["code"] for b in result.execution_blockers}
        assert "POLICY_COUNTERTREND_DISABLED" in codes
        assert "RISK_REWARD_BELOW_MINIMUM" in codes


class TestEnforcementViolationDirectionMismatch:
    """Scenario 7: DIRECTION_MISMATCH enforcement violation.

    The decider produces BUY_SETUP but the deterministic trade direction
    is BEARISH. The enforcement gate detects the mismatch, blocks
    execution, and records the violation. ACTION_NOT_ALLOWED also
    fires since BUY_SETUP is not in the allowed set for BEARISH.
    """

    def test_direction_mismatch_detected(self) -> None:
        setup = _make_setup(
            grade=SetupGrade.AAA,
            trade_direction=TradeDirection.BEARISH,
            geometry=GeometryStatus.VALID,
        )
        # With BEARISH direction and no blockers → allowed_actions = (SELL_SETUP,)
        policy = _make_policy(
            trade_direction=TradeDirection.BEARISH,
            execution_blockers=(),
        )
        risk = _make_risk_policy()
        decision = _make_decision(
            action=DecisionAction.BUY_SETUP,
            reasoning="Bullish signal detected",
        )
        review = _make_review(status=ReviewStatus.APPROVED)

        enforcement, result = _run_pipeline(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
        )

        # ── Enforcement gate ─────────────────────────────────────────────
        # Violations: DIRECTION_MISMATCH (BUY_SETUP vs BEARISH direction)
        #             ACTION_NOT_ALLOWED (BUY_SETUP ∉ {SELL_SETUP})
        assert len(enforcement.enforcement_violations) > 0
        violation_codes = {v.code for v in enforcement.enforcement_violations}
        assert EnforcementViolationCode.DIRECTION_MISMATCH in violation_codes

        assert enforcement.final_execution_status == ExecutionStatus.BLOCKED_BY_ENFORCEMENT
        assert enforcement.final_action == DecisionAction.NO_TRADE

        # ── Output assembler ─────────────────────────────────────────────
        assert result.final_action == "no_trade"
        assert result.status == "partial"  # violations trigger "partial" status
        assert len(result.enforcement_violations) > 0
        assert result.execution_status == "ACTIONABLE"  # unchanged from policy
