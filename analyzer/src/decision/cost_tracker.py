"""CostTracker — tracks LLM API call costs.

Exposes a single :class:`CostTracker` that records per-call token usage
and accumulates total cost using per-model pricing rates.

Pricing is supplied externally (typically from :class:`Settings`).
There is no compiled-in default pricing table — see ``config/settings.py``.
"""

from __future__ import annotations

import logging
from dataclasses import replace

from src.decision.usage import LLMUsage

logger = logging.getLogger(__name__)


class CostLimitExceeded(Exception):  # noqa: N818
    """Raised when per-symbol LLM cost exceeds the configured limit."""

    def __init__(self, limit: float, total_cost: float, symbol: str | None = None) -> None:
        self.limit = limit
        self.total_cost = total_cost
        self.symbol = symbol
        msg = f"Cost limit ${limit:.4f} exceeded (total: ${total_cost:.4f})"
        if symbol:
            msg += f" for {symbol}"
        super().__init__(msg)


class CostTracker:
    """Tracks LLM API call costs using per-model token pricing.

    Each instance is independent — no global state is shared.
    Thread safety is not provided (single-threaded use only).

    Parameters
    ----------
    pricing:
        Mapping of ``model_name -> {"input_per_million": rate,
        "cached_input_per_million": rate, "output_per_million": rate}``.
        When ``None``, an empty dict is used (all costs will be zero
        and a warning is logged on the first call).
    """

    def __init__(
        self,
        pricing: dict[str, dict[str, float]] | None = None,
    ) -> None:
        self._pricing = pricing if pricing is not None else {}
        self._total_cost: float = 0.0
        self._call_count: int = 0
        self._limit: float | None = None
        self._symbol: str | None = None

    def set_limit(self, limit: float) -> None:
        """Set a per-symbol cost limit.

        When *limit* is ``<= 0`` or ``None`` the limit check is disabled.
        When *total_cost* exceeds *limit* after a ``record_call()``,
        :class:`CostLimitExceeded` is raised.
        """
        if limit is None or limit <= 0:
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
        usage: LLMUsage,
    ) -> LLMUsage:
        """Record an LLM API call and return its usage with cost filled in.

        Parameters
        ----------
        model:
            Model identifier (e.g. ``"gpt-4o"``).  If the model is not
            present in *pricing* a warning is logged, token usage is
            preserved, and all costs are set to ``0.0``.
        usage:
            Parsed token usage (without costs — those are filled here).

        Returns
        -------
        LLMUsage
            A new ``LLMUsage`` with cost fields populated.

        Raises
        ------
        CostLimitExceeded
            If the accumulated total exceeds the configured limit.
        """
        self._call_count += 1

        prices = self._pricing.get(model)
        if prices is None:
            if not self._pricing:
                logger.warning("Pricing table is empty — costs are zero for all models")
            else:
                logger.warning(
                    "Unknown model %r — token usage preserved, costs set to zero",
                    model,
                )
            return replace(
                usage,
                input_cost=0.0,
                cached_input_cost=0.0,
                output_cost=0.0,
                total_cost=0.0,
            )

        # Extract prices — every key defaults to 0.0 when absent.
        input_price = prices.get("input_per_million", 0.0)
        cached_input_price = prices.get("cached_input_per_million", 0.0)
        output_price = prices.get("output_per_million", 0.0)

        input_cost = usage.uncached_input_tokens * input_price / 1_000_000
        cached_input_cost = usage.cached_input_tokens * cached_input_price / 1_000_000
        output_cost = usage.output_tokens * output_price / 1_000_000
        total_cost = input_cost + cached_input_cost + output_cost

        enriched = replace(
            usage,
            input_cost=input_cost,
            cached_input_cost=cached_input_cost,
            output_cost=output_cost,
            total_cost=total_cost,
        )

        self._total_cost += total_cost
        if self._limit is not None and self._total_cost > self._limit:
            raise CostLimitExceeded(
                limit=self._limit,
                total_cost=self._total_cost,
                symbol=self._symbol,
            )
        return enriched

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
