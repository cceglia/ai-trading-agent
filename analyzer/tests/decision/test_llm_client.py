"""Tests for LLMCommunicationClient provider correctness (Phase 3A).

Verifies:
- OpenAI provider constructs successfully
- Resolved identity is OpenAI with correct family/version
- Family/version overrides are honored
- Anthropic provider raises UnsupportedLLMProviderError
- Generic provider raises UnsupportedLLMProviderError
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from src.decision.llm_client import LLMCommunicationClient, UnsupportedLLMProviderError
from src.decision.llm_config import ProviderKind, ResolutionStatus


class TestLLMCommunicationClientProvider:
    """Provider-awareness of LLMCommunicationClient."""

    @patch("src.decision.llm_client.instructor")
    @patch("src.decision.llm_client.OpenAI")
    @patch("src.decision.llm_client.AsyncOpenAI")
    def test_openai_provider_constructs(self, _mock_async, _mock_sync, _mock_instructor):
        """OpenAI provider constructs without error."""
        client = LLMCommunicationClient(
            provider=ProviderKind.OPENAI,
            model="gpt-4o-2024-08-06",
        )
        assert client.model_identity.provider == ProviderKind.OPENAI

    @patch("src.decision.llm_client.instructor")
    @patch("src.decision.llm_client.OpenAI")
    @patch("src.decision.llm_client.AsyncOpenAI")
    def test_openai_identity_resolves_family_and_version(
        self, _mock_async, _mock_sync, _mock_instructor
    ):
        """OpenAI model identity resolves family and version from model string."""
        client = LLMCommunicationClient(
            provider=ProviderKind.OPENAI,
            model="gpt-4o-2024-08-06",
        )
        identity = client.model_identity
        assert identity.provider == ProviderKind.OPENAI
        assert identity.model_family == "gpt-4o"
        assert identity.model_version == "2024-08-06"
        assert identity.resolution_status == ResolutionStatus.RESOLVED

    @patch("src.decision.llm_client.instructor")
    @patch("src.decision.llm_client.OpenAI")
    @patch("src.decision.llm_client.AsyncOpenAI")
    def test_family_override_is_honored(self, _mock_async, _mock_sync, _mock_instructor):
        """Family override replaces detected family."""
        client = LLMCommunicationClient(
            provider=ProviderKind.OPENAI,
            model="gpt-4o-2024-08-06",
            family_override="gpt-4o-mini",
        )
        identity = client.model_identity
        assert identity.model_family == "gpt-4o-mini"
        assert identity.model_version == "2024-08-06"
        assert identity.resolution_status == ResolutionStatus.OVERRIDDEN

    @patch("src.decision.llm_client.instructor")
    @patch("src.decision.llm_client.OpenAI")
    @patch("src.decision.llm_client.AsyncOpenAI")
    def test_version_override_is_honored(self, _mock_async, _mock_sync, _mock_instructor):
        """Version override replaces detected version."""
        client = LLMCommunicationClient(
            provider=ProviderKind.OPENAI,
            model="gpt-4o-2024-08-06",
            version_override="2024-12-01",
        )
        identity = client.model_identity
        assert identity.model_family == "gpt-4o"
        assert identity.model_version == "2024-12-01"
        assert identity.resolution_status == ResolutionStatus.OVERRIDDEN

    @patch("src.decision.llm_client.instructor")
    @patch("src.decision.llm_client.OpenAI")
    @patch("src.decision.llm_client.AsyncOpenAI")
    def test_both_overrides_honored(self, _mock_async, _mock_sync, _mock_instructor):
        """Both overrides applied together."""
        client = LLMCommunicationClient(
            provider=ProviderKind.OPENAI,
            model="gpt-4o-2024-08-06",
            family_override="custom-family",
            version_override="custom-version",
        )
        identity = client.model_identity
        assert identity.model_family == "custom-family"
        assert identity.model_version == "custom-version"

    def test_anthropic_provider_raises(self):
        """Anthropic provider raises UnsupportedLLMProviderError."""
        with pytest.raises(UnsupportedLLMProviderError, match="anthropic"):
            LLMCommunicationClient(
                provider=ProviderKind.ANTHROPIC,
                model="claude-3-opus-20240229",
            )

    def test_generic_provider_raises(self):
        """Generic provider raises UnsupportedLLMProviderError."""
        with pytest.raises(UnsupportedLLMProviderError, match="generic"):
            LLMCommunicationClient(
                provider=ProviderKind.GENERIC,
                model="some-model",
            )

    @patch("src.decision.llm_client.instructor")
    @patch("src.decision.llm_client.OpenAI")
    @patch("src.decision.llm_client.AsyncOpenAI")
    def test_default_provider_is_openai(self, _mock_async, _mock_sync, _mock_instructor):
        """Default provider parameter is OPENAI."""
        client = LLMCommunicationClient(model="gpt-4o")
        assert client.model_identity.provider == ProviderKind.OPENAI

    @patch("src.decision.llm_client.instructor")
    @patch("src.decision.llm_client.OpenAI")
    @patch("src.decision.llm_client.AsyncOpenAI")
    def test_unrecognized_model_still_resolves_as_openai(
        self, _mock_async, _mock_sync, _mock_instructor
    ):
        """Unrecognized model string still resolves as OPENAI provider."""
        client = LLMCommunicationClient(
            provider=ProviderKind.OPENAI,
            model="custom-model-name",
        )
        identity = client.model_identity
        assert identity.provider == ProviderKind.OPENAI
        assert identity.model_family == "custom-model-name"
        assert identity.resolution_status == ResolutionStatus.UNRECOGNIZED

    @patch("src.decision.llm_client.instructor")
    @patch("src.decision.llm_client.OpenAI")
    @patch("src.decision.llm_client.AsyncOpenAI")
    def test_model_property_returns_model_string(self, _mock_async, _mock_sync, _mock_instructor):
        """model property returns the raw model string."""
        client = LLMCommunicationClient(
            provider=ProviderKind.OPENAI,
            model="gpt-4o-2024-08-06",
        )
        assert client.model == "gpt-4o-2024-08-06"
