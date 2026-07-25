from __future__ import annotations

from typing import Any

from .engine import analyze_multi_timeframe, analyze_snapshot
from .utils import sha256_digest


def _without_review_volatility(value: dict[str, Any]) -> dict[str, Any]:
    # Current engine output has no wall-clock execution timestamp. Keep this helper
    # for future schema extensions and explicitly exclude reviewer-owned fields.
    result = dict(value)
    result.pop("review", None)
    return result


def review_analysis(
    snapshot: dict[str, Any],
    expected: dict[str, Any],
    *,
    parent_context: dict[str, Any] | None = None,
    parent_context_mode: str = "STANDALONE",
    profile_overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    actual = analyze_snapshot(
        snapshot,
        timeframe=expected.get("timeframe"),
        parent_context=parent_context,
        parent_context_mode=parent_context_mode,
        profile_overrides=profile_overrides,
    )
    expected_digest = sha256_digest(_without_review_volatility(expected))
    actual_digest = sha256_digest(_without_review_volatility(actual))
    fields = [
        "technical_context",
        "swings",
        "market_structure",
        "events",
        "levels",
        "liquidity",
        "scoring",
        "analysis_context",
    ]
    mismatches = [field for field in fields if expected.get(field) != actual.get(field)]
    approved = not mismatches and expected_digest == actual_digest
    return {
        "review_status": "APPROVED" if approved else "REJECTED_NON_DETERMINISTIC_OUTPUT",
        "approved_for_publication": approved,
        "mismatched_sections": mismatches,
        "expected_digest_sha256": expected_digest,
        "recalculated_digest_sha256": actual_digest,
        "entry_authorized": False,
    }


def review_multi_timeframe(
    request: dict[str, Any],
    expected: dict[str, Any],
    *,
    profile_overrides: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    actual = analyze_multi_timeframe(request, profile_overrides=profile_overrides)
    expected_digest = sha256_digest(_without_review_volatility(expected))
    actual_digest = sha256_digest(_without_review_volatility(actual))
    mismatches = [
        field for field in ("timeframes", "confluence") if expected.get(field) != actual.get(field)
    ]
    approved = not mismatches and expected_digest == actual_digest
    return {
        "review_status": "APPROVED" if approved else "REJECTED_NON_DETERMINISTIC_OUTPUT",
        "approved_for_publication": approved,
        "mismatched_sections": mismatches,
        "expected_digest_sha256": expected_digest,
        "recalculated_digest_sha256": actual_digest,
        "entry_authorized": False,
    }
