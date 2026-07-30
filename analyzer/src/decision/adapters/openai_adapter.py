"""OpenAI provider adapter — instructor-based structured output.

Wraps the ``instructor`` library to provide a provider-specific adapter
that conforms to :class:`~src.decision.llm_provider_adapter.LLMProviderAdapter`
and implements :class:`~src.decision.llm_client.LLMClientProtocol`.

This adapter is the concrete implementation for OpenAI and
OpenAI-compatible providers (e.g. Azure, local proxies).

Usage::

    from src.decision.llm_config import LLMModelConfig, ProviderKind
    from src.decision.adapters.openai_adapter import OpenAIProviderAdapter

    config = LLMModelConfig(
        model="gpt-4o-2024-08-06",
        api_key="sk-...",
        provider=ProviderKind.OPENAI,
    )
    adapter = OpenAIProviderAdapter(config)
    result = await adapter.generate_structured(
        messages=[{"role": "user", "content": "..."}],
        response_model=MyModel,
    )
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import instructor
from openai import AsyncOpenAI, OpenAI
from pydantic import BaseModel

from src.decision.llm_client import LLMClientError, T
from src.decision.llm_config import (
    LLMModelConfig,
    LLMModelIdentity,
    ProviderKind,
    resolve_model_identity,
)
from src.decision.usage import LLMUsage, parse_usage

logger = logging.getLogger(__name__)


class OpenAIProviderAdapter:
    """OpenAI provider adapter using ``instructor`` for structured output.

    Conforms to both :class:`LLMProviderAdapter` (factory protocol) and
    :class:`LLMClientProtocol` (client protocol), making it usable both
    as a standalone client and as a drop-in for the existing agent
    infrastructure.

    Parameters
    ----------
    config:
        Model configuration with API key, base URL, and model identifier.
    default_max_retries:
        Default retry count when not specified per-call.
    default_temperature:
        Default temperature when not specified per-call.
    """

    def __init__(
        self,
        config: LLMModelConfig,
        *,
        default_max_retries: int = 3,
        default_temperature: float | None = None,
    ) -> None:
        self._config = config
        self._model = config.model
        self._reasoning_effort = config.reasoning_effort
        self._default_max_retries = default_max_retries
        self._default_temperature = default_temperature

        # Resolve model identity.
        self._identity = resolve_model_identity(config.model, config.provider)

        # Build OpenAI client kwargs.
        openai_kwargs: dict[str, Any] = {}
        if config.api_key:
            openai_kwargs["api_key"] = config.api_key
        if config.base_url:
            openai_kwargs["base_url"] = config.base_url

        # Create instructor-patched clients (sync + async).
        self._sync_client = instructor.from_openai(OpenAI(**openai_kwargs))
        self._async_client = instructor.from_openai(AsyncOpenAI(**openai_kwargs))

        logger.info(
            "OpenAIProviderAdapter initialised: model=%s provider=%s family=%s reasoning_effort=%s",
            self._model,
            self._identity.provider.value,
            self._identity.model_family,
            self._reasoning_effort,
        )

    # -- LLMProviderAdapter properties ----------------------------------------

    @property
    def provider(self) -> ProviderKind:
        """The provider this adapter handles."""
        return ProviderKind.OPENAI

    @property
    def model_identity(self) -> LLMModelIdentity:
        """Resolved identity for the configured model."""
        return self._identity

    @property
    def client(self) -> Any:
        """The underlying sync instructor-patched OpenAI client."""
        return self._sync_client

    @property
    def model(self) -> str:
        """The raw model identifier."""
        return self._model

    @property
    def reasoning_effort(self) -> str | None:
        """Optional reasoning effort level."""
        return self._reasoning_effort

    # -- LLMClientProtocol (async) --------------------------------------------

    async def generate_structured(
        self,
        messages: list[dict[str, str]],
        response_model: type[T],
        *,
        temperature: float | None = None,
        max_retries: int | None = None,
        **kwargs: Any,
    ) -> T:
        """Send messages to the LLM and return a structured Pydantic model.

        Runs the synchronous ``instructor`` call in a thread pool so it
        can be ``await``-ed from async orchestration code.

        Args:
            messages: Chat messages in OpenAI format (``role``/``content``).
            response_model: Pydantic model class for structured output.
            temperature: Optional temperature override (0.0–2.0).
            max_retries: Optional max-retries override for instructor.
            **kwargs: Additional provider-specific parameters forwarded
                to the underlying ``instructor`` client.

        Returns:
            An instance of *response_model* populated by the LLM.

        Raises:
            LLMClientError: On provider errors after all retries exhausted.
            ValueError: If *messages* is empty or *response_model* is invalid.
        """
        if not messages:
            raise ValueError("messages must not be empty")
        if not (isinstance(response_model, type) and issubclass(response_model, BaseModel)):
            raise ValueError("response_model must be a BaseModel subclass")

        effective_max_retries = (
            max_retries if max_retries is not None else self._default_max_retries
        )
        effective_temperature = (
            temperature if temperature is not None else self._default_temperature
        )

        create_kwargs: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "response_model": response_model,
            "max_retries": effective_max_retries,
        }
        if effective_temperature is not None:
            create_kwargs["temperature"] = effective_temperature
        if self._reasoning_effort is not None:
            create_kwargs["reasoning_effort"] = self._reasoning_effort
        create_kwargs.update(kwargs)

        logger.debug(
            "OpenAI generate_structured: model=%s response_model=%s max_retries=%d",
            self._model,
            response_model.__name__,
            effective_max_retries,
        )

        try:
            loop = asyncio.get_running_loop()
            response, raw_response = await loop.run_in_executor(
                None,
                lambda: self._sync_client.create_with_completion(**create_kwargs),
            )

            usage = parse_usage(raw_response)
            logger.info(
                "OpenAI structured call OK: model=%s response_model=%s "
                "input=%d output=%d reasoning=%d",
                self._model,
                response_model.__name__,
                usage.input_tokens,
                usage.output_tokens,
                usage.reasoning_tokens,
            )
            return response  # type: ignore[no-any-return]

        except Exception as exc:
            raise LLMClientError(
                f"OpenAI LLM call failed for {response_model.__name__}: {exc}",
                model=self._model,
                cause=exc,
            ) from exc

    # -- Sync convenience -----------------------------------------------------

    def generate_structured_sync(
        self,
        messages: list[dict[str, str]],
        response_model: type[T],
        *,
        temperature: float | None = None,
        max_retries: int | None = None,
        **kwargs: Any,
    ) -> tuple[T, LLMUsage]:
        """Synchronous variant of :meth:`generate_structured`.

        Returns ``(response, usage)`` so callers can track costs.

        Useful for non-async callers (e.g. the existing agent classes).
        """
        if not messages:
            raise ValueError("messages must not be empty")
        if not (isinstance(response_model, type) and issubclass(response_model, BaseModel)):
            raise ValueError("response_model must be a BaseModel subclass")

        effective_max_retries = (
            max_retries if max_retries is not None else self._default_max_retries
        )
        effective_temperature = (
            temperature if temperature is not None else self._default_temperature
        )

        create_kwargs: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "response_model": response_model,
            "max_retries": effective_max_retries,
        }
        if effective_temperature is not None:
            create_kwargs["temperature"] = effective_temperature
        if self._reasoning_effort is not None:
            create_kwargs["reasoning_effort"] = self._reasoning_effort
        create_kwargs.update(kwargs)

        logger.debug(
            "OpenAI generate_structured_sync: model=%s response_model=%s max_retries=%d",
            self._model,
            response_model.__name__,
            effective_max_retries,
        )

        try:
            response, raw_response = self._sync_client.create_with_completion(**create_kwargs)

            usage = parse_usage(raw_response)
            logger.info(
                "OpenAI structured call OK (sync): model=%s response_model=%s "
                "input=%d output=%d reasoning=%d",
                self._model,
                response_model.__name__,
                usage.input_tokens,
                usage.output_tokens,
                usage.reasoning_tokens,
            )
            return response, usage

        except Exception as exc:
            raise LLMClientError(
                f"OpenAI LLM call failed for {response_model.__name__}: {exc}",
                model=self._model,
                cause=exc,
            ) from exc
