from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Trading agent configuration."""

    # LLM Configuration
    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o", description="Model to use")
    openai_base_url: str = Field(
        default="", description="OpenAI-compatible base URL (empty = use default)"
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
        default="analysis", description="Base directory for analysis cache"
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
