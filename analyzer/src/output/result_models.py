from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from src.decision.models import DecisionOutput, MarketContextSummary, ReviewVerdict


class OHLCBar(BaseModel):
    """Single OHLC bar for chart rendering."""

    time: str
    open: float
    high: float
    low: float
    close: float


class OHLCData(BaseModel):
    """OHLC data keyed by timeframe."""

    D1: list[OHLCBar] = Field(default_factory=list)
    H4: list[OHLCBar] = Field(default_factory=list)
    H1: list[OHLCBar] = Field(default_factory=list)


class SLTPOverlay(BaseModel):
    """Entry, stop-loss and take-profit overlay for charts."""

    entry_price: float | None = None
    stop_loss: float | None = None
    take_profit: float | None = None


class AnalysisResult(BaseModel):
    """Top-level pipeline output serialized to JSON for the web viewer."""

    version: str = "1.0"
    symbol: str
    run_id: str
    started_at: datetime
    completed_at: datetime
    status: str  # "success" | "partial" | "error"
    errors: list[str] = Field(default_factory=list)
    fatal_error: str | None = None
    market_context: MarketContextSummary | None = None
    decision: DecisionOutput | None = None
    review: ReviewVerdict | None = None
    ohlc: OHLCData = Field(default_factory=OHLCData)
    sl_tp_overlay: SLTPOverlay = Field(default_factory=SLTPOverlay)
