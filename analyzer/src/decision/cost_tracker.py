"""CostTracker — tracks LLM API call costs.

Exposes a single :class:`CostTracker` that records per-call token usage
and accumulates total cost using per-model pricing rates.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class CostLimitExceeded(Exception):  # noqa: N818 — domain-specific exception; "Exceeded" suffix is convention in this codebase
    """Raised when per-symbol LLM cost exceeds the configured limit."""

    def __init__(self, limit: float, total_cost: float, symbol: str | None = None) -> None:
        self.limit = limit
        self.total_cost = total_cost
        self.symbol = symbol
        msg = f"Cost limit ${limit:.4f} exceeded (total: ${total_cost:.4f})"
        if symbol:
            msg += f" for {symbol}"
        super().__init__(msg)


DEFAULT_PRICING: dict[str, dict[str, float]] = {
    "gpt-4o": {"prompt": 0.0000025, "completion": 0.00001},
    "gpt-4o-mini": {"prompt": 0.00000015, "completion": 0.0000006},
    "gpt-4": {"prompt": 0.00003, "completion": 0.00006},
    "gpt-3.5-turbo": {"prompt": 0.0000005, "completion": 0.0000015},
}


class CostTracker:
    """Tracks LLM API call costs using per-model token pricing.

    Each instance is independent — no global state is shared.
    Thread safety is not provided (single-threaded use only).

    Parameters
    ----------
    pricing:
        Mapping of ``model_name -> {"prompt": rate, "completion": rate}``.
        If ``None``, :data:`DEFAULT_PRICING` is used.
    """

    def __init__(
        self,
        pricing: dict[str, dict[str, float]] | None = None,
    ) -> None:
        self._pricing = pricing if pricing is not None else DEFAULT_PRICING
        self._total_cost: float = 0.0
        self._call_count: int = 0
        self._limit: float | None = None
        self._symbol: str | None = None  # ← NEW: symbol for error context

    def set_limit(self, limit: float) -> None:
        """Set a per-symbol cost limit.

        When *limit* is ``<= 0`` the limit check is disabled.
        When *total_cost* exceeds *limit* after a ``record_call()``,
        ``CostLimitExceeded`` is raised.
        """
        if limit is None or limit <= 0:  # ← was: if limit <= 0
            self._limit = None
        else:
            self._limit = limit

    def set_symbol(self, symbol: str) -> None:
        """Set the current symbol for error context.

        The symbol is used by :meth:`record_call` when raising
        :class:`CostLimitExceeded` to indicate which symbol
        exceeded the cost limit.

        Args:
            symbol: Trading symbol (e.g. ``"XAUUSD"``).
        """
        self._symbol = symbol

    def record_call(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> float:
        """Record an LLM API call and return its cost.

        Parameters
        ----------
        model:
            Model identifier (e.g. ``"gpt-4o"``). If the model is not
            present in *pricing*, a warning is logged and ``gpt-4o``
            rates are used as a fallback.
        prompt_tokens:
            Number of prompt (input) tokens consumed.
        completion_tokens:
            Number of completion (output) tokens consumed.

        Returns
        -------
        float
            The cost of this individual call.

        Raises
        ------
        ValueError
            If either token count is negative.
        """
        if prompt_tokens < 0 or completion_tokens < 0:
            raise ValueError("token counts must not be negative")

        if prompt_tokens == 0 and completion_tokens == 0:
            return 0.0

        if model not in self._pricing:
            logger.warning("Unknown model '%s', falling back to gpt-4o pricing", model)
            model = "gpt-4o"

        if model not in self._pricing:
            raise ValueError("empty pricing table — no model rates available")

        rates = self._pricing[model]
        cost = prompt_tokens * rates["prompt"] + completion_tokens * rates["completion"]
        self._total_cost += cost
        self._call_count += 1
        if self._limit is not None and self._total_cost > self._limit:
            raise CostLimitExceeded(
                limit=self._limit,
                total_cost=self._total_cost,
                symbol=self._symbol,
            )
        return cost

    @property
    def total_cost(self) -> float:
        """Accumulated cost across all recorded calls."""
        return self._total_cost

    @property
    def call_count(self) -> int:
        """Number of calls recorded."""
        return self._call_count

    def reset(self) -> None:
        """Reset accumulated cost and call count to zero."""
        self._total_cost = 0.0
        self._call_count = 0
