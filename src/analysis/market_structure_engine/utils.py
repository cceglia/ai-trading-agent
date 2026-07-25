from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Iterable
from datetime import datetime
from typing import Any


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def sha256_digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def finite_number(value: Any) -> bool:
    return (
        isinstance(value, int | float)
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def safe_div(numerator: float, denominator: float, default: float = 0.0) -> float:
    return numerator / denominator if denominator else default


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def round_or_none(value: float | None, digits: int = 8) -> float | None:
    return None if value is None else round(float(value), digits)


def parse_iso_timestamp(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


def last_non_none(values: Iterable[float | None]) -> float | None:
    for value in reversed(list(values)):
        if value is not None:
            return value
    return None


def stable_id(prefix: str, *parts: object) -> str:
    payload = "|".join(str(part) for part in parts)
    return f"{prefix}_{hashlib.sha1(payload.encode('utf-8')).hexdigest()[:12]}"
