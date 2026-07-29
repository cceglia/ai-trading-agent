"""Tests for agent cost-logging helper extraction."""

import logging

import pytest

from src.decision.agents import _log_llm_call
from src.decision.cost_tracker import CostTracker
from src.decision.usage import LLMUsage


class TestLogLlmCall:
    """_log_llm_call extracts duplicated cost-logging from agents."""

    # New format: dollars-per-million tokens
    _PRICING = {
        "gpt-4o": {
            "input_per_million": 2.50,
            "cached_input_per_million": 1.25,
            "output_per_million": 10.00,
        },
    }

    def test_logs_cost_with_usage(self, caplog):
        """When usage is provided, logs cost details."""
        ct = CostTracker(pricing=self._PRICING)
        caplog.set_level(logging.INFO)

        usage = LLMUsage(
            input_tokens=1000,
            cached_input_tokens=0,
            uncached_input_tokens=1000,
            output_tokens=500,
            total_tokens=1500,
        )

        enriched = _log_llm_call("SynthesizerAgent", "gpt-4o", usage, ct)

        # cost = 1000 * 2.50 / 1_000_000 + 0 + 500 * 10.00 / 1_000_000
        #       = 0.0025 + 0.005 = 0.0075
        assert enriched.total_cost == pytest.approx(0.0075)
        assert "LLM call: agent=SynthesizerAgent" in caplog.text
        assert "gpt-4o" in caplog.text
        assert "input=1000" in caplog.text
        assert "output=500" in caplog.text

    def test_logs_no_usage(self, caplog):
        """When usage is all-zero (no usage data), logs zero cost."""
        ct = CostTracker(pricing=self._PRICING)
        caplog.set_level(logging.INFO)

        usage = LLMUsage()  # all zeroes — simulates no usage data

        enriched = _log_llm_call("DeciderAgent", "gpt-4o", usage, ct)

        assert enriched.total_cost == 0.0
        assert "cost=$0.000000" in caplog.text

    def test_records_call_on_tracker(self):
        """Records the call on the cost tracker when usage is provided."""
        ct = CostTracker(pricing=self._PRICING)

        usage = LLMUsage(
            input_tokens=1000,
            cached_input_tokens=0,
            uncached_input_tokens=1000,
            output_tokens=500,
            total_tokens=1500,
        )

        _log_llm_call("ReviewerAgent", "gpt-4o", usage, ct)

        assert ct.call_count == 1
        assert ct.total_cost == pytest.approx(0.0075)
