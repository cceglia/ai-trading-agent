from __future__ import annotations

import platform
from copy import deepcopy
from typing import Any

from . import __version__
from .candles import analyze_candles
from .config import get_profile
from .context import build_confluence, build_timeframe_context
from .errors import ParentContextError, ValidationError
from .events import scan_events
from .indicators import calculate_indicators
from .levels import build_levels
from .liquidity import analyze_liquidity
from .scoring import calculate_score
from .structure import classify_structure
from .swings import detect_swings
from .utils import sha256_digest
from .validation import validate_snapshot


def _apply_structural_event_transition(
    structure: dict[str, Any],
    events: dict[str, Any],
) -> dict[str, Any]:
    adjusted = deepcopy(structure)
    latest = events.get("latest_primary_event")
    if not latest:
        return adjusted
    event_type = latest["event_type"]
    primary = adjusted["primary_structure"]
    if event_type == "BEARISH_CHOCH" and primary == "BULLISH":
        adjusted["previous_primary_structure"] = "BULLISH"
        adjusted["primary_structure"] = "TRANSITION"
        adjusted["transition_reason"] = "PRIMARY_BEARISH_CHOCH"
    elif event_type == "BULLISH_CHOCH" and primary == "BEARISH":
        adjusted["previous_primary_structure"] = "BEARISH"
        adjusted["primary_structure"] = "TRANSITION"
        adjusted["transition_reason"] = "PRIMARY_BULLISH_CHOCH"
    return adjusted


def analyze_snapshot(
    snapshot: dict[str, Any],
    *,
    timeframe: str | None = None,
    parent_context: dict[str, Any] | None = None,
    parent_context_mode: str = "STANDALONE",
    profile_overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    requested = (
        timeframe or snapshot.get("requested_timeframe") or snapshot.get("timeframe") or ""
    ).upper()
    profile = get_profile(requested, profile_overrides)
    normalized = validate_snapshot(snapshot, profile)
    bars = normalized["bars"]
    indicators_full = calculate_indicators(bars, profile)
    swings = detect_swings(bars, indicators_full["series"]["atr_14"], profile)
    structure = classify_structure(bars, swings, indicators_full)
    events = scan_events(bars, swings, structure, indicators_full["series"]["atr_14"], profile)
    structure = _apply_structural_event_transition(structure, events)
    latest_atr = indicators_full["latest"]["atr_14"] or 0.0
    levels = build_levels(bars, swings, latest_atr, profile)
    liquidity = analyze_liquidity(bars, swings, latest_atr, profile)
    candle = analyze_candles(bars, latest_atr)
    scoring = calculate_score(structure, events, indicators_full, liquidity, candle)
    scoring["latest_close"] = indicators_full["latest"]["close"]

    analysis_context = build_timeframe_context(
        requested,
        normalized["market"],
        structure,
        events,
        levels,
        liquidity,
        scoring,
        parent_context,
        parent_context_mode.upper(),
    )

    input_digest = sha256_digest(normalized)
    parent_digest = sha256_digest(parent_context or {})
    output: dict[str, Any] = {
        "schema_version": "6.0",
        "engine": {
            "name": "market-structure-multi-timeframe",
            "version": __version__,
            "calculation_mode": "PYTHON_ONLY_FROM_OHLC",
            "external_indicator_values_accepted": False,
            "external_indicator_values_used": False,
            "volume_analysis_enabled": False,
            "entry_authorized": False,
        },
        "market": normalized["market"],
        "timeframe": requested,
        "timeframe_role": profile.role,
        "source_audit": {
            "source_type": normalized["source"]["type"],
            "requested_timeframe": normalized["requested_timeframe"],
            "returned_timeframe": normalized["returned_timeframe"],
            "candle_closure_verified": normalized["candle_closure_verified"],
            "latest_closed_candle_time": normalized["latest_closed_candle_time"],
            "bar_count_used": len(bars),
        },
        "technical_context": indicators_full["latest"],
        "candles": candle,
        "swings": swings,
        "market_structure": structure,
        "events": events,
        "levels": levels,
        "liquidity": liquidity,
        "scoring": scoring,
        "analysis_context": analysis_context,
        "decision_context": analysis_context,
        "calculation_metadata": {
            "profile": profile.to_dict(),
            "formula_metadata": indicators_full["formula_metadata"],
            "determinism": {
                "deterministic_engine": True,
                "random_seed_used": False,
                "canonical_sorting": True,
                "canonical_json_serialization": True,
                "python_version": platform.python_version(),
            },
            "input_digest_sha256": input_digest,
            "parent_context_digest_sha256": parent_digest,
        },
        "approved_for_decision_agent": analysis_context["approved_for_decision_agent"],
        "entry_authorized": False,
    }
    output["calculation_metadata"]["output_digest_sha256"] = sha256_digest(output)
    return output


def _check_same_market(outputs: list[dict[str, Any]]) -> None:
    markets = {(item["market"]["symbol"], item["market"]["provider"]) for item in outputs}
    if len(markets) != 1:
        raise ParentContextError("All timeframe snapshots must use the same symbol and provider.")


def analyze_multi_timeframe(
    request: dict[str, Any], *, profile_overrides: dict[str, dict[str, Any]] | None = None
) -> dict[str, Any]:
    if request.get("analysis_mode") != "MULTI_TIMEFRAME":
        raise ValidationError("analysis_mode must be MULTI_TIMEFRAME.")
    order = request.get("timeframes", ["D1", "H4", "H1"])
    if order != ["D1", "H4", "H1"]:
        raise ValidationError("Multi-timeframe execution order must be exactly D1, H4, H1.")
    snapshots = request.get("snapshots")
    if not isinstance(snapshots, dict) or any(tf not in snapshots for tf in order):
        raise ValidationError("snapshots must contain D1, H4 and H1.")

    profile_overrides = profile_overrides or {}
    d1 = analyze_snapshot(
        snapshots["D1"],
        timeframe="D1",
        parent_context_mode="STANDALONE",
        profile_overrides=profile_overrides.get("D1"),
    )
    d1_parent = d1["analysis_context"]
    h4 = analyze_snapshot(
        snapshots["H4"],
        timeframe="H4",
        parent_context={"D1": d1_parent},
        parent_context_mode="REQUIRED",
        profile_overrides=profile_overrides.get("H4"),
    )
    h4_parent = h4["analysis_context"]
    h1 = analyze_snapshot(
        snapshots["H1"],
        timeframe="H1",
        parent_context={"D1": d1_parent, "H4": h4_parent},
        parent_context_mode="REQUIRED",
        profile_overrides=profile_overrides.get("H1"),
    )
    _check_same_market([d1, h4, h1])
    confluence = build_confluence(d1, h4, h1)
    result = {
        "schema_version": "6.0",
        "analysis_mode": "MULTI_TIMEFRAME",
        "execution_order": ["D1", "H4", "H1"],
        "parallel_execution_allowed": False,
        "market": d1["market"],
        "timeframes": {"D1": d1, "H4": h4, "H1": h1},
        "confluence": confluence,
        "approved_for_decision_agent": all(
            item["approved_for_decision_agent"] for item in (d1, h4, h1)
        ),
        "entry_authorized": False,
        "calculation_metadata": {
            "engine_version": __version__,
            "request_digest_sha256": sha256_digest(request),
        },
    }
    result["calculation_metadata"]["output_digest_sha256"] = sha256_digest(result)
    return result
