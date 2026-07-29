"""LLM usage tracking — parse provider responses and extract token counts.

This module is the single point where raw provider responses are parsed into
structured :class:`LLMUsage` objects.  It has no knowledge of pricing or cost
calculation — those belong in :mod:`cost_tracker`.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Safe integer normaliser
# ---------------------------------------------------------------------------


def safe_non_negative_int(value: object) -> int:
    """Return a non-negative ``int`` or ``0`` for invalid/missing values.

    Handles ``None``, booleans, negative numbers, NaN, infinity,
    non-numeric strings, and unrecognised types gracefully — all
    produce ``0`` with a warning for unrecognised input.

    An explicitly passed ``float`` (e.g. ``100.0``) is converted to
    ``int`` via truncation toward zero.
    """
    if value is None:
        return 0

    if isinstance(value, bool):
        logger.warning("Boolean %r treated as 0 for token count", value)
        return 0

    if isinstance(value, str):
        try:
            parsed = float(value)
        except (ValueError, TypeError):
            logger.warning("Non-numeric string %r treated as 0 for token count", value)
            return 0
        if math.isnan(parsed) or math.isinf(parsed):
            logger.warning("NaN/inf string %r treated as 0 for token count", value)
            return 0
        if parsed < 0:
            return 0
        return int(parsed)

    if isinstance(value, int | float):
        if math.isnan(value) or math.isinf(value):
            logger.warning("%r treated as 0 for token count", value)
            return 0
        if value < 0:
            return 0
        return int(value)

    logger.warning(
        "Unexpected type %s (%r) treated as 0 for token count", type(value).__name__, value
    )
    return 0


# ---------------------------------------------------------------------------
# LLMUsage dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LLMUsage:
    """Immutable record of token usage for a single LLM API call.

    Token fields are non-negative integers, cost fields are non-negative
    floats.  Costs are filled in by :class:`CostTracker` after pricing
    lookup — they default to ``0.0`` when usage data is unavailable.
    """

    input_tokens: int = 0
    cached_input_tokens: int = 0
    uncached_input_tokens: int = 0
    output_tokens: int = 0
    reasoning_tokens: int = 0
    total_tokens: int = 0

    input_cost: float = 0.0
    cached_input_cost: float = 0.0
    output_cost: float = 0.0
    total_cost: float = 0.0


# ---------------------------------------------------------------------------
# Nested-field access helpers
# ---------------------------------------------------------------------------


def _field_exists(usage: Any, *keys: str) -> bool:
    """Return ``True`` if the nested attribute/dict path exists.

    Works with objects, dicts, or a mix.  An intermediate ``None``
    value is treated as *non-existent*.
    """
    current = usage
    for key in keys:
        if current is None:
            return False
        if isinstance(current, dict):
            if key not in current:
                return False
            current = current[key]
        else:
            if not hasattr(current, key):
                return False
            current = getattr(current, key)
    return True


def _get_field(usage: Any, *keys: str) -> Any:
    """Return the value at a nested attribute/dict path, or ``None``."""
    current = usage
    for key in keys:
        if current is None:
            return None
        if isinstance(current, dict):
            current = current.get(key)
        else:
            current = getattr(current, key, None)
    return current


def _extract_int(
    usage: Any,
    primary: tuple[str, ...],
    fallback: tuple[str, ...],
) -> int:
    """Extract a scalar integer field with primary → fallback resolution.

    If the primary path *exists* (even with value ``None``) its value is
    used (normalised).  Otherwise the fallback path is tried.  If neither
    exists returns ``0``.
    """
    if _field_exists(usage, *primary):
        return safe_non_negative_int(_get_field(usage, *primary))
    if _field_exists(usage, *fallback):
        return safe_non_negative_int(_get_field(usage, *fallback))
    return 0


def _extract_total_tokens(
    usage: Any,
    input_tokens: int,
    output_tokens: int,
) -> int:
    """Extract ``total_tokens`` or derive from ``input_tokens + output_tokens``.

    If the provider explicitly returned a ``total_tokens`` field with a
    non-``None`` value (including ``0``) it is used.  When the field is
    structurally absent **or** ``None`` we derive from input + output.
    """
    if _field_exists(usage, "total_tokens"):
        val = _get_field(usage, "total_tokens")
        if val is not None:
            return safe_non_negative_int(val)
    return input_tokens + output_tokens


# ---------------------------------------------------------------------------
# Main parser
# ---------------------------------------------------------------------------


def parse_usage(response: Any) -> LLMUsage:
    """Extract an ``LLMUsage`` from a provider response.

    Handles:
    * ``None`` response
    * missing ``usage`` field
    * ``usage = None``
    * partial data structures
    * both Responses API and Chat Completions field names
    * nested ``input_tokens_details`` / ``output_tokens_details`` being absent or ``None``

    All missing/invalid fields default to ``0`` / ``0.0``.
    No exception is raised for missing data.
    """
    if response is None:
        return LLMUsage()

    # Extract ``usage`` from object or dict.
    if isinstance(response, dict):
        usage = response.get("usage")
    else:
        usage = getattr(response, "usage", None)

    if usage is None:
        return LLMUsage()

    # ---- Extract token counts with primary/fallback paths ----
    input_tokens = _extract_int(
        usage,
        primary=("input_tokens",),
        fallback=("prompt_tokens",),
    )
    output_tokens = _extract_int(
        usage,
        primary=("output_tokens",),
        fallback=("completion_tokens",),
    )
    cached_input_tokens = _extract_int(
        usage,
        primary=("input_tokens_details", "cached_tokens"),
        fallback=("prompt_tokens_details", "cached_tokens"),
    )
    reasoning_tokens = _extract_int(
        usage,
        primary=("output_tokens_details", "reasoning_tokens"),
        fallback=("completion_tokens_details", "reasoning_tokens"),
    )

    total_tokens = _extract_total_tokens(usage, input_tokens, output_tokens)

    # Clamp cached to input — logs must never show cached > total input.
    cached_input_tokens = min(cached_input_tokens, input_tokens)
    uncached_input_tokens = max(input_tokens - cached_input_tokens, 0)

    return LLMUsage(
        input_tokens=input_tokens,
        cached_input_tokens=cached_input_tokens,
        uncached_input_tokens=uncached_input_tokens,
        output_tokens=output_tokens,
        reasoning_tokens=reasoning_tokens,
        total_tokens=total_tokens,
    )
