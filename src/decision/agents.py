import logging
from typing import Any

import instructor
from openai import OpenAI

from src.decision.cost_tracker import CostTracker
from src.decision.models import DecisionOutput, MarketContextSummary, ReviewVerdict
from src.decision.prompts import (
    DECIDER_SYSTEM_PROMPT,
    REVIEWER_SYSTEM_PROMPT,
    SYNTHESIZER_SYSTEM_PROMPT,
)

logger = logging.getLogger(__name__)


def _log_llm_call(
    agent_name: str,
    model: str,
    usage: Any,
    cost_tracker: CostTracker,
) -> float | None:
    """Record an LLM call and log its cost. Returns cost or None if no usage."""
    if usage is not None:
        cost = cost_tracker.record_call(model, usage.prompt_tokens, usage.completion_tokens)
        logger.info(
            "LLM call: agent=%s model=%s tokens=(prompt=%d completion=%d total=%d) cost=$%.4f",
            agent_name,
            model,
            usage.prompt_tokens,
            usage.completion_tokens,
            usage.total_tokens,
            cost,
        )
        return cost
    else:
        logger.info(
            "LLM call: agent=%s model=%s tokens=N/A cost=N/A (no usage data)",
            agent_name,
            model,
        )
        return None


class SynthesizerAgent:
    """Synthesizes market context from structure analysis and calendar."""

    def __init__(
        self,
        client: OpenAI | None = None,
        model: str = "gpt-4o",
        api_key: str | None = None,
        base_url: str | None = None,
        reasoning_effort: str | None = None,
        cost_tracker: CostTracker | None = None,
    ):
        if client is not None:
            self.client = instructor.from_openai(client)
        else:
            openai_kwargs: dict[str, Any] = {}
            if api_key is not None:
                openai_kwargs["api_key"] = api_key
            if base_url is not None:
                openai_kwargs["base_url"] = base_url
            self.client = instructor.from_openai(OpenAI(**openai_kwargs))
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.cost_tracker = cost_tracker or CostTracker()
        logger.info("Agent=%s reasoning_effort=%s", self.__class__.__name__, self.reasoning_effort)

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

        create_kwargs: dict[str, Any] = {
            "model": self.model,
            "response_model": MarketContextSummary,
            "messages": [
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
            ],
        }
        if self.reasoning_effort:
            create_kwargs["reasoning_effort"] = self.reasoning_effort
        response, raw_response = self.client.create_with_completion(**create_kwargs)

        _log_llm_call(self.__class__.__name__, self.model, raw_response.usage, self.cost_tracker)

        logger.info("Synthesis complete: bias=%s confidence=%s", response.bias, response.confidence)
        return response  # type: ignore[no-any-return]


class DeciderAgent:
    """Makes trading decisions based on market context."""

    def __init__(
        self,
        client: OpenAI | None = None,
        model: str = "gpt-4o",
        api_key: str | None = None,
        base_url: str | None = None,
        reasoning_effort: str | None = None,
        cost_tracker: CostTracker | None = None,
    ):
        if client is not None:
            self.client = instructor.from_openai(client)
        else:
            openai_kwargs: dict[str, Any] = {}
            if api_key is not None:
                openai_kwargs["api_key"] = api_key
            if base_url is not None:
                openai_kwargs["base_url"] = base_url
            self.client = instructor.from_openai(OpenAI(**openai_kwargs))
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.cost_tracker = cost_tracker or CostTracker()
        logger.info("Agent=%s reasoning_effort=%s", self.__class__.__name__, self.reasoning_effort)

    def decide(
        self,
        context: MarketContextSummary,
        positions: list[dict[str, Any]],
        pending_orders: list[dict[str, Any]],
        feedback: str | None = None,
        *,
        current_price: float | None = None,
    ) -> DecisionOutput:
        logger.info("Making decision for %s", context.symbol)

        prompt = (
            f"Anchor entry_price and risk_reward_ratio to current_price={current_price}. "
            f"Context: {context.model_dump_json()}\n"
            f"Positions: {positions}\n"
            f"Orders: {pending_orders}"
        )
        if feedback:
            prompt += f"\nReviewer feedback: {feedback}"

        create_kwargs: dict[str, Any] = {
            "model": self.model,
            "response_model": DecisionOutput,
            "messages": [
                {"role": "system", "content": DECIDER_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        }
        if self.reasoning_effort:
            create_kwargs["reasoning_effort"] = self.reasoning_effort
        response, raw_response = self.client.create_with_completion(**create_kwargs)

        _log_llm_call(self.__class__.__name__, self.model, raw_response.usage, self.cost_tracker)

        logger.info("Decision: action=%s", response.action)
        return response  # type: ignore[no-any-return]


class ReviewerAgent:
    """Reviews trading decisions and provides feedback."""

    def __init__(
        self,
        client: OpenAI | None = None,
        model: str = "gpt-4o",
        api_key: str | None = None,
        base_url: str | None = None,
        reasoning_effort: str | None = None,
        cost_tracker: CostTracker | None = None,
    ):
        if client is not None:
            self.client = instructor.from_openai(client)
        else:
            openai_kwargs: dict[str, Any] = {}
            if api_key is not None:
                openai_kwargs["api_key"] = api_key
            if base_url is not None:
                openai_kwargs["base_url"] = base_url
            self.client = instructor.from_openai(OpenAI(**openai_kwargs))
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.cost_tracker = cost_tracker or CostTracker()
        logger.info("Agent=%s reasoning_effort=%s", self.__class__.__name__, self.reasoning_effort)

    def review(
        self,
        decision: DecisionOutput,
        context: MarketContextSummary,
        calendar_events: list[dict[str, Any]],
    ) -> ReviewVerdict:
        logger.info("Reviewing decision for %s", decision.symbol)

        create_kwargs: dict[str, Any] = {
            "model": self.model,
            "response_model": ReviewVerdict,
            "messages": [
                {"role": "system", "content": REVIEWER_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Decision: {decision.model_dump_json()}\n"
                        f"Context: {context.model_dump_json()}\n"
                        f"Calendar: {calendar_events}"
                    ),
                },
            ],
        }
        if self.reasoning_effort:
            create_kwargs["reasoning_effort"] = self.reasoning_effort
        response, raw_response = self.client.create_with_completion(**create_kwargs)

        _log_llm_call(self.__class__.__name__, self.model, raw_response.usage, self.cost_tracker)

        logger.info("Review complete: approved=%s", response.approved)
        return response  # type: ignore[no-any-return]
