"""Server-specific Pydantic models."""

from pydantic import BaseModel


class RunSummary(BaseModel):
    """Summary of a single analysis run, matching Node.js RunSummary shape."""

    symbol: str
    date: str  # YYYY-MM-DD
    time: str  # HH-MM
    bias: str
    confidence: float
    action: str
    review_approved: bool
    current_price: float | None = None
    file_path: str  # relative path from data dir


class RunRequest(BaseModel):
    """Request body for POST /api/run."""

    symbols: list[str]
    model: str | None = None
    base_url: str | None = None
