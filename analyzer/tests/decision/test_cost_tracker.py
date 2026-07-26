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
