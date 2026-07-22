"""Tests for prompt usage in agents."""

from unittest.mock import MagicMock, patch

from src.decision.models import (
    BiasLevel,
    DecisionAction,
    DecisionOutput,
    MarketContextSummary,
    ReviewVerdict,
)


class TestAgentPrompts:
    def test_synthesizer_uses_detailed_prompt(self):
        """SynthesizerAgent must use SYNTHESIZER_SYSTEM_PROMPT from prompts.py."""
        from src.decision.agents import SynthesizerAgent

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            mock_from.return_value = mock_client
            mock_client.create.return_value = MarketContextSummary(
                symbol="EURUSD", bias=BiasLevel.BULLISH, confidence=75.0, reasoning="test"
            )
            agent = SynthesizerAgent(api_key="test")
            agent.synthesize({}, [], "EURUSD")

            # Extract the messages sent
            call_kwargs = mock_client.create.call_args
            messages = call_kwargs[1]["messages"]
            system_msg = messages[0]["content"]

            # Must contain evidence hierarchy from prompts.py
            assert "Evidence Hierarchy" in system_msg
            assert "Non-negotiable Rules" in system_msg

    def test_decider_uses_detailed_prompt(self):
        """DeciderAgent must use DECIDER_SYSTEM_PROMPT from prompts.py."""
        from src.decision.agents import DeciderAgent

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            mock_from.return_value = mock_client
            mock_client.create.return_value = DecisionOutput(
                symbol="EURUSD",
                action=DecisionAction.NO_TRADE,
                reasoning="test",
                entry_authorized=False,
            )
            agent = DeciderAgent(api_key="test")
            context = MarketContextSummary(
                symbol="EURUSD", bias=BiasLevel.BULLISH, confidence=75.0, reasoning="test"
            )
            agent.decide(context, [], [])

            call_kwargs = mock_client.create.call_args
            messages = call_kwargs[1]["messages"]
            system_msg = messages[0]["content"]

            assert "advisory only" in system_msg.lower()
            assert "2:1" in system_msg

    def test_reviewer_uses_detailed_prompt(self):
        """ReviewerAgent must use REVIEWER_SYSTEM_PROMPT from prompts.py."""
        from src.decision.agents import ReviewerAgent

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            mock_from.return_value = mock_client
            mock_client.create.return_value = ReviewVerdict(approved=True, reasoning="test")
            agent = ReviewerAgent(api_key="test")
            context = MarketContextSummary(
                symbol="EURUSD", bias=BiasLevel.BULLISH, confidence=75.0, reasoning="test"
            )
            decision = DecisionOutput(
                symbol="EURUSD",
                action=DecisionAction.NO_TRADE,
                reasoning="test",
                entry_authorized=False,
            )
            agent.review(decision, context, [])

            call_kwargs = mock_client.create.call_args
            messages = call_kwargs[1]["messages"]
            system_msg = messages[0]["content"]

            assert "Risk Management" in system_msg
            assert "Higher-Timeframe" in system_msg
