import json
import logging
from typing import Self

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings

# ExecutionMode is defined in the market_structure_engine models (canonical home).
# This try/except handles the case where the server test suite imports config.settings
# without the analyzer's src directory on sys.path.  The inline fallback mirrors the
# canonical enum exactly so there is never a value mismatch.
try:
    from src.analysis.market_structure_engine.models import ExecutionMode
except ImportError:
    from enum import StrEnum

    class ExecutionMode(StrEnum):  # type: ignore[no-redef]
        DETERMINISTIC_BACKTEST = "DETERMINISTIC_BACKTEST"
        FULL_CHAIN_BACKTEST = "FULL_CHAIN_BACKTEST"
        DEVELOPMENT = "DEVELOPMENT"
        SHADOW = "SHADOW"
        PAPER = "PAPER"
        LIVE = "LIVE"


logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Trading agent configuration."""

    # LLM Configuration
    primary_llm_provider: str = Field(
        default="openai",
        description="Provider for the primary LLM (currently only 'openai' is supported)",
    )
    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o", description="Model to use")
    openai_base_url: str = Field(
        default="", description="OpenAI-compatible base URL (empty = use default)"
    )

    openai_reasoning_effort: str = Field(
        default="", description="OpenAI reasoning_effort (low/medium/high), empty = not set"
    )

    openai_temperature: float = Field(
        default=0.0,
        ge=0.0,
        le=2.0,
        description="Temperature for the primary LLM (synthesizer + decider)",
    )

    openai_model_family_override: str | None = Field(
        default=None,
        description="Override the detected model family for the primary LLM",
    )
    openai_model_version_override: str | None = Field(
        default=None,
        description="Override the detected model version for the primary LLM",
    )

    # Reviewer LLM Configuration
    reviewer_llm_provider: str = Field(
        default="openai",
        description="Provider for the reviewer LLM (e.g. openai, anthropic)",
    )
    reviewer_model: str = Field(
        default="",
        description="Model identifier for the reviewer LLM (empty = use primary model)",
    )
    reviewer_model_family_override: str | None = Field(
        default=None,
        description="Override the detected model family for the reviewer",
    )
    reviewer_model_version_override: str | None = Field(
        default=None,
        description="Override the detected model version for the reviewer",
    )
    reviewer_api_key: str = Field(
        default="",
        description="API key for the reviewer LLM (empty = use primary API key)",
    )
    reviewer_base_url: str = Field(
        default="",
        description="Base URL for the reviewer LLM (empty = use default for provider)",
    )
    reviewer_temperature: float = Field(
        default=0.0,
        description="Temperature setting for the reviewer LLM",
    )
    reviewer_reasoning_effort: str = Field(
        default="",
        description="Reasoning effort for reviewer (low/medium/high), empty = not set",
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

    # Setup Policy
    enable_countertrend: bool = Field(
        default=False,
        description="Allow countertrend setups when enabled",
    )

    # R/R Thresholds
    min_rr_aaa: float = Field(
        default=2.0,
        description="Minimum reward-to-risk ratio for AAA-grade setups",
    )
    min_rr_aa: float = Field(
        default=2.0,
        description="Minimum reward-to-risk ratio for AA-grade setups",
    )
    min_rr_countertrend: float = Field(
        default=2.5,
        description="Minimum reward-to-risk ratio for countertrend setups",
    )

    # Risk Multipliers
    risk_multiplier_aaa: float = Field(
        default=1.0,
        description="Risk multiplier for AAA-grade setups",
    )
    risk_multiplier_aa: float = Field(
        default=0.5,
        description="Risk multiplier for AA-grade setups",
    )
    risk_multiplier_countertrend: float = Field(
        default=0.25,
        description="Risk multiplier for countertrend setups",
    )

    # Lifecycle Configuration
    setup_expiration_h1_bars: int = Field(
        default=3,
        description="Number of H1 bars before a setup expires",
    )

    # Reviewer Policy
    require_reviewer: bool = Field(
        default=True,
        description="Require an independent reviewer for executable decisions",
    )
    allow_unreviewed_decisions: bool = Field(
        default=False,
        description="Allow decisions without review (forbidden in paper/live mode)",
    )
    allow_same_model_different_deployment: bool = Field(
        default=False,
        description="Allow reviewer to use the same model family with a different deployment",
    )

    # Execution Mode
    execution_mode: ExecutionMode = Field(
        default=ExecutionMode.PAPER,
        description="Current execution mode of the trading system",
    )

    # Cost Configuration
    cost_per_symbol_limit: float = Field(
        default=0.05, description="Maximum cost per symbol analysis in USD"
    )

    # Model Pricing Configuration
    #
    # Environment variable (JSON — overrides the defaults below):
    #
    #   TRADING_MODEL_PRICING='{"gpt-4o": {"input_per_million": 2.5,
    #       "cached_input_per_million": 1.25, "output_per_million": 10.0}}'
    #
    # Migration from old format (removed):
    #   Old keys: {"prompt": $/token, "completion": $/token}
    #   New keys: {"input_per_million": $/M,
    #       "cached_input_per_million": $/M, "output_per_million": $/M}
    #
    # Prices are in dollars per million tokens.  Set cached_input_per_million to 0.0
    # when the provider does not offer a cached-input discount or when the price
    # has not been verified from official documentation.
    #
    # Only models with verified official pricing are included below.  Add additional
    # models via the TRADING_MODEL_PRICING env var.
    model_pricing: dict[str, dict[str, float]] = Field(
        default={
            "gpt-4o": {
                "input_per_million": 2.50,
                "cached_input_per_million": 1.25,  # verified OpenAI discount
                "output_per_million": 10.00,
            },
            "gpt-4o-mini": {
                "input_per_million": 0.15,
                "cached_input_per_million": 0.075,  # verified OpenAI discount
                "output_per_million": 0.60,
            },
            "gpt-4": {
                "input_per_million": 30.00,
                "cached_input_per_million": 0.0,  # not configured — no official cached-input price
                "output_per_million": 60.00,
            },
            "gpt-3.5-turbo": {
                "input_per_million": 0.50,
                "cached_input_per_million": 0.0,  # not configured — no official cached-input price
                "output_per_million": 1.50,
            },
        },
        description=(
            "Per-model token pricing: "
            "{model: {input_per_million: $/M, "
            "cached_input_per_million: $/M, output_per_million: $/M}}"
        ),
    )

    @field_validator("model_pricing", mode="before")
    @classmethod
    def parse_model_pricing(cls, v: object) -> object:
        """Parse JSON string env var and validate prices.

        Accepts only the new format keys (``input_per_million``,
        ``cached_input_per_million``, ``output_per_million``).
        Rejects booleans, negative values, NaN, infinity, and
        non-numeric values.
        """
        import math

        if isinstance(v, str):
            v = json.loads(v)
        if isinstance(v, dict):
            allowed_keys = {"input_per_million", "cached_input_per_million", "output_per_million"}
            for model, prices in v.items():
                if not isinstance(prices, dict):
                    raise ValueError(
                        f"Invalid pricing for {model!r}: expected dict, got {type(prices).__name__}"
                    )
                for key in allowed_keys:
                    val = prices.get(key, 0.0)
                    # A missing key is fine — defaults to 0.0 at lookup time
                    if key not in prices:
                        continue
                    if isinstance(val, bool):
                        raise ValueError(
                            f"Boolean {val!r} not allowed as {key!r} price for {model!r}"
                        )
                    if not isinstance(val, int | float):
                        raise ValueError(f"Invalid {key!r} price for {model!r}: {val!r}")
                    if math.isnan(val) or math.isinf(val):
                        raise ValueError(f"NaN/inf not allowed as {key!r} price for {model!r}")
                    if val < 0:
                        raise ValueError(
                            f"{key!r} price for {model!r} must be non-negative, got {val}"
                        )
                    # price == 0.0 is accepted silently (valid configuration)
        return v

    # Calendar Configuration
    calendar_cache_hours: int = Field(default=4, description="Hours to cache calendar events")

    # Telegram Notification Configuration
    telegram_bot_token: str = Field(
        default="", description="Telegram bot token for trade notifications"
    )
    telegram_chat_id: str = Field(default="", description="Telegram chat ID for notifications")
    web_ui_base_url: str = Field(
        default="http://localhost:3000", description="Web UI base URL for notification links"
    )

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

    @property
    def resolved_analysis_cache_dir(self) -> str:
        """Resolve ``analysis_cache_dir`` to an absolute path.

        Both the analyzer and server write/read from the same directory tree.
        Relative paths are resolved against the **project root** (the parent
        directory of ``analyzer/``) so that the default ``"data"`` produces
        ``<project_root>/data`` regardless of which package is the working
        directory.

        .. code-block:: text

            TRADING_ANALYSIS_CACHE_DIR=data   →  …/data
            TRADING_ANALYSIS_CACHE_DIR=/abs   →  /abs  (unchanged)
        """
        from pathlib import Path

        path = Path(self.analysis_cache_dir)
        if path.is_absolute():
            return str(path)
        # Resolve relative to the project root (parent of analyzer/)
        project_root = Path(__file__).resolve().parent.parent.parent
        return str(project_root / path)

    @model_validator(mode="after")
    def validate_execution_policy(self) -> Self:
        """Validate execution policy settings based on execution mode.

        Paper and Live modes require:
        - ``require_reviewer`` must be ``True``
        - ``allow_unreviewed_decisions`` must be ``False``
        - ``allow_same_model_different_deployment`` must be ``False``
        """
        if self.execution_mode in (ExecutionMode.PAPER, ExecutionMode.LIVE):
            if not self.require_reviewer:
                raise ValueError("require_reviewer must be True in paper/live execution mode")
            if self.allow_unreviewed_decisions:
                raise ValueError(
                    "allow_unreviewed_decisions must be False in paper/live execution mode"
                )
            if self.allow_same_model_different_deployment:
                raise ValueError(
                    "allow_same_model_different_deployment must be False "
                    "in paper/live execution mode"
                )
        return self

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
