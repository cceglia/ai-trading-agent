"""Server-specific Pydantic models."""

from pydantic import BaseModel


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
    """Request body for POST /api/run."""

    symbols: list[str]
    model: str | None = None
    base_url: str | None = None
