"""Tests for deterministic setup grading (Section 16.1).

Tests the grade_setup() function and its helper functions to verify:
- AAA grade when all three timeframes aligned (D1 directional, H4 aligned, H1 BOS)
- AA grade when two timeframes aligned (CHoCH-based or pending trigger)
- COUNTERTREND grade when H4 not aligned with D1
- NO_SETUP when D1 is neutral or direction is unclear
- Lifecycle status transitions based on trigger confirmation
- Geometry status derivation
"""

from __future__ import annotations

from typing import Any

from src.analysis.market_structure_engine.execution_policy import (
    evaluate_execution_policy,
)
from src.analysis.market_structure_engine.grading import (
    _determine_d1_directional,
    _determine_geometry_status,
    _determine_h1_choch_based,
    _determine_h1_trigger_confirmed,
    _determine_h4_aligned,
    _determine_lifecycle_status,
    _determine_trade_direction,
    grade_setup,
)
from src.analysis.market_structure_engine.models import (
    DecisionAction,
    ExecutionBlockerType,
    ExecutionStatus,
    GeometryStatus,
    SetupClassificationStatus,
    SetupGrade,
    SetupLifecycleStatus,
    SetupRejectionCode,
    TradeDirection,
)
from src.analysis.market_structure_engine.risk_policy import build_risk_policy

# ============================================================================
# _determine_trade_direction
# ============================================================================


class TestDetermineTradeDirection:
    def test_h4_bullish_preferred(self) -> None:
        assert _determine_trade_direction("BULLISH", "BULLISH") == TradeDirection.BULLISH

    def test_h4_bearish_preferred(self) -> None:
        assert _determine_trade_direction("BEARISH", "BEARISH") == TradeDirection.BEARISH

    def test_h4_neutral_falls_back_to_d1_bullish(self) -> None:
        assert _determine_trade_direction("STRONG_BULLISH", "NEUTRAL") == TradeDirection.BULLISH

    def test_h4_neutral_falls_back_to_d1_bearish(self) -> None:
        assert _determine_trade_direction("STRONG_BEARISH", "NEUTRAL") == TradeDirection.BEARISH

    def test_h4_neutral_d1_neutral(self) -> None:
        assert _determine_trade_direction("NEUTRAL", "NEUTRAL") == TradeDirection.NEUTRAL

    def test_h4_unknown_d1_neutral(self) -> None:
        assert _determine_trade_direction("NEUTRAL", "UNKNOWN") == TradeDirection.NEUTRAL

    def test_h4_unknown_d1_bullish(self) -> None:
        assert _determine_trade_direction("BULLISH", "UNKNOWN") == TradeDirection.BULLISH


# ============================================================================
# _determine_d1_directional
# ============================================================================


class TestDetermineD1Directional:
    def test_strong_bullish(self) -> None:
        assert _determine_d1_directional("STRONG_BULLISH") is True

    def test_bullish(self) -> None:
        assert _determine_d1_directional("BULLISH") is True

    def test_strong_bearish(self) -> None:
        assert _determine_d1_directional("STRONG_BEARISH") is True

    def test_bearish(self) -> None:
        assert _determine_d1_directional("BEARISH") is True

    def test_neutral(self) -> None:
        assert _determine_d1_directional("NEUTRAL") is False

    def test_neutral_bullish(self) -> None:
        assert _determine_d1_directional("NEUTRAL_BULLISH") is False

    def test_neutral_bearish(self) -> None:
        assert _determine_d1_directional("NEUTRAL_BEARISH") is False

    def test_unknown(self) -> None:
        assert _determine_d1_directional("UNKNOWN") is True


# ============================================================================
# _determine_h4_aligned
# ============================================================================


class TestDetermineH4Aligned:
    def test_aligned_continuation(self) -> None:
        assert (
            _determine_h4_aligned(
                "ALIGNED_CONTINUATION", TradeDirection.BULLISH, TradeDirection.BULLISH
            )
            is True
        )

    def test_aligned_pullback(self) -> None:
        assert (
            _determine_h4_aligned(
                "ALIGNED_PULLBACK", TradeDirection.BULLISH, TradeDirection.BEARISH
            )
            is True
        )

    def test_transition(self) -> None:
        assert (
            _determine_h4_aligned("TRANSITION", TradeDirection.BULLISH, TradeDirection.BEARISH)
            is False
        )

    def test_same_direction_non_neutral(self) -> None:
        assert (
            _determine_h4_aligned("UNKNOWN", TradeDirection.BULLISH, TradeDirection.BULLISH) is True
        )

    def test_opposite_direction(self) -> None:
        assert (
            _determine_h4_aligned("UNKNOWN", TradeDirection.BULLISH, TradeDirection.BEARISH)
            is False
        )

    def test_neutral_direction(self) -> None:
        assert (
            _determine_h4_aligned("UNKNOWN", TradeDirection.NEUTRAL, TradeDirection.NEUTRAL)
            is False
        )


# ============================================================================
# _determine_h1_trigger_confirmed
# ============================================================================


class TestDetermineH1TriggerConfirmed:
    def test_valid_setup(self) -> None:
        assert (
            _determine_h1_trigger_confirmed("VALID_SETUP", "BULLISH_BOS", "CONFIRMED_TRIGGER")
            is True
        )

    def test_bos_confirmed(self) -> None:
        assert (
            _determine_h1_trigger_confirmed("SOME_STATUS", "BULLISH_BOS", "CONFIRMED_TRIGGER")
            is True
        )

    def test_bos_not_confirmed(self) -> None:
        assert (
            _determine_h1_trigger_confirmed("SOME_STATUS", "BULLISH_BOS", "PENDING_CONFIRMATION")
            is False
        )

    def test_unknown_trigger_no_confirm(self) -> None:
        assert _determine_h1_trigger_confirmed("SOME_STATUS", "NONE", "NO_TRIGGER") is False

    def test_reclaim_pending(self) -> None:
        assert (
            _determine_h1_trigger_confirmed("SOME_STATUS", "RECLAIM", "PENDING_CONFIRMATION")
            is False
        )

    def test_retest_pending(self) -> None:
        assert _determine_h1_trigger_confirmed("SOME_STATUS", "RETEST", "NO_TRIGGER") is False


# ============================================================================
# _determine_h1_choch_based
# ============================================================================


class TestDetermineH1ChochBased:
    def test_bullish_choch(self) -> None:
        assert _determine_h1_choch_based("BULLISH_CHOCH") is True

    def test_bearish_choch(self) -> None:
        assert _determine_h1_choch_based("BEARISH_CHOCH") is True

    def test_bos_not_choch(self) -> None:
        assert _determine_h1_choch_based("BULLISH_BOS") is False

    def test_reclaim_not_choch(self) -> None:
        assert _determine_h1_choch_based("RECLAIM") is False

    def test_retest_not_choch(self) -> None:
        assert _determine_h1_choch_based("RETEST") is False

    def test_none_not_choch(self) -> None:
        assert _determine_h1_choch_based("NONE") is False


# ============================================================================
# _determine_geometry_status
# ============================================================================


class TestDetermineGeometryStatus:
    def test_valid(self) -> None:
        assert _determine_geometry_status("VALID_SETUP", True, True) == GeometryStatus.VALID

    def test_valid_needs_all_three(self) -> None:
        assert (
            _determine_geometry_status("VALID_SETUP", True, False)
            == GeometryStatus.TEMPORARILY_UNAVAILABLE
        )
        assert (
            _determine_geometry_status("VALID_SETUP", False, True)
            == GeometryStatus.TEMPORARILY_UNAVAILABLE
        )

    def test_blocked_by_liquidity(self) -> None:
        assert (
            _determine_geometry_status("BLOCKED_BY_LIQUIDITY", True, True)
            == GeometryStatus.TEMPORARILY_UNAVAILABLE
        )

    def test_conflict_with_higher_timeframe(self) -> None:
        assert (
            _determine_geometry_status("CONFLICT_WITH_HIGHER_TIMEFRAME", False, False)
            == GeometryStatus.PERMANENTLY_INVALID
        )

    def test_unknown_fallback(self) -> None:
        assert (
            _determine_geometry_status("SOME_OTHER_STATUS", False, False)
            == GeometryStatus.TEMPORARILY_UNAVAILABLE
        )

    def test_no_setup_fallback(self) -> None:
        assert (
            _determine_geometry_status("NO_SETUP", False, False)
            == GeometryStatus.TEMPORARILY_UNAVAILABLE
        )


# ============================================================================
# _determine_lifecycle_status
# ============================================================================


class TestDetermineLifecycleStatus:
    def test_triggered(self) -> None:
        assert (
            _determine_lifecycle_status(True, "CONFIRMED_TRIGGER", "VALID_SETUP")
            == SetupLifecycleStatus.TRIGGERED
        )

    def test_pending_early_transition(self) -> None:
        assert (
            _determine_lifecycle_status(False, "EARLY_TRANSITION", "SOME_STATUS")
            == SetupLifecycleStatus.PENDING
        )

    def test_pending_pending_confirmation(self) -> None:
        assert (
            _determine_lifecycle_status(False, "PENDING_CONFIRMATION", "SOME_STATUS")
            == SetupLifecycleStatus.PENDING
        )

    def test_ready_valid_setup_no_confirm(self) -> None:
        assert (
            _determine_lifecycle_status(False, "NO_TRIGGER", "VALID_SETUP")
            == SetupLifecycleStatus.READY
        )

    def test_invalidated_no_setup(self) -> None:
        assert (
            _determine_lifecycle_status(False, "NO_TRIGGER", "NO_SETUP")
            == SetupLifecycleStatus.INVALIDATED
        )

    def test_invalidated_conflict_higher(self) -> None:
        assert (
            _determine_lifecycle_status(False, "NO_TRIGGER", "CONFLICT_WITH_HIGHER_TIMEFRAME")
            == SetupLifecycleStatus.INVALIDATED
        )

    def test_pending_other_status(self) -> None:
        assert (
            _determine_lifecycle_status(False, "NO_TRIGGER", "SOME_OTHER_STATUS")
            == SetupLifecycleStatus.PENDING
        )


# ============================================================================
# grade_setup — integration tests
# ============================================================================


def _d1_context(bias: str = "BULLISH", structure: str = "BULLISH") -> dict[str, Any]:
    return {
        "strategic_bias": {
            "bias": bias,
            "primary_structure": structure,
            "structure_context": "BULLISH_TREND"
            if bias in ("BULLISH", "STRONG_BULLISH")
            else "NEUTRAL",
        },
    }


def _h4_context(
    alignment: str = "ALIGNED_CONTINUATION",
    direction: str = "BULLISH",
    structure: str = "BULLISH",
) -> dict[str, Any]:
    return {
        "operational_context": {
            "alignment_status": alignment,
            "preferred_direction": direction,
            "h4_structure": structure,
            "h4_internal_structure": {"phase": "CONTINUATION"},
            "parent_daily_bias": "BULLISH",
        },
    }


def _h1_context(
    setup_status: str = "VALID_SETUP",
    trigger_type: str = "BULLISH_BOS",
    room_to_target: bool = True,
    reward_risk_ok: bool = True,
) -> dict[str, Any]:
    return {
        "setup_context": {
            "setup_status": setup_status,
            "preferred_direction": "BULLISH",
            "room_to_target_passed": room_to_target,
            "reward_risk_filter_passed": reward_risk_ok,
            "latest_trigger_event": {"event_type": trigger_type},
        },
    }


class TestGradeSetupAAA:
    """AAA grade when all three timeframes aligned: D1 directional,
    H4 aligned continuation, H1 BOS trigger confirmed."""

    def test_aaa_bullish(self) -> None:
        result = grade_setup(
            _h1_context(setup_status="VALID_SETUP", trigger_type="BULLISH_BOS"),
            _h4_context(alignment="ALIGNED_CONTINUATION", direction="BULLISH"),
            _d1_context(bias="BULLISH"),
        )
        assert result.setup_classification_status == SetupClassificationStatus.CLASSIFIED
        assert result.setup_grade == SetupGrade.AAA
        assert result.trade_direction == TradeDirection.BULLISH

    def test_aaa_bearish(self) -> None:
        result = grade_setup(
            _h1_context(setup_status="VALID_SETUP", trigger_type="BEARISH_BOS"),
            _h4_context(alignment="ALIGNED_CONTINUATION", direction="BEARISH"),
            _d1_context(bias="BEARISH"),
        )
        assert result.setup_classification_status == SetupClassificationStatus.CLASSIFIED
        assert result.setup_grade == SetupGrade.AAA
        assert result.trade_direction == TradeDirection.BEARISH

    def test_aaa_h4_aligned_pullback(self) -> None:
        """AAA can be achieved with ALIGNED_PULLBACK as well."""
        result = grade_setup(
            _h1_context(setup_status="VALID_SETUP", trigger_type="BULLISH_BOS"),
            _h4_context(alignment="ALIGNED_PULLBACK", direction="BULLISH"),
            _d1_context(bias="BULLISH"),
        )
        assert result.setup_grade == SetupGrade.AAA


class TestGradeSetupAA:
    """AA grade when two timeframes aligned but H1 trigger is CHoCH-based."""

    def test_aa_choch_trigger(self) -> None:
        result = grade_setup(
            _h1_context(setup_status="VALID_SETUP", trigger_type="BULLISH_CHOCH"),
            _h4_context(alignment="ALIGNED_CONTINUATION", direction="BULLISH"),
            _d1_context(bias="BULLISH"),
        )
        assert result.setup_classification_status == SetupClassificationStatus.CLASSIFIED
        assert result.setup_grade == SetupGrade.AA

    def test_aa_no_trigger_event_falls_to_no_setup(self) -> None:
        """Without a trigger event, grade_setup defaults to NO_SETUP."""
        h1 = _h1_context(setup_status="SOME_STATUS", trigger_type="BULLISH_BOS")
        h1["setup_context"]["latest_trigger_event"] = None
        result = grade_setup(
            h1,
            _h4_context(alignment="ALIGNED_CONTINUATION", direction="BULLISH"),
            _d1_context(bias="BULLISH"),
        )
        assert result.setup_classification_status == SetupClassificationStatus.NO_SETUP
        assert result.setup_grade is None

    def test_aa_pending_not_classified_when_no_trigger(self) -> None:
        """When H1 setup status is not VALID_SETUP and no trigger event exists,
        grade_setup returns NO_SETUP (the else branch)."""
        h1 = _h1_context(setup_status="SOME_NON_VALID_STATUS", trigger_type="BULLISH_BOS")
        h1["setup_context"]["latest_trigger_event"] = None
        result = grade_setup(
            h1,
            _h4_context(alignment="ALIGNED_CONTINUATION", direction="BULLISH"),
            _d1_context(bias="BULLISH"),
        )
        # _determine_h1_trigger_confirmed("SOME_NON_VALID_STATUS", "NONE", "NO_TRIGGER")
        # → h1_setup_status != "VALID_SETUP" and trigger_type not BOS → False
        # Falls all the way to else → NO_SETUP
        assert result.setup_classification_status == SetupClassificationStatus.NO_SETUP
        assert result.setup_grade is None


class TestGradeSetupCountertrend:
    """COUNTERTREND grade when H4 not aligned with D1."""

    def test_countertrend_h4_opposite(self) -> None:
        result = grade_setup(
            _h1_context(setup_status="VALID_SETUP", trigger_type="BULLISH_BOS"),
            _h4_context(alignment="UNKNOWN", direction="BEARISH"),
            _d1_context(bias="BULLISH"),
        )
        # H4 direction "BEARISH" diverges from D1 "BULLISH",
        # so h4_aligned=False leading to COUNTERTREND.
        assert result.setup_classification_status == SetupClassificationStatus.CLASSIFIED
        assert result.setup_grade == SetupGrade.COUNTERTREND

    def test_countertrend_h4_transition(self) -> None:
        result = grade_setup(
            _h1_context(setup_status="VALID_SETUP", trigger_type="BULLISH_BOS"),
            _h4_context(alignment="TRANSITION", direction="BULLISH"),
            _d1_context(bias="BULLISH"),
        )
        # H4 alignment TRANSITION → h4_aligned = False → COUNTERTREND
        assert result.setup_grade == SetupGrade.COUNTERTREND


class TestGradeSetupNoSetup:
    """No setup when D1 is neutral or direction is NEUTRAL."""

    def test_d1_neutral(self) -> None:
        result = grade_setup(
            _h1_context(setup_status="VALID_SETUP", trigger_type="BULLISH_BOS"),
            _h4_context(alignment="ALIGNED_CONTINUATION", direction="BULLISH"),
            _d1_context(bias="NEUTRAL"),
        )
        assert result.setup_classification_status == SetupClassificationStatus.NO_SETUP
        assert result.setup_grade is None

    def test_trade_direction_neutral(self) -> None:
        result = grade_setup(
            _h1_context(setup_status="VALID_SETUP", trigger_type="BULLISH_BOS"),
            _h4_context(alignment="ALIGNED_CONTINUATION", direction="NEUTRAL"),
            _d1_context(bias="NEUTRAL"),
        )
        assert result.setup_classification_status == SetupClassificationStatus.NO_SETUP
        assert result.setup_grade is None


class TestGradeSetupLifecycle:
    """Lifecycle status in grade_setup output."""

    def test_aaa_triggers_triggered_lifecycle(self) -> None:
        result = grade_setup(
            _h1_context(setup_status="VALID_SETUP", trigger_type="BULLISH_BOS"),
            _h4_context(alignment="ALIGNED_CONTINUATION", direction="BULLISH"),
            _d1_context(bias="BULLISH"),
        )
        assert result.setup_lifecycle_status == SetupLifecycleStatus.TRIGGERED

    def test_invalidated_when_no_setup(self) -> None:
        result = grade_setup(
            _h1_context(setup_status="NO_SETUP", trigger_type="NONE"),
            _h4_context(alignment="ALIGNED_CONTINUATION", direction="BULLISH"),
            _d1_context(bias="BULLISH"),
        )
        # D1 is directional, but H4 alignment check: h4_alignment="ALIGNED_CONTINUATION"
        # But h1_setup_status="NO_SETUP", h1_trigger_confirmed = False
        # h1_trigger_status_str = "NO_TRIGGER" (no event)
        # H1 trigger event is NONE, _determine_h1_choch_based("NONE") = False
        # _determine_h1_trigger_confirmed("NO_SETUP", "NONE", "NO_TRIGGER"):
        #   h1_setup_status != "VALID_SETUP", trigger_type not in BOS → False
        # lifecycle: not confirmed, status NO_TRIGGER, status "NO_SETUP" → INVALIDATED
        assert result.setup_lifecycle_status == SetupLifecycleStatus.INVALIDATED


class TestGradeSetupGeometry:
    """Geometry status in grade_setup output."""

    def test_geometry_valid(self) -> None:
        result = grade_setup(
            _h1_context(
                setup_status="VALID_SETUP",
                trigger_type="BULLISH_BOS",
                room_to_target=True,
                reward_risk_ok=True,
            ),
            _h4_context(alignment="ALIGNED_CONTINUATION", direction="BULLISH"),
            _d1_context(bias="BULLISH"),
        )
        assert result.geometry_status == GeometryStatus.VALID

    def test_geometry_temporarily_unavailable(self) -> None:
        result = grade_setup(
            _h1_context(setup_status="BLOCKED_BY_LIQUIDITY", trigger_type="BULLISH_BOS"),
            _h4_context(alignment="ALIGNED_CONTINUATION", direction="BULLISH"),
            _d1_context(bias="BULLISH"),
        )
        assert result.geometry_status == GeometryStatus.TEMPORARILY_UNAVAILABLE


# ============================================================================
# grade_setup edge cases
# ============================================================================


class TestGradeSetupEdgeCases:
    """Edge cases for grade_setup."""

    def test_d1_context_without_strategic_bias_key(self) -> None:
        """grade_setup handles d1_context that is itself the bias dict."""
        result = grade_setup(
            _h1_context(setup_status="VALID_SETUP", trigger_type="BULLISH_BOS"),
            _h4_context(alignment="ALIGNED_CONTINUATION", direction="BULLISH"),
            {"bias": "BULLISH", "primary_structure": "BULLISH"},
        )
        assert result.setup_grade == SetupGrade.AAA

    def test_h4_context_without_operational_context_key(self) -> None:
        result = grade_setup(
            _h1_context(setup_status="VALID_SETUP", trigger_type="BULLISH_BOS"),
            {"alignment_status": "ALIGNED_CONTINUATION", "preferred_direction": "BULLISH"},
            _d1_context(bias="BULLISH"),
        )
        assert result.setup_grade == SetupGrade.AAA

    def test_h1_context_without_setup_context_key(self) -> None:
        result = grade_setup(
            {
                "setup_status": "VALID_SETUP",
                "preferred_direction": "BULLISH",
                "latest_trigger_event": {"event_type": "BULLISH_BOS"},
            },
            _h4_context(alignment="ALIGNED_CONTINUATION", direction="BULLISH"),
            _d1_context(bias="BULLISH"),
        )
        assert result.setup_grade == SetupGrade.AAA

    def test_empty_d1_context(self) -> None:
        result = grade_setup(
            _h1_context(setup_status="VALID_SETUP", trigger_type="BULLISH_BOS"),
            _h4_context(alignment="ALIGNED_CONTINUATION", direction="BULLISH"),
            {},
        )
        assert result.setup_classification_status == SetupClassificationStatus.NO_SETUP

    def test_trigger_type_maps_correctly(self) -> None:
        result = grade_setup(
            _h1_context(setup_status="VALID_SETUP", trigger_type="BEARISH_CHOCH"),
            _h4_context(alignment="ALIGNED_CONTINUATION", direction="BEARISH"),
            _d1_context(bias="BEARISH"),
        )
        assert result.h1_trigger_type.value == "BEARISH_CHOCH"
        assert result.setup_grade == SetupGrade.AA  # CHoCH-based

    def test_all_bias_levels_mapped(self) -> None:
        """grade_setup correctly maps all bias level strings to enums."""
        for bias_str in (
            "STRONG_BULLISH",
            "BULLISH",
            "NEUTRAL_BULLISH",
            "NEUTRAL",
            "NEUTRAL_BEARISH",
            "BEARISH",
            "STRONG_BEARISH",
        ):
            result = grade_setup(
                _h1_context(setup_status="VALID_SETUP", trigger_type="BULLISH_BOS"),
                _h4_context(alignment="ALIGNED_CONTINUATION", direction="BULLISH"),
                _d1_context(bias=bias_str),
            )
            assert result.d1_bias.value == bias_str


# ============================================================================
# NO_SETUP rejection codes (regression: result-23.json US100.cash 2026-08-04)
# ============================================================================


class TestGradeSetupRejectionCodes:
    """NO_SETUP must carry structural rejection codes, never INSUFFICIENT_DATA.

    The artifact scenario: H1 setup status CONFLICT_WITH_HIGHER_TIMEFRAME with
    a FAILED_BULLISH_BREAKOUT trigger. The classification is NO_SETUP because
    the trigger is not confirmed; the entry absence is intentional, not a
    data-quality problem.
    """

    def test_conflict_with_higher_timeframe_structural_codes(self) -> None:
        result = grade_setup(
            _h1_context(
                setup_status="CONFLICT_WITH_HIGHER_TIMEFRAME",
                trigger_type="FAILED_BULLISH_BREAKOUT",
            ),
            _h4_context(alignment="DAILY_BIAS_AT_RISK", direction="BEARISH", structure="BULLISH"),
            _d1_context(bias="STRONG_BEARISH", structure="BEARISH"),
        )
        assert result.setup_classification_status == SetupClassificationStatus.NO_SETUP
        assert result.setup_grade is None
        assert SetupRejectionCode.INSUFFICIENT_DATA not in result.rejection_codes
        assert SetupRejectionCode.HIGHER_TIMEFRAME_CONFLICT in result.rejection_codes
        assert SetupRejectionCode.TRIGGER_NOT_CONFIRMED in result.rejection_codes

    def test_no_setup_no_insufficient_data(self) -> None:
        """A plain NO_SETUP (D1 neutral) carries no INSUFFICIENT_DATA either."""
        result = grade_setup(
            _h1_context(setup_status="VALID_SETUP", trigger_type="BULLISH_BOS"),
            _h4_context(alignment="ALIGNED_CONTINUATION", direction="BULLISH"),
            _d1_context(bias="NEUTRAL"),
        )
        assert result.setup_classification_status == SetupClassificationStatus.NO_SETUP
        assert SetupRejectionCode.INSUFFICIENT_DATA not in result.rejection_codes

    def test_classified_setup_keeps_empty_rejection_codes(self) -> None:
        """A healthy CLASSIFIED setup with a complete plan keeps empty codes."""
        h1 = _h1_context(setup_status="VALID_SETUP", trigger_type="BULLISH_BOS")
        h1["setup_context"].update(
            {
                "current_price": 1.12,
                "entry_price": 1.121,
                "stop_price": 1.118,
                "invalidation_price": 1.118,
                "target_price": 1.13,
            }
        )
        result = grade_setup(
            h1,
            _h4_context(alignment="ALIGNED_CONTINUATION", direction="BULLISH"),
            _d1_context(bias="BULLISH"),
        )
        assert result.setup_classification_status == SetupClassificationStatus.CLASSIFIED
        assert result.rejection_codes == ()


class TestNoCandidatePipeline:
    """Full deterministic chain for the result-23.json artifact scenario.

    Mirrors graph._grade_setup -> _build_risk_policy -> _evaluate_execution_policy
    with the exact analysis-context shape from the real MTF file. Guards the
    end-to-end invariants: NO_SETUP stays NO_SETUP, no fake data-quality error,
    no fabricated grade, and the execution status is NON_EXECUTABLE.
    """

    def test_artifact_no_candidate_chain(self) -> None:
        h1 = _h1_context(
            setup_status="CONFLICT_WITH_HIGHER_TIMEFRAME",
            trigger_type="FAILED_BULLISH_BREAKOUT",
        )
        h1["setup_context"].update(
            {
                "current_price": 29750.23,
                "technical_invalidation": 29780.18,
                "first_objective": 28887.83,
            }
        )
        h4 = _h4_context(alignment="DAILY_BIAS_AT_RISK", direction="BEARISH", structure="BULLISH")
        d1 = _d1_context(bias="STRONG_BEARISH", structure="BEARISH")

        setup = grade_setup(h1_context=h1, h4_context=h4, d1_context=d1)
        risk = build_risk_policy(
            setup_grade=setup.setup_grade,
            base_risk_percentage=1.0,
            estimated_reward_risk=setup.estimated_reward_risk,
        )
        policy = evaluate_execution_policy(setup=setup, risk_policy=risk)

        # Classification stays NO_SETUP with structural codes
        assert setup.setup_classification_status == SetupClassificationStatus.NO_SETUP
        assert setup.setup_grade is None
        assert SetupRejectionCode.INSUFFICIENT_DATA not in setup.rejection_codes
        assert SetupRejectionCode.HIGHER_TIMEFRAME_CONFLICT in setup.rejection_codes
        assert SetupRejectionCode.TRIGGER_NOT_CONFIRMED in setup.rejection_codes

        # No candidate → no deterministic plan levels at all
        assert setup.entry_price is None
        assert setup.invalidation_price is None
        assert setup.target_price is None
        assert setup.estimated_reward_risk is None
        assert setup.entry_type is None

        # No fabricated grade / risk allocation
        assert risk.grade_risk_multiplier == 0.0
        assert risk.final_risk_percentage == 0.0

        # No fake data-quality blockers; status is NON_EXECUTABLE
        assert not any(
            b.blocker_type == ExecutionBlockerType.DATA_QUALITY for b in policy.execution_blockers
        )
        assert not any(
            b.blocker_type == ExecutionBlockerType.RISK_REWARD for b in policy.execution_blockers
        )
        assert policy.pre_review_execution_status == ExecutionStatus.NON_EXECUTABLE
        assert policy.allowed_actions == (DecisionAction.NO_TRADE,)
