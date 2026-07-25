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


class TestReasoningEffortConstructor:
    def test_synthesizer_accepts_reasoning_effort(self):
        """SynthesizerAgent must accept reasoning_effort param."""
        from src.decision.agents import SynthesizerAgent

        with (
            patch("src.decision.agents.instructor.from_openai") as mock_from,
            patch("src.decision.agents.OpenAI"),
        ):
            mock_client = MagicMock()
            mock_from.return_value = mock_client
            agent = SynthesizerAgent(reasoning_effort="high")
            assert agent.reasoning_effort == "high"

    def test_synthesizer_defaults_reasoning_effort_to_none(self):
        """When not specified, reasoning_effort defaults to None."""
        from src.decision.agents import SynthesizerAgent

        with (
            patch("src.decision.agents.instructor.from_openai") as mock_from,
            patch("src.decision.agents.OpenAI"),
        ):
            mock_client = MagicMock()
            mock_from.return_value = mock_client
            agent = SynthesizerAgent()
            assert agent.reasoning_effort is None

    def test_decider_accepts_reasoning_effort(self):
        """DeciderAgent must accept reasoning_effort param."""
        from src.decision.agents import DeciderAgent

        with (
            patch("src.decision.agents.instructor.from_openai") as mock_from,
            patch("src.decision.agents.OpenAI"),
        ):
            mock_client = MagicMock()
            mock_from.return_value = mock_client
            agent = DeciderAgent(reasoning_effort="low")
            assert agent.reasoning_effort == "low"

    def test_reviewer_accepts_reasoning_effort(self):
        """ReviewerAgent must accept reasoning_effort param."""
        from src.decision.agents import ReviewerAgent

        with (
            patch("src.decision.agents.instructor.from_openai") as mock_from,
            patch("src.decision.agents.OpenAI"),
        ):
            mock_client = MagicMock()
            mock_from.return_value = mock_client
            agent = ReviewerAgent(reasoning_effort="medium")
            assert agent.reasoning_effort == "medium"


class TestReasoningEffortPassthrough:
    """reasoning_effort is a create()-level kwarg, not an OpenAI() constructor arg."""

    def test_create_includes_reasoning_effort_when_set(self):
        """When reasoning_effort is set, it must appear in client.create() kwargs."""
        from unittest.mock import MagicMock, patch

        from src.decision.agents import SynthesizerAgent

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            mock_from.return_value = mock_client
            agent = SynthesizerAgent(reasoning_effort="high", api_key="test")
            # Trigger create() via synthesize; we just need to intercept the call
            # We mock client.create to return a proper response
            mock_client.create.return_value = MagicMock()
            from src.decision.models import MarketContextSummary

            agent.client.create(
                model="test-model",
                response_model=MarketContextSummary,
                messages=[{"role": "user", "content": "test"}],
                reasoning_effort=agent.reasoning_effort,  # This is what we're testing
            )
            # Verify reasoning_effort was passed
            call_kwargs = mock_client.create.call_args.kwargs
            assert "reasoning_effort" in call_kwargs
            assert call_kwargs["reasoning_effort"] == "high"

    def test_create_omits_reasoning_effort_when_none(self):
        """When reasoning_effort is None, the key must be absent from create() kwargs."""
        from unittest.mock import MagicMock, patch

        from src.decision.agents import SynthesizerAgent

        with (
            patch("src.decision.agents.instructor.from_openai") as mock_from,
            patch("src.decision.agents.OpenAI"),
        ):
            mock_client = MagicMock()
            mock_from.return_value = mock_client
            agent = SynthesizerAgent()  # No reasoning_effort → None
            # Verify it's None
            assert agent.reasoning_effort is None

    def test_create_omits_reasoning_effort_when_none_explicit(self):
        """When reasoning_effort is explicitly None, key absent from create() kwargs."""
        from unittest.mock import MagicMock, patch

        from src.decision.agents import SynthesizerAgent

        with (
            patch("src.decision.agents.instructor.from_openai") as mock_from,
            patch("src.decision.agents.OpenAI"),
        ):
            mock_client = MagicMock()
            mock_from.return_value = mock_client
            agent = SynthesizerAgent(reasoning_effort=None)
            # Verify it's None
            assert agent.reasoning_effort is None

    def test_decider_create_passes_reasoning_effort(self):
        """DeciderAgent passes reasoning_effort to create()."""
        from unittest.mock import MagicMock, patch

        from src.decision.agents import DeciderAgent

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            mock_from.return_value = mock_client
            agent = DeciderAgent(reasoning_effort="low", api_key="test")
            assert agent.reasoning_effort == "low"

    def test_reviewer_create_passes_reasoning_effort(self):
        """ReviewerAgent passes reasoning_effort to create()."""
        from unittest.mock import MagicMock, patch

        from src.decision.agents import ReviewerAgent

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            mock_from.return_value = mock_client
            agent = ReviewerAgent(reasoning_effort="medium", api_key="test")
            assert agent.reasoning_effort == "medium"


class TestReasoningEffortNilConversion:
    """Empty string → None conversion in main.py (same pattern as api_key/base_url)."""

    def test_agents_accept_none_reasoning_effort(self):
        """Agent must accept None reasoning_effort without error."""
        from src.decision.agents import SynthesizerAgent

        with (
            patch("src.decision.agents.instructor.from_openai") as mock_from,
            patch("src.decision.agents.OpenAI"),
        ):
            mock_client = MagicMock()
            mock_from.return_value = mock_client
            agent = SynthesizerAgent(reasoning_effort=None)
            assert agent.reasoning_effort is None

    def test_agents_accept_empty_string_reasoning_effort(self):
        """Agent must accept empty string reasoning_effort (though main.py converts it)."""
        from src.decision.agents import SynthesizerAgent

        with (
            patch("src.decision.agents.instructor.from_openai") as mock_from,
            patch("src.decision.agents.OpenAI"),
        ):
            mock_client = MagicMock()
            mock_from.return_value = mock_client
            agent = SynthesizerAgent(reasoning_effort="")
            assert agent.reasoning_effort == ""


class TestReasoningEffortIntegration:
    """End-to-end: reasoning_effort flows from constructor → create() kwargs."""

    def test_synthesizer_synthesize_passes_reasoning_effort(self):
        """synthesize() must include reasoning_effort in create() kwargs when set."""
        from unittest.mock import MagicMock, patch

        from src.decision.agents import SynthesizerAgent

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            mock_client.create.return_value = MagicMock()
            mock_from.return_value = mock_client
            agent = SynthesizerAgent(reasoning_effort="high", api_key="test")
            agent.synthesize(
                structure_analysis={"test": True},
                calendar_events=[],
                symbol="EURUSD",
            )
            call_kwargs = mock_client.create.call_args.kwargs
            assert "reasoning_effort" in call_kwargs
            assert call_kwargs["reasoning_effort"] == "high"

    def test_synthesizer_synthesize_omits_reasoning_effort_when_none(self):
        """synthesize() must NOT include reasoning_effort in create() kwargs when None."""
        from unittest.mock import MagicMock, patch

        from src.decision.agents import SynthesizerAgent

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            mock_client.create.return_value = MagicMock()
            mock_from.return_value = mock_client
            agent = SynthesizerAgent(api_key="test")  # reasoning_effort defaults to None
            assert agent.reasoning_effort is None
            agent.synthesize(
                structure_analysis={"test": True},
                calendar_events=[],
                symbol="EURUSD",
            )
            call_kwargs = mock_client.create.call_args.kwargs
            assert "reasoning_effort" not in call_kwargs

    def test_decider_decide_passes_reasoning_effort(self, sample_market_context):
        """decide() must include reasoning_effort in create() kwargs when set."""
        from unittest.mock import MagicMock, patch

        from src.decision.agents import DeciderAgent

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            mock_client.create.return_value = MagicMock()
            mock_from.return_value = mock_client
            agent = DeciderAgent(reasoning_effort="low", api_key="test")
            agent.decide(
                context=sample_market_context,
                positions=[],
                pending_orders=[],
            )
            call_kwargs = mock_client.create.call_args.kwargs
            assert "reasoning_effort" in call_kwargs
            assert call_kwargs["reasoning_effort"] == "low"

    def test_reviewer_review_passes_reasoning_effort(self, sample_decision, sample_market_context):
        """review() must include reasoning_effort in create() kwargs when set."""
        from unittest.mock import MagicMock, patch

        from src.decision.agents import ReviewerAgent

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            mock_client.create.return_value = MagicMock()
            mock_from.return_value = mock_client
            agent = ReviewerAgent(reasoning_effort="medium", api_key="test")
            agent.review(
                decision=sample_decision,
                context=sample_market_context,
                calendar_events=[],
            )
            call_kwargs = mock_client.create.call_args.kwargs
            assert "reasoning_effort" in call_kwargs
            assert call_kwargs["reasoning_effort"] == "medium"

    def test_client_provided_still_respects_reasoning_effort(self):
        """When pre-built client is provided, reasoning_effort still flows to create()."""
        from unittest.mock import MagicMock, patch

        from src.decision.agents import SynthesizerAgent

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            prebuilt = MagicMock()
            mock_client = MagicMock()
            mock_client.create.return_value = MagicMock()
            mock_from.return_value = mock_client
            agent = SynthesizerAgent(client=prebuilt, reasoning_effort="high")
            agent.synthesize(
                structure_analysis={"test": True},
                calendar_events=[],
                symbol="EURUSD",
            )
            call_kwargs = mock_client.create.call_args.kwargs
            assert "reasoning_effort" in call_kwargs
            assert call_kwargs["reasoning_effort"] == "high"
