import json
import logging

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Trading agent configuration."""

    # LLM Configuration
    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o", description="Model to use")
    openai_base_url: str = Field(
        default="", description="OpenAI-compatible base URL (empty = use default)"
    )

    openai_reasoning_effort: str = Field(
        default="", description="OpenAI reasoning_effort (low/medium/high), empty = not set"
    )

    # Terminal MCP Configuration
    terminal_server_url: str = Field(
        default="http://127.0.0.1:22346/mcp", description="Terminal MCP server URL for candle data"
    )
    terminal_api_key: str = Field(
        default="", description="Bearer token for terminal MCP server authentication"
    )

    # Review Configuration
    max_review_attempts: int = Field(default=2, description="Maximum review retry attempts")

    # Cost Configuration
    cost_per_symbol_limit: float = Field(
        default=0.05, description="Maximum cost per symbol analysis in USD"
    )

    # Model Pricing Configuration
    model_pricing: dict[str, dict[str, float]] = Field(
        default={
            "gpt-4o": {"prompt": 0.0000025, "completion": 0.00001},
            "gpt-4o-mini": {"prompt": 0.00000015, "completion": 0.0000006},
            "gpt-4": {"prompt": 0.00003, "completion": 0.00006},
            "gpt-3.5-turbo": {"prompt": 0.0000005, "completion": 0.0000015},
            "DeepSeek-V4-Flash": {"prompt": 0.00000009, "completion": 0.00000018},
            "DeepSeek-V4-Pro": {"prompt": 0.000000435, "completion": 0.00000087},
        },
        description="Per-model token pricing: {model: {prompt: $/token, completion: $/token}}",
    )

    @field_validator("model_pricing", mode="before")
    @classmethod
    def parse_model_pricing(cls, v: object) -> object:
        """Parse JSON string env var and validate all prices are non-negative."""
        if isinstance(v, str):
            v = json.loads(v)
        if isinstance(v, dict):
            for model, prices in v.items():
                if not isinstance(prices, dict):
                    raise ValueError(
                        f"Invalid pricing for {model!r}: expected dict, got {type(prices).__name__}"
                    )
                for key in ("prompt", "completion"):
                    val = prices.get(key)
                    if val is None:
                        raise ValueError(f"Missing {key!r} price for {model!r}")
                    if not isinstance(val, int | float):
                        raise ValueError(f"Invalid {key!r} price for {model!r}: {val!r}")
                    if val == 0:
                        logger.warning(
                            "Zero %s price for model %r — cost tracking will undercount",
                            key,
                            model,
                        )
                    if val < 0:
                        raise ValueError(
                            f"{key!r} price for {model!r} must be non-negative, got {val}"
                        )
        return v

    # Calendar Configuration
    calendar_cache_hours: int = Field(default=4, description="Hours to cache calendar events")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")

    # Candle Cache Configuration
    d1_close_time: str = Field(
        default="17:00", description="D1 candle close time (HH:MM broker time)"
    )
    h4_close_time: str = Field(default="00:00", description="H4 anchor time (HH:MM broker time)")
    h4_close_interval_hours: int = Field(default=4, description="H4 interval in hours")
    analysis_cache_dir: str = Field(
        default="data", description="Base directory for analysis cache and run results"
    )
    synthesizer_cache_enabled: bool = Field(
        default=True, description="Enable synthesizer output caching"
    )

    model_config = {"env_prefix": "TRADING_", "env_file": ".env"}


"""
## Cost Analysis

### LLM Calls per Symbol
1. Synthesizer: 1 call (structure + calendar → context)
2. Decider: 1 call (context + positions → decision)
3. Reviewer: 1 call (context + decision → verdict)
4. Decider retry: up to MAX_REVIEW_ATTEMPTS calls (with feedback)
5. Reviewer retry: up to MAX_REVIEW_ATTEMPTS calls (re-review)

**Total: up to (2 + 2 * MAX_REVIEW_ATTEMPTS) LLM calls per symbol**
With default MAX_REVIEW_ATTEMPTS=2: up to 6 calls per symbol

### Token Estimates (GPT-4o)
- Synthesizer: ~2000 input, ~500 output
- Decider: ~1500 input, ~300 output
- Reviewer: ~1500 input, ~200 output

**Total: ~5000 input, ~1000 output per symbol**

### Cost Estimate (GPT-4o)
- Input: $2.50/1M tokens → $0.0125
- Output: $10.00/1M tokens → $0.0100
- **Total: ~$0.0225 per symbol**

### Optimization Strategies
1. MAX_REVIEW_ATTEMPTS: Configurable (default: 2)
2. Prompt optimization: Reduce token count
3. Caching: Cache similar analyses
4. Batch processing: Process multiple symbols
"""
