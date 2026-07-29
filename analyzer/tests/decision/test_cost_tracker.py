"""Tests for CostTracker — tracks LLM API call costs.

CostTracker lives in ``src/decision/cost_tracker.py``.
All tests import from the module directly.
"""

import logging

import pytest

from src.decision.cost_tracker import CostTracker
from src.decision.usage import LLMUsage


class TestCostTracker:
    """CostTracker: tracks LLM API call costs."""

    # ------------------------------------------------------------------
    # Pricing fixture — new format (dollars-per-million tokens)
    # ------------------------------------------------------------------
    _PRICING: dict[str, dict[str, float]] = {
        "gpt-4o": {
            "input_per_million": 2.50,
            "cached_input_per_million": 1.25,
            "output_per_million": 10.00,
        },
    }

    @staticmethod
    def _usage(
        input_tokens: int = 1000,
        output_tokens: int = 500,
        cached_input_tokens: int = 0,
        reasoning_tokens: int = 0,
    ) -> LLMUsage:
        """Build an LLMUsage with computed uncached and total."""
        cached = min(cached_input_tokens, input_tokens)
        return LLMUsage(
            input_tokens=input_tokens,
            cached_input_tokens=cached,
            uncached_input_tokens=input_tokens - cached,
            output_tokens=output_tokens,
            reasoning_tokens=reasoning_tokens,
            total_tokens=input_tokens + output_tokens,
        )

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
        """record_call returns the per-call cost in LLMUsage.total_cost."""
        ct = CostTracker(pricing=self._PRICING)
        usage = self._usage(input_tokens=1000, output_tokens=500)
        enriched = ct.record_call("gpt-4o", usage)
        # 1000 * 2.50 / 1_000_000 + 0 + 500 * 10.00 / 1_000_000
        # = 0.0025 + 0.0 + 0.005 = 0.0075
        assert enriched.total_cost == pytest.approx(0.0075)
        assert enriched.input_cost == pytest.approx(0.0025)
        assert enriched.output_cost == pytest.approx(0.005)

    # ------------------------------------------------------------------
    # 3. Accumulated total
    # ------------------------------------------------------------------
    def test_record_call_updates_total(self):
        """record_call accumulates total_cost across calls."""
        ct = CostTracker(pricing=self._PRICING)
        ct.record_call("gpt-4o", self._usage(input_tokens=1000, output_tokens=500))  # 0.0075
        ct.record_call("gpt-4o", self._usage(input_tokens=2000, output_tokens=1000))  # 0.0150
        assert ct.total_cost == pytest.approx(0.0225)

    # ------------------------------------------------------------------
    # 4. Call count
    # ------------------------------------------------------------------
    def test_record_call_increments_call_count(self):
        """record_call increments call_count."""
        ct = CostTracker(pricing=self._PRICING)
        assert ct.call_count == 0
        ct.record_call("gpt-4o", self._usage(input_tokens=100, output_tokens=50))
        assert ct.call_count == 1
        ct.record_call("gpt-4o", self._usage(input_tokens=200, output_tokens=100))
        assert ct.call_count == 2

    # ------------------------------------------------------------------
    # 5. Reset
    # ------------------------------------------------------------------
    def test_reset_zeroes_state(self):
        """After reset(), total_cost=0 and call_count=0."""
        ct = CostTracker(pricing=self._PRICING)
        ct.record_call("gpt-4o", self._usage(input_tokens=1000, output_tokens=500))
        ct.reset()
        assert ct.total_cost == 0.0
        assert ct.call_count == 0

    # ------------------------------------------------------------------
    # 6. Unknown model preserves tokens, zero costs
    # ------------------------------------------------------------------
    def test_unknown_model_preserves_tokens_and_returns_zero_cost(self, caplog):
        """Unknown model logs warning, preserves token fields, cost fields zero."""
        ct = CostTracker(pricing=self._PRICING)
        caplog.set_level(logging.WARNING)
        usage = self._usage(input_tokens=1000, output_tokens=500, cached_input_tokens=200)
        enriched = ct.record_call("nonexistent-model", usage)

        # Token fields preserved
        assert enriched.input_tokens == 1000
        assert enriched.cached_input_tokens == 200
        assert enriched.uncached_input_tokens == 800
        assert enriched.output_tokens == 500
        assert enriched.total_tokens == 1500

        # Cost fields zero
        assert enriched.input_cost == 0.0
        assert enriched.cached_input_cost == 0.0
        assert enriched.output_cost == 0.0
        assert enriched.total_cost == 0.0

        # Call counted
        assert ct.call_count == 1
        assert ct.total_cost == 0.0

        assert "nonexistent-model" in caplog.text

    # ------------------------------------------------------------------
    # 7. Missing price keys default to zero
    # ------------------------------------------------------------------
    def test_missing_cached_input_price(self):
        """Missing cached_input_per_million → cached_input_cost = 0.0."""
        pricing = {
            "gpt-4o": {
                "input_per_million": 2.50,
                # cached_input_per_million is absent
                "output_per_million": 10.00,
            },
        }
        ct = CostTracker(pricing=pricing)
        usage = self._usage(input_tokens=1000, output_tokens=500, cached_input_tokens=200)
        enriched = ct.record_call("gpt-4o", usage)
        assert enriched.cached_input_cost == 0.0  # missing key → zero
        assert enriched.input_cost == pytest.approx(0.002)  # 800 * 2.50 / 1_000_000 = 0.002
        assert enriched.output_cost == pytest.approx(0.005)

    def test_missing_input_price(self):
        """Missing input_per_million → input_cost = 0.0."""
        pricing = {
            "gpt-4o": {
                # input_per_million is absent
                "cached_input_per_million": 1.25,
                "output_per_million": 10.00,
            },
        }
        ct = CostTracker(pricing=pricing)
        usage = self._usage(input_tokens=1000, output_tokens=500)
        enriched = ct.record_call("gpt-4o", usage)
        assert enriched.input_cost == 0.0
        assert enriched.output_cost == pytest.approx(0.005)

    # ------------------------------------------------------------------
    # 7b. Zero tokens
    # ------------------------------------------------------------------
    def test_zero_tokens_zero_cost(self):
        """Zero tokens result in zero cost but call IS counted."""
        ct = CostTracker(pricing=self._PRICING)
        usage = self._usage(input_tokens=0, output_tokens=0)
        enriched = ct.record_call("gpt-4o", usage)
        assert enriched.total_cost == 0.0
        assert ct.total_cost == 0.0
        assert ct.call_count == 1  # Call is still counted

    # ------------------------------------------------------------------
    # 8. Empty pricing table
    # ------------------------------------------------------------------
    def test_empty_pricing_table(self):
        """CostTracker(pricing={}) — record_call warns and returns zero costs."""
        ct = CostTracker(pricing={})
        usage = self._usage(input_tokens=100, output_tokens=50)
        enriched = ct.record_call("gpt-4o", usage)
        assert enriched.total_cost == 0.0
        assert ct.total_cost == 0.0
        assert ct.call_count == 1

    # ------------------------------------------------------------------
    # 9. Many calls
    # ------------------------------------------------------------------
    def test_multiple_calls_accumulate(self):
        """Many calls accumulate total_cost correctly."""
        ct = CostTracker(pricing=self._PRICING)
        expected = 0.04125
        for i in range(1, 11):
            pt = 100 * i
            ct_ = 50 * i
            ct.record_call("gpt-4o", self._usage(input_tokens=pt, output_tokens=ct_))
        assert ct.total_cost == pytest.approx(expected)
        assert ct.call_count == 10

    # ------------------------------------------------------------------
    # 10. Missing output price
    # ------------------------------------------------------------------
    def test_missing_output_price(self):
        """Missing output_per_million → output_cost = 0.0."""
        pricing = {
            "gpt-4o": {
                "input_per_million": 2.50,
                "cached_input_per_million": 1.25,
                # output_per_million is absent
            },
        }
        ct = CostTracker(pricing=pricing)
        usage = self._usage(input_tokens=1000, output_tokens=500, cached_input_tokens=200)
        enriched = ct.record_call("gpt-4o", usage)
        assert enriched.output_cost == 0.0
        assert enriched.input_cost == pytest.approx(0.002)  # 800 * 2.50 / 1_000_000
        assert enriched.cached_input_cost == pytest.approx(0.00025)  # 200 * 1.25 / 1_000_000

    # ==================================================================
    # Cost Limit Enforcement Tests
    # ==================================================================

    # ------------------------------------------------------------------
    # 11. CostLimitExceeded is an Exception
    # ------------------------------------------------------------------
    def test_cost_limit_exceeded_is_exception(self):
        """CostLimitExceeded is a subclass of Exception."""
        from src.decision.cost_tracker import CostLimitExceeded

        assert issubclass(CostLimitExceeded, Exception)

    # ------------------------------------------------------------------
    # 12. set_limit stores limit
    # ------------------------------------------------------------------
    def test_set_limit_stores_limit(self):
        """After set_limit(0.05), internal _limit reflects the value."""
        ct = CostTracker(pricing=self._PRICING)
        ct.set_limit(0.05)
        assert ct._limit == 0.05  # type: ignore[attr-defined]

    # ------------------------------------------------------------------
    # 13. record_call raises when exceeds limit
    # ------------------------------------------------------------------
    def test_record_call_raises_when_exceeds_limit(self):
        """record_call raises CostLimitExceeded when total_cost > limit."""
        from src.decision.cost_tracker import CostLimitExceeded

        ct = CostTracker(pricing=self._PRICING)
        ct.set_limit(0.02)
        # call 1: cost = 0.0075 → total = 0.0075
        ct.record_call("gpt-4o", self._usage(input_tokens=1000, output_tokens=500))
        # call 2: cost = 0.0075 → total = 0.015
        ct.record_call("gpt-4o", self._usage(input_tokens=1000, output_tokens=500))
        # call 3: cost = 0.0075 → total = 0.0225 > 0.02
        with pytest.raises(CostLimitExceeded):
            ct.record_call("gpt-4o", self._usage(input_tokens=1000, output_tokens=500))

    # ------------------------------------------------------------------
    # 14. Equal to limit does NOT raise
    # ------------------------------------------------------------------
    def test_record_call_does_not_raise_when_equal_to_limit(self):
        """total_cost == limit does NOT raise (strict > comparison)."""
        ct = CostTracker(pricing=self._PRICING)
        ct.set_limit(0.0225)
        # Three calls of (1000, 500) each = 0.0225 total
        ct.record_call("gpt-4o", self._usage(input_tokens=1000, output_tokens=500))
        ct.record_call("gpt-4o", self._usage(input_tokens=1000, output_tokens=500))
        ct.record_call("gpt-4o", self._usage(input_tokens=1000, output_tokens=500))
        assert ct.total_cost == pytest.approx(0.0225)

    # ------------------------------------------------------------------
    # 15. Below limit does NOT raise
    # ------------------------------------------------------------------
    def test_record_call_does_not_raise_when_below_limit(self):
        """total_cost < limit does NOT raise."""
        ct = CostTracker(pricing=self._PRICING)
        ct.set_limit(0.05)
        ct.record_call("gpt-4o", self._usage(input_tokens=1000, output_tokens=500))
        assert ct.total_cost == pytest.approx(0.0075)

    # ------------------------------------------------------------------
    # 16. Zero limit disables enforcement
    # ------------------------------------------------------------------
    def test_zero_limit_disables_enforcement(self):
        """set_limit(0) disables enforcement."""
        ct = CostTracker(pricing=self._PRICING)
        ct.set_limit(0)
        for _ in range(10):
            ct.record_call("gpt-4o", self._usage(input_tokens=1000, output_tokens=500))
        assert ct.total_cost == pytest.approx(0.075)

    # ------------------------------------------------------------------
    # 17. Negative limit disables enforcement
    # ------------------------------------------------------------------
    def test_negative_limit_disables_enforcement(self):
        """set_limit(-1) disables enforcement."""
        ct = CostTracker(pricing=self._PRICING)
        ct.set_limit(-1)
        for _ in range(10):
            ct.record_call("gpt-4o", self._usage(input_tokens=1000, output_tokens=500))
        assert ct.total_cost == pytest.approx(0.075)

    # ------------------------------------------------------------------
    # 18. No limit set = no enforcement
    # ------------------------------------------------------------------
    def test_no_limit_set_does_not_raise(self):
        """Default CostTracker without set_limit() never raises."""
        ct = CostTracker(pricing=self._PRICING)
        for _ in range(100):
            ct.record_call("gpt-4o", self._usage(input_tokens=1000, output_tokens=500))
        assert ct.total_cost == pytest.approx(0.75)
        assert ct.call_count == 100

    # ------------------------------------------------------------------
    # 19. set_limit does not check existing cost
    # ------------------------------------------------------------------
    def test_set_limit_does_not_check_existing_cost(self):
        """set_limit() after calls already recorded does not retroactively raise."""
        from src.decision.cost_tracker import CostLimitExceeded

        ct = CostTracker(pricing=self._PRICING)
        ct.record_call("gpt-4o", self._usage(input_tokens=1000, output_tokens=500))
        ct.record_call("gpt-4o", self._usage(input_tokens=2000, output_tokens=1000))
        assert ct.total_cost == pytest.approx(0.0225)

        ct.set_limit(0.01)
        # Subsequent call should raise (total 0.0225 > limit 0.01)
        with pytest.raises(CostLimitExceeded):
            ct.record_call("gpt-4o", self._usage(input_tokens=100, output_tokens=50))

    # ------------------------------------------------------------------
    # 20. CostLimitExceeded message
    # ------------------------------------------------------------------
    def test_cost_limit_exceeded_message(self):
        """Exception string representation includes limit, total_cost, and symbol."""
        from src.decision.cost_tracker import CostLimitExceeded

        exc1 = CostLimitExceeded(limit=0.05, total_cost=0.075)
        msg1 = str(exc1)
        assert "0.05" in msg1
        assert "0.075" in msg1

        exc2 = CostLimitExceeded(limit=0.05, total_cost=0.075, symbol="EURUSD")
        msg2 = str(exc2)
        assert "0.05" in msg2
        assert "0.075" in msg2
        assert "EURUSD" in msg2

    # ------------------------------------------------------------------
    # 21. set_symbol stores symbol
    # ------------------------------------------------------------------
    def test_set_symbol_stores_symbol(self):
        """set_symbol('XAUUSD') stores symbol internally."""
        ct = CostTracker(pricing=self._PRICING)
        ct.set_symbol("XAUUSD")
        assert ct._symbol == "XAUUSD"  # type: ignore[attr-defined]

    # ------------------------------------------------------------------
    # 22. record_call raises with symbol
    # ------------------------------------------------------------------
    def test_record_call_raises_with_symbol(self):
        """record_call raises CostLimitExceeded with symbol in message."""
        from src.decision.cost_tracker import CostLimitExceeded

        ct = CostTracker(pricing=self._PRICING)
        ct.set_limit(0.01)
        ct.set_symbol("XAUUSD")
        ct.record_call("gpt-4o", self._usage(input_tokens=1000, output_tokens=500))
        with pytest.raises(CostLimitExceeded) as exc_info:
            ct.record_call("gpt-4o", self._usage(input_tokens=1000, output_tokens=500))
        assert "XAUUSD" in str(exc_info.value)

    # ------------------------------------------------------------------
    # 23. record_call raises without symbol
    # ------------------------------------------------------------------
    def test_record_call_raises_without_symbol(self):
        """record_call raises without symbol when not set."""
        from src.decision.cost_tracker import CostLimitExceeded

        ct = CostTracker(pricing=self._PRICING)
        ct.set_limit(0.01)
        ct.record_call("gpt-4o", self._usage(input_tokens=1000, output_tokens=500))
        with pytest.raises(CostLimitExceeded) as exc_info:
            ct.record_call("gpt-4o", self._usage(input_tokens=1000, output_tokens=500))
        assert "for " not in str(exc_info.value)

    # ------------------------------------------------------------------
    # 24. set_limit(None) disables enforcement
    # ------------------------------------------------------------------
    def test_set_limit_none_disables_enforcement(self):
        """set_limit(None) disables enforcement."""
        ct = CostTracker(pricing=self._PRICING)
        ct.set_limit(None)
        for _ in range(10):
            ct.record_call("gpt-4o", self._usage(input_tokens=1000, output_tokens=500))
        assert ct.total_cost == pytest.approx(0.075)

    # ------------------------------------------------------------------
    # 25. set_symbol overwrites
    # ------------------------------------------------------------------
    def test_set_symbol_cleared_by_set_symbol(self):
        """set_symbol('B') after set_symbol('A') overwrites symbol."""
        ct = CostTracker(pricing=self._PRICING)
        ct.set_symbol("XAUUSD")
        assert ct._symbol == "XAUUSD"  # type: ignore[attr-defined]
        ct.set_symbol("EURUSD")
        assert ct._symbol == "EURUSD"  # type: ignore[attr-defined]
        assert ct._symbol != "XAUUSD"  # type: ignore[attr-defined]

    # ------------------------------------------------------------------
    # 26. record_call with cached tokens — correct cost split
    # ------------------------------------------------------------------
    def test_cached_tokens_cost(self):
        """Cached input tokens are priced at cached_input_per_million."""
        ct = CostTracker(pricing=self._PRICING)
        usage = self._usage(
            input_tokens=1000,
            output_tokens=500,
            cached_input_tokens=300,
        )
        enriched = ct.record_call("gpt-4o", usage)
        # uncached: 700 * 2.50 / 1_000_000 = 0.00175
        assert enriched.input_cost == pytest.approx(0.00175)
        # cached: 300 * 1.25 / 1_000_000 = 0.000375
        assert enriched.cached_input_cost == pytest.approx(0.000375)
        # output: 500 * 10.00 / 1_000_000 = 0.005
        assert enriched.output_cost == pytest.approx(0.005)
        # total: 0.00175 + 0.000375 + 0.005 = 0.007125
        assert enriched.total_cost == pytest.approx(0.007125)

    # ------------------------------------------------------------------
    # 27. Default pricing fallback when no pricing given
    # ------------------------------------------------------------------
    def test_default_no_pricing(self):
        """CostTracker() with no args uses empty pricing → zero costs."""
        ct = CostTracker()  # no pricing → {}
        usage = self._usage(input_tokens=1000, output_tokens=500)
        enriched = ct.record_call("gpt-4o", usage)
        assert enriched.total_cost == 0.0
        assert ct.total_cost == 0.0
        assert ct.call_count == 1
