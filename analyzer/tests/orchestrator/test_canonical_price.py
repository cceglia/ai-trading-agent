"""RED-first tests for the canonical current-price selection helper (TASK-6).

These tests target the module-level pure function
``src.orchestrator.graph._select_canonical_current_price`` which does NOT
exist yet. They are expected to FAIL (RED) until TASK-6 implements the
helper. The import is performed lazily inside each test so that collection
of the orchestrator suite is not aborted — only these tests fail (RED).
"""

from __future__ import annotations

import pytest


def _select_canonical_current_price(timeframes):  # type: ignore[no-untyped-def]
    """Lazy-import the not-yet-existing helper so collection succeeds.

    Raises ``ImportError`` at call time (RED) until TASK-6 adds the real
    symbol to ``src.orchestrator.graph``.
    """
    from src.orchestrator.graph import (
        _select_canonical_current_price as _impl,
    )

    return _impl(timeframes)


def _tf(close: float | None, latest_closed: str | None) -> dict:
    """Build a single per-timeframe engine-output dict for the selector."""
    tf: dict = {"market_structure": {"primary_structure": "BULLISH"}}
    if latest_closed is not None:
        tf["source_audit"] = {"latest_closed_candle_time": latest_closed}
    else:
        tf["source_audit"] = {}
    tf["technical_context"] = {"close": close}
    return tf


class TestSelectCanonicalCurrentPrice:
    def test_select_picks_max_latest_closed_candle_time(self) -> None:
        timeframes = {
            "D1": _tf(1.10, "2024-01-03T00:00:00"),
            "H4": _tf(1.11, "2024-01-03T12:00:00"),
            "H1": _tf(1.12, "2024-01-03T20:00:00"),
        }
        price, ts = _select_canonical_current_price(timeframes)
        assert (price, ts) == (1.12, "2024-01-03T20:00:00")

    def test_select_tie_break_prefers_h1_over_h4_over_d1(self) -> None:
        timeframes = {
            "D1": _tf(1.10, "2024-01-03T00:00:00"),
            "H4": _tf(1.11, "2024-01-03T00:00:00"),
            "H1": _tf(1.12, "2024-01-03T00:00:00"),
        }
        price, ts = _select_canonical_current_price(timeframes)
        # All timestamps tie — H1 wins the tie-break.
        assert (price, ts) == (1.12, "2024-01-03T00:00:00")

    def test_select_returns_none_when_all_missing(self) -> None:
        timeframes = {
            "D1": _tf(1.10, None),
            "H4": _tf(1.11, None),
            "H1": _tf(1.12, None),
        }
        price, ts = _select_canonical_current_price(timeframes)
        assert (price, ts) == (None, None)

    def test_select_skips_tf_with_none_close(self) -> None:
        # H1 has a valid timestamp but close=None — it must be skipped,
        # so the next-best (H4) is selected.
        timeframes = {
            "D1": _tf(1.10, "2024-01-03T00:00:00"),
            "H4": _tf(1.11, "2024-01-03T12:00:00"),
            "H1": _tf(None, "2024-01-03T20:00:00"),
        }
        price, ts = _select_canonical_current_price(timeframes)
        assert (price, ts) == (1.11, "2024-01-03T12:00:00")


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__, "-v"])
