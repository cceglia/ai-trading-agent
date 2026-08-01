"""Tests for final decision output assembler (Section 16.9).

Tests the FinalOutputAssembler class from decision/output_assembler.py:

- Entry/stop/target from DeterministicSetupState
- Risk from RiskPolicyState
- Reasoning from LLM
- Enforcement violations in output
- NOT_REQUIRED review for early bypass
- LLM never overrides deterministic values
"""

from __future__ import annotations

from src.analysis.market_structure_engine.models import (
    BlockerSeverity,
    DecisionAction,
    DeterministicSetupState,
    EnforcementViolation,
    EnforcementViolationCode,
    EntryType,
    ExecutionBlocker,
    ExecutionBlockerCode,
    ExecutionBlockerType,
    ExecutionPolicyState,
    ExecutionStatus,
    FinalDecisionState,
    GeometryStatus,
    ReviewStatus,
    RiskPolicyState,
    SetupClassificationStatus,
    SetupGrade,
    SetupLifecycleStatus,
    SetupRejectionCode,
    TradeDirection,
    TriggerStatus,
)
from src.decision.models import AdvisoryLevels, DecisionOutput, ReviewVerdict
from src.decision.output_assembler import FinalOutputAssembler

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_setup(
    *,
    grade: SetupGrade = SetupGrade.AAA,
    trade_direction: TradeDirection = TradeDirection.BULLISH,
    classification: SetupClassificationStatus = SetupClassificationStatus.CLASSIFIED,
    lifecycle: SetupLifecycleStatus = SetupLifecycleStatus.TRIGGERED,
    geometry: GeometryStatus = GeometryStatus.VALID,
    entry_price: float | None = 1.1010,
    target_price: float | None = 1.1100,
    invalidation_price: float | None = 1.0980,
    estimated_rr: float | None = 3.0,
    entry_type: EntryType | None = EntryType.STOP,
    **kwargs,
) -> DeterministicSetupState:
    params = dict(
        setup_classification_status=classification,
        setup_grade=grade,
        trade_direction=trade_direction,
        setup_lifecycle_status=lifecycle,
        geometry_status=geometry,
        h1_trigger_status=TriggerStatus.CONFIRMED_TRIGGER,
        h1_setup_status="VALID_SETUP",
        current_price=1.1000,
        entry_type=entry_type,
        entry_price=entry_price,
        entry_zone_low=1.1005,
        entry_zone_high=1.1015,
        trigger_level=1.1010,
        invalidation_price=invalidation_price,
        target_price=target_price,
        estimated_reward_risk=estimated_rr,
    )
    params.update(kwargs)
    return DeterministicSetupState(**params)


def _make_policy(
    *,
    trade_direction: TradeDirection = TradeDirection.BULLISH,
    execution_blockers: tuple[ExecutionBlocker, ...] = (),
) -> ExecutionPolicyState:
    """Create ExecutionPolicyState with blockers.

    The computed fields pre_review_execution_status and allowed_actions
    are derived automatically from the blockers and trade_direction.
    """
    return ExecutionPolicyState(
        trade_direction=trade_direction,
        execution_blockers=execution_blockers,
    )


def _make_risk(
    *,
    base_risk: float = 1.0,
    multiplier: float = 1.0,
    min_rr: float = 2.0,
    estimated_rr: float | None = 3.0,
) -> RiskPolicyState:
    return RiskPolicyState(
        base_risk_percentage=base_risk,
        grade_risk_multiplier=multiplier,
        minimum_reward_risk=min_rr,
        estimated_reward_risk=estimated_rr,
    )


def _make_decision(
    *,
    action: DecisionAction = DecisionAction.BUY_SETUP,
    symbol: str = "EURUSD",
    reasoning: str = "Bullish structure with confirmed BOS on H1",
    advisory_levels: AdvisoryLevels | None = None,
) -> DecisionOutput:
    return DecisionOutput(
        symbol=symbol,
        action=action,
        reasoning=reasoning,
        advisory_levels=advisory_levels,
    )


def _make_review(
    *,
    status: ReviewStatus = ReviewStatus.APPROVED,
    reasoning: str = "All criteria met",
    approved: bool = True,
    advisory_levels: AdvisoryLevels | None = None,
) -> ReviewVerdict:
    return ReviewVerdict(status=status, reasoning=reasoning, advisory_levels=advisory_levels)


def _make_enforcement(
    *,
    status: ExecutionStatus = ExecutionStatus.ACTIONABLE,
    action: DecisionAction = DecisionAction.BUY_SETUP,
    violations: tuple = (),
    review_status: ReviewStatus = ReviewStatus.APPROVED,
) -> FinalDecisionState:
    return FinalDecisionState(
        review_status=review_status,
        final_execution_status=status,
        final_action=action,
        enforcement_violations=violations,
    )


def _calendar_blocker() -> ExecutionBlocker:
    return ExecutionBlocker(
        blocker_type=ExecutionBlockerType.CALENDAR,
        code=ExecutionBlockerCode.CALENDAR_HIGH_IMPACT_SOON,
        reason="High-impact event imminent",
        severity=BlockerSeverity.EXECUTION_ONLY,
    )


# ============================================================================
# Entry/stop/target from DeterministicSetupState
# ============================================================================


class TestDeterministicPricesInOutput:
    """Entry, stop-loss, and take-profit come from the deterministic setup."""

    def test_entry_price_in_sl_tp_overlay(self) -> None:
        setup = _make_setup(entry_price=1.1050)
        policy = _make_policy()
        risk = _make_risk()
        decision = _make_decision()
        review = _make_review()
        enforcement = _make_enforcement()

        assembler = FinalOutputAssembler()
        result = assembler.assemble(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            enforcement=enforcement,
        )
        assert result.sl_tp_overlay.entry_price == 1.1050

    def test_stop_loss_from_invalidation_price(self) -> None:
        setup = _make_setup(invalidation_price=1.0950)
        policy = _make_policy()
        risk = _make_risk()
        decision = _make_decision()
        review = _make_review()
        enforcement = _make_enforcement()

        assembler = FinalOutputAssembler()
        result = assembler.assemble(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            enforcement=enforcement,
        )
        assert result.sl_tp_overlay.stop_loss == 1.0950

    def test_take_profit_from_target_price(self) -> None:
        setup = _make_setup(target_price=1.1200)
        policy = _make_policy()
        risk = _make_risk()
        decision = _make_decision()
        review = _make_review()
        enforcement = _make_enforcement()

        assembler = FinalOutputAssembler()
        result = assembler.assemble(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            enforcement=enforcement,
        )
        assert result.sl_tp_overlay.take_profit == 1.1200

    def test_advisory_levels_are_separate_from_deterministic_levels(self) -> None:
        advisory = AdvisoryLevels(entry_price=1.1020, stop_loss=1.0970, take_profit=1.1150)
        result = FinalOutputAssembler().assemble(
            setup=_make_setup(entry_price=1.1010, invalidation_price=1.0980, target_price=1.1100),
            policy=_make_policy(),
            risk=_make_risk(),
            decision=_make_decision(advisory_levels=advisory),
            review=_make_review(advisory_levels=advisory),
            enforcement=_make_enforcement(),
        )

        assert result.advisory_levels == advisory
        assert result.review_advisory_levels == advisory
        assert result.sl_tp_overlay.entry_price == 1.1010
        assert result.sl_tp_overlay.stop_loss == 1.0980
        assert result.sl_tp_overlay.take_profit == 1.1100

    def test_sl_tp_overlay_none_when_missing(self) -> None:
        setup = _make_setup(entry_price=None, target_price=None, invalidation_price=None)
        policy = _make_policy()
        risk = _make_risk()
        decision = _make_decision()
        review = _make_review()
        enforcement = _make_enforcement()

        assembler = FinalOutputAssembler()
        result = assembler.assemble(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            enforcement=enforcement,
        )
        assert result.sl_tp_overlay.entry_price is None
        assert result.sl_tp_overlay.stop_loss is None
        assert result.sl_tp_overlay.take_profit is None

    def test_order_type_is_deterministic(self) -> None:
        result = FinalOutputAssembler().assemble(
            setup=_make_setup(entry_price=1.1010),
            policy=_make_policy(),
            risk=_make_risk(),
            decision=_make_decision(),
            review=_make_review(),
            enforcement=_make_enforcement(),
        )
        assert result.order_type == "STOP"

    def test_missing_prices_have_unavailable_order_type(self) -> None:
        result = FinalOutputAssembler().assemble(
            setup=_make_setup(
                entry_price=None,
                target_price=None,
                invalidation_price=None,
                entry_type=None,
            ),
            policy=_make_policy(),
            risk=_make_risk(),
            decision=_make_decision(),
            review=_make_review(),
            enforcement=_make_enforcement(),
        )
        assert result.order_type is None
        assert result.deterministic_setup_complete is False


# ============================================================================
# Risk from RiskPolicyState
# ============================================================================


class TestRiskInOutput:
    """Risk policy values appear in the assembled output."""

    def test_risk_multiplier_in_output(self) -> None:
        setup = _make_setup()
        policy = _make_policy()
        risk = _make_risk(multiplier=0.5)
        decision = _make_decision()
        review = _make_review()
        enforcement = _make_enforcement()

        assembler = FinalOutputAssembler()
        result = assembler.assemble(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            enforcement=enforcement,
        )
        assert result.risk_multiplier == 0.5

    def test_final_risk_percentage_in_output(self) -> None:
        setup = _make_setup()
        policy = _make_policy()
        risk = RiskPolicyState(
            base_risk_percentage=2.0,
            grade_risk_multiplier=0.5,
            minimum_reward_risk=2.0,
            estimated_reward_risk=3.0,
        )
        decision = _make_decision()
        review = _make_review()
        enforcement = _make_enforcement()

        assembler = FinalOutputAssembler()
        result = assembler.assemble(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            enforcement=enforcement,
        )
        assert result.final_risk_percentage == 1.0  # 2.0 * 0.5


# ============================================================================
# Reasoning from LLM
# ============================================================================


class TestLLMReasoningInOutput:
    """LLM reasoning appears in the output decision."""

    def test_reasoning_preserved(self) -> None:
        setup = _make_setup()
        policy = _make_policy()
        risk = _make_risk()
        decision = _make_decision(reasoning="Strong bullish breakout on H1 with volume")
        review = _make_review()
        enforcement = _make_enforcement()

        assembler = FinalOutputAssembler()
        result = assembler.assemble(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            enforcement=enforcement,
        )
        assert result.decision is not None
        assert "Strong bullish breakout" in result.decision.reasoning

    def test_llm_symbol_preserved(self) -> None:
        setup = _make_setup()
        policy = _make_policy()
        risk = _make_risk()
        decision = _make_decision(symbol="GBPUSD")
        review = _make_review()
        enforcement = _make_enforcement()

        assembler = FinalOutputAssembler()
        result = assembler.assemble(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            enforcement=enforcement,
        )
        assert result.symbol == "GBPUSD"
        assert result.decision is not None
        assert result.decision.symbol == "GBPUSD"


# ============================================================================
# Enforcement violations in output
# ============================================================================


class TestEnforcementViolationsInOutput:
    """Enforcement violations are serialised into the output."""

    def test_violations_serialised_to_dict(self) -> None:
        setup = _make_setup()
        policy = _make_policy()
        risk = _make_risk()
        decision = _make_decision()
        review = _make_review()
        violations = (
            EnforcementViolation(
                code=EnforcementViolationCode.CANDIDATE_NOT_GENERATED,
                reason="No candidate generated",
            ),
        )
        enforcement = _make_enforcement(
            status=ExecutionStatus.BLOCKED_BY_ENFORCEMENT,
            action=DecisionAction.NO_TRADE,
            violations=violations,
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
        assert len(result.enforcement_violations) == 1
        assert result.enforcement_violations[0]["code"] == "CANDIDATE_NOT_GENERATED"
        assert result.enforcement_violations[0]["reason"] == "No candidate generated"

    def test_multiple_violations_serialised(self) -> None:
        setup = _make_setup()
        policy = _make_policy()
        risk = _make_risk()
        decision = _make_decision()
        review = _make_review()
        violations = (
            EnforcementViolation(
                code=EnforcementViolationCode.CANDIDATE_NOT_GENERATED,
                reason="No candidate",
            ),
            EnforcementViolation(
                code=EnforcementViolationCode.DIRECTION_MISMATCH,
                reason="Direction conflict",
            ),
            EnforcementViolation(
                code=EnforcementViolationCode.INVALID_GEOMETRY,
                reason="Bad geometry",
            ),
        )
        enforcement = _make_enforcement(
            status=ExecutionStatus.BLOCKED_BY_ENFORCEMENT,
            action=DecisionAction.NO_TRADE,
            violations=violations,
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
        assert len(result.enforcement_violations) == 3

    def test_empty_violations_list(self) -> None:
        setup = _make_setup()
        policy = _make_policy()
        risk = _make_risk()
        decision = _make_decision()
        review = _make_review()
        enforcement = _make_enforcement()

        assembler = FinalOutputAssembler()
        result = assembler.assemble(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            enforcement=enforcement,
        )
        assert result.enforcement_violations == []


# ============================================================================
# NOT_REQUIRED review for early bypass
# ============================================================================


class TestNotRequiredReviewInOutput:
    """NOT_REQUIRED review status is passed through to output."""

    def test_not_required_in_output(self) -> None:
        setup = _make_setup()
        policy = _make_policy()
        risk = _make_risk()
        decision = _make_decision(action=DecisionAction.NO_TRADE)
        review = _make_review(status=ReviewStatus.NOT_REQUIRED, approved=False)
        enforcement = _make_enforcement(
            review_status=ReviewStatus.NOT_REQUIRED,
            status=ExecutionStatus.ACTIONABLE,
            action=DecisionAction.NO_TRADE,
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
        assert result.review is not None
        assert result.review.status == ReviewStatus.NOT_REQUIRED


# ============================================================================
# LLM never overrides deterministic values
# ============================================================================


class TestLLMDoesNotOverrideDeterministic:
    """LLM action is overridden by deterministic enforcement action."""

    def test_enforcement_action_overrides_llm(self) -> None:
        """Final action comes from enforcement gate, not LLM decision."""
        setup = _make_setup()
        policy = _make_policy()
        risk = _make_risk()
        # LLM says BUY_SETUP ...
        decision = _make_decision(action=DecisionAction.BUY_SETUP)
        review = _make_review()
        # ... but enforcement says NO_TRADE
        enforcement = _make_enforcement(
            status=ExecutionStatus.NOT_READY,
            action=DecisionAction.NO_TRADE,
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
        # The output's final_action reflects enforcement, not LLM
        assert result.final_action == "no_trade"

    def test_deterministic_setup_grade_in_output(self) -> None:
        """Setup grade comes from deterministic setup."""
        setup = _make_setup(grade=SetupGrade.AA)
        policy = _make_policy()
        risk = _make_risk()
        decision = _make_decision()
        review = _make_review()
        enforcement = _make_enforcement()

        assembler = FinalOutputAssembler()
        result = assembler.assemble(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            enforcement=enforcement,
        )
        assert result.setup_grade == "AA"

    def test_trade_direction_in_output(self) -> None:
        setup = _make_setup(trade_direction=TradeDirection.BEARISH)
        policy = _make_policy(trade_direction=TradeDirection.BEARISH)
        risk = _make_risk()
        decision = _make_decision(action=DecisionAction.SELL_SETUP)
        review = _make_review()
        enforcement = _make_enforcement(action=DecisionAction.SELL_SETUP)

        assembler = FinalOutputAssembler()
        result = assembler.assemble(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            enforcement=enforcement,
        )
        assert result.trade_direction == "BEARISH"


# ============================================================================
# Execution blockers in output
# ============================================================================


class TestExecutionBlockersInOutput:
    """Execution blockers are serialised in the output."""

    def test_blockers_serialised_to_dict(self) -> None:
        setup = _make_setup()
        policy = _make_policy(execution_blockers=(_calendar_blocker(),))
        risk = _make_risk()
        decision = _make_decision(action=DecisionAction.NO_TRADE)
        review = _make_review()
        enforcement = _make_enforcement(
            status=ExecutionStatus.BLOCKED_BY_CALENDAR,
            action=DecisionAction.NO_TRADE,
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
        assert len(result.execution_blockers) == 1
        assert result.execution_blockers[0]["code"] == "CALENDAR_HIGH_IMPACT_SOON"

    def test_execution_status_in_output(self) -> None:
        """Execution status is derived from policy blockers via computed field.

        With a CALENDAR blocker, pre_review_execution_status becomes
        BLOCKED_BY_CALENDAR, and that value appears in the output.
        """
        setup = _make_setup()
        policy = _make_policy(execution_blockers=(_calendar_blocker(),))
        risk = _make_risk()
        decision = _make_decision(action=DecisionAction.NO_TRADE)
        review = _make_review()
        enforcement = _make_enforcement(
            status=ExecutionStatus.BLOCKED_BY_CALENDAR,
            action=DecisionAction.NO_TRADE,
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
        assert result.execution_status == "BLOCKED_BY_CALENDAR"


# ============================================================================
# Status inference
# ============================================================================


class TestStatusInference:
    """Output status is 'partial' when violations exist, 'success' otherwise."""

    def test_success_when_no_violations(self) -> None:
        setup = _make_setup()
        policy = _make_policy()
        risk = _make_risk()
        decision = _make_decision()
        review = _make_review()
        enforcement = _make_enforcement()

        assembler = FinalOutputAssembler()
        result = assembler.assemble(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            enforcement=enforcement,
        )
        assert result.status == "success"

    def test_partial_when_violations_exist(self) -> None:
        setup = _make_setup()
        policy = _make_policy()
        risk = _make_risk()
        decision = _make_decision()
        review = _make_review()
        violations = (
            EnforcementViolation(
                code=EnforcementViolationCode.CANDIDATE_NOT_GENERATED,
                reason="Test",
            ),
        )
        enforcement = _make_enforcement(
            status=ExecutionStatus.BLOCKED_BY_ENFORCEMENT,
            action=DecisionAction.NO_TRADE,
            violations=violations,
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
        assert result.status == "partial"


# ============================================================================
# Lifecycle and classification in output
# ============================================================================


class TestLifecycleAndClassification:
    """Lifecycle and classification status appear in output."""

    def test_lifecycle_status_in_output(self) -> None:
        setup = _make_setup(lifecycle=SetupLifecycleStatus.TRIGGERED)
        policy = _make_policy()
        risk = _make_risk()
        decision = _make_decision()
        review = _make_review()
        enforcement = _make_enforcement()

        assembler = FinalOutputAssembler()
        result = assembler.assemble(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            enforcement=enforcement,
        )
        assert result.setup_lifecycle_status == "TRIGGERED"

    def test_classification_in_output(self) -> None:
        setup = _make_setup(classification=SetupClassificationStatus.CLASSIFIED)
        policy = _make_policy()
        risk = _make_risk()
        decision = _make_decision()
        review = _make_review()
        enforcement = _make_enforcement()

        assembler = FinalOutputAssembler()
        result = assembler.assemble(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            enforcement=enforcement,
        )
        assert result.setup_classification_status == "CLASSIFIED"

    def test_estimated_reward_risk_in_output(self) -> None:
        setup = _make_setup(estimated_rr=2.5)
        policy = _make_policy()
        risk = _make_risk()
        decision = _make_decision()
        review = _make_review()
        enforcement = _make_enforcement()

        assembler = FinalOutputAssembler()
        result = assembler.assemble(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            enforcement=enforcement,
        )
        assert result.estimated_reward_risk == 2.5

    def test_grade_none_when_no_setup(self) -> None:
        setup = _make_setup(
            grade=None,
            classification=SetupClassificationStatus.NO_SETUP,
            trade_direction=TradeDirection.NEUTRAL,
        )
        policy = _make_policy(trade_direction=TradeDirection.NEUTRAL)
        risk = _make_risk()
        decision = _make_decision(action=DecisionAction.NO_TRADE)
        review = _make_review()
        enforcement = _make_enforcement(action=DecisionAction.NO_TRADE)

        assembler = FinalOutputAssembler()
        result = assembler.assemble(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            enforcement=enforcement,
        )
        assert result.setup_grade is None
        assert result.setup_classification_status == "NO_SETUP"

    def test_rejection_codes_mapped_to_result(self) -> None:
        """rejection_codes from DeterministicSetupState appear in AnalysisResult."""
        # Override rejection_codes on the frozen model via constructor
        setup_with_rejections = DeterministicSetupState(
            setup_classification_status=SetupClassificationStatus.INSUFFICIENT_DATA,
            trade_direction=TradeDirection.NEUTRAL,
            rejection_codes=(SetupRejectionCode.INVALID_TRADE_DIRECTION,),
        )
        policy = _make_policy(trade_direction=TradeDirection.NEUTRAL)
        risk = _make_risk()
        decision = _make_decision(action=DecisionAction.NO_TRADE)
        review = _make_review()
        enforcement = _make_enforcement(action=DecisionAction.NO_TRADE)

        assembler = FinalOutputAssembler()
        result = assembler.assemble(
            setup=setup_with_rejections,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            enforcement=enforcement,
        )
        assert result.rejection_codes == ["INVALID_TRADE_DIRECTION"]

    def test_rejection_codes_empty_by_default(self) -> None:
        """rejection_codes defaults to empty list when no rejections."""
        setup = _make_setup()
        policy = _make_policy()
        risk = _make_risk()
        decision = _make_decision()
        review = _make_review()
        enforcement = _make_enforcement()

        assembler = FinalOutputAssembler()
        result = assembler.assemble(
            setup=setup,
            policy=policy,
            risk=risk,
            decision=decision,
            review=review,
            enforcement=enforcement,
        )
        assert result.rejection_codes == []
