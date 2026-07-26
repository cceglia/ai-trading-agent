"""Tests for agent cost-logging helper extraction."""

import logging
from unittest.mock import MagicMock

import pytest

from src.decision.agents import _log_llm_call
from src.decision.cost_tracker import CostTracker


class TestLogLlmCall:
    """_log_llm_call extracts duplicated cost-logging from agents."""

    _PRICING = {"gpt-4o": {"prompt": 0.0000025, "completion": 0.00001}}

    def test_logs_cost_with_usage(self, caplog):
        """When usage is provided, logs cost details."""
        ct = CostTracker(pricing=self._PRICING)
        caplog.set_level(logging.INFO)

        usage = MagicMock()
        usage.prompt_tokens = 1000
        usage.completion_tokens = 500
        usage.total_tokens = 1500

        cost = _log_llm_call("SynthesizerAgent", "gpt-4o", usage, ct)

        assert cost == pytest.approx(0.0075)
        assert "LLM call: agent=SynthesizerAgent" in caplog.text
        assert "gpt-4o" in caplog.text
        assert "prompt=1000" in caplog.text
        assert "completion=500" in caplog.text

    def test_logs_no_usage(self, caplog):
        """When usage is None, logs N/A."""
        ct = CostTracker(pricing=self._PRICING)
        caplog.set_level(logging.INFO)

        cost = _log_llm_call("DeciderAgent", "gpt-4o", None, ct)

        assert cost is None
        assert "tokens=N/A" in caplog.text

    def test_records_call_on_tracker(self):
        """Records the call on the cost tracker when usage is provided."""
        ct = CostTracker(pricing=self._PRICING)

        usage = MagicMock()
        usage.prompt_tokens = 1000
        usage.completion_tokens = 500
        usage.total_tokens = 1500

        _log_llm_call("ReviewerAgent", "gpt-4o", usage, ct)

        assert ct.call_count == 1
        assert ct.total_cost == pytest.approx(0.0075)
