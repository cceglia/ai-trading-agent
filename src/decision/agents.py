import logging
from typing import Any

import instructor
from openai import OpenAI

from src.decision.models import DecisionOutput, MarketContextSummary, ReviewVerdict
from src.decision.prompts import (
    DECIDER_SYSTEM_PROMPT,
    REVIEWER_SYSTEM_PROMPT,
    SYNTHESIZER_SYSTEM_PROMPT,
)

logger = logging.getLogger(__name__)


class SynthesizerAgent:
    """Synthesizes market context from structure analysis and calendar."""

    def __init__(
        self,
        client: OpenAI | None = None,
        model: str = "gpt-4o",
        api_key: str | None = None,
        base_url: str | None = None,
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

    def synthesize(
        self,
        structure_analysis: dict[str, Any],
        calendar_events: list[dict[str, Any]],
        symbol: str,
    ) -> MarketContextSummary:
        logger.info("Synthesizing context for %s", symbol)

        result = self.client.create(
            model=self.model,
            response_model=MarketContextSummary,
            messages=[
                {"role": "system", "content": SYNTHESIZER_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Analyze {symbol} with structure: {structure_analysis} "
                        f"and events: {calendar_events}"
                    ),
                },
            ],
        )

        logger.info("Synthesis complete: bias=%s confidence=%s", result.bias, result.confidence)
        return result


class DeciderAgent:
    """Makes trading decisions based on market context."""

    def __init__(
        self,
        client: OpenAI | None = None,
        model: str = "gpt-4o",
        api_key: str | None = None,
        base_url: str | None = None,
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

    def decide(
        self,
        context: MarketContextSummary,
        positions: list[dict[str, Any]],
        pending_orders: list[dict[str, Any]],
        feedback: str | None = None,
    ) -> DecisionOutput:
        logger.info("Making decision for %s", context.symbol)

        prompt = (
            f"Context: {context.model_dump_json()}\n"
            f"Positions: {positions}\n"
            f"Orders: {pending_orders}"
        )
        if feedback:
            prompt += f"\nReviewer feedback: {feedback}"

        result = self.client.create(
            model=self.model,
            response_model=DecisionOutput,
            messages=[
                {"role": "system", "content": DECIDER_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )

        logger.info("Decision: action=%s", result.action)
        return result


class ReviewerAgent:
    """Reviews trading decisions and provides feedback."""

    def __init__(
        self,
        client: OpenAI | None = None,
        model: str = "gpt-4o",
        api_key: str | None = None,
        base_url: str | None = None,
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

    def review(
        self,
        decision: DecisionOutput,
        context: MarketContextSummary,
        calendar_events: list[dict[str, Any]],
    ) -> ReviewVerdict:
        logger.info("Reviewing decision for %s", decision.symbol)

        result = self.client.create(
            model=self.model,
            response_model=ReviewVerdict,
            messages=[
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
        )

        logger.info("Review complete: approved=%s", result.approved)
        return result
