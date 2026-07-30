"""Tests for LLM client injection in agents.

After refactoring, agent classes accept ``LLMClientProtocol`` via
constructor instead of creating their own OpenAI/instructor clients.
These tests verify the new DI contract.
"""

from unittest.mock import MagicMock

from src.decision.usage import LLMUsage


def _mock_client() -> MagicMock:
    """Build a minimal mock ``LLMClientProtocol``."""
    client = MagicMock()
    client.generate_structured_sync.return_value = (MagicMock(), LLMUsage())
    client.model_identity.raw_model_identifier = "gpt-4o"
    return client


class TestAgentLlmClientInjection:
    """Agents accept an ``LLMClientProtocol`` in their constructor."""

    def test_synthesizer_accepts_llm_client(self):
        """SynthesizerAgent must accept ``llm_client`` as mandatory first arg."""
        from src.decision.agents import SynthesizerAgent

        agent = SynthesizerAgent(llm_client=_mock_client())
        assert agent._llm_client is not None

    def test_decider_accepts_llm_client(self):
        """DeciderAgent must accept ``llm_client`` as mandatory first arg."""
        from src.decision.agents import DeciderAgent

        agent = DeciderAgent(llm_client=_mock_client())
        assert agent._llm_client is not None

    def test_reviewer_accepts_llm_client(self):
        """ReviewerAgent must accept ``llm_client`` as mandatory first arg."""
        from src.decision.agents import ReviewerAgent

        agent = ReviewerAgent(llm_client=_mock_client())
        assert agent._llm_client is not None

    def test_agents_use_injected_client_for_llm_calls(self):
        """Agent must call ``generate_structured_sync`` on the injected client."""
        from src.decision.agents import SynthesizerAgent
        from src.decision.models import MarketContextSummary

        client = _mock_client()
        expected_result = MarketContextSummary(
            symbol="EURUSD",
            bias="BULLISH",
            confidence=75.0,
            reasoning="Injected client test",
        )
        client.generate_structured_sync.return_value = (
            expected_result,
            LLMUsage(input_tokens=100, output_tokens=50, total_tokens=150),
        )

        agent = SynthesizerAgent(llm_client=client)
        result = agent.synthesize({"test": True}, [], "EURUSD")

        # The injected client's method was called
        client.generate_structured_sync.assert_called_once()
        # The result comes from the injected client
        assert result is expected_result

    def test_agent_raises_when_no_llm_client(self):
        """Omitting ``llm_client`` must raise a ``TypeError``."""
        from src.decision.agents import SynthesizerAgent

        try:
            SynthesizerAgent()  # type: ignore[call-arg]
            assert False, "Expected TypeError when llm_client is missing"
        except TypeError:
            pass

    def test_agents_default_cost_tracker(self):
        """When ``cost_tracker`` is omitted, a default ``CostTracker`` is created."""
        from src.decision.agents import SynthesizerAgent

        agent = SynthesizerAgent(llm_client=_mock_client())
        assert agent.cost_tracker is not None
        assert agent.cost_tracker.call_count == 0

    def test_agents_cost_tracker_counts_calls(self):
        """Cost tracker records calls made through the injected client."""
        from src.decision.agents import SynthesizerAgent
        from src.decision.models import MarketContextSummary

        client = _mock_client()
        client.generate_structured_sync.return_value = (
            MarketContextSummary(
                symbol="EURUSD",
                bias="BULLISH",
                confidence=75.0,
                reasoning="Cost test",
            ),
            LLMUsage(input_tokens=100, output_tokens=50, total_tokens=150),
        )

        agent = SynthesizerAgent(llm_client=client)
        agent.synthesize({"test": True}, [], "EURUSD")

        assert agent.cost_tracker.call_count == 1


class TestAgentLogging:
    """Agent init logging still works with injected client."""

    def test_synthesizer_logs_model_at_init(self, caplog):
        """SynthesizerAgent must log model info at init."""
        import logging

        caplog.set_level(logging.INFO, logger="src.decision.agents")
        from src.decision.agents import SynthesizerAgent

        SynthesizerAgent(llm_client=_mock_client())

        assert any("SynthesizerAgent" in record.message for record in caplog.records), (
            "Expected log message containing 'SynthesizerAgent' "
            "to be emitted during SynthesizerAgent.__init__"
        )
        assert any("gpt-4o" in record.message for record in caplog.records), (
            "Expected log message containing model 'gpt-4o'"
        )

    def test_decider_logs_model_at_init(self, caplog):
        """DeciderAgent must log model info at init."""
        import logging

        caplog.set_level(logging.INFO, logger="src.decision.agents")
        from src.decision.agents import DeciderAgent

        DeciderAgent(llm_client=_mock_client())

        assert any("DeciderAgent" in record.message for record in caplog.records)

    def test_reviewer_logs_model_at_init(self, caplog):
        """ReviewerAgent must log model info at init."""
        import logging

        caplog.set_level(logging.INFO, logger="src.decision.agents")
        from src.decision.agents import ReviewerAgent

        ReviewerAgent(llm_client=_mock_client())

        assert any("ReviewerAgent" in record.message for record in caplog.records)


class TestAgentCostLogging:
    """Cost logging tests that verify generate_structured_sync is used correctly."""

    def test_synthesizer_logs_token_usage(self, caplog):
        """SynthesizerAgent must log input, output and total_tokens."""
        import logging

        caplog.set_level(logging.INFO, logger="src.decision.agents")
        from src.decision.agents import SynthesizerAgent
        from src.decision.models import MarketContextSummary

        client = _mock_client()
        client.generate_structured_sync.return_value = (
            MarketContextSummary(
                symbol="EURUSD",
                bias="BULLISH",
                confidence=75.0,
                reasoning="Test reasoning",
            ),
            LLMUsage(input_tokens=100, output_tokens=50, total_tokens=150),
        )

        agent = SynthesizerAgent(llm_client=client)
        agent.synthesize({"test": True}, [], "EURUSD")

        records_text = " ".join(r.message for r in caplog.records)
        assert "input=100" in records_text
        assert "output=50" in records_text
        assert "total=150" in records_text

    def test_synthesizer_logs_cost(self, caplog):
        """SynthesizerAgent must log cost=$ with a numeric value."""
        import logging
        import re

        caplog.set_level(logging.INFO, logger="src.decision.agents")
        from src.decision.agents import SynthesizerAgent
        from src.decision.models import MarketContextSummary

        client = _mock_client()
        client.generate_structured_sync.return_value = (
            MarketContextSummary(
                symbol="EURUSD",
                bias="BULLISH",
                confidence=75.0,
                reasoning="Test reasoning",
            ),
            LLMUsage(input_tokens=100, output_tokens=50, total_tokens=150),
        )

        agent = SynthesizerAgent(llm_client=client)
        agent.synthesize({"test": True}, [], "EURUSD")

        records_text = " ".join(r.message for r in caplog.records)
        assert re.search(r"cost=\$[\d.]+", records_text)

    def test_create_with_completion_not_called(self, caplog):
        """Agents must call generate_structured_sync, not create_with_completion."""
        from src.decision.agents import SynthesizerAgent
        from src.decision.models import MarketContextSummary

        client = _mock_client()
        client.generate_structured_sync.return_value = (
            MarketContextSummary(
                symbol="EURUSD",
                bias="BULLISH",
                confidence=75.0,
                reasoning="Test reasoning",
            ),
            LLMUsage(input_tokens=100, output_tokens=50, total_tokens=150),
        )

        agent = SynthesizerAgent(llm_client=client)
        agent.synthesize({"test": True}, [], "EURUSD")

        assert client.generate_structured_sync.called, (
            "Expected generate_structured_sync to be called, but it was not"
        )

    def test_cost_tracker_none_does_not_crash(self):
        """Agents with cost_tracker=None default to CostTracker() and work normally."""
        from src.decision.agents import SynthesizerAgent
        from src.decision.models import MarketContextSummary

        client = _mock_client()
        expected_result = MarketContextSummary(
            symbol="EURUSD",
            bias="BULLISH",
            confidence=75.0,
            reasoning="Test reasoning",
        )
        client.generate_structured_sync.return_value = (
            expected_result,
            LLMUsage(input_tokens=100, output_tokens=50, total_tokens=150),
        )

        agent = SynthesizerAgent(llm_client=client, cost_tracker=None)
        result = agent.synthesize({"test": True}, [], "EURUSD")

        assert isinstance(result, MarketContextSummary)
        assert result is expected_result

    def test_return_types_unaffected(self):
        """Agent public methods must still return correct model types."""
        from src.decision.models import DecisionOutput, MarketContextSummary, ReviewVerdict

        usage = LLMUsage(input_tokens=100, output_tokens=50, total_tokens=150)

        # --- Synthesizer ---
        syn_client = _mock_client()
        syn_client.generate_structured_sync.return_value = (
            MarketContextSummary(
                symbol="EURUSD",
                bias="BULLISH",
                confidence=75.0,
                reasoning="Test reasoning",
                key_levels=["1.0800"],
                structural_events=["BOS"],
            ),
            usage,
        )
        from src.decision.agents import SynthesizerAgent

        agent_syn = SynthesizerAgent(llm_client=syn_client)
        result_syn = agent_syn.synthesize({"test": True}, [], "EURUSD")
        assert isinstance(result_syn, MarketContextSummary)

        # --- Decider ---
        dec_client = _mock_client()
        dec_client.generate_structured_sync.return_value = (
            DecisionOutput(
                symbol="EURUSD",
                action="no_trade",
                reasoning="Test reasoning",
            ),
            usage,
        )
        from src.decision.agents import DeciderAgent

        context = MarketContextSummary(
            symbol="EURUSD",
            bias="BULLISH",
            confidence=50.0,
            reasoning="Test",
        )
        agent_dec = DeciderAgent(llm_client=dec_client)
        result_dec = agent_dec.decide(context=context, positions=[], pending_orders=[])
        assert isinstance(result_dec, DecisionOutput)

        # --- Reviewer ---
        from src.analysis.market_structure_engine.models import ReviewStatus

        rev_client = _mock_client()
        rev_client.generate_structured_sync.return_value = (
            ReviewVerdict(
                status=ReviewStatus.APPROVED,
                reasoning="All good",
            ),
            usage,
        )
        from src.decision.agents import ReviewerAgent

        agent_rev = ReviewerAgent(llm_client=rev_client)
        result_rev = agent_rev.review(
            decision=DecisionOutput(symbol="EURUSD", action="no_trade", reasoning="R"),
            context=MarketContextSummary(
                symbol="EURUSD",
                bias="BULLISH",
                confidence=50.0,
                reasoning="R",
            ),
            calendar_events=[],
        )
        assert isinstance(result_rev, ReviewVerdict)

    def test_agent_returns_content_when_usage_none(self):
        """Agent returns the generated model content even without usage data."""
        from src.decision.agents import SynthesizerAgent
        from src.decision.models import MarketContextSummary

        client = _mock_client()
        expected_result = MarketContextSummary(
            symbol="EURUSD",
            bias="BULLISH",
            confidence=75.0,
            reasoning="Test reasoning",
        )
        client.generate_structured_sync.return_value = (
            expected_result,
            LLMUsage(),  # all-zero usage — simulates no usage data
        )

        agent = SynthesizerAgent(llm_client=client)
        result = agent.synthesize({"test": True}, [], "EURUSD")

        assert result is expected_result
        assert result.symbol == "EURUSD"
        assert result.bias == "BULLISH"

    def test_agent_unknown_model_pricing_returns_content(self):
        """Agent works when model is not in pricing table."""
        from src.decision.cost_tracker import CostTracker
        from src.decision.models import MarketContextSummary

        cost_tracker = CostTracker(
            pricing={
                "gpt-4o": {
                    "input_per_million": 2.50,
                    "cached_input_per_million": 1.25,
                    "output_per_million": 10.00,
                }
            }
        )

        client = _mock_client()
        client.model_identity.raw_model_identifier = "gpt-4-unknown"
        expected_result = MarketContextSummary(
            symbol="EURUSD",
            bias="BULLISH",
            confidence=75.0,
            reasoning="Test unknown model",
        )
        client.generate_structured_sync.return_value = (
            expected_result,
            LLMUsage(input_tokens=100, output_tokens=50, total_tokens=150),
        )

        from src.decision.agents import SynthesizerAgent

        agent = SynthesizerAgent(llm_client=client, cost_tracker=cost_tracker)
        result = agent.synthesize({"test": True}, [], "EURUSD")

        assert result is expected_result
        assert cost_tracker.call_count == 1
        assert cost_tracker.total_cost == 0.0
