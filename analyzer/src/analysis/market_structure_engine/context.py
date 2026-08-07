from __future__ import annotations

from typing import Any

from .config import MIN_RR
from .errors import ParentContextError
from .utils import round_or_none, safe_div


def _direction_from_bias(bias: str | None) -> str:
    if not bias:
        return "NEUTRAL"
    if "BULLISH" in bias:
        return "BULLISH"
    if "BEARISH" in bias:
        return "BEARISH"
    return "NEUTRAL"


def _require_parent(
    parent_context: dict[str, Any] | None,
    timeframe: str,
    mode: str,
    market: dict[str, Any],
) -> dict[str, Any]:
    parent_context = parent_context or {}
    if mode == "STANDALONE":
        return parent_context
    required = [] if timeframe == "D1" else ["D1"] if timeframe == "H4" else ["D1", "H4"]
    missing = [name for name in required if name not in parent_context]
    if missing:
        raise ParentContextError(
            f"{timeframe} contextual analysis requires approved "
            f"parent context(s): {', '.join(missing)}.",
            details={"missing": missing},
        )
    for name in required:
        parent = parent_context[name]
        if parent.get("approved_for_decision_agent") is not True:
            raise ParentContextError(f"Parent {name} is not approved for the decision agent.")
        parent_market = parent.get("market")
        if not isinstance(parent_market, dict):
            raise ParentContextError(f"Parent {name} does not declare its market identity.")
        if parent_market.get("symbol") != market.get("symbol") or parent_market.get(
            "provider"
        ) != market.get("provider"):
            raise ParentContextError(
                f"Parent {name} belongs to a different symbol or provider.",
                details={"current_market": market, "parent_market": parent_market},
            )
    return parent_context


def build_timeframe_context(
    timeframe: str,
    market: dict[str, Any],
    structure: dict[str, Any],
    events: dict[str, Any],
    levels: dict[str, Any],
    liquidity: dict[str, Any],
    scoring: dict[str, Any],
    parent_context: dict[str, Any] | None,
    parent_context_mode: str,
) -> dict[str, Any]:
    parents = _require_parent(parent_context, timeframe, parent_context_mode, market)
    common = {
        "timeframe": timeframe,
        "market": market,
        "parent_context_mode": parent_context_mode,
        "entry_authorized": False,
    }
    if timeframe == "D1":
        direction = _direction_from_bias(scoring["bias"])
        status = {
            "BULLISH": "LOOK_FOR_LONGS_ON_LOWER_TIMEFRAMES",
            "BEARISH": "LOOK_FOR_SHORTS_ON_LOWER_TIMEFRAMES",
            "NEUTRAL": "NO_DIRECTIONAL_EDGE",
        }[direction]
        return {
            **common,
            "role": "STRATEGIC_BIAS",
            "strategic_bias": {
                "bias": scoring["bias"],
                "confidence_score": scoring["confidence_score"],
                "primary_structure": structure["primary_structure"],
                "structural_bias": structure.get("structural_bias", structure["primary_structure"]),
                "structure_context": structure.get("structure_context"),
                "previous_primary_structure": structure["previous_primary_structure"],
                "internal_structure": structure["internal_structure"],
                "operational_status": status,
                "nearest_major_support": levels.get("nearest_support"),
                "nearest_major_resistance": levels.get("nearest_resistance"),
                "dominant_liquidity_draw": liquidity.get("dominant_draw"),
                "lower_timeframe_confirmation_required": True,
            },
            "operational_context": None,
            "setup_context": None,
            "multi_timeframe_decision_allowed": False,
            "approved_for_decision_agent": True,
        }

    d1 = parents.get("D1", {})
    d1_bias = d1.get("strategic_bias", {}).get("bias") or d1.get("bias")
    d1_direction = _direction_from_bias(d1_bias)
    # When local structure is RANGE/TRANSITION, use structural_bias (broader
    # directional context inferred from swing displacement) instead of the
    # primary_structure alone.  This makes H4 alignment correctly detect
    # conflicts (e.g. a bearish macro context while H4 tries to go long).
    if structure["primary_structure"] in ("BULLISH", "BEARISH"):
        current_direction = structure["primary_structure"]
    else:
        sb = structure.get("structural_bias", structure["primary_structure"])
        current_direction = _direction_from_bias(sb if sb in ("BULLISH", "BEARISH") else None)

    if timeframe == "H4":
        if parent_context_mode == "STANDALONE":
            alignment = "STANDALONE_NO_PARENT"
            operational = "STRUCTURE_ONLY"
            parent_status = "NOT_EVALUATED"
        elif d1_direction == "NEUTRAL":
            alignment = "RANGE_INSIDE_DAILY_STRUCTURE"
            operational = "NO_H4_EDGE"
            parent_status = "SUPPORTED"
        elif (
            current_direction == d1_direction
            and structure["internal_structure"]["phase"] == "CONTINUATION"
        ):
            alignment = "ALIGNED_CONTINUATION"
            operational = f"LOOK_FOR_H1_{d1_direction}_CONFIRMATION"
            parent_status = "CONFIRMED"
        elif (
            current_direction == d1_direction
            and structure["internal_structure"]["phase"] == "PULLBACK"
        ):
            alignment = "ALIGNED_PULLBACK"
            operational = f"WAIT_FOR_H1_{d1_direction}_REVERSAL_CONFIRMATION"
            parent_status = "SUPPORTED"
        elif current_direction != d1_direction and structure["primary_structure"] in (
            "BULLISH",
            "BEARISH",
        ):
            alignment = "DAILY_BIAS_AT_RISK"
            operational = "BLOCK_NEW_SETUPS_AND_REASSESS_D1"
            parent_status = "AT_RISK"
        else:
            alignment = "TRANSITION"
            operational = "WAIT_FOR_STRUCTURE_CLARITY"
            parent_status = "WEAKENED"
        return {
            **common,
            "role": "OPERATIONAL_CONTEXT",
            "strategic_bias": None,
            "operational_context": {
                "parent_daily_bias": d1_bias,
                "daily_bias_status": parent_status,
                "h4_structure": structure["primary_structure"],
                "h4_internal_structure": structure["internal_structure"],
                "alignment_status": alignment,
                "operational_status": operational,
                "preferred_direction": d1_direction,
                "key_levels": {
                    "nearest_support": levels.get("nearest_support"),
                    "nearest_resistance": levels.get("nearest_resistance"),
                    "nearest_buy_side_liquidity": liquidity.get("nearest_buy_side"),
                    "nearest_sell_side_liquidity": liquidity.get("nearest_sell_side"),
                },
                "h1_confirmation_required": True,
            },
            "setup_context": None,
            "multi_timeframe_decision_allowed": parent_context_mode != "STANDALONE",
            "approved_for_decision_agent": parent_context_mode != "STANDALONE",
        }

    h4 = parents.get("H4", {})
    h4_operational = h4.get("operational_context", {})
    h4_alignment = h4_operational.get("alignment_status") or h4.get("alignment_status")
    preferred = h4_operational.get("preferred_direction") or d1_direction
    event = events.get("latest_material_event")
    liquidity_event = liquidity.get("latest_event")
    bullish_trigger = bool(event and event["event_type"] in ("BULLISH_BOS", "BULLISH_CHOCH"))
    bearish_trigger = bool(event and event["event_type"] in ("BEARISH_BOS", "BEARISH_CHOCH"))
    sweep_support = bool(
        liquidity_event
        and liquidity_event["event_type"] in ("RECLAIMED", "RECLAIMED_AGAIN", "SWEEP_AND_RECLAIM")
        and (
            (preferred == "BULLISH" and liquidity_event["side"] == "SELL_SIDE")
            or (preferred == "BEARISH" and liquidity_event["side"] == "BUY_SIDE")
        )
    )
    trigger = (
        bullish_trigger
        if preferred == "BULLISH"
        else bearish_trigger
        if preferred == "BEARISH"
        else False
    )
    blocker = (
        h4_alignment in ("DAILY_BIAS_AT_RISK", "CONFLICT_WITH_DAILY") or preferred == "NEUTRAL"
    )
    nearest_target = (
        liquidity.get("nearest_buy_side")
        if preferred == "BULLISH"
        else liquidity.get("nearest_sell_side")
    )
    nearest_invalidation = (
        levels.get("nearest_eligible_support")
        if preferred == "BULLISH"
        else levels.get("nearest_eligible_resistance")
    )
    close = scoring.get("latest_close")
    target_price = nearest_target.get("price") if nearest_target else None
    invalidation_price = nearest_invalidation.get("price") if nearest_invalidation else None
    rr = None
    if close is not None and target_price is not None and invalidation_price is not None:
        if preferred == "BULLISH":
            reward = target_price - close
            risk = close - invalidation_price
        else:  # BEARISH
            reward = close - target_price
            risk = invalidation_price - close
        rr = safe_div(reward, risk, 0.0)
    room_ok = nearest_target is not None and nearest_target.get("distance_atr", 0) >= 0.75
    minimum_required_rr = MIN_RR
    rr_ok = rr is not None and rr >= minimum_required_rr
    if blocker:
        setup_status = "CONFLICT_WITH_HIGHER_TIMEFRAME"
    elif nearest_invalidation is None:
        setup_status = "BLOCKED_BY_INVALIDATION_LEVEL"
    elif trigger and room_ok and rr_ok:
        setup_status = "VALID_SETUP"
    elif trigger and not room_ok:
        setup_status = "BLOCKED_BY_LIQUIDITY"
    elif trigger and not rr_ok:
        setup_status = "VALID_SETUP_BUT_POOR_RR"
    elif sweep_support:
        setup_status = "CONFIRMATION_PENDING"
    else:
        setup_status = "NO_SETUP"
    return {
        **common,
        "role": "SETUP_CONFIRMATION",
        "strategic_bias": None,
        "operational_context": None,
        "setup_context": {
            "parent_daily_bias": d1_bias,
            "parent_h4_alignment": h4_alignment,
            "preferred_direction": preferred,
            "setup_status": setup_status,
            "h1_structure": structure["primary_structure"],
            "latest_trigger_event": event,
            "supportive_liquidity_event": liquidity_event if sweep_support else None,
            "entry_interest_zone": nearest_invalidation,
            "invalidation_level_id": (
                nearest_invalidation.get("level_id") if nearest_invalidation else None
            ),
            "invalidation_timeframe": timeframe,
            "technical_invalidation": invalidation_price,
            "first_objective": target_price,
            "estimated_reward_risk": round_or_none(rr, 4),
            "calculated_rr": round_or_none(rr, 4),
            "minimum_required_rr": minimum_required_rr,
            "rr_pass": rr_ok,
            "room_to_target_passed": room_ok,
            "reward_risk_filter_passed": rr_ok,
            "blockers": (
                ["HIGHER_TIMEFRAME_CONFLICT"]
                if blocker
                else ["NO_ELIGIBLE_INVALIDATION_LEVEL"]
                if nearest_invalidation is None
                else []
            ),
            "lower_timeframe_confirmation_required": False,
        },
        "multi_timeframe_decision_allowed": parent_context_mode != "STANDALONE",
        "approved_for_decision_agent": parent_context_mode != "STANDALONE",
    }


def build_confluence(d1: dict[str, Any], h4: dict[str, Any], h1: dict[str, Any]) -> dict[str, Any]:
    d1_context = d1["analysis_context"]["strategic_bias"]
    h4_context = h4["analysis_context"]["operational_context"]
    h1_context = h1["analysis_context"]["setup_context"]
    valid = (
        d1["analysis_context"]["approved_for_decision_agent"]
        and h4["analysis_context"]["approved_for_decision_agent"]
        and h1["analysis_context"]["approved_for_decision_agent"]
        and h4_context["alignment_status"] not in ("DAILY_BIAS_AT_RISK", "TRANSITION")
        and h1_context["setup_status"] == "VALID_SETUP"
        and not h1_context["blockers"]
    )
    direction = h1_context["preferred_direction"]
    return {
        "status": f"VALID_{direction}_CANDIDATE" if valid else "NO_VALID_CANDIDATE",
        "directional_alignment": h4_context["preferred_direction"] == direction,
        "daily_direction_valid": _direction_from_bias(d1_context["bias"]) == direction,
        "h4_context_aligned": h4_context["alignment_status"].startswith("ALIGNED"),
        "h1_trigger_confirmed": h1_context["setup_status"] == "VALID_SETUP",
        "liquidity_filter_passed": h1_context["room_to_target_passed"],
        "reward_risk_filter_passed": h1_context["reward_risk_filter_passed"],
        "technical_blockers_absent": not h1_context["blockers"],
        "event_risk_blockers_absent": None,
        "candidate_generated": valid,
        "entry_authorized": False,
    }
