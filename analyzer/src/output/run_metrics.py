"""Bounded per-batch run metrics counters (NFR §18).

Counters are process-local and bounded: the symbol label set is capped, only
symbols actually run in this process are counted, and values are small
integers. No secrets or raw dumps are stored. The summary is emitted as a
single log line at the end of a CLI batch.
"""

from __future__ import annotations

import logging
from collections import Counter
from typing import Any

logger = logging.getLogger(__name__)


def _field(value: Any, key: str, default: Any = None) -> Any:
    """Read ``key`` from a pydantic model or dict, tolerating ``None``."""
    if value is None:
        return default
    if isinstance(value, dict):
        return value.get(key, default)
    return getattr(value, key, default)


class RunMetrics:
    """Aggregate analysis outcome counters for one CLI batch (NFR §18)."""

    def __init__(self, symbol_label_limit: int = 50) -> None:
        self._outcomes: Counter[str] = Counter()
        self._symbols: set[str] = set()
        self._symbol_label_limit = symbol_label_limit
        self.llm_calls = 0
        self.notifications_sent = 0
        self.notifications_suppressed = 0

    def record(self, symbol: str, outcome_status: str, result: dict[str, Any]) -> None:
        """Categorize one symbol run into a bounded outcome bucket.

        Args:
            symbol: The normalized symbol (bounded label set).
            outcome_status: ``"success"`` or ``"error"`` from the CLI runner.
            result: The pipeline output dict for the symbol.
        """
        if len(self._symbols) < self._symbol_label_limit:
            self._symbols.add(symbol)
        if outcome_status == "error" or result.get("fatal_error"):
            self._outcomes["analysis_error"] += 1
            return
        analysis = result.get("analysis_result")
        status = _field(analysis, "status", "error")
        validation_status = _field(analysis, "validation_status", "INVALID")
        if status == "degraded":
            self._outcomes["analysis_degraded"] += 1
        elif status == "success":
            self._outcomes["analysis_success"] += 1
        elif validation_status == "INVALID":
            self._outcomes["analysis_invalid"] += 1
        else:
            # METRICS-002: fallback bucket. Unrecognized partial/validation
            # statuses (e.g. status ``"partial"`` with a ``VALID`` validation)
            # have no dedicated counter and are deliberately aggregated as
            # ``analysis_degraded`` — they are not full successes and they are
            # not invalid. No separate bucket exists to keep the summary line
            # bounded; this branch is latent for the current pipeline statuses.
            self._outcomes["analysis_degraded"] += 1

    def record_notification(self, sent: bool) -> None:
        """Count a sent or suppressed Telegram notification."""
        if sent:
            self.notifications_sent += 1
        else:
            self.notifications_suppressed += 1

    def log_summary(self) -> None:
        """Emit one bounded summary line with all counters."""
        logger.info(
            "Run metrics: symbols=%d llm_calls=%d analysis_success=%d "
            "analysis_degraded=%d analysis_invalid=%d analysis_error=%d "
            "notifications_sent=%d notifications_suppressed=%d",
            len(self._symbols),
            self.llm_calls,
            self._outcomes["analysis_success"],
            self._outcomes["analysis_degraded"],
            self._outcomes["analysis_invalid"],
            self._outcomes["analysis_error"],
            self.notifications_sent,
            self.notifications_suppressed,
        )
