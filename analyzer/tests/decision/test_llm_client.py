"""Tests for LLM provider adapters and factory (Phase 3B).

Verifies:
- OpenAIProviderAdapter constructs and resolves identity
- Family/version overrides are honored
- create_llm_client factory dispatches correctly
- Unsupported providers raise UnsupportedLLMProviderError
- LLMCommunicationClient deprecated alias works with warning
- LLMClientProtocol structural compliance
"""

from __future__ import annotations

import warnings
from unittest.mock import patch

import pytest
from instructor import Mode

from src.decision.llm_client import (
    LLMClientProtocol,
    OpenAIProviderAdapter,
    UnsupportedLLMProviderError,
    create_llm_client,
)
from src.decision.llm_config import ProviderKind, ResolutionStatus

# ---------------------------------------------------------------------------
# OpenAIProviderAdapter
# ---------------------------------------------------------------------------


class TestOpenAIProviderAdapter:
    """Provider-awareness of OpenAIProviderAdapter."""

    @patch("src.decision.llm_client.instructor")
    @patch("src.decision.llm_client.OpenAI")
    @patch("src.decision.llm_client.AsyncOpenAI")
    def test_constructs(self, _mock_async, _mock_sync, _mock_instructor):
        adapter = OpenAIProviderAdapter(model="gpt-4o-2024-08-06")
        assert adapter.model_identity.provider == ProviderKind.OPENAI

    @patch("src.decision.llm_client.instructor")
    @patch("src.decision.llm_client.OpenAI")
    @patch("src.decision.llm_client.AsyncOpenAI")
    def test_resolves_family_and_version(self, _mock_async, _mock_sync, _mock_instructor):
        adapter = OpenAIProviderAdapter(model="gpt-4o-2024-08-06")
        identity = adapter.model_identity
        assert identity.provider == ProviderKind.OPENAI
        assert identity.model_family == "gpt-4o"
        assert identity.model_version == "2024-08-06"
        assert identity.resolution_status == ResolutionStatus.RESOLVED

    @patch("src.decision.llm_client.instructor")
    @patch("src.decision.llm_client.OpenAI")
    @patch("src.decision.llm_client.AsyncOpenAI")
    def test_family_override(self, _mock_async, _mock_sync, _mock_instructor):
        adapter = OpenAIProviderAdapter(model="gpt-4o-2024-08-06", family_override="gpt-4o-mini")
        assert adapter.model_identity.model_family == "gpt-4o-mini"
        assert adapter.model_identity.resolution_status == ResolutionStatus.OVERRIDDEN

    @patch("src.decision.llm_client.instructor")
    @patch("src.decision.llm_client.OpenAI")
    @patch("src.decision.llm_client.AsyncOpenAI")
    def test_version_override(self, _mock_async, _mock_sync, _mock_instructor):
        adapter = OpenAIProviderAdapter(model="gpt-4o-2024-08-06", version_override="2024-12-01")
        assert adapter.model_identity.model_version == "2024-12-01"

    @patch("src.decision.llm_client.instructor")
    @patch("src.decision.llm_client.OpenAI")
    @patch("src.decision.llm_client.AsyncOpenAI")
    def test_model_property(self, _mock_async, _mock_sync, _mock_instructor):
        adapter = OpenAIProviderAdapter(model="gpt-4o-2024-08-06")
        assert adapter.model == "gpt-4o-2024-08-06"

    @patch("src.decision.llm_client.instructor")
    @patch("src.decision.llm_client.OpenAI")
    @patch("src.decision.llm_client.AsyncOpenAI")
    def test_satisfies_protocol(self, _mock_async, _mock_sync, _mock_instructor):
        adapter = OpenAIProviderAdapter(model="gpt-4o")
        assert isinstance(adapter, LLMClientProtocol)


class TestOpenAIProviderAdapterModeAndTimeout:
    """instructor_mode and timeout are forwarded to the underlying clients."""

    @patch("src.decision.llm_client.instructor")
    @patch("src.decision.llm_client.OpenAI")
    @patch("src.decision.llm_client.AsyncOpenAI")
    def test_forwards_json_mode_and_timeout(self, mock_async, mock_sync, mock_instructor):
        OpenAIProviderAdapter(model="gpt-4o", instructor_mode="json_mode", timeout=120)

        # Both OpenAI clients receive the per-attempt timeout.
        assert mock_sync.call_args.kwargs["timeout"] == 120
        assert mock_async.call_args.kwargs["timeout"] == 120

        # instructor.from_openai receives mode=Mode.JSON for both clients.
        assert mock_instructor.from_openai.call_count == 2
        for call in mock_instructor.from_openai.call_args_list:
            assert call.kwargs["mode"] == Mode.JSON

    @patch("src.decision.llm_client.instructor")
    @patch("src.decision.llm_client.OpenAI")
    @patch("src.decision.llm_client.AsyncOpenAI")
    def test_forwards_tool_call_mode(self, _mock_async, _mock_sync, mock_instructor):
        OpenAIProviderAdapter(model="gpt-4o", instructor_mode="tool_call")

        for call in mock_instructor.from_openai.call_args_list:
            assert call.kwargs["mode"] == Mode.TOOLS

    @patch("src.decision.llm_client.instructor")
    @patch("src.decision.llm_client.OpenAI")
    @patch("src.decision.llm_client.AsyncOpenAI")
    def test_defaults_to_json_mode_without_timeout_kwarg(
        self, mock_async, mock_sync, mock_instructor
    ):
        OpenAIProviderAdapter(model="gpt-4o")

        for call in mock_instructor.from_openai.call_args_list:
            assert call.kwargs["mode"] == Mode.JSON

        # When timeout is None (inherit default), the clients are not given a
        # timeout kwarg so the SDK's own default applies.
        assert "timeout" not in mock_sync.call_args.kwargs
        assert "timeout" not in mock_async.call_args.kwargs


# ---------------------------------------------------------------------------
# create_llm_client factory
# ---------------------------------------------------------------------------


class TestCreateLLMClient:
    """Factory dispatches to the correct adapter."""

    @patch("src.decision.llm_client.instructor")
    @patch("src.decision.llm_client.OpenAI")
    @patch("src.decision.llm_client.AsyncOpenAI")
    def test_openai_dispatches_to_adapter(self, _mock_async, _mock_sync, _mock_instructor):
        client = create_llm_client(provider=ProviderKind.OPENAI, model="gpt-4o")
        assert isinstance(client, OpenAIProviderAdapter)

    def test_anthropic_raises(self):
        with pytest.raises(UnsupportedLLMProviderError, match="anthropic"):
            create_llm_client(provider=ProviderKind.ANTHROPIC, model="claude-3-opus")

    def test_generic_raises(self):
        with pytest.raises(UnsupportedLLMProviderError, match="generic"):
            create_llm_client(provider=ProviderKind.GENERIC, model="some-model")

    @patch("src.decision.llm_client.instructor")
    @patch("src.decision.llm_client.OpenAI")
    @patch("src.decision.llm_client.AsyncOpenAI")
    def test_passes_overrides(self, _mock_async, _mock_sync, _mock_instructor):
        client = create_llm_client(
            provider=ProviderKind.OPENAI,
            model="gpt-4o-2024-08-06",
            family_override="gpt-4o-mini",
            version_override="2024-12-01",
        )
        assert client.model_identity.model_family == "gpt-4o-mini"
        assert client.model_identity.model_version == "2024-12-01"

    @patch("src.decision.llm_client.instructor")
    @patch("src.decision.llm_client.OpenAI")
    @patch("src.decision.llm_client.AsyncOpenAI")
    def test_forwards_instructor_mode_and_timeout(self, mock_async, mock_sync, mock_instructor):
        create_llm_client(
            provider=ProviderKind.OPENAI,
            model="gpt-4o",
            instructor_mode="tool_call",
            timeout=42,
        )

        # The factory forwards the timeout to the OpenAI clients and the
        # instructor mode to instructor.from_openai.
        assert mock_sync.call_args.kwargs["timeout"] == 42
        assert mock_async.call_args.kwargs["timeout"] == 42
        assert mock_instructor.from_openai.call_count == 2
        for call in mock_instructor.from_openai.call_args_list:
            assert call.kwargs["mode"] == Mode.TOOLS


# ---------------------------------------------------------------------------
# LLMCommunicationClient deprecated alias
# ---------------------------------------------------------------------------


class TestLLMCommunicationClientDeprecated:
    """Deprecated alias still works but emits DeprecationWarning."""

    @patch("src.decision.llm_client.instructor")
    @patch("src.decision.llm_client.OpenAI")
    @patch("src.decision.llm_client.AsyncOpenAI")
    def test_emits_deprecation_warning(self, _mock_async, _mock_sync, _mock_instructor):
        from src.decision.llm_client import LLMCommunicationClient

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            client = LLMCommunicationClient(model="gpt-4o")
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "deprecated" in str(w[0].message).lower()
        assert isinstance(client, OpenAIProviderAdapter)

    @patch("src.decision.llm_client.instructor")
    @patch("src.decision.llm_client.OpenAI")
    @patch("src.decision.llm_client.AsyncOpenAI")
    def test_rejects_non_openai(self, _mock_async, _mock_sync, _mock_instructor):
        from src.decision.llm_client import LLMCommunicationClient

        with pytest.raises(UnsupportedLLMProviderError):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                LLMCommunicationClient(provider=ProviderKind.ANTHROPIC, model="claude-3")
