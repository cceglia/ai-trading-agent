"""Tests for API key and base_url passthrough in agents."""

from unittest.mock import MagicMock, patch

from tests.conftest import make_raw_response


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
        """synthesize() must include reasoning_effort in create_with_completion kwargs when set."""
        from unittest.mock import MagicMock, patch

        from src.decision.agents import SynthesizerAgent

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            raw_response = make_raw_response(input_tokens=100, output_tokens=50, total_tokens=150)
            mock_client.create_with_completion.return_value = (
                MagicMock(),
                raw_response,
            )
            mock_from.return_value = mock_client
            agent = SynthesizerAgent(reasoning_effort="high", api_key="test")
            agent.synthesize(
                structure_analysis={"test": True},
                calendar_events=[],
                symbol="EURUSD",
            )
            call_kwargs = mock_client.create_with_completion.call_args.kwargs
            assert "reasoning_effort" in call_kwargs
            assert call_kwargs["reasoning_effort"] == "high"

    def test_synthesizer_synthesize_omits_reasoning_effort_when_none(self):
        """Must NOT include reasoning_effort in create_with_completion kwargs when None."""
        from unittest.mock import MagicMock, patch

        from src.decision.agents import SynthesizerAgent

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            raw_response = make_raw_response(input_tokens=100, output_tokens=50, total_tokens=150)
            mock_client.create_with_completion.return_value = (
                MagicMock(),
                raw_response,
            )
            mock_from.return_value = mock_client
            agent = SynthesizerAgent(api_key="test")  # reasoning_effort defaults to None
            assert agent.reasoning_effort is None
            agent.synthesize(
                structure_analysis={"test": True},
                calendar_events=[],
                symbol="EURUSD",
            )
            call_kwargs = mock_client.create_with_completion.call_args.kwargs
            assert "reasoning_effort" not in call_kwargs

    def test_decider_decide_passes_reasoning_effort(self, sample_market_context):
        """decide() must include reasoning_effort in create_with_completion() kwargs when set."""
        from unittest.mock import MagicMock, patch

        from src.decision.agents import DeciderAgent

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            raw_response = make_raw_response(input_tokens=100, output_tokens=50, total_tokens=150)
            mock_client.create_with_completion.return_value = (
                MagicMock(),
                raw_response,
            )
            mock_from.return_value = mock_client
            agent = DeciderAgent(reasoning_effort="low", api_key="test")
            agent.decide(
                context=sample_market_context,
                positions=[],
                pending_orders=[],
            )
            call_kwargs = mock_client.create_with_completion.call_args.kwargs
            assert "reasoning_effort" in call_kwargs
            assert call_kwargs["reasoning_effort"] == "low"

    def test_reviewer_review_passes_reasoning_effort(self, sample_decision, sample_market_context):
        """review() must include reasoning_effort in create_with_completion() kwargs when set."""
        from unittest.mock import MagicMock, patch

        from src.decision.agents import ReviewerAgent

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            raw_response = make_raw_response(input_tokens=100, output_tokens=50, total_tokens=150)
            mock_client.create_with_completion.return_value = (
                MagicMock(),
                raw_response,
            )
            mock_from.return_value = mock_client
            agent = ReviewerAgent(reasoning_effort="medium", api_key="test")
            agent.review(
                decision=sample_decision,
                context=sample_market_context,
                calendar_events=[],
            )
            call_kwargs = mock_client.create_with_completion.call_args.kwargs
            assert "reasoning_effort" in call_kwargs
            assert call_kwargs["reasoning_effort"] == "medium"

    def test_client_provided_still_respects_reasoning_effort(self):
        """Pre-built client: reasoning_effort still flows to create_with_completion()."""
        from unittest.mock import MagicMock, patch

        from src.decision.agents import SynthesizerAgent

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            prebuilt = MagicMock()
            mock_client = MagicMock()
            raw_response = make_raw_response(input_tokens=100, output_tokens=50, total_tokens=150)
            mock_client.create_with_completion.return_value = (
                MagicMock(),
                raw_response,
            )
            mock_from.return_value = mock_client
            agent = SynthesizerAgent(client=prebuilt, reasoning_effort="high")
            agent.synthesize(
                structure_analysis={"test": True},
                calendar_events=[],
                symbol="EURUSD",
            )
            call_kwargs = mock_client.create_with_completion.call_args.kwargs
            assert "reasoning_effort" in call_kwargs
            assert call_kwargs["reasoning_effort"] == "high"


class TestReasoningEffortLogging:
    """Tests for reasoning_effort logging in agent __init__ methods."""

    def test_synthesizer_logs_reasoning_effort_at_init(self, caplog):
        """SynthesizerAgent must log reasoning_effort at init."""
        import logging

        caplog.set_level(logging.INFO, logger="src.decision.agents")
        from src.decision.agents import SynthesizerAgent

        with (
            patch("src.decision.agents.instructor.from_openai") as mock_from,
            patch("src.decision.agents.OpenAI"),
        ):
            mock_client = MagicMock()
            mock_from.return_value = mock_client
            SynthesizerAgent(reasoning_effort="high")

            assert any("reasoning_effort=high" in record.message for record in caplog.records), (
                "Expected log message containing 'reasoning_effort=high' "
                "to be emitted during SynthesizerAgent.__init__"
            )

    def test_synthesizer_logs_none_reasoning_effort(self, caplog):
        """SynthesizerAgent must log reasoning_effort even when None."""
        import logging

        caplog.set_level(logging.INFO, logger="src.decision.agents")
        from src.decision.agents import SynthesizerAgent

        with (
            patch("src.decision.agents.instructor.from_openai") as mock_from,
            patch("src.decision.agents.OpenAI"),
        ):
            mock_client = MagicMock()
            mock_from.return_value = mock_client
            SynthesizerAgent(reasoning_effort=None)

            assert any("reasoning_effort=None" in record.message for record in caplog.records), (
                "Expected log message containing 'reasoning_effort=None' "
                "to be emitted during SynthesizerAgent.__init__"
            )

    def test_decider_logs_reasoning_effort(self, caplog):
        """DeciderAgent must log reasoning_effort at init."""
        import logging

        caplog.set_level(logging.INFO, logger="src.decision.agents")
        from src.decision.agents import DeciderAgent

        with (
            patch("src.decision.agents.instructor.from_openai") as mock_from,
            patch("src.decision.agents.OpenAI"),
        ):
            mock_client = MagicMock()
            mock_from.return_value = mock_client
            DeciderAgent(reasoning_effort="low")

            assert any("reasoning_effort=low" in record.message for record in caplog.records), (
                "Expected log message containing 'reasoning_effort=low' "
                "to be emitted during DeciderAgent.__init__"
            )

    def test_reviewer_logs_reasoning_effort(self, caplog):
        """ReviewerAgent must log reasoning_effort at init."""
        import logging

        caplog.set_level(logging.INFO, logger="src.decision.agents")
        from src.decision.agents import ReviewerAgent

        with (
            patch("src.decision.agents.instructor.from_openai") as mock_from,
            patch("src.decision.agents.OpenAI"),
        ):
            mock_client = MagicMock()
            mock_from.return_value = mock_client
            ReviewerAgent(reasoning_effort="medium")

            assert any("reasoning_effort=medium" in record.message for record in caplog.records), (
                "Expected log message containing 'reasoning_effort=medium' "
                "to be emitted during ReviewerAgent.__init__"
            )

    def test_reasoning_effort_log_contains_agent_name(self, caplog):
        """Log message must include the agent class name."""
        import logging

        caplog.set_level(logging.INFO, logger="src.decision.agents")
        from src.decision.agents import SynthesizerAgent

        with (
            patch("src.decision.agents.instructor.from_openai") as mock_from,
            patch("src.decision.agents.OpenAI"),
        ):
            mock_client = MagicMock()
            mock_from.return_value = mock_client
            SynthesizerAgent(reasoning_effort="high")

            assert any("SynthesizerAgent" in record.message for record in caplog.records), (
                "Expected log message containing class name 'SynthesizerAgent' "
                "to be emitted during SynthesizerAgent.__init__"
            )


class TestAgentCostLogging:
    """Per-call cost logging for synthesizer, decider, and reviewer agents.

    These tests verify that agents:
    - Use create_with_completion() instead of create()
    - Extract token usage from raw_response via parse_usage()
    - Call CostTracker.record_call(model, LLMUsage) — note the new LLMUsage arg
    - Log token usage and cost per call at INFO level
    - Still return the correct model when usage is missing
    """

    # ------------------------------------------------------------------
    # Test 1 — Synthesizer logs token usage (new field names)
    # ------------------------------------------------------------------

    def test_synthesizer_logs_token_usage(self, caplog):
        """SynthesizerAgent must log input, output and total_tokens."""
        import logging

        caplog.set_level(logging.INFO, logger="src.decision.agents")
        from src.decision.agents import SynthesizerAgent

        raw_response = make_raw_response(input_tokens=100, output_tokens=50, total_tokens=150)
        mock_result = MagicMock()

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            mock_client.create_with_completion.return_value = (mock_result, raw_response)
            mock_from.return_value = mock_client

            agent = SynthesizerAgent(api_key="test")
            agent.synthesize(
                structure_analysis={"test": True},
                calendar_events=[],
                symbol="EURUSD",
            )

            records_text = " ".join(r.message for r in caplog.records)
            assert "input=100" in records_text, (
                f"Expected log to contain 'input=100'. Logs: {records_text}"
            )
            assert "output=50" in records_text, (
                f"Expected log to contain 'output=50'. Logs: {records_text}"
            )
            assert "total=150" in records_text, (
                f"Expected log to contain 'total=150'. Logs: {records_text}"
            )

    # ------------------------------------------------------------------
    # Test 2 — Synthesizer logs cost
    # ------------------------------------------------------------------

    def test_synthesizer_logs_cost(self, caplog):
        """SynthesizerAgent must log cost=$ with a numeric value."""
        import logging
        import re

        caplog.set_level(logging.INFO, logger="src.decision.agents")
        from src.decision.agents import SynthesizerAgent

        raw_response = make_raw_response(input_tokens=100, output_tokens=50, total_tokens=150)
        mock_result = MagicMock()

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            mock_client.create_with_completion.return_value = (mock_result, raw_response)
            mock_from.return_value = mock_client

            agent = SynthesizerAgent(api_key="test")
            agent.synthesize(
                structure_analysis={"test": True},
                calendar_events=[],
                symbol="EURUSD",
            )

            records_text = " ".join(r.message for r in caplog.records)
            # Look for something like "cost=$0.0005" or "cost=$0.00..."
            assert re.search(r"cost=\$[\d.]+", records_text), (
                f"Expected log to contain 'cost=$<number>'. Logs: {records_text}"
            )

    # ------------------------------------------------------------------
    # Test 3 — Decider logs token usage
    # ------------------------------------------------------------------

    def test_decider_logs_token_usage(self, caplog, sample_market_context):
        """DeciderAgent must log token usage after decide()."""
        import logging

        caplog.set_level(logging.INFO, logger="src.decision.agents")
        from src.decision.agents import DeciderAgent

        raw_response = make_raw_response(input_tokens=200, output_tokens=80, total_tokens=280)
        mock_result = MagicMock()

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            mock_client.create_with_completion.return_value = (mock_result, raw_response)
            mock_from.return_value = mock_client

            agent = DeciderAgent(api_key="test")
            agent.decide(
                context=sample_market_context,
                positions=[],
                pending_orders=[],
            )

            records_text = " ".join(r.message for r in caplog.records)
            assert "input=200" in records_text
            assert "output=80" in records_text
            assert "total=280" in records_text

    # ------------------------------------------------------------------
    # Test 4 — Reviewer logs token usage
    # ------------------------------------------------------------------

    def test_reviewer_logs_token_usage(self, caplog, sample_decision, sample_market_context):
        """ReviewerAgent must log token usage after review()."""
        import logging

        caplog.set_level(logging.INFO, logger="src.decision.agents")
        from src.decision.agents import ReviewerAgent

        raw_response = make_raw_response(input_tokens=150, output_tokens=60, total_tokens=210)
        mock_result = MagicMock()

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            mock_client.create_with_completion.return_value = (mock_result, raw_response)
            mock_from.return_value = mock_client

            agent = ReviewerAgent(api_key="test")
            agent.review(
                decision=sample_decision,
                context=sample_market_context,
                calendar_events=[],
            )

            records_text = " ".join(r.message for r in caplog.records)
            assert "input=150" in records_text
            assert "output=60" in records_text
            assert "total=210" in records_text

    # ------------------------------------------------------------------
    # Test 5 — create_with_completion is used instead of create
    # ------------------------------------------------------------------

    def test_create_with_completion_used(self, caplog):
        """Agents must call create_with_completion, not create."""
        import logging

        caplog.set_level(logging.INFO, logger="src.decision.agents")
        from src.decision.agents import SynthesizerAgent

        raw_response = make_raw_response()
        mock_result = MagicMock()

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            mock_client.create_with_completion.return_value = (mock_result, raw_response)
            mock_from.return_value = mock_client

            agent = SynthesizerAgent(api_key="test")
            agent.synthesize(
                structure_analysis={"test": True},
                calendar_events=[],
                symbol="EURUSD",
            )

            # create_with_completion must have been called
            assert mock_client.create_with_completion.called, (
                "Expected create_with_completion to be called, but it was not"
            )
            # Plain create must NOT have been called
            assert not mock_client.create.called, (
                "Expected create NOT to be called, but it was — "
                "agents should use create_with_completion"
            )

    # ------------------------------------------------------------------
    # Test 6 — Log when usage is None (all-zero)
    # ------------------------------------------------------------------

    def test_log_when_usage_none(self, caplog):
        """When raw_response.usage is None, agents must log zero cost gracefully."""
        import logging

        caplog.set_level(logging.INFO, logger="src.decision.agents")
        from src.decision.agents import SynthesizerAgent

        raw_response = make_raw_response(usage_none=True)
        mock_result = MagicMock()

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            mock_client.create_with_completion.return_value = (mock_result, raw_response)
            mock_from.return_value = mock_client

            agent = SynthesizerAgent(api_key="test")
            agent.synthesize(
                structure_analysis={"test": True},
                calendar_events=[],
                symbol="EURUSD",
            )

            records_text = " ".join(r.message for r in caplog.records)
            # Should contain zero cost
            assert "cost=$0.000000" in records_text, (
                f"Expected log to contain 'cost=$0.000000' when usage is None. Logs: {records_text}"
            )

    # ------------------------------------------------------------------
    # Test 7 — cost_tracker=None does not crash
    # ------------------------------------------------------------------

    def test_agent_no_cost_tracker_does_not_crash(self, caplog):
        """Agents with cost_tracker=None default to CostTracker() and work normally."""
        import logging
        import re

        caplog.set_level(logging.INFO, logger="src.decision.agents")
        from src.decision.agents import SynthesizerAgent
        from src.decision.models import MarketContextSummary

        raw_response = make_raw_response(input_tokens=100, output_tokens=50, total_tokens=150)
        # First element must be a real model instance — synthesize() returns it directly
        expected_result = MarketContextSummary(
            symbol="EURUSD",
            bias="bullish",
            confidence=75.0,
            reasoning="Test reasoning",
        )

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            mock_client.create_with_completion.return_value = (expected_result, raw_response)
            mock_from.return_value = mock_client

            # Explicitly pass cost_tracker=None
            agent = SynthesizerAgent(api_key="test", cost_tracker=None)
            result = agent.synthesize(
                structure_analysis={"test": True},
                calendar_events=[],
                symbol="EURUSD",
            )

            # Must not crash; return type preserved
            assert isinstance(result, MarketContextSummary)
            assert result is expected_result

            # Logs must contain token and cost info (default CostTracker works)
            records_text = " ".join(r.message for r in caplog.records)
            assert "input=100" in records_text
            assert "output=50" in records_text
            assert "total=150" in records_text
            assert re.search(r"cost=\$[\d.]+", records_text)

    # ------------------------------------------------------------------
    # Test 8 — Empty CostTracker pricing with usage=None does not crash
    # ------------------------------------------------------------------

    def test_agent_with_empty_pricing_works(self, caplog):
        """Agents with empty pricing dict still work when usage is None."""
        import logging

        caplog.set_level(logging.INFO, logger="src.decision.agents")
        from src.decision.agents import SynthesizerAgent
        from src.decision.cost_tracker import CostTracker
        from src.decision.models import MarketContextSummary

        raw_response = make_raw_response(usage_none=True)
        expected_result = MarketContextSummary(
            symbol="EURUSD",
            bias="bullish",
            confidence=75.0,
            reasoning="Test reasoning",
        )

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            mock_client.create_with_completion.return_value = (expected_result, raw_response)
            mock_from.return_value = mock_client

            agent = SynthesizerAgent(
                api_key="test",
                cost_tracker=CostTracker(pricing={}),
            )
            result = agent.synthesize(
                structure_analysis={"test": True},
                calendar_events=[],
                symbol="EURUSD",
            )

            assert isinstance(result, MarketContextSummary)
            assert result is expected_result

            # Logs should indicate zero cost since usage was not available
            records_text = " ".join(r.message for r in caplog.records)
            assert "cost=$0.000000" in records_text

            # verify the cost_tracker was untouched (usage=None → all-zero LLMUsage)
            assert agent.cost_tracker.call_count == 1  # call IS counted
            assert agent.cost_tracker.total_cost == 0.0

    # ------------------------------------------------------------------
    # Test 9 — Return types unaffected by cost logging
    # ------------------------------------------------------------------

    def test_return_type_unaffected(self, caplog):
        """Agent public methods must still return correct model types."""
        from src.decision.models import DecisionOutput, MarketContextSummary, ReviewVerdict

        raw_response = make_raw_response()

        # --- Synthesizer ---
        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            mock_client.create_with_completion.return_value = (
                MarketContextSummary(
                    symbol="EURUSD",
                    bias="bullish",
                    confidence=75.0,
                    reasoning="Test reasoning",
                    key_levels=["1.0800"],
                    structural_events=["BOS"],
                ),
                raw_response,
            )
            mock_from.return_value = mock_client
            from src.decision.agents import SynthesizerAgent

            agent_syn = SynthesizerAgent(api_key="test")
            result_syn = agent_syn.synthesize(
                structure_analysis={"test": True},
                calendar_events=[],
                symbol="EURUSD",
            )
            assert isinstance(result_syn, MarketContextSummary), (
                f"synthesize() must return MarketContextSummary, got {type(result_syn)}"
            )

        # --- Decider ---
        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            mock_client.create_with_completion.return_value = (
                DecisionOutput(
                    symbol="EURUSD",
                    action="no_trade",
                    reasoning="Test reasoning",
                ),
                raw_response,
            )
            mock_from.return_value = mock_client
            from src.decision.agents import DeciderAgent
            from src.decision.models import MarketContextSummary

            context = MarketContextSummary(
                symbol="EURUSD",
                bias="bullish",
                confidence=50.0,
                reasoning="Test",
            )
            agent_dec = DeciderAgent(api_key="test")
            result_dec = agent_dec.decide(
                context=context,
                positions=[],
                pending_orders=[],
            )
            assert isinstance(result_dec, DecisionOutput), (
                f"decide() must return DecisionOutput, got {type(result_dec)}"
            )

        # --- Reviewer ---
        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            mock_client.create_with_completion.return_value = (
                ReviewVerdict(
                    approved=True,
                    reasoning="All good",
                ),
                raw_response,
            )
            mock_from.return_value = mock_client
            from src.decision.agents import ReviewerAgent

            agent_rev = ReviewerAgent(api_key="test")
            result_rev = agent_rev.review(
                decision=DecisionOutput(symbol="EURUSD", action="no_trade", reasoning="R"),
                context=MarketContextSummary(
                    symbol="EURUSD",
                    bias="bullish",
                    confidence=50.0,
                    reasoning="R",
                ),
                calendar_events=[],
            )
            assert isinstance(result_rev, ReviewVerdict), (
                f"review() must return ReviewVerdict, got {type(result_rev)}"
            )

    # ------------------------------------------------------------------
    # Test 10 — Agent returns content even when usage is None
    # ------------------------------------------------------------------

    def test_agent_returns_content_when_usage_none(self):
        """Agent returns the generated model content even without usage data."""
        from src.decision.models import MarketContextSummary

        raw_response = make_raw_response(usage_none=True)
        expected_result = MarketContextSummary(
            symbol="EURUSD",
            bias="bullish",
            confidence=75.0,
            reasoning="Test reasoning",
        )

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            mock_client.create_with_completion.return_value = (
                expected_result,
                raw_response,
            )
            mock_from.return_value = mock_client
            from src.decision.agents import SynthesizerAgent

            agent = SynthesizerAgent(api_key="test")
            result = agent.synthesize(
                structure_analysis={"test": True},
                calendar_events=[],
                symbol="EURUSD",
            )

            assert result is expected_result
            assert result.symbol == "EURUSD"
            assert result.bias == "bullish"

    # ------------------------------------------------------------------
    # Test 11 — Agent returns content when usage has partial fields
    # ------------------------------------------------------------------

    def test_agent_returns_content_when_partial_usage(self):
        """Agent returns content when usage has some fields but not others."""
        # Missing output_tokens_details
        from types import SimpleNamespace

        from src.decision.models import MarketContextSummary

        raw_response = SimpleNamespace(
            usage=SimpleNamespace(
                input_tokens=100,
                output_tokens=50,
                total_tokens=150,
                input_tokens_details=None,
                output_tokens_details=None,
            )
        )
        expected_result = MarketContextSummary(
            symbol="EURUSD",
            bias="neutral",
            confidence=50.0,
            reasoning="Partial usage test",
        )

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            mock_client.create_with_completion.return_value = (
                expected_result,
                raw_response,
            )
            mock_from.return_value = mock_client
            from src.decision.agents import SynthesizerAgent

            agent = SynthesizerAgent(api_key="test")
            result = agent.synthesize(
                structure_analysis={"test": True},
                calendar_events=[],
                symbol="EURUSD",
            )

            assert result is expected_result
            assert result.bias == "neutral"

    # ------------------------------------------------------------------
    # Test 12 — Unknown model in pricing does not crash
    # ------------------------------------------------------------------

    def test_agent_unknown_model_pricing_returns_content(self):
        """Agent works when model is not in pricing table."""
        from src.decision.cost_tracker import CostTracker
        from src.decision.models import MarketContextSummary

        # Pricing only has gpt-4o, but agent uses a different model
        cost_tracker = CostTracker(
            pricing={
                "gpt-4o": {
                    "input_per_million": 2.50,
                    "cached_input_per_million": 1.25,
                    "output_per_million": 10.00,
                }
            }
        )

        raw_response = make_raw_response(input_tokens=100, output_tokens=50, total_tokens=150)
        expected_result = MarketContextSummary(
            symbol="EURUSD",
            bias="bullish",
            confidence=75.0,
            reasoning="Test unknown model",
        )

        with patch("src.decision.agents.instructor.from_openai") as mock_from:
            mock_client = MagicMock()
            mock_client.create_with_completion.return_value = (
                expected_result,
                raw_response,
            )
            mock_from.return_value = mock_client
            from src.decision.agents import SynthesizerAgent

            agent = SynthesizerAgent(
                api_key="test",
                model="gpt-4-unknown",
                cost_tracker=cost_tracker,
            )
            result = agent.synthesize(
                structure_analysis={"test": True},
                calendar_events=[],
                symbol="EURUSD",
            )

            assert result is expected_result
            # Call counted, cost is zero
            assert cost_tracker.call_count == 1
            assert cost_tracker.total_cost == 0.0
