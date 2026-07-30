"""LLM client protocol and communication client for structured LLM calls.

This module defines the abstract protocol for LLM communication and
provides a concrete implementation with retry logic and error handling.
It uses the ``instructor`` library to return structured Pydantic models
from LLM responses.

Usage::

    from src.decision.llm_client import LLMCommunicationClient

    client = LLMCommunicationClient(
        api_key="...",
        model="gpt-4o",
    )
    result = await client.generate_structured(
        messages=[{"role": "user", "content": "..."}],
        response_model=MyModel,
    )
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Protocol, TypeVar, runtime_checkable

import instructor
from openai import AsyncOpenAI, OpenAI
from pydantic import BaseModel

from src.decision.llm_config import (
    LLMModelIdentity,
    ProviderKind,
    resolve_model_identity,
)
from src.decision.usage import LLMUsage, parse_usage

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


# ---------------------------------------------------------------------------
# Protocol
# ---------------------------------------------------------------------------


@runtime_checkable
class LLMClientProtocol(Protocol):
    """Abstract protocol for LLM communication with structured output.

    Implementations must support ``generate_structured`` which returns
    a Pydantic model validated by ``instructor``, and expose a
    ``model_identity`` property for logging and cost tracking.
    """

    @property
    def model_identity(self) -> LLMModelIdentity:
        """Return identity information about the configured LLM."""
        ...

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
        ...

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

        Returns the response model together with usage information for
        cost tracking.  Non-async callers (e.g. the agent classes) use
        this instead of the async variant.

        Args:
            messages: Chat messages in OpenAI format (``role``/``content``).
            response_model: Pydantic model class for structured output.
            temperature: Optional temperature override (0.0–2.0).
            max_retries: Optional max-retries override for instructor.
            **kwargs: Additional provider-specific parameters forwarded
                to the underlying ``instructor`` client.

        Returns:
            A ``(response, usage)`` tuple where *response* is an instance
            of *response_model* and *usage* holds token-count information.

        Raises:
            LLMClientError: On provider errors after all retries exhausted.
            ValueError: If *messages* is empty or *response_model* is invalid.
        """
        ...


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class LLMClientError(Exception):
    """Raised when an LLM API call fails after all retries."""

    def __init__(
        self,
        message: str,
        *,
        model: str | None = None,
        cause: BaseException | None = None,
    ) -> None:
        self.model = model
        self.cause = cause
        super().__init__(message)


class UnsupportedLLMProviderError(Exception):
    """Raised when an unsupported LLM provider is requested."""


# ---------------------------------------------------------------------------
# Concrete implementation
# ---------------------------------------------------------------------------


class LLMCommunicationClient:
    """Concrete LLM client implementing ``LLMClientProtocol``.

    Wraps an ``instructor``-patched OpenAI client and provides:

    * **Structured output** — ``generate_structured`` returns a Pydantic
      model validated by ``instructor``.
    * **Retry logic** — configurable per-call ``max_retries`` with
      exponential back-off managed by ``instructor``.
    * **Error handling** — provider/network errors are caught and
      re-raised as :class:`LLMClientError` with context.

    Parameters
    ----------
    api_key:
        API key for the LLM provider.  Passed directly to ``OpenAI``.
    base_url:
        Optional base URL for OpenAI-compatible providers.
    model:
        Model identifier (e.g. ``"gpt-4o"``).
    reasoning_effort:
        Optional reasoning effort level (``"low"``/``"medium"``/``"high"``).
    default_max_retries:
        Default number of retries when not specified per-call.
        Defaults to ``3``.
    default_temperature:
        Default temperature when not specified per-call.  When ``None``
        the provider's default is used.
    """

    def __init__(
        self,
        *,
        api_key: str = "",
        base_url: str | None = None,
        model: str = "gpt-4o",
        provider: ProviderKind = ProviderKind.OPENAI,
        family_override: str | None = None,
        version_override: str | None = None,
        reasoning_effort: str | None = None,
        default_max_retries: int = 3,
        default_temperature: float | None = None,
    ) -> None:
        # Only OpenAI transport is supported in this client.
        if provider is not ProviderKind.OPENAI:
            raise UnsupportedLLMProviderError(
                f"LLMCommunicationClient only supports OpenAI; got {provider.value}"
            )

        self._model = model
        self._provider = provider
        self._reasoning_effort = reasoning_effort
        self._default_max_retries = default_max_retries
        self._default_temperature = default_temperature

        # Resolve and store model identity with optional overrides.
        self._identity = resolve_model_identity(
            model,
            provider,
            family_override=family_override,
            version_override=version_override,
        )

        # Build OpenAI kwargs and create the synchronous client.
        openai_kwargs: dict[str, Any] = {}
        if api_key:
            openai_kwargs["api_key"] = api_key
        if base_url:
            openai_kwargs["base_url"] = base_url

        self._sync_client = instructor.from_openai(OpenAI(**openai_kwargs))
        self._async_client = instructor.from_openai(AsyncOpenAI(**openai_kwargs))

        logger.info(
            "LLMCommunicationClient initialised: model=%s provider=%s "
            "family=%s version=%s reasoning_effort=%s",
            self._model,
            self._identity.provider.value,
            self._identity.model_family,
            self._identity.model_version or "N/A",
            self._reasoning_effort,
        )

    # -- Properties -----------------------------------------------------------

    @property
    def model_identity(self) -> LLMModelIdentity:
        """Return the resolved identity information about the configured LLM."""
        return self._identity

    @property
    def model(self) -> str:
        """The model identifier."""
        return self._model

    # -- Core API -------------------------------------------------------------

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

        This method runs the synchronous ``instructor`` call in a thread
        pool so it can be ``await``-ed from async orchestration code.
        """
        if not messages:
            raise ValueError("messages must not be empty")
        if not (isinstance(response_model, type) and issubclass(response_model, BaseModel)):
            raise ValueError("response_model must be a BaseModel subclass")

        if max_retries is not None:
            effective_max_retries = max_retries
        else:
            effective_max_retries = self._default_max_retries
        effective_temperature = (
            temperature if temperature is not None else self._default_temperature
        )

        # Merge extra kwargs.
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
            "LLM generate_structured: model=%s response_model=%s max_retries=%d",
            self._model,
            response_model.__name__,
            effective_max_retries,
        )

        try:
            # Run synchronous instructor call in a thread to stay non-blocking.
            loop = asyncio.get_running_loop()
            response, raw_response = await loop.run_in_executor(
                None,
                lambda: self._sync_client.create_with_completion(**create_kwargs),
            )

            usage = parse_usage(raw_response)
            logger.info(
                "LLM structured call OK: model=%s response_model=%s "
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
                f"LLM call failed for {response_model.__name__}: {exc}",
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

        if max_retries is not None:
            effective_max_retries = max_retries
        else:
            effective_max_retries = self._default_max_retries
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
            "LLM generate_structured_sync: model=%s response_model=%s max_retries=%d",
            self._model,
            response_model.__name__,
            effective_max_retries,
        )

        try:
            response, raw_response = self._sync_client.create_with_completion(**create_kwargs)

            usage = parse_usage(raw_response)
            logger.info(
                "LLM structured call OK (sync): model=%s response_model=%s "
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
                f"LLM call failed for {response_model.__name__}: {exc}",
                model=self._model,
                cause=exc,
            ) from exc
