"""Tests for API key passthrough in agents."""

from unittest.mock import MagicMock, patch


class TestAgentApiKey:
    def test_synthesizer_passes_api_key_to_client(self):
        """SynthesizerAgent must pass api_key to OpenAI constructor."""
        from src.decision.agents import SynthesizerAgent

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            mock_from.return_value = mock_client
            agent = SynthesizerAgent(api_key="test-key-123")
            # Verify OpenAI was called with api_key kwarg
            call_args = mock_from.call_args
            openai_client = call_args[0][0]
            assert openai_client.api_key == "test-key-123"

    def test_decider_passes_api_key_to_client(self):
        """DeciderAgent must pass api_key to OpenAI constructor."""
        from src.decision.agents import DeciderAgent

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            mock_from.return_value = mock_client
            agent = DeciderAgent(api_key="test-key-456")
            call_args = mock_from.call_args
            openai_client = call_args[0][0]
            assert openai_client.api_key == "test-key-456"

    def test_reviewer_passes_api_key_to_client(self):
        """ReviewerAgent must pass api_key to OpenAI constructor."""
        from src.decision.agents import ReviewerAgent

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            mock_from.return_value = mock_client
            agent = ReviewerAgent(api_key="test-key-789")
            call_args = mock_from.call_args
            openai_client = call_args[0][0]
            assert openai_client.api_key == "test-key-789"

    def test_agents_default_to_none_api_key(self):
        """When no api_key given, OpenAI() uses its own default."""
        from src.decision.agents import SynthesizerAgent

        with patch("src.decision.agents.instructor.from_openai") as mock_from, \
             patch("src.decision.agents.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_from.return_value = mock_client
            agent = SynthesizerAgent()  # No api_key
            mock_openai_cls.assert_called_once()
