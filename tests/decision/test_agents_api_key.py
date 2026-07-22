"""Tests for API key and base_url passthrough in agents."""

from unittest.mock import MagicMock, patch


class TestAgentApiKey:
    def test_synthesizer_passes_api_key_to_client(self):
        """SynthesizerAgent must pass api_key to OpenAI constructor."""
        from src.decision.agents import SynthesizerAgent

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            mock_from.return_value = mock_client
            SynthesizerAgent(api_key="test-key-123")
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
            DeciderAgent(api_key="test-key-456")
            call_args = mock_from.call_args
            openai_client = call_args[0][0]
            assert openai_client.api_key == "test-key-456"

    def test_reviewer_passes_api_key_to_client(self):
        """ReviewerAgent must pass api_key to OpenAI constructor."""
        from src.decision.agents import ReviewerAgent

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            mock_from.return_value = mock_client
            ReviewerAgent(api_key="test-key-789")
            call_args = mock_from.call_args
            openai_client = call_args[0][0]
            assert openai_client.api_key == "test-key-789"

    def test_agents_default_to_none_api_key(self):
        """When no api_key given, OpenAI() uses its own default."""
        from src.decision.agents import SynthesizerAgent

        with (
            patch("src.decision.agents.instructor.from_openai") as mock_from,
            patch("src.decision.agents.OpenAI") as mock_openai_cls,
        ):
            mock_client = MagicMock()
            mock_from.return_value = mock_client
            SynthesizerAgent()  # No api_key
            mock_openai_cls.assert_called_once()


class TestAgentBaseUrl:
    def test_synthesizer_passes_base_url_to_client(self):
        """SynthesizerAgent must pass base_url to OpenAI constructor."""
        from src.decision.agents import SynthesizerAgent

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            mock_from.return_value = mock_client
            SynthesizerAgent(base_url="http://localhost:8080/v1", api_key="test")
            client = mock_from.call_args[0][0]
            assert str(client.base_url) == "http://localhost:8080/v1/"

    def test_decider_passes_base_url_to_client(self):
        """DeciderAgent must pass base_url to OpenAI constructor."""
        from src.decision.agents import DeciderAgent

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            mock_from.return_value = mock_client
            DeciderAgent(base_url="http://localhost:8080/v1", api_key="test")
            client = mock_from.call_args[0][0]
            assert str(client.base_url) == "http://localhost:8080/v1/"

    def test_reviewer_passes_base_url_to_client(self):
        """ReviewerAgent must pass base_url to OpenAI constructor."""
        from src.decision.agents import ReviewerAgent

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            mock_from.return_value = mock_client
            ReviewerAgent(base_url="http://localhost:8080/v1", api_key="test")
            client = mock_from.call_args[0][0]
            assert str(client.base_url) == "http://localhost:8080/v1/"

    def test_agents_default_to_none_base_url(self):
        """When no base_url given, OpenAI() uses its own default."""
        from src.decision.agents import SynthesizerAgent

        with (
            patch("src.decision.agents.instructor.from_openai") as mock_from,
            patch("src.decision.agents.OpenAI") as mock_openai_cls,
        ):
            mock_client = MagicMock()
            mock_from.return_value = mock_client
            SynthesizerAgent()  # No base_url
            mock_openai_cls.assert_called_once()
            assert "base_url" not in mock_openai_cls.call_args.kwargs

    def test_base_url_ignored_when_client_provided(self):
        """When a pre-built client is provided, base_url must be ignored."""
        from src.decision.agents import SynthesizerAgent

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            prebuilt_client = MagicMock()
            mock_client = MagicMock()
            mock_from.return_value = mock_client
            SynthesizerAgent(client=prebuilt_client, base_url="http://localhost:8080/v1")
            assert mock_from.call_args[0][0] is prebuilt_client

    def test_base_url_and_api_key_together(self):
        """SynthesizerAgent must pass both api_key and base_url when provided."""
        from src.decision.agents import SynthesizerAgent

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            mock_from.return_value = mock_client
            SynthesizerAgent(api_key="key-123", base_url="http://localhost:8080/v1")
            client = mock_from.call_args[0][0]
            assert client.api_key == "key-123"
            assert str(client.base_url) == "http://localhost:8080/v1/"
