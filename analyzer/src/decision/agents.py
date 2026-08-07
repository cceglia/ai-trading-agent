"""LLM agents for the trading pipeline.

The synthesizer is the only LLM integration point. Decisions and enforcement
are produced by the deterministic market-structure pipeline.
"""

from __future__ import annotations

import logging
from typing import Any

from src.decision.cost_tracker import CostTracker
from src.decision.llm_client import LLMClientProtocol
from src.decision.models import MarketContextSummary
from src.decision.prompts import SYNTHESIZER_SYSTEM_PROMPT
from src.decision.usage import LLMUsage

logger = logging.getLogger(__name__)


def _log_llm_call(
    agent_name: str,
    model: str,
    usage: LLMUsage,
    cost_tracker: CostTracker,
) -> LLMUsage:
    """Record an LLM call and log its cost. Returns enriched usage with costs."""
    enriched = cost_tracker.record_call(model, usage)
    logger.info(
        "LLM call: agent=%s model=%s input=%d cached=%d uncached=%d "
        "output=%d reasoning=%d total=%d cost=$%.6f",
        agent_name,
        model,
        enriched.input_tokens,
        enriched.cached_input_tokens,
        enriched.uncached_input_tokens,
        enriched.output_tokens,
        enriched.reasoning_tokens,
        enriched.total_tokens,
        enriched.total_cost,
    )
    return enriched


class SynthesizerAgent:
    """Synthesizes market context from structure analysis and calendar."""

    def __init__(
        self,
        llm_client: LLMClientProtocol,
        cost_tracker: CostTracker | None = None,
    ) -> None:
        self._llm_client = llm_client
        self.cost_tracker = cost_tracker or CostTracker()
        model = self._llm_client.model_identity.raw_model_identifier
        logger.info(
            "Agent=%s model=%s",
            self.__class__.__name__,
            model,
        )

    def synthesize(
        self,
        structure_analysis: dict[str, Any],
        calendar_events: list[dict[str, Any]],
        symbol: str,
        *,
        current_price: float | None = None,
        current_price_time: str | None = None,
        deterministic_setup: Any = None,
        risk_policy: Any = None,
        execution_policy: Any = None,
    ) -> MarketContextSummary:
        logger.info("Synthesizing context for %s", symbol)

        messages: list[dict[str, str]] = [
            {"role": "system", "content": SYNTHESIZER_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Analyze {symbol} with structure: {structure_analysis} "
                    f"and events: {calendar_events}"
                    f" Current price (canonical most-recent closed bar across D1/H4/H1): "
                    f"{current_price} as of {current_price_time}. "
                    "The following deterministic facts are authoritative and must only be "
                    "explained, never changed: "
                    f"setup={deterministic_setup}, risk_policy={risk_policy}, "
                    f"execution_policy={execution_policy}."
                ),
            },
        ]

        response, usage = self._llm_client.generate_structured_sync(
            messages=messages,
            response_model=MarketContextSummary,
        )

        model = self._llm_client.model_identity.raw_model_identifier
        _log_llm_call(self.__class__.__name__, model, usage, self.cost_tracker)

        logger.info("Synthesis complete: bias=%s confidence=%s", response.bias, response.confidence)
        return response
