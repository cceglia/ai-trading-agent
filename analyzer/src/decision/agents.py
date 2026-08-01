"""LLM agents for the trading pipeline.

Each agent owns a slice of the analysis pipeline (synthesise context, make
a decision, review) and delegates all LLM communication to an injected
:class:`LLMClientProtocol` implementation.
"""

from __future__ import annotations

import logging
from typing import Any

from src.decision.cost_tracker import CostTracker
from src.decision.llm_client import LLMClientProtocol
from src.decision.models import DecisionOutput, MarketContextSummary, ReviewVerdict
from src.decision.prompts import (
    DECIDER_SYSTEM_PROMPT,
    REVIEWER_SYSTEM_PROMPT,
    SYNTHESIZER_SYSTEM_PROMPT,
)
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
                    f"{current_price} as of {current_price_time}"
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


class DeciderAgent:
    """Makes trading decisions based on market context."""

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

    def decide(
        self,
        context: MarketContextSummary,
        positions: list[dict[str, Any]],
        pending_orders: list[dict[str, Any]],
        feedback: str | None = None,
        *,
        current_price: float | None = None,
        order_type: str | None = None,
    ) -> DecisionOutput:
        logger.info("Making decision for %s", context.symbol)

        prompt = (
            f"Use current_price={current_price} as the price anchor. "
            f"The deterministic order_type is {order_type}; it is immutable canonical context "
            "and may be explained or flagged but never overridden. "
            f"Context: {context.model_dump_json()}\n"
            f"Positions: {positions}\n"
            f"Orders: {pending_orders}"
        )
        if feedback:
            prompt += f"\nReviewer feedback: {feedback}"

        messages: list[dict[str, str]] = [
            {"role": "system", "content": DECIDER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        response, usage = self._llm_client.generate_structured_sync(
            messages=messages,
            response_model=DecisionOutput,
        )

        model = self._llm_client.model_identity.raw_model_identifier
        _log_llm_call(self.__class__.__name__, model, usage, self.cost_tracker)

        logger.info("Decision: action=%s", response.action)
        return response


class ReviewerAgent:
    """Reviews trading decisions and provides feedback."""

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

    def review(
        self,
        decision: DecisionOutput,
        context: MarketContextSummary,
        calendar_events: list[dict[str, Any]],
        *,
        order_type: str | None = None,
    ) -> ReviewVerdict:
        logger.info("Reviewing decision for %s", decision.symbol)

        messages: list[dict[str, str]] = [
            {"role": "system", "content": REVIEWER_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Deterministic order_type (immutable canonical context): {order_type}\n"
                    f"Decision: {decision.model_dump_json()}\n"
                    f"Context: {context.model_dump_json()}\n"
                    f"Calendar: {calendar_events}"
                ),
            },
        ]

        response, usage = self._llm_client.generate_structured_sync(
            messages=messages,
            response_model=ReviewVerdict,
        )

        model = self._llm_client.model_identity.raw_model_identifier
        _log_llm_call(self.__class__.__name__, model, usage, self.cost_tracker)

        logger.info("Review complete: approved=%s", response.approved)
        return response
