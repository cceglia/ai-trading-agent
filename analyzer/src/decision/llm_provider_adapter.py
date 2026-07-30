"""LLM provider adapter — base interface and factory.

Defines the abstract adapter protocol that provider-specific
implementations must satisfy, and a registry-based factory for
creating adapters by :class:`~src.decision.llm_config.ProviderKind`.

New providers are added by:

1. Creating a class that implements :class:`LLMProviderAdapter`.
2. Registering it with :meth:`LLMProviderAdapterFactory.register`.

No existing code needs to be modified — the factory handles
dispatch automatically (Open/Closed Principle).

Usage::

    from src.decision.llm_provider_adapter import LLMProviderAdapterFactory
    from src.decision.adapters.openai_adapter import OpenAIProviderAdapter

    LLMProviderAdapterFactory.register(ProviderKind.OPENAI, OpenAIProviderAdapter)
    adapter = LLMProviderAdapterFactory.create(config)
"""

from __future__ import annotations

import logging
from typing import Any, Protocol

from src.decision.llm_config import LLMModelConfig, LLMModelIdentity, ProviderKind

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Adapter protocol
# ---------------------------------------------------------------------------


class LLMProviderAdapter(Protocol):
    """Abstract protocol for LLM provider adapters.

    An adapter encapsulates the provider-specific logic for:

    * Creating an instructor-patched client from a config.
    * Resolving the model identity.
    * Exposing the raw client for direct use by agent code.

    Implementations must be stateless or self-contained — the factory
    creates a new instance per config.
    """

    @property
    def provider(self) -> ProviderKind:
        """The provider this adapter handles."""
        ...

    @property
    def model_identity(self) -> LLMModelIdentity:
        """Resolved identity for the configured model."""
        ...

    @property
    def client(self) -> Any:
        """The underlying instructor-patched client.

        The concrete type depends on the provider (e.g. an
        ``instructor``-patched ``OpenAI`` instance for OpenAI).
        """
        ...

    @property
    def model(self) -> str:
        """The raw model identifier."""
        ...

    @property
    def reasoning_effort(self) -> str | None:
        """Optional reasoning effort level."""
        ...


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


class LLMProviderAdapterFactory:
    """Registry-based factory for LLM provider adapters.

    Adapters are registered by :class:`ProviderKind` and instantiated
    on demand from an :class:`LLMModelConfig`.

    Example::

        LLMProviderAdapterFactory.register(ProviderKind.OPENAI, OpenAIAdapter)
        adapter = LLMProviderAdapterFactory.create(config)
    """

    _registry: dict[ProviderKind, type[Any]] = {}

    @classmethod
    def register(cls, provider: ProviderKind, adapter_cls: type[Any]) -> None:
        """Register an adapter class for a provider.

        Args:
            provider: Provider kind to handle.
            adapter_cls: Class implementing :class:`LLMProviderAdapter`.

        Raises:
            TypeError: If *adapter_cls* does not satisfy the protocol.
        """
        if not isinstance(adapter_cls, type):
            raise TypeError(f"{adapter_cls!r} is not a class")
        cls._registry[provider] = adapter_cls
        logger.info("Registered adapter %s for provider %s", adapter_cls.__name__, provider.value)

    @classmethod
    def create(cls, config: LLMModelConfig) -> Any:
        """Create an adapter instance for the given config.

        Args:
            config: Model configuration specifying provider and model.

        Returns:
            A new adapter instance.

        Raises:
            ValueError: If no adapter is registered for the config's provider.
        """
        adapter_cls = cls._registry.get(config.provider)
        if adapter_cls is None:
            registered = ", ".join(p.value for p in cls._registry)
            raise ValueError(
                f"No adapter registered for provider {config.provider.value!r}. "
                f"Registered providers: [{registered}]"
            )
        adapter = adapter_cls(config)
        logger.debug(
            "Created %s adapter for model %s",
            config.provider.value,
            config.model,
        )
        return adapter

    @classmethod
    def registered_providers(cls) -> list[ProviderKind]:
        """Return the list of providers with registered adapters."""
        return list(cls._registry.keys())

    @classmethod
    def reset(cls) -> None:
        """Clear all registered adapters.  Intended for testing only."""
        cls._registry.clear()
