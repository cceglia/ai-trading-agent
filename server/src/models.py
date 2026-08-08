"""Server-specific Pydantic models."""

import re
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, field_validator


class RunSummary(BaseModel):
    """Summary of a single analysis run (schema-v2 summary contract).

    Exactly: symbol, date, time, bias, confidence, action, validation status,
    setup status, direction, operational, and file path. There is no
    ``review``-derived field: legacy runs are always UNKNOWN and
    non-operational, v2 runs carry their deterministic validation.

    Consistency note: ``confidence`` and ``bias`` are passed through from the
    underlying envelope without rescaling. v2 confidence is the deterministic
    0–100 score and bias is the uppercase trade direction (``BULLISH``);
    legacy confidence is the 0–1 interpretive value and legacy bias keeps the
    stored case (``bullish``). Consumers must treat them as display hints, not
    a normalized scale.
    """

    symbol: str
    date: str  # YYYY-MM-DD
    time: str  # HH-MM
    bias: str
    confidence: float
    action: str
    validation_status: str
    setup_status: str
    direction: str
    operational: bool
    file_path: str  # relative path from data dir


class RunRequest(BaseModel):
    """Request body for POST /api/run.

    Accepts 1–20 validated symbols plus optional ``model``/``provider_id``
    id fields. ``base_url`` is intentionally absent: provider endpoints are
    resolved server-side from ``provider_id`` (FR-039 / DEC-014), so any
    free-form URL in the request is rejected as an unknown field.
    """

    symbols: list[str]
    model: str | None = None
    provider_id: str | None = None

    model_config = ConfigDict(extra="forbid")

    @field_validator("model")
    @classmethod
    def _validate_model(cls, value: str | None) -> str | None:
        """Bound model id length/format (NFR-004 input hygiene)."""
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("model must not be empty")
        if len(value) > 100:
            raise ValueError("model must be 100 characters or fewer")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:/+-]*", value):
            raise ValueError("model contains unsupported characters")
        return value

    @field_validator("provider_id")
    @classmethod
    def _validate_provider_id(cls, value: str | None) -> str | None:
        """Bound provider_id length/format (FR-039 input hygiene).

        Provider ids are server-side keys into ``PROVIDER_CONFIG``; bounding
        length and character format keeps the id out of logs/errors and
        prevents oversized or structurally hostile values from reaching the
        config lookup.
        """
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("provider_id must not be empty")
        if len(value) > 32:
            raise ValueError("provider_id must be 32 characters or fewer")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", value):
            raise ValueError("provider_id contains unsupported characters")
        return value


class SymbolError(BaseModel):
    """Safe per-symbol terminal error envelope (§12.3).

    Carries a stable diagnostic ``code`` and a human-readable ``message``
    that never contains secrets or process stderr.
    """

    code: str
    message: str


BatchStatus = Literal["success", "partial", "error"]


class BatchResponse(BaseModel):
    """Batch envelope returned by POST /api/run (§12.3, FR-033).

    ``results`` is keyed by normalized symbol with exactly one terminal
    outcome per symbol; ``errors`` is keyed by failed symbol. ``status`` is
    ``success`` when all symbols complete, ``partial`` when at least one
    completes and at least one errors, and ``error`` when none produces a
    reliable result.
    """

    status: BatchStatus
    results: dict[str, dict[str, Any]]
    errors: dict[str, SymbolError]
