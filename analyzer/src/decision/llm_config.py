"""LLM model configuration and provider-aware identity resolution.

This module defines the configuration dataclass for LLM endpoints and a
registry of provider-specific model identity resolvers.  Each resolver
knows how to parse model strings from its provider (e.g.
``gpt-4o-2024-08-06`` → OpenAI family/date, ``claude-3-opus-20240229``
→ Anthropic family/date) and falls back to a generic alias resolver
when no provider-specific pattern matches.

Usage::

    from src.decision.llm_config import (
        LLMModelConfig,
        resolve_model_identity,
        ProviderKind,
    )

    config = LLMModelConfig(
        model="gpt-4o-2024-08-06",
        api_key="sk-...",
        provider=ProviderKind.OPENAI,
    )
    identity = resolve_model_identity(config.model, config.provider)
    print(identity.model_family)  # "gpt-4o"
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol, runtime_checkable

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ProviderKind(StrEnum):
    """Supported LLM provider identifiers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GENERIC = "generic"


class ResolutionStatus(StrEnum):
    """Outcome of a model identity resolution attempt."""

    RESOLVED = "resolved"
    OVERRIDDEN = "overridden"
    FALLBACK = "fallback"
    UNRECOGNIZED = "unrecognized"


# ---------------------------------------------------------------------------
# Configuration dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LLMModelConfig:
    """Immutable configuration for an LLM endpoint.

    Attributes:
        model: Model identifier string (e.g. ``"gpt-4o"``).
        api_key: API key for the provider.
        base_url: Optional base URL for OpenAI-compatible providers.
        provider: Provider kind.  When ``GENERIC``, the resolver
            attempts heuristic detection from the model string.
        reasoning_effort: Optional reasoning effort level
            (``"low"`` / ``"medium"`` / ``"high"``).
    """

    model: str
    api_key: str = ""
    base_url: str | None = None
    provider: ProviderKind = ProviderKind.GENERIC
    reasoning_effort: str | None = None


# ---------------------------------------------------------------------------
# Model identity dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LLMModelIdentity:
    """Immutable, provider-aware identity for a resolved LLM model.

    This is the canonical model identity type used throughout the
    decision subsystem.  It carries richer metadata than the raw
    model string, enabling provider-specific adapter selection,
    cost tracking, and logging.

    Attributes:
        provider: Detected or configured provider.
        raw_model_identifier: The original model string as passed
            by the user (e.g. ``"gpt-4o-2024-08-06"``).
        model_family: Normalised family name (e.g. ``"gpt-4o"``).
        model_version: Version/date qualifier extracted from the
            identifier, or ``None`` when absent.
        resolution_status: How the identity was resolved.
    """

    provider: ProviderKind
    raw_model_identifier: str
    model_family: str
    model_version: str | None = None
    resolution_status: ResolutionStatus = ResolutionStatus.RESOLVED

    @property
    def display_name(self) -> str:
        """Human-readable model identity string for logging."""
        parts = [self.provider.value, self.model_family]
        if self.model_version:
            parts.append(self.model_version)
        return "/".join(parts)


# ---------------------------------------------------------------------------
# Resolver protocol
# ---------------------------------------------------------------------------


@runtime_checkable
class ModelIdentityResolver(Protocol):
    """Protocol for provider-specific model identity resolvers.

    Implementations must be able to *support* a model string (i.e.
    recognise it as belonging to their provider) and *resolve* it into
    an :class:`LLMModelIdentity`.
    """

    def supports(self, model: str, provider: ProviderKind | None = None) -> bool:
        """Return ``True`` if this resolver can handle *model*."""
        ...

    def resolve(self, model: str, provider: ProviderKind | None = None) -> LLMModelIdentity:
        """Resolve *model* into an :class:`LLMModelIdentity`."""
        ...


# ---------------------------------------------------------------------------
# OpenAI resolver
# ---------------------------------------------------------------------------


class OpenAIModelIdentityResolver:
    """Resolver for OpenAI model identifiers.

    Recognises patterns like ``gpt-4o-2024-08-06``,
    ``gpt-4o-mini-2024-07-18``, ``o3-2025-04-16``.
    """

    # Matches: gpt-{family}-{version} or o{family}-{version}
    _OPENAI_PATTERN = re.compile(
        r"^(?P<family>gpt-[a-z0-9]+(?:-mini)?|o[0-9]+)"
        r"(?:-(?P<version>\d{4}-\d{2}-\d{2}))?$",
        re.IGNORECASE,
    )

    def supports(self, model: str, provider: ProviderKind | None = None) -> bool:
        if provider is ProviderKind.OPENAI:
            return True
        if provider is not None and provider is not ProviderKind.GENERIC:
            return False
        return self._OPENAI_PATTERN.match(model) is not None

    def resolve(self, model: str, provider: ProviderKind | None = None) -> LLMModelIdentity:
        match = self._OPENAI_PATTERN.match(model)
        if match is None:
            return LLMModelIdentity(
                provider=ProviderKind.OPENAI,
                raw_model_identifier=model,
                model_family=model,
                resolution_status=ResolutionStatus.UNRECOGNIZED,
            )
        family = match.group("family")
        version = match.group("version")
        return LLMModelIdentity(
            provider=ProviderKind.OPENAI,
            raw_model_identifier=model,
            model_family=family,
            model_version=version,
            resolution_status=ResolutionStatus.RESOLVED,
        )


# ---------------------------------------------------------------------------
# Anthropic resolver
# ---------------------------------------------------------------------------


class AnthropicModelIdentityResolver:
    """Resolver for Anthropic model identifiers.

    Recognises patterns like ``claude-3-opus-20240229``,
    ``claude-3-5-sonnet-20241022``.
    """

    # Matches: claude-{version}-{variant}-{date}
    _ANTHROPIC_PATTERN = re.compile(
        r"^(?P<family>claude-[\w-]+?)(?:-(?P<version>\d{8}))$",
        re.IGNORECASE,
    )

    def supports(self, model: str, provider: ProviderKind | None = None) -> bool:
        if provider is ProviderKind.ANTHROPIC:
            return True
        if provider is not None and provider is not ProviderKind.GENERIC:
            return False
        return self._ANTHROPIC_PATTERN.match(model) is not None

    def resolve(self, model: str, provider: ProviderKind | None = None) -> LLMModelIdentity:
        match = self._ANTHROPIC_PATTERN.match(model)
        if match is None:
            return LLMModelIdentity(
                provider=ProviderKind.ANTHROPIC,
                raw_model_identifier=model,
                model_family=model,
                resolution_status=ResolutionStatus.UNRECOGNIZED,
            )
        family = match.group("family")
        version = match.group("version")
        return LLMModelIdentity(
            provider=ProviderKind.ANTHROPIC,
            raw_model_identifier=model,
            model_family=family,
            model_version=version,
            resolution_status=ResolutionStatus.RESOLVED,
        )


# ---------------------------------------------------------------------------
# Generic / fallback resolver
# ---------------------------------------------------------------------------


class GenericAliasModelIdentityResolver:
    """Fallback resolver that treats the entire model string as the family.

    Used when no provider-specific resolver recognises the model.
    """

    def supports(self, model: str, provider: ProviderKind | None = None) -> bool:
        # Always succeeds — this is the fallback.
        return True

    def resolve(self, model: str, provider: ProviderKind | None = None) -> LLMModelIdentity:
        effective_provider = provider if provider is not None else ProviderKind.GENERIC
        return LLMModelIdentity(
            provider=effective_provider,
            raw_model_identifier=model,
            model_family=model,
            model_version=None,
            resolution_status=ResolutionStatus.FALLBACK,
        )


# ---------------------------------------------------------------------------
# Resolver registry
# ---------------------------------------------------------------------------

_RESOLVERS: list[ModelIdentityResolver] = [
    OpenAIModelIdentityResolver(),
    AnthropicModelIdentityResolver(),
    GenericAliasModelIdentityResolver(),
]


def resolve_model_identity(
    model: str,
    provider: ProviderKind | None = None,
    *,
    family_override: str | None = None,
    version_override: str | None = None,
) -> LLMModelIdentity:
    """Resolve a model string to its provider-aware identity.

    Iterates through registered resolvers in order.  The first resolver
    that *supports* the model (considering the optional *provider* hint)
    performs the resolution.

    When *provider* is explicitly set, provider-specific resolvers are
    tried first; the generic fallback always succeeds as a last resort.

    When *family_override* or *version_override* are provided, they
    override the detected values in the resolved identity.

    Args:
        model: Raw model identifier string.
        provider: Optional provider hint to disambiguate.
        family_override: Override the detected model family.
        version_override: Override the detected model version.

    Returns:
        A resolved :class:`LLMModelIdentity`.
    """
    for resolver in _RESOLVERS:
        if resolver.supports(model, provider):
            identity = resolver.resolve(model, provider)
            logger.debug(
                "Resolved model identity: %s → %s (status=%s)",
                model,
                identity.display_name,
                identity.resolution_status.value,
            )
            # Apply overrides when provided.
            if family_override is not None or version_override is not None:
                identity = LLMModelIdentity(
                    provider=identity.provider,
                    raw_model_identifier=identity.raw_model_identifier,
                    model_family=family_override or identity.model_family,
                    model_version=version_override or identity.model_version,
                    resolution_status=ResolutionStatus.OVERRIDDEN
                    if (family_override or version_override)
                    else identity.resolution_status,
                )
            return identity
    # Should never reach here (generic resolver always succeeds), but
    # satisfy the type checker.
    return GenericAliasModelIdentityResolver().resolve(model, provider)
