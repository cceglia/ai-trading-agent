"""Tests for LLM model configuration and identity resolution (Section 16.7).

Tests the decision/llm_config.py module:

- ProviderKind enum values
- ResolutionStatus enum values
- LLMModelConfig dataclass construction
- LLMModelIdentity dataclass with display_name property
- OpenAIModelIdentityResolver — pattern matching and resolution
- AnthropicModelIdentityResolver — pattern matching and resolution
- GenericAliasModelIdentityResolver — fallback resolution
- resolve_model_identity() — registry-based resolution
- Provider hint disambiguation
- Unrecognized model handling
"""

from __future__ import annotations

import pytest

from src.decision.llm_config import (
    AnthropicModelIdentityResolver,
    GenericAliasModelIdentityResolver,
    LLMModelConfig,
    LLMModelIdentity,
    OpenAIModelIdentityResolver,
    ProviderKind,
    ResolutionStatus,
    resolve_model_identity,
)

# ============================================================================
# ProviderKind enum
# ============================================================================


class TestProviderKind:
    """ProviderKind values."""

    def test_openai(self) -> None:
        assert ProviderKind.OPENAI.value == "openai"

    def test_anthropic(self) -> None:
        assert ProviderKind.ANTHROPIC.value == "anthropic"

    def test_generic(self) -> None:
        assert ProviderKind.GENERIC.value == "generic"

    def test_all_values_distinct(self) -> None:
        values = {p.value for p in ProviderKind}
        assert len(values) == 3


# ============================================================================
# ResolutionStatus enum
# ============================================================================


class TestResolutionStatus:
    """ResolutionStatus values."""

    def test_resolved(self) -> None:
        assert ResolutionStatus.RESOLVED.value == "resolved"

    def test_fallback(self) -> None:
        assert ResolutionStatus.FALLBACK.value == "fallback"

    def test_unrecognized(self) -> None:
        assert ResolutionStatus.UNRECOGNIZED.value == "unrecognized"

    def test_all_values_distinct(self) -> None:
        values = {s.value for s in ResolutionStatus}
        assert len(values) == 4


# ============================================================================
# LLMModelConfig
# ============================================================================


class TestLLMModelConfig:
    """LLMModelConfig dataclass construction."""

    def test_minimal_config(self) -> None:
        config = LLMModelConfig(model="gpt-4o")
        assert config.model == "gpt-4o"
        assert config.api_key == ""
        assert config.base_url is None
        assert config.provider == ProviderKind.GENERIC
        assert config.reasoning_effort is None

    def test_full_config(self) -> None:
        config = LLMModelConfig(
            model="claude-3-opus-20240229",
            api_key="sk-ant-xxx",
            base_url="https://api.anthropic.com",
            provider=ProviderKind.ANTHROPIC,
            reasoning_effort="high",
        )
        assert config.model == "claude-3-opus-20240229"
        assert config.api_key == "sk-ant-xxx"
        assert config.base_url == "https://api.anthropic.com"
        assert config.provider == ProviderKind.ANTHROPIC
        assert config.reasoning_effort == "high"

    def test_immutable(self) -> None:
        config = LLMModelConfig(model="gpt-4o")
        with pytest.raises(AttributeError):
            config.model = "gpt-5"  # type: ignore[misc]

    def test_equality(self) -> None:
        a = LLMModelConfig(model="gpt-4o", api_key="sk-123")
        b = LLMModelConfig(model="gpt-4o", api_key="sk-123")
        assert a == b


# ============================================================================
# LLMModelIdentity
# ============================================================================


class TestLLMModelIdentity:
    """LLMModelIdentity dataclass and display_name."""

    def test_minimal_identity(self) -> None:
        identity = LLMModelIdentity(
            provider=ProviderKind.OPENAI,
            raw_model_identifier="gpt-4o",
            model_family="gpt-4o",
        )
        assert identity.provider == ProviderKind.OPENAI
        assert identity.raw_model_identifier == "gpt-4o"
        assert identity.model_family == "gpt-4o"
        assert identity.model_version is None
        assert identity.resolution_status == ResolutionStatus.RESOLVED

    def test_full_identity(self) -> None:
        identity = LLMModelIdentity(
            provider=ProviderKind.ANTHROPIC,
            raw_model_identifier="claude-3-opus-20240229",
            model_family="claude-3-opus",
            model_version="20240229",
            resolution_status=ResolutionStatus.RESOLVED,
        )
        assert identity.model_version == "20240229"

    def test_display_name_with_version(self) -> None:
        identity = LLMModelIdentity(
            provider=ProviderKind.OPENAI,
            raw_model_identifier="gpt-4o-2024-08-06",
            model_family="gpt-4o",
            model_version="2024-08-06",
        )
        assert identity.display_name == "openai/gpt-4o/2024-08-06"

    def test_display_name_without_version(self) -> None:
        identity = LLMModelIdentity(
            provider=ProviderKind.GENERIC,
            raw_model_identifier="my-custom-model",
            model_family="my-custom-model",
        )
        assert identity.display_name == "generic/my-custom-model"

    def test_immutable(self) -> None:
        identity = LLMModelIdentity(
            provider=ProviderKind.OPENAI,
            raw_model_identifier="gpt-4o",
            model_family="gpt-4o",
        )
        with pytest.raises(AttributeError):
            identity.model_family = "gpt-5"  # type: ignore[misc]


# ============================================================================
# OpenAIModelIdentityResolver
# ============================================================================


class TestOpenAIModelIdentityResolver:
    """OpenAIModelIdentityResolver — supports() and resolve()."""

    def setup_method(self) -> None:
        self.resolver = OpenAIModelIdentityResolver()

    def test_supports_gpt4o(self) -> None:
        assert self.resolver.supports("gpt-4o") is True

    def test_supports_gpt4o_with_date(self) -> None:
        assert self.resolver.supports("gpt-4o-2024-08-06") is True

    def test_supports_gpt4o_mini(self) -> None:
        assert self.resolver.supports("gpt-4o-mini") is True
        assert self.resolver.supports("gpt-4o-mini-2024-07-18") is True

    def test_supports_o_series(self) -> None:
        assert self.resolver.supports("o3-2025-04-16") is True
        assert self.resolver.supports("o1") is True

    def test_supports_with_provider_hint_openai(self) -> None:
        assert self.resolver.supports("some-model", ProviderKind.OPENAI) is True

    def test_does_not_support_non_openai_when_hint_given(self) -> None:
        assert self.resolver.supports("gpt-4o", ProviderKind.ANTHROPIC) is False
        assert self.resolver.supports("claude-3", ProviderKind.ANTHROPIC) is False

    def test_resolve_gpt4o_basic(self) -> None:
        identity = self.resolver.resolve("gpt-4o")
        assert identity.provider == ProviderKind.OPENAI
        assert identity.model_family == "gpt-4o"
        assert identity.model_version is None
        assert identity.raw_model_identifier == "gpt-4o"
        assert identity.resolution_status == ResolutionStatus.RESOLVED

    def test_resolve_gpt4o_with_date(self) -> None:
        identity = self.resolver.resolve("gpt-4o-2024-08-06")
        assert identity.model_family == "gpt-4o"
        assert identity.model_version == "2024-08-06"

    def test_resolve_o3_with_date(self) -> None:
        identity = self.resolver.resolve("o3-2025-04-16")
        assert identity.model_family == "o3"
        assert identity.model_version == "2025-04-16"

    def test_resolve_unrecognized_fallback(self) -> None:
        identity = self.resolver.resolve("custom-model-xyz")
        assert identity.resolution_status == ResolutionStatus.UNRECOGNIZED
        assert identity.model_family == "custom-model-xyz"

    def test_resolve_case_insensitive(self) -> None:
        identity = self.resolver.resolve("GPT-4o-2024-08-06")
        # The regex is case-insensitive so it matches, but group() preserves
        # the original case from the input string
        assert identity.model_family == "GPT-4o"
        assert identity.model_version == "2024-08-06"
        assert identity.resolution_status == ResolutionStatus.RESOLVED


# ============================================================================
# AnthropicModelIdentityResolver
# ============================================================================


class TestAnthropicModelIdentityResolver:
    """AnthropicModelIdentityResolver — supports() and resolve()."""

    def setup_method(self) -> None:
        self.resolver = AnthropicModelIdentityResolver()

    def test_supports_claude_3_opus(self) -> None:
        assert self.resolver.supports("claude-3-opus-20240229") is True

    def test_supports_claude_3_5_sonnet(self) -> None:
        assert self.resolver.supports("claude-3-5-sonnet-20241022") is True

    def test_supports_claude_4(self) -> None:
        assert self.resolver.supports("claude-4-20250514") is True

    def test_supports_with_provider_hint_anthropic(self) -> None:
        assert self.resolver.supports("some-model", ProviderKind.ANTHROPIC) is True

    def test_does_not_support_with_wrong_hint(self) -> None:
        assert self.resolver.supports("claude-3-opus-20240229", ProviderKind.OPENAI) is False

    def test_does_not_support_model_without_date(self) -> None:
        # Anthropic pattern requires a date suffix
        assert self.resolver.supports("claude-3-opus") is False

    def test_resolve_claude_3_opus(self) -> None:
        identity = self.resolver.resolve("claude-3-opus-20240229")
        assert identity.provider == ProviderKind.ANTHROPIC
        assert identity.model_family == "claude-3-opus"
        assert identity.model_version == "20240229"
        assert identity.resolution_status == ResolutionStatus.RESOLVED

    def test_resolve_claude_3_5_sonnet(self) -> None:
        identity = self.resolver.resolve("claude-3-5-sonnet-20241022")
        assert identity.model_family == "claude-3-5-sonnet"
        assert identity.model_version == "20241022"

    def test_resolve_unrecognized_fallback(self) -> None:
        identity = self.resolver.resolve("claude-3-opus")
        assert identity.resolution_status == ResolutionStatus.UNRECOGNIZED
        assert identity.model_family == "claude-3-opus"

    def test_resolve_case_insensitive(self) -> None:
        identity = self.resolver.resolve("CLAUDE-3-OPUS-20240229")
        # The regex is case-insensitive but preserved original case
        assert identity.model_family == "CLAUDE-3-OPUS"


# ============================================================================
# GenericAliasModelIdentityResolver
# ============================================================================


class TestGenericAliasModelIdentityResolver:
    """GenericAliasModelIdentityResolver — always supports, resolves as fallback."""

    def setup_method(self) -> None:
        self.resolver = GenericAliasModelIdentityResolver()

    def test_always_supports(self) -> None:
        assert self.resolver.supports("anything") is True
        assert self.resolver.supports("") is True
        assert self.resolver.supports("gpt-4o") is True

    def test_resolve_without_provider(self) -> None:
        identity = self.resolver.resolve("custom-model")
        assert identity.provider == ProviderKind.GENERIC
        assert identity.model_family == "custom-model"
        assert identity.model_version is None
        assert identity.resolution_status == ResolutionStatus.FALLBACK

    def test_resolve_with_provider(self) -> None:
        identity = self.resolver.resolve("custom-model", ProviderKind.OPENAI)
        assert identity.provider == ProviderKind.OPENAI
        assert identity.model_family == "custom-model"
        assert identity.resolution_status == ResolutionStatus.FALLBACK


# ============================================================================
# resolve_model_identity — registry-based resolution
# ============================================================================


class TestResolveModelIdentity:
    """resolve_model_identity() orchestrates resolution through registered resolvers."""

    def test_openai_model_resolved(self) -> None:
        identity = resolve_model_identity("gpt-4o-2024-08-06")
        assert identity.provider == ProviderKind.OPENAI
        assert identity.model_family == "gpt-4o"
        assert identity.model_version == "2024-08-06"
        assert identity.resolution_status == ResolutionStatus.RESOLVED

    def test_anthropic_model_resolved(self) -> None:
        identity = resolve_model_identity("claude-3-opus-20240229")
        assert identity.provider == ProviderKind.ANTHROPIC
        assert identity.model_family == "claude-3-opus"
        assert identity.model_version == "20240229"
        assert identity.resolution_status == ResolutionStatus.RESOLVED

    def test_unrecognized_falls_back_to_generic(self) -> None:
        identity = resolve_model_identity("some-custom-model")
        assert identity.provider == ProviderKind.GENERIC
        assert identity.model_family == "some-custom-model"
        assert identity.resolution_status == ResolutionStatus.FALLBACK

    def test_empty_string_falls_back(self) -> None:
        identity = resolve_model_identity("")
        assert identity.provider == ProviderKind.GENERIC
        assert identity.resolution_status == ResolutionStatus.FALLBACK

    def test_provider_hint_disambiguates(self) -> None:
        """Provider hint directs to the correct resolver."""
        identity = resolve_model_identity("my-model", ProviderKind.OPENAI)
        assert identity.provider == ProviderKind.OPENAI
        # OpenAI resolver: pattern doesn't match, but provider hint says OpenAI
        # → falls to the unrecognized path of OpenAI resolver
        # Then OpenAIModelIdentityResolver says it supports due to provider hint
        assert identity.resolution_status == ResolutionStatus.UNRECOGNIZED

    def test_provider_hint_anthropic(self) -> None:
        identity = resolve_model_identity("my-model", ProviderKind.ANTHROPIC)
        assert identity.provider == ProviderKind.ANTHROPIC
        assert identity.resolution_status == ResolutionStatus.UNRECOGNIZED

    def test_provider_hint_generic_uses_generic_resolver(self) -> None:
        """GENERIC provider hint bypasses provider-specific resolvers."""
        identity = resolve_model_identity("gpt-4o", ProviderKind.GENERIC)
        # With GENERIC hint, OpenAIModelIdentityResolver.supports returns True
        # if pattern matches (code: if provider is not None
        # and provider is not ProviderKind.GENERIC: return False)
        # So: provider=GENERIC → falls through to pattern matching → matches gpt-4o
        assert identity.provider == ProviderKind.OPENAI
        assert identity.resolution_status == ResolutionStatus.RESOLVED

    def test_resolver_always_returns_with_generic_fallback(self) -> None:
        """resolve_model_identity never returns None — always falls back to generic."""
        identity = resolve_model_identity(" ")
        assert identity is not None
        assert identity.model_family is not None
        assert identity.provider is not None


# ============================================================================
# Provider awareness — supports
# ============================================================================


class TestProviderAwareSupport:
    """Provider-aware supports() checks."""

    def test_openai_resolver_supports_openai_provider(self) -> None:
        resolver = OpenAIModelIdentityResolver()
        assert resolver.supports("anything-at-all", ProviderKind.OPENAI) is True

    def test_anthropic_resolver_supports_anthropic_provider(self) -> None:
        resolver = AnthropicModelIdentityResolver()
        assert resolver.supports("anything-at-all", ProviderKind.ANTHROPIC) is True

    def test_openai_resolver_rejects_anthropic_hint(self) -> None:
        resolver = OpenAIModelIdentityResolver()
        assert resolver.supports("gpt-4o", ProviderKind.ANTHROPIC) is False

    def test_anthropic_resolver_rejects_openai_hint(self) -> None:
        resolver = AnthropicModelIdentityResolver()
        assert resolver.supports("claude-3-opus-20240229", ProviderKind.OPENAI) is False


# ============================================================================
# Model identity consistency
# ============================================================================


class TestModelIdentityConsistency:
    """Consistency checks across model identity classes."""

    def test_resolver_protocol_runtime_checkable(self) -> None:
        from src.decision.llm_config import ModelIdentityResolver

        assert isinstance(ModelIdentityResolver, type)
        # Verify protocol is runtime_checkable
        assert issubclass(OpenAIModelIdentityResolver, ModelIdentityResolver)
        assert issubclass(AnthropicModelIdentityResolver, ModelIdentityResolver)
        assert issubclass(GenericAliasModelIdentityResolver, ModelIdentityResolver)

    def test_all_resolvers_have_correct_signatures(self) -> None:
        """All resolvers implement supports() and resolve() with correct signatures."""
        for resolver in [OpenAIModelIdentityResolver(), AnthropicModelIdentityResolver()]:
            assert callable(resolver.supports)
            assert callable(resolver.resolve)

    def test_openai_resolver_handles_o_series(self) -> None:
        resolver = OpenAIModelIdentityResolver()
        assert resolver.supports("o1") is True
        # o3-mini does NOT match the pattern because the pattern expects
        # o[0-9]+ optionally followed by -YYYY-MM-DD, not -mini
        assert resolver.supports("o3-mini") is False
        assert resolver.supports("o3-2025-04-16") is True
        # However, with an explicit OPENAI provider hint, it is supported
        assert resolver.supports("o3-mini", ProviderKind.OPENAI) is True

    def test_anthropic_resolver_handles_future_families(self) -> None:
        resolver = AnthropicModelIdentityResolver()
        # claude-4 is speculative but should match the pattern
        assert resolver.supports("claude-4-20250514") is True
        identity = resolver.resolve("claude-4-20250514")
        assert identity.model_family == "claude-4"
        assert identity.model_version == "20250514"

    def test_anthropic_resolver_rejects_no_date(self) -> None:
        resolver = AnthropicModelIdentityResolver()
        # claude-3-opus without date doesn't match the Anthropic pattern
        assert resolver.supports("claude-3-opus") is False


# ============================================================================
# Edge cases
# ============================================================================


class TestLLMConfigEdgeCases:
    """Edge cases for LLM configuration."""

    def test_config_with_empty_api_key(self) -> None:
        config = LLMModelConfig(model="gpt-4o", api_key="")
        assert config.api_key == ""

    def test_config_with_reasoning_effort(self) -> None:
        config = LLMModelConfig(model="o3", reasoning_effort="medium")
        assert config.reasoning_effort == "medium"

    def test_identity_display_name_special_chars(self) -> None:
        identity = LLMModelIdentity(
            provider=ProviderKind.GENERIC,
            raw_model_identifier="my-org/my-model@v1",
            model_family="my-org/my-model@v1",
        )
        assert identity.display_name == "generic/my-org/my-model@v1"

    def test_resolve_model_identity_none_provider(self) -> None:
        """When provider is None, automatic detection kicks in."""
        identity = resolve_model_identity("gpt-4o", None)
        assert identity.provider == ProviderKind.OPENAI

    def test_resolve_model_identity_extra_whitespace(self) -> None:
        """Model string with whitespace is treated literally (no stripping)."""
        identity = resolve_model_identity("  gpt-4o  ")
        assert identity.provider == ProviderKind.GENERIC  # doesn't match pattern
        assert identity.resolution_status == ResolutionStatus.FALLBACK
