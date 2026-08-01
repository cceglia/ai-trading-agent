from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from src.output.result_models import AnalysisResult, OHLCBar, OHLCData, SLTPOverlay

logger = logging.getLogger(__name__)


class ResultWriterContractError(Exception):
    """Raised when ResultWriter receives an invalid or incomplete result."""


class ResultWriter:
    """Writes analysis results to JSON files in the data/ directory tree."""

    def __init__(self, base_dir: str | Path | None = None) -> None:
        if base_dir is None:
            from config.settings import Settings

            base_dir = Settings().resolved_analysis_cache_dir
        self.base_dir = Path(base_dir)

    def write(
        self,
        symbol: str,
        result: dict[str, Any],
        ohlc: dict[str, list[OHLCBar]],
        broker_now: datetime,
    ) -> Path | None:
        """Write a successful or partial result JSON to disk.

        Fatal pipeline failures are deliberately not persisted: they do not
        contain a usable analysis result and would otherwise pollute the run
        history with records that cannot be rendered by the dashboard.

        Returns the written file path, or ``None`` for a fatal result.

        Args:
            symbol: Trading symbol (e.g., "XAUUSD")
            result: Pipeline output dict from TradingGraph.run()
            ohlc: Dict of timeframe -> list[OHLCBar]
            broker_now: Broker local time (used for path construction)

        Returns:
            Path to the written file, or ``None`` when a fatal result is skipped.
        """
        fatal_error = result.get("fatal_error")
        if fatal_error is not None:
            logger.warning(
                "Skipping persistence of failed analysis for %s: %s",
                symbol,
                fatal_error,
            )
            return None

        path = self._build_path(symbol, broker_now)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Determine status
        errors = result.get("errors", [])
        if errors:
            status = "partial"
        else:
            status = "success"

        # Build run_id from broker_now
        run_id = broker_now.strftime("%Y-%m-%dT%H:%M:%S")

        # Map ohlc dict -> OHLCData
        ohlc_data = OHLCData(
            D1=ohlc.get("D1", []),
            H4=ohlc.get("H4", []),
            H1=ohlc.get("H1", []),
        )

        # Build SL/TP overlay from analysis_result (deterministic engine)
        analysis_result_obj = result.get("analysis_result")
        if analysis_result_obj is not None:
            overlay = getattr(analysis_result_obj, "sl_tp_overlay", None)
            if overlay is not None:
                sl_tp_overlay = overlay
            else:
                sl_tp_overlay = SLTPOverlay()
        else:
            # No analysis_result available. Use an empty overlay only for
            # partial results; successful results must contain deterministic
            # trade levels.
            if not errors:
                raise ResultWriterContractError(
                    "AnalysisResult is required to write deterministic trade levels"
                )
            sl_tp_overlay = SLTPOverlay()

        decision = result.get("decision")
        analysis_result = AnalysisResult(
            symbol=symbol,
            run_id=run_id,
            started_at=broker_now,
            completed_at=broker_now,
            status=status,
            errors=errors,
            fatal_error=fatal_error,
            market_context=result.get("market_context"),
            decision=decision,
            review=result.get("review"),
            ohlc=ohlc_data,
            sl_tp_overlay=sl_tp_overlay,
        )

        # Serialize to JSON — use model_dump(mode="json") for Pydantic v2
        raw = analysis_result.model_dump(mode="json", by_alias=False)
        path.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")

        logger.info("Wrote analysis result to %s", path)
        return path

    def _build_path(self, symbol: str, broker_now: datetime) -> Path:
        """Compute data/YYYY/MM/DD/SYMBOL/result-HH.json path."""
        return (
            self.base_dir
            / f"{broker_now:%Y}"
            / f"{broker_now:%m}"
            / f"{broker_now:%d}"
            / symbol
            / f"result-{broker_now:%H}.json"
        )
