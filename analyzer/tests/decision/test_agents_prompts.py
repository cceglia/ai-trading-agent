"""Tests for prompt usage in agents."""

from unittest.mock import MagicMock

from src.analysis.market_structure_engine.models import ReviewStatus
from src.decision.models import (
    BiasLevel,
    DecisionAction,
    DecisionOutput,
    MarketContextSummary,
    ReviewVerdict,
)
from src.decision.usage import LLMUsage


def _make_mock_client() -> MagicMock:
    """Build a mock ``LLMClientProtocol`` that returns a valid usage tuple."""
    client = MagicMock()
    usage = LLMUsage(input_tokens=100, output_tokens=50, total_tokens=150)
    client.generate_structured_sync.return_value = (MagicMock(), usage)
    client.model_identity.raw_model_identifier = "gpt-4o"
    return client


class TestAgentPrompts:
    def test_synthesizer_uses_detailed_prompt(self):
        """SynthesizerAgent must use SYNTHESIZER_SYSTEM_PROMPT from prompts.py."""
        from src.decision.agents import SynthesizerAgent

        mock_client = _make_mock_client()
        mock_client.generate_structured_sync.return_value = (
            MarketContextSummary(
                symbol="EURUSD", bias=BiasLevel.BULLISH, confidence=75.0, reasoning="test"
            ),
            LLMUsage(input_tokens=100, output_tokens=50, total_tokens=150),
        )
        agent = SynthesizerAgent(llm_client=mock_client)
        agent.synthesize({}, [], "EURUSD")

        call_kwargs = mock_client.generate_structured_sync.call_args
        messages = call_kwargs[1]["messages"]
        system_msg = messages[0]["content"]

        # Must contain evidence hierarchy from prompts.py
        assert "Evidence Hierarchy" in system_msg
        assert "Non-negotiable Rules" in system_msg

    def test_decider_uses_detailed_prompt(self):
        """DeciderAgent must use DECIDER_SYSTEM_PROMPT from prompts.py."""
        from src.decision.agents import DeciderAgent

        mock_client = _make_mock_client()
        mock_client.generate_structured_sync.return_value = (
            DecisionOutput(
                symbol="EURUSD",
                action=DecisionAction.NO_TRADE,
                reasoning="test",
            ),
            LLMUsage(input_tokens=100, output_tokens=50, total_tokens=150),
        )
        agent = DeciderAgent(llm_client=mock_client)
        context = MarketContextSummary(
            symbol="EURUSD", bias=BiasLevel.BULLISH, confidence=75.0, reasoning="test"
        )
        agent.decide(context, [], [])

        call_kwargs = mock_client.generate_structured_sync.call_args
        messages = call_kwargs[1]["messages"]
        system_msg = messages[0]["content"]

        assert "advisory only" in system_msg.lower()
        assert "2:1" in system_msg

    def test_reviewer_uses_detailed_prompt(self):
        """ReviewerAgent must use REVIEWER_SYSTEM_PROMPT from prompts.py."""
        from src.decision.agents import ReviewerAgent

        mock_client = _make_mock_client()
        mock_client.generate_structured_sync.return_value = (
            ReviewVerdict(status=ReviewStatus.APPROVED, reasoning="test"),
            LLMUsage(input_tokens=100, output_tokens=50, total_tokens=150),
        )
        agent = ReviewerAgent(llm_client=mock_client)
        context = MarketContextSummary(
            symbol="EURUSD", bias=BiasLevel.BULLISH, confidence=75.0, reasoning="test"
        )
        decision = DecisionOutput(
            symbol="EURUSD",
            action=DecisionAction.NO_TRADE,
            reasoning="test",
        )
        agent.review(decision, context, [])

        call_kwargs = mock_client.generate_structured_sync.call_args
        messages = call_kwargs[1]["messages"]
        system_msg = messages[0]["content"]

        assert "Risk Management" in system_msg
        assert "Higher-Timeframe" in system_msg

    def test_synthesizer_accepts_current_price_kwargs(self):
        """SynthesizerAgent.synthesize must accept current_price/current_price_time kwargs."""
        from src.decision.agents import SynthesizerAgent

        mock_client = _make_mock_client()
        mock_client.generate_structured_sync.return_value = (
            MarketContextSummary(
                symbol="EURUSD", bias=BiasLevel.BULLISH, confidence=75.0, reasoning="test"
            ),
            LLMUsage(input_tokens=100, output_tokens=50, total_tokens=150),
        )
        agent = SynthesizerAgent(llm_client=mock_client)

        # Must not raise TypeError; must return a MarketContextSummary
        result = agent.synthesize(
            {},
            [],
            "EURUSD",
            current_price=1.0875,
            current_price_time="2024-01-03T00:00:00",
        )

        assert isinstance(result, MarketContextSummary)

    def test_synthesizer_user_message_contains_current_price(self):
        """User prompt must render current_price and current_price_time values."""
        from src.decision.agents import SynthesizerAgent

        mock_client = _make_mock_client()
        mock_client.generate_structured_sync.return_value = (
            MarketContextSummary(
                symbol="EURUSD", bias=BiasLevel.BULLISH, confidence=75.0, reasoning="test"
            ),
            LLMUsage(input_tokens=100, output_tokens=50, total_tokens=150),
        )
        agent = SynthesizerAgent(llm_client=mock_client)
        agent.synthesize(
            {},
            [],
            "EURUSD",
            current_price=1.0875,
            current_price_time="2024-01-03T00:00:00",
        )

        messages = mock_client.generate_structured_sync.call_args[1]["messages"]
        user_msg = messages[1]["content"]

        assert "1.0875" in user_msg
        assert "2024-01-03T00:00:00" in user_msg
        assert "current price" in user_msg.lower()

    def test_synthesizer_user_message_states_none_when_missing(self):
        """When no price is supplied, the current-price line must state None."""
        from src.decision.agents import SynthesizerAgent

        mock_client = _make_mock_client()
        mock_client.generate_structured_sync.return_value = (
            MarketContextSummary(
                symbol="EURUSD", bias=BiasLevel.BULLISH, confidence=75.0, reasoning="test"
            ),
            LLMUsage(input_tokens=100, output_tokens=50, total_tokens=150),
        )
        agent = SynthesizerAgent(llm_client=mock_client)
        agent.synthesize({}, [], "EURUSD")

        messages = mock_client.generate_structured_sync.call_args[1]["messages"]
        user_msg = messages[1]["content"]

        # The current-price line must mention None when price is absent
        assert "current price" in user_msg.lower()
        assert "None" in user_msg

    def test_synthesizer_existing_positional_call_still_works(self):
        """SynthesizerAgent.synthesize must accept current_price/current_price_time kwargs."""
        from src.decision.agents import SynthesizerAgent

        mock_client = _make_mock_client()
        mock_client.generate_structured_sync.return_value = (
            MarketContextSummary(
                symbol="EURUSD", bias=BiasLevel.BULLISH, confidence=75.0, reasoning="test"
            ),
            LLMUsage(input_tokens=100, output_tokens=50, total_tokens=150),
        )
        agent = SynthesizerAgent(llm_client=mock_client)

        # Must not raise
        result = agent.synthesize({}, [], "EURUSD")

        assert isinstance(result, MarketContextSummary)

    def test_decider_accepts_current_price_kwarg(self):
        """DeciderAgent.decide must accept a current_price keyword argument."""
        from src.decision.agents import DeciderAgent

        mock_client = _make_mock_client()
        mock_client.generate_structured_sync.return_value = (
            DecisionOutput(
                symbol="EURUSD",
                action=DecisionAction.NO_TRADE,
                reasoning="test",
            ),
            LLMUsage(input_tokens=100, output_tokens=50, total_tokens=150),
        )
        agent = DeciderAgent(llm_client=mock_client)
        context = MarketContextSummary(
            symbol="EURUSD", bias=BiasLevel.BULLISH, confidence=75.0, reasoning="test"
        )

        # Must not raise TypeError; must return a DecisionOutput
        result = agent.decide(context, [], [], current_price=1.0875)

        assert isinstance(result, DecisionOutput)

    def test_decider_user_message_contains_current_price_anchor(self):
        """DeciderAgent user prompt must render the current_price anchor value."""
        from src.decision.agents import DeciderAgent

        mock_client = _make_mock_client()
        mock_client.generate_structured_sync.return_value = (
            DecisionOutput(
                symbol="EURUSD",
                action=DecisionAction.NO_TRADE,
                reasoning="test",
            ),
            LLMUsage(input_tokens=100, output_tokens=50, total_tokens=150),
        )
        agent = DeciderAgent(llm_client=mock_client)
        context = MarketContextSummary(
            symbol="EURUSD", bias=BiasLevel.BULLISH, confidence=75.0, reasoning="test"
        )
        agent.decide(context, [], [], current_price=1.0875)

        messages = mock_client.generate_structured_sync.call_args[1]["messages"]
        user_msg = messages[1]["content"]

        assert "current_price" in user_msg
        assert "1.0875" in user_msg

    def test_decider_existing_positional_call_still_works(self):
        """Regression guard: positional decide(context, [], []) must not raise."""
        from src.decision.agents import DeciderAgent

        mock_client = _make_mock_client()
        mock_client.generate_structured_sync.return_value = (
            DecisionOutput(
                symbol="EURUSD",
                action=DecisionAction.NO_TRADE,
                reasoning="test",
            ),
            LLMUsage(input_tokens=100, output_tokens=50, total_tokens=150),
        )
        agent = DeciderAgent(llm_client=mock_client)
        context = MarketContextSummary(
            symbol="EURUSD", bias=BiasLevel.BULLISH, confidence=75.0, reasoning="test"
        )

        # Must not raise
        result = agent.decide(context, [], [])

        assert isinstance(result, DecisionOutput)
