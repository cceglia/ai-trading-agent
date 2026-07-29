"""Tests for CostTracker — tracks LLM API call costs.

CostTracker lives in ``src/decision/cost_tracker.py`` and has no external
dependencies.  All tests import from the not-yet-existing module so they
fail RED with ``ModuleNotFoundError``.
"""

import logging

import pytest

from src.decision.cost_tracker import CostTracker


class TestCostTracker:
    """CostTracker: tracks LLM API call costs."""

    # ------------------------------------------------------------------
    # Pricing fixture shared by most tests — exact values from the plan
    # ------------------------------------------------------------------
    _PRICING: dict[str, dict[str, float]] = {
        "gpt-4o": {"prompt": 0.0000025, "completion": 0.00001},
    }

    # ------------------------------------------------------------------
    # 1. Initial state
    # ------------------------------------------------------------------
    def test_initial_state(self):
        """total_cost=0.0, call_count=0 on fresh instance."""
        ct = CostTracker(pricing=self._PRICING)
        assert ct.total_cost == 0.0
        assert ct.call_count == 0

    # ------------------------------------------------------------------
    # 2. record_call returns cost
    # ------------------------------------------------------------------
    def test_record_call_returns_cost(self):
        """record_call returns the per-call cost."""
        ct = CostTracker(pricing=self._PRICING)
        cost = ct.record_call("gpt-4o", prompt_tokens=1000, completion_tokens=500)
        # 1000 * 0.0000025 + 500 * 0.00001 = 0.0025 + 0.005 = 0.0075
        assert cost == pytest.approx(0.0075)

    # ------------------------------------------------------------------
    # 3. Accumulated total
    # ------------------------------------------------------------------
    def test_record_call_updates_total(self):
        """record_call accumulates total_cost across calls."""
        ct = CostTracker(pricing=self._PRICING)
        ct.record_call("gpt-4o", prompt_tokens=1000, completion_tokens=500)  # 0.0075
        ct.record_call("gpt-4o", prompt_tokens=2000, completion_tokens=1000)  # 0.0150
        assert ct.total_cost == pytest.approx(0.0225)

    # ------------------------------------------------------------------
    # 4. Call count
    # ------------------------------------------------------------------
    def test_record_call_increments_call_count(self):
        """record_call increments call_count."""
        ct = CostTracker(pricing=self._PRICING)
        assert ct.call_count == 0
        ct.record_call("gpt-4o", prompt_tokens=100, completion_tokens=50)
        assert ct.call_count == 1
        ct.record_call("gpt-4o", prompt_tokens=200, completion_tokens=100)
        assert ct.call_count == 2

    # ------------------------------------------------------------------
    # 5. Reset
    # ------------------------------------------------------------------
    def test_reset_zeroes_state(self):
        """After reset(), total_cost=0 and call_count=0."""
        ct = CostTracker(pricing=self._PRICING)
        ct.record_call("gpt-4o", prompt_tokens=1000, completion_tokens=500)
        ct.reset()
        assert ct.total_cost == 0.0
        assert ct.call_count == 0

    # ------------------------------------------------------------------
    # 6. Unknown model fallback
    # ------------------------------------------------------------------
    def test_unknown_model_uses_default(self, caplog):
        """Unknown model logs warning and falls back to gpt-4o pricing."""
        ct = CostTracker(pricing=self._PRICING)
        caplog.set_level(logging.WARNING)
        cost = ct.record_call("nonexistent-model", prompt_tokens=1000, completion_tokens=500)
        # Falls back to gpt-4o pricing → same as test_record_call_returns_cost
        assert cost == pytest.approx(0.0075)
        assert "nonexistent-model" in caplog.text
        # The fallback model mentioned in the log message
        assert "gpt-4o" in caplog.text

    # ------------------------------------------------------------------
    # 7. Negative tokens
    # ------------------------------------------------------------------
    def test_negative_tokens_raises_error(self):
        """Negative prompt or completion tokens raise ValueError."""
        ct = CostTracker(pricing=self._PRICING)
        with pytest.raises(ValueError, match="negative"):
            ct.record_call("gpt-4o", prompt_tokens=-100, completion_tokens=0)
        with pytest.raises(ValueError, match="negative"):
            ct.record_call("gpt-4o", prompt_tokens=0, completion_tokens=-50)
        with pytest.raises(ValueError, match="negative"):
            ct.record_call("gpt-4o", prompt_tokens=-1, completion_tokens=-1)

    # ------------------------------------------------------------------
    # 8. Zero tokens
    # ------------------------------------------------------------------
    def test_zero_tokens_zero_cost(self):
        """Zero tokens result in zero cost and call is NOT recorded."""
        ct = CostTracker(pricing=self._PRICING)
        cost = ct.record_call("gpt-4o", prompt_tokens=0, completion_tokens=0)
        assert cost == pytest.approx(0.0)
        assert ct.total_cost == 0.0
        assert ct.call_count == 0  # Changed from 1 to 0

    # ------------------------------------------------------------------
    # 9. Default pricing
    # ------------------------------------------------------------------
    def test_default_pricing_if_none_passed(self):
        """CostTracker() with no args uses default pricing from settings."""
        ct = CostTracker()
        # gpt-4o is always present in the default pricing:
        #   prompt=0.0000025, completion=0.00001
        cost = ct.record_call("gpt-4o", prompt_tokens=1000, completion_tokens=500)
        assert cost == pytest.approx(0.0075)

    # ------------------------------------------------------------------
    # 10. Empty pricing table — edge case
    # ------------------------------------------------------------------
    def test_empty_pricing_table_raises_value_error(self):
        """CostTracker(pricing={}) — record_call raises ValueError (not KeyError)
        because no model (including the gpt-4o fallback) exists in an empty pricing table.
        """
        ct = CostTracker(pricing={})
        with pytest.raises(ValueError, match="empty pricing"):
            ct.record_call("gpt-4o", prompt_tokens=100, completion_tokens=50)
        assert ct.total_cost == 0.0
        assert ct.call_count == 0

    # ------------------------------------------------------------------
    # 11. Many calls
    # ------------------------------------------------------------------
    def test_multiple_calls_accumulate(self):
        """Many calls accumulate total_cost correctly."""
        ct = CostTracker(pricing=self._PRICING)
        expected = 0.04125
        for i in range(1, 11):
            pt = 100 * i
            ct_ = 50 * i
            ct.record_call("gpt-4o", prompt_tokens=pt, completion_tokens=ct_)
        assert ct.total_cost == pytest.approx(expected)
        assert ct.call_count == 10

    # ==================================================================
    # Cost Limit Enforcement Tests  (TASK-1)
    #
    # These tests will fail RED because:
    #   - CostLimitExceeded doesn't exist yet         → ImportError
    #   - CostTracker.set_limit() doesn't exist yet   → AttributeError
    #   - No limit guard in record_call() yet         → AssertionError
    # ==================================================================

    # ------------------------------------------------------------------
    # 12. CostLimitExceeded is an Exception
    # ------------------------------------------------------------------
    def test_cost_limit_exceeded_is_exception(self):
        """CostLimitExceeded is a subclass of Exception."""
        from src.decision.cost_tracker import CostLimitExceeded

        assert issubclass(CostLimitExceeded, Exception)

    # ------------------------------------------------------------------
    # 13. set_limit stores limit
    # ------------------------------------------------------------------
    def test_set_limit_stores_limit(self):
        """After set_limit(0.05), internal _limit reflects the value."""
        ct = CostTracker(pricing=self._PRICING)
        ct.set_limit(0.05)
        assert ct._limit == 0.05  # type: ignore[attr-defined]

    # ------------------------------------------------------------------
    # 14. record_call raises when exceeds limit
    # ------------------------------------------------------------------
    def test_record_call_raises_when_exceeds_limit(self):
        """record_call raises CostLimitExceeded when total_cost > limit."""
        from src.decision.cost_tracker import CostLimitExceeded

        ct = CostTracker(pricing=self._PRICING)
        ct.set_limit(0.02)
        # call 1: 1000*0.0000025 + 500*0.00001 = 0.0075 → total = 0.0075
        ct.record_call("gpt-4o", prompt_tokens=1000, completion_tokens=500)
        # call 2: 1000*0.0000025 + 500*0.00001 = 0.0075 → total = 0.015
        ct.record_call("gpt-4o", prompt_tokens=1000, completion_tokens=500)
        # call 3: 1000*0.0000025 + 500*0.00001 = 0.0075 → total = 0.0225 > 0.02
        with pytest.raises(CostLimitExceeded):
            ct.record_call("gpt-4o", prompt_tokens=1000, completion_tokens=500)

    # ------------------------------------------------------------------
    # 15. Equal to limit does NOT raise
    # ------------------------------------------------------------------
    def test_record_call_does_not_raise_when_equal_to_limit(self):
        """total_cost == limit does NOT raise (strict > comparison)."""
        ct = CostTracker(pricing=self._PRICING)
        ct.set_limit(0.0225)
        # Three calls of (1000, 500) each = 0.0225 total
        ct.record_call("gpt-4o", prompt_tokens=1000, completion_tokens=500)
        ct.record_call("gpt-4o", prompt_tokens=1000, completion_tokens=500)
        ct.record_call("gpt-4o", prompt_tokens=1000, completion_tokens=500)
        # total_cost == limit == 0.0225 → should NOT raise
        assert ct.total_cost == pytest.approx(0.0225)

    # ------------------------------------------------------------------
    # 16. Below limit does NOT raise
    # ------------------------------------------------------------------
    def test_record_call_does_not_raise_when_below_limit(self):
        """total_cost < limit does NOT raise."""
        ct = CostTracker(pricing=self._PRICING)
        ct.set_limit(0.05)
        ct.record_call("gpt-4o", prompt_tokens=1000, completion_tokens=500)  # 0.0075 < 0.05
        assert ct.total_cost == pytest.approx(0.0075)

    # ------------------------------------------------------------------
    # 17. Zero limit disables enforcement
    # ------------------------------------------------------------------
    def test_zero_limit_disables_enforcement(self):
        """set_limit(0) disables enforcement — no raise regardless of cost."""
        ct = CostTracker(pricing=self._PRICING)
        ct.set_limit(0)
        # Accumulate well past any typical limit
        for _ in range(10):
            ct.record_call("gpt-4o", prompt_tokens=1000, completion_tokens=500)
        assert ct.total_cost == pytest.approx(0.075)

    # ------------------------------------------------------------------
    # 18. Negative limit disables enforcement
    # ------------------------------------------------------------------
    def test_negative_limit_disables_enforcement(self):
        """set_limit(-1) disables enforcement — no raise regardless of cost."""
        ct = CostTracker(pricing=self._PRICING)
        ct.set_limit(-1)
        for _ in range(10):
            ct.record_call("gpt-4o", prompt_tokens=1000, completion_tokens=500)
        assert ct.total_cost == pytest.approx(0.075)

    # ------------------------------------------------------------------
    # 19. No limit set = no enforcement
    # ------------------------------------------------------------------
    def test_no_limit_set_does_not_raise(self):
        """Default CostTracker without set_limit() never raises.

        Verifies backward compatibility: existing code that uses CostTracker
        without setting a limit continues to work unchanged.
        """

        ct = CostTracker(pricing=self._PRICING)
        # Many calls — no limit was set, so no CostLimitExceeded should occur
        for _ in range(100):
            ct.record_call("gpt-4o", prompt_tokens=1000, completion_tokens=500)
        assert ct.total_cost == pytest.approx(0.75)
        assert ct.call_count == 100

    # ------------------------------------------------------------------
    # 20. set_limit does not check existing cost
    # ------------------------------------------------------------------
    def test_set_limit_does_not_check_existing_cost(self):
        """set_limit() after calls already recorded does not retroactively raise."""
        from src.decision.cost_tracker import CostLimitExceeded

        ct = CostTracker(pricing=self._PRICING)
        # Accumulate cost first
        ct.record_call("gpt-4o", prompt_tokens=1000, completion_tokens=500)  # 0.0075
        ct.record_call("gpt-4o", prompt_tokens=2000, completion_tokens=1000)  # 0.015
        # total_cost = 0.0225
        assert ct.total_cost == pytest.approx(0.0225)

        # Now set a limit below current total — should NOT raise
        ct.set_limit(0.01)
        # The limit is now 0.01, but set_limit should not check existing cost

        # However, a subsequent call SHOULD raise (total 0.0225 > limit 0.01)
        with pytest.raises(CostLimitExceeded):
            ct.record_call("gpt-4o", prompt_tokens=100, completion_tokens=50)

    # ------------------------------------------------------------------
    # 21. CostLimitExceeded message includes limit and total_cost
    # ------------------------------------------------------------------
    def test_cost_limit_exceeded_message(self):
        """Exception string representation includes limit, total_cost, and symbol."""
        from src.decision.cost_tracker import CostLimitExceeded

        # Without symbol
        exc1 = CostLimitExceeded(limit=0.05, total_cost=0.075)
        msg1 = str(exc1)
        assert "0.05" in msg1
        assert "0.075" in msg1

        # With symbol
        exc2 = CostLimitExceeded(limit=0.05, total_cost=0.075, symbol="EURUSD")
        msg2 = str(exc2)
        assert "0.05" in msg2
        assert "0.075" in msg2
        assert "EURUSD" in msg2

    # ------------------------------------------------------------------
    # 22. set_symbol stores symbol
    # ------------------------------------------------------------------
    def test_set_symbol_stores_symbol(self):
        """set_symbol('XAUUSD') stores symbol internally."""
        ct = CostTracker(pricing=self._PRICING)
        ct.set_symbol("XAUUSD")
        assert ct._symbol == "XAUUSD"  # type: ignore[attr-defined]

    # ------------------------------------------------------------------
    # 23. record_call raises with symbol in message
    # ------------------------------------------------------------------
    def test_record_call_raises_with_symbol(self):
        """record_call raises CostLimitExceeded with symbol in message."""
        from src.decision.cost_tracker import CostLimitExceeded

        ct = CostTracker(pricing=self._PRICING)
        ct.set_limit(0.01)
        ct.set_symbol("XAUUSD")
        ct.record_call("gpt-4o", prompt_tokens=1000, completion_tokens=500)  # 0.0075
        with pytest.raises(CostLimitExceeded) as exc_info:
            ct.record_call("gpt-4o", prompt_tokens=1000, completion_tokens=500)  # 0.015 > 0.01
        assert "XAUUSD" in str(exc_info.value)

    # ------------------------------------------------------------------
    # 24. record_call raises without symbol
    # ------------------------------------------------------------------
    def test_record_call_raises_without_symbol(self):
        """record_call raises CostLimitExceeded without symbol when not set."""
        from src.decision.cost_tracker import CostLimitExceeded

        ct = CostTracker(pricing=self._PRICING)
        ct.set_limit(0.01)
        ct.record_call("gpt-4o", prompt_tokens=1000, completion_tokens=500)  # 0.0075
        with pytest.raises(CostLimitExceeded) as exc_info:
            ct.record_call("gpt-4o", prompt_tokens=1000, completion_tokens=500)  # 0.015 > 0.01
        assert "for " not in str(exc_info.value)

    # ------------------------------------------------------------------
    # 25. set_limit(None) disables enforcement
    # ------------------------------------------------------------------
    def test_set_limit_none_disables_enforcement(self):
        """set_limit(None) disables enforcement — no raise, no crash."""
        ct = CostTracker(pricing=self._PRICING)
        ct.set_limit(None)  # should not raise TypeError
        for _ in range(10):
            ct.record_call("gpt-4o", prompt_tokens=1000, completion_tokens=500)
        assert ct.total_cost == pytest.approx(0.075)

    # ------------------------------------------------------------------
    # 26. set_symbol overwrites symbol
    # ------------------------------------------------------------------
    def test_set_symbol_cleared_by_set_symbol(self):
        """set_symbol('B') after set_symbol('A') overwrites symbol."""
        ct = CostTracker(pricing=self._PRICING)
        ct.set_symbol("XAUUSD")
        assert ct._symbol == "XAUUSD"  # type: ignore[attr-defined]
        ct.set_symbol("EURUSD")
        assert ct._symbol == "EURUSD"  # type: ignore[attr-defined]
        assert ct._symbol != "XAUUSD"  # type: ignore[attr-defined]
