# Trading AI Agent

AI-powered trading agent for multi-timeframe market structure analysis, economic calendar monitoring, and advisory-only trading decision-making.

## Overview

This agent combines a **16-module deterministic market structure engine** with **LLM-based decision synthesis** to provide advisory-only trading recommendations. It analyzes market structure across D1, H4, and H1 timeframes, evaluates economic calendar events, and produces structured trading decisions through a LangGraph orchestration pipeline with automated review loops.

**Key characteristics:**

- **Advisory-only** — `entry_authorized` is always `False`; the system never executes trades
- **Protocol-based dependency injection** — all dependencies wired via `DataSource`, `CalendarProvider`, and `StructureAnalyzer` protocols
- **Deterministic market structure engine** — 16 self-contained modules for swing detection, BOS/CHoCH, liquidity, support/resistance, and confidence scoring
- **LLM-enhanced synthesis** — context synthesis, decision generation, and independent review via structured output (Instructor + OpenAI)
- **Cost-controlled** — `CostTracker` tracks per-symbol spend against configurable limits using model-specific pricing tables
- **Synthesizer caching** — caches identical analysis inputs to eliminate redundant LLM calls
- **MTF candle caching** — disk-backed cache keyed by symbol/timeframe/close-time for faster re-analysis
- **Knowledge graph** — graphify-updated dependency graph supports codebase queries and cross-file navigation
- **Pre-commit hooks** — automated `ruff` lint+format, `mypy` static checks, and graphify update on commit

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Trading Graph                               │
│                     (LangGraph Orchestrator)                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐     │
│  │  fetch   │───▶│ analyze  │───▶│evaluate  │───▶│synthesize│     │
│  │  _data   │    │structure │    │calendar  │    │ _context │     │
│  └──────────┘    └──────────┘    └──────────┘    └────┬─────┘     │
│                                                        │           │
│                                              ┌─────────▼────────┐  │
│                                              │     decide       │  │
│                                              └─────────┬────────┘  │
│                                                        │           │
│                                    ┌───────────────────▼─────────┐ │
│                                    │          review             │ │
│                                    └───────────────────┬─────────┘ │
│                                                        │           │
│                                        ┌───────────────▼────────┐  │
│                                        │  retry (if rejected)   │  │
│                                        └────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

Dependencies (Protocol-based DI):
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   DataSource     │  │StructureAnalyzer │  │CalendarProvider  │
│   (Protocol)     │  │   (Protocol)     │  │   (Protocol)     │
└────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘
         │                     │                      │
┌────────▼─────────┐  ┌────────▼─────────┐  ┌────────▼─────────┐
│TerminalDataProv. │  │MarketStructure   │  │ForexFactory      │
│  (MT5 via MCP)   │  │    Engine        │  │   Calendar       │
└──────────────────┘  └──────────────────┘  └──────────────────┘

Supporting Modules:
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   CandleCache    │  │   Synthesizer    │  │   CostTracker    │
│ (MTF disk cache) │  │ Cache (LLM dedup)│  │ (model pricing)  │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

### Design Principles

- **SOLID**: Single responsibility per module, open for extension via protocols
- **Dependency Injection**: All dependencies injected via protocol interfaces; orchestration code never imports concrete implementations
- **Advisory-Only**: System never executes trades; `entry_authorized` is always `False` (enforced via invariant check)
- **Cost Control**: Configurable per-symbol spend limits with model-specific token pricing
- **Cache-Heavy**: Multi-level caching (candle data + synthesizer output) reduces redundant computation and LLM calls
- **Broker-Local Time**: All time-sensitive operations align to broker/server time, not local wall clock

## Installation

### Prerequisites

- Python 3.11+
- MetaTrader 5 terminal running (for live data) with a matching MCP server
- OpenAI API key or compatible LLM endpoint

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd Agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -e .

# Install dev dependencies (optional)
pip install -e ".[dev]"
```

### Environment Configuration

```bash
# Copy environment template
cp .env.template .env

# Edit .env with your settings (see configuration table below)
```

## Configuration

### Environment Variables

All settings use the `TRADING_` prefix and are loaded via `pydantic-settings` from `.env` or the environment.

| Variable | Default | Description |
|----------|---------|-------------|
| **Terminal / Data** | | |
| `TRADING_TERMINAL_SERVER_URL` | `http://127.0.0.1:22346/mcp` | MCP server URL for MT5 candle data and positions |
| `TRADING_TERMINAL_API_KEY` | — | Bearer token for terminal MCP server authentication |
| **LLM** | | |
| `TRADING_OPENAI_API_KEY` | — | OpenAI API key (or compatible provider) |
| `TRADING_OPENAI_MODEL` | `gpt-4o` | LLM model identifier |
| `TRADING_OPENAI_BASE_URL` | `""` | OpenAI-compatible base URL (e.g. Ollama `http://localhost:11434/v1`, Groq, etc.); empty = `https://api.openai.com/v1` |
| `TRADING_OPENAI_REASONING_EFFORT` | `""` | Reasoning effort level (`low`, `medium`, `high`); empty = model default |
| **Review & Cost** | | |
| `TRADING_MAX_REVIEW_ATTEMPTS` | `2` | Maximum review retry attempts per symbol |
| `TRADING_COST_PER_SYMBOL_LIMIT` | `0.05` | Maximum allowed LLM cost per symbol (USD) |
| `TRADING_MODEL_PRICING` | *(see below)* | JSON dict of per-model token prices: `{"model": {"prompt": $/token, "completion": $/token}}` |
| **Caching & Calendar** | | |
| `TRADING_CALENDAR_CACHE_HOURS` | `4` | Hours to cache ForexFactory calendar events |
| `TRADING_SYNTHESIZER_CACHE_ENABLED` | `True` | Enable LLM synthesizer output caching |
| `TRADING_ANALYSIS_CACHE_DIR` | `analysis` | Base directory for analysis disk cache |
| **Candle Close Times** | | |
| `TRADING_D1_CLOSE_TIME` | `17:00` | D1 candle close time (`HH:MM` in broker time) |
| `TRADING_H4_CLOSE_TIME` | `00:00` | H4 anchor time (`HH:MM` in broker time) |
| `TRADING_H4_CLOSE_INTERVAL_HOURS` | `4` | H4 interval in hours |
| **Logging** | | |
| `TRADING_LOG_LEVEL` | `INFO` | Logging level |

### Default Model Pricing

```json
{
  "gpt-4o":             {"prompt": 0.0000025,  "completion": 0.00001},
  "gpt-4o-mini":        {"prompt": 0.00000015, "completion": 0.0000006},
  "gpt-4":              {"prompt": 0.00003,    "completion": 0.00006},
  "gpt-3.5-turbo":      {"prompt": 0.0000005,  "completion": 0.0000015},
  "DeepSeek-V4-Flash":  {"prompt": 0.00000009, "completion": 0.00000018},
  "DeepSeek-V4-Pro":    {"prompt": 0.000000435,"completion": 0.00000087}
}
```

Override via `TRADING_MODEL_PRICING` as a JSON environment variable. Any price set to `0` logs a warning — cost tracking will undercount.

### Cost Analysis

LLM calls per symbol pipeline:

| Step | Calls | Description |
|------|-------|-------------|
| 1. Synthesizer | 1 | Structure analysis + calendar → market context |
| 2. Decider | 1 | Context + positions → decision |
| 3. Reviewer | 1 | Context + decision → verdict |
| 4. Decider retry | up to `MAX_REVIEW_ATTEMPTS` | Revised decision with reviewer feedback |
| 5. Reviewer retry | up to `MAX_REVIEW_ATTEMPTS` | Re-review of revised decision |

**Total: up to `(2 + 2 × MAX_REVIEW_ATTEMPTS)` LLM calls per symbol**

With default `MAX_REVIEW_ATTEMPTS=2`: **up to 6 calls per symbol**

#### Token Estimates (GPT-4o)

| Agent | Input tokens | Output tokens |
|-------|-------------|--------------|
| Synthesizer | ~2,000 | ~500 |
| Decider | ~1,500 | ~300 |
| Reviewer | ~1,500 | ~200 |
| **Total** | **~5,000** | **~1,000** |

#### Cost Estimate (GPT-4o)

- Input: $2.50/1M tokens → $0.0125
- Output: $10.00/1M tokens → $0.0100
- **Total: ~$0.0225 per symbol** (without retries)

`CostTracker` enforces the per-symbol limit at runtime and logs cumulative costs.

## Usage

### CLI

```bash
# Analyze a single symbol
python main.py EURUSD

# Specify model and base URL (e.g., for local Ollama)
python main.py EURUSD --model DeepSeek-V4-Flash --base-url http://localhost:11434/v1

# Override log level
python main.py EURUSD --log-level DEBUG
```

### Programmatic Usage

```python
from config.settings import Settings
from src.data.terminal_data_provider import TerminalDataProvider
from src.analysis.structure_analyzer import MarketStructureEngine
from src.calendar.forexfactory import ForexFactoryCalendar
from src.decision.agents import SynthesizerAgent, DeciderAgent, ReviewerAgent
from src.decision.cost_tracker import CostTracker
from src.orchestrator.graph import TradingGraph

# Initialize settings (loads from .env / environment)
settings = Settings()

# Cost tracking with model-specific pricing
cost_tracker = CostTracker(pricing=settings.model_pricing)

# Wire up data provider
data_provider = TerminalDataProvider(
    server_url=settings.terminal_server_url,
    api_key=settings.terminal_api_key,
)

# Wire up analysis and calendar
structure_analyzer = MarketStructureEngine()
calendar_provider = ForexFactoryCalendar()

# Wire up LLM agents (all share the same cost_tracker)
synthesizer = SynthesizerAgent(
    model=settings.openai_model,
    api_key=settings.openai_api_key or None,
    base_url=settings.openai_base_url or None,
    reasoning_effort=settings.openai_reasoning_effort or None,
    cost_tracker=cost_tracker,
)
decider = DeciderAgent(
    model=settings.openai_model,
    api_key=settings.openai_api_key or None,
    base_url=settings.openai_base_url or None,
    reasoning_effort=settings.openai_reasoning_effort or None,
    cost_tracker=cost_tracker,
)
reviewer = ReviewerAgent(
    model=settings.openai_model,
    api_key=settings.openai_api_key or None,
    base_url=settings.openai_base_url or None,
    reasoning_effort=settings.openai_reasoning_effort or None,
    cost_tracker=cost_tracker,
)

# Create and run graph
graph = TradingGraph(
    data_provider=data_provider,
    structure_analyzer=structure_analyzer,
    calendar_provider=calendar_provider,
    synthesizer=synthesizer,
    decider=decider,
    reviewer=reviewer,
)

result = graph.run("EURUSD")
```

## Project Structure

```
├── main.py                          # CLI entry point
├── config/
│   └── settings.py                  # Pydantic BaseSettings with env prefix TRADING_
├── src/
│   ├── logging_config.py            # Logging configuration
│   ├── analysis/
│   │   ├── candle_cache.py          # MTF candle data disk cache
│   │   ├── structure_analyzer.py    # Protocol adapter → engine
│   │   └── market_structure_engine/ # 16-module deterministic engine
│   │       ├── candles.py           # Candle data handling
│   │       ├── config.py            # Engine configuration
│   │       ├── context.py           # Analysis context
│   │       ├── engine.py            # Core engine pipeline
│   │       ├── errors.py            # Error definitions
│   │       ├── events.py            # BOS/CHoCH detection
│   │       ├── indicators.py        # Technical indicators
│   │       ├── levels.py            # Support/resistance mapping
│   │       ├── liquidity.py         # Liquidity analysis
│   │       ├── review.py            # Analysis review
│   │       ├── scoring.py           # Confidence scoring
│   │       ├── structure.py         # Market structure state
│   │       ├── swings.py            # Swing detection
│   │       ├── utils.py             # Utilities
│   │       └── validation.py        # Data validation
│   ├── decision/
│   │   ├── protocols.py             # DataSource, CalendarProvider, StructureAnalyzer
│   │   ├── models.py                # Pydantic models for structured output
│   │   ├── agents.py                # SynthesizerAgent, DeciderAgent, ReviewerAgent
│   │   ├── prompts.py               # Agent system/user prompts
│   │   ├── cost_tracker.py          # Per-symbol cost tracking with model pricing
│   │   └── synthesizer_cache.py     # LLM output deduplication cache
│   ├── data/
│   │   ├── terminal_data_provider.py # MT5 data via MCP server (retry, auth, broker-time)
│   │   └── snapshot_builder.py       # Multi-timeframe data snapshots
│   ├── calendar/
│   │   ├── forexfactory.py          # ForexFactory scraper with 4h cache
│   │   └── evaluator.py             # Event filtering by currency & impact
│   └── orchestrator/
│       └── graph.py                  # LangGraph state machine (6-node pipeline)
├── tests/                           # 356 tests (unit + integration)
│   ├── analysis/
│   │   ├── test_candle_cache.py
│   │   └── test_engine_fields.py
│   ├── calendar/
│   │   └── test_evaluator.py
│   ├── config/
│   │   └── test_settings.py
│   ├── data/
│   │   ├── test_snapshot_builder.py
│   │   └── test_terminal_data_provider.py
│   ├── decision/
│   │   ├── test_agents.py
│   │   ├── test_agents_api_key.py
│   │   ├── test_agents_prompts.py
│   │   ├── test_cost_tracker.py
│   │   ├── test_models.py
│   │   ├── test_prompts.py
│   │   ├── test_protocols.py
│   │   └── test_synthesizer_cache.py
│   └── orchestrator/
│       ├── test_canonical_price.py
│       ├── test_graph.py
│       └── test_synthesizer_cache.py
├── rules.json                       # Bias calculation rules & evidence hierarchy
├── .pre-commit-config.yaml          # ruff, mypy, trailing-whitespace, graphify
├── graphify-out/                    # Auto-generated knowledge graph
├── pyproject.toml                   # Project metadata & tool config
└── .env.template                    # Environment variable template
```

## Components

### Data Layer (`src/data/`)

- **TerminalDataProvider** (`DataSource` protocol): Fetches OHLC candles, positions, pending orders, and broker-local time from MetaTrader 5 via an MCP server. Implements retry logic with exponential backoff and optional bearer-token authentication.
- **SnapshotBuilder** (`src/data/snapshot_builder.py`): Constructs multi-timeframe (D1/H4/H1) data snapshots enriched with current price, structure analysis results, and calendar events.

### Analysis Layer (`src/analysis/`)

- **MarketStructureEngine** (`StructureAnalyzer` protocol): 16-module deterministic engine for technical analysis. Operates on OHLC data without any stochastic or LLM components:
  - Swing detection and classification
  - BOS (Break of Structure) and CHoCH (Change of Character) identification
  - Support/resistance level mapping (swing highs/lows, structural levels)
  - Liquidity analysis (stop-run clusters, order-block detection)
  - Multi-timeframe alignment and confidence scoring
  - All outputs are deterministic — same input always produces same result
- **Candle Cache** (`src/analysis/candle_cache.py`): Disk-backed cache for MTF analysis results, keyed by `symbol/timeframe/candle_close_time`. Determines when re-analysis is needed based on broker-local time and cached candle periods. Reduces MCP server round-trips on repeated analysis of the same closed candles.

### Decision Layer (`src/decision/`)

- **Protocols** (`protocols.py`): `DataSource`, `CalendarProvider`, `StructureAnalyzer` — runtime-checkable `typing.Protocol` interfaces for dependency injection.
- **Models** (`models.py`): Pydantic models for `MarketContextSummary`, `DecisionOutput` (with `entry_authorized: bool = False`), `ReviewVerdict`, and supporting types.
- **Agents** (`agents.py`): LLM-powered agents using Instructor for structured JSON output:
  - `SynthesizerAgent` — combines structure analysis + calendar events → market context summary
  - `DeciderAgent` — generates trading decision (direction, entry, SL, TP, risk-reward) based on context
  - `ReviewerAgent` — independent quality review of the decision with veto power
- **CostTracker** (`cost_tracker.py`): Tracks cumulative token usage and USD cost per analysis run using model-specific pricing tables. Raises a `CostLimitExceeded` error when `cost_per_symbol_limit` is reached.
- **SynthesizerCache** (`synthesizer_cache.py`): Content-addressable cache for synthesizer outputs. When identical analysis inputs are re-encountered (same structure state + calendar events), the cached LLM response is returned, saving both time and cost.

### Calendar Layer (`src/calendar/`)

- **ForexFactoryCalendar** (`CalendarProvider` protocol): Scrapes ForexFactory economic calendar with 4-hour in-memory caching. Filters by upcoming events.
- **Evaluator**: Filters events by relevant currencies and impact level (high/medium/low) for the analyzed symbol.

### Orchestrator (`src/orchestrator/`)

- **TradingGraph**: LangGraph state machine managing the 6-node analysis pipeline:
  1. `fetch_data` — retrieves candles, positions, and broker time
  2. `analyze_structure` — runs the deterministic market structure engine
  3. `evaluate_calendar` — fetches and filters economic events
  4. `synthesize_context` — LLM combines structure + calendar into a narrative context
  5. `decide` — LLM generates a trading decision with specific levels
  6. `review` — LLM independently reviews the decision; if rejected, loops back to `decide` (up to `MAX_REVIEW_ATTEMPTS`)
  - The advisory-only invariant is enforced at the model layer: `DecisionOutput.entry_authorized` defaults to `False` and its Pydantic validator forces it to `False` regardless of LLM output; the structure analyzer also rejects any engine result where `entry_authorized` is not `False`.

### Configuration (`config/`)

- **Settings**: Pydantic `BaseSettings` class binding all environment variables (`TRADING_*` prefix). Supports `.env` file loading, field validation, and complex types like `dict[str, dict[str, float]]` for model pricing (auto-parsed from JSON env var).

## Testing

```bash
# Run all tests (356 tests)
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run a specific test file
pytest tests/decision/test_cost_tracker.py -v

# Run tests matching a keyword
pytest -k "cache"
```

### Test Coverage

The test suite contains **356 tests** covering:

- **Analysis**: Candle cache engine fields
- **Calendar**: Event evaluator logic
- **Config**: Settings loading, env prefix, validation, model pricing
- **Data**: Snapshot builder, terminal data provider (retry, auth, broker time)
- **Decision**: Agents (API key handling, prompt rendering), cost tracker, models, protocols, synthesizer cache
- **Orchestrator**: Full graph pipeline, canonical price handling, synthesizer cache integration
- **Main**: CLI entry point argument handling

All external dependencies (MT5 terminal, LLM API, ForexFactory) are mocked in tests.

## Development

### Code Quality

```bash
# Static type checking (strict mode)
mypy src/

# Linting
ruff check src/

# Auto-format
ruff format src/
```

### Pre-commit Hooks

The repository includes a `.pre-commit-config.yaml` that runs automatically on `git commit`:

| Hook | Action |
|------|--------|
| `ruff` | Lint with auto-fix (blocks on unfixed issues) |
| `ruff-format` | Format Python code |
| `mypy` | Static type check (`src/` only) |
| `trailing-whitespace` | Trim trailing whitespace |
| `end-of-file-fixer` | Ensure files end with newline |
| `check-yaml` | Validate YAML files |
| `check-added-large-files` | Warn on large files (excludes `graphify-out/`) |
| `check-merge-conflict` | Block unresolved merge markers |
| `debug-statements` | Catch stray `pdb`/`breakpoint()` calls |
| `graphify-update` | Rebuild knowledge graph on code changes |

Install hooks:

```bash
pre-commit install
```

### Knowledge Graph

A persistent knowledge graph is maintained at `graphify-out/` with god nodes, community structure, and cross-file relationships. It auto-updates on commit via pre-commit hook, or can be rebuilt manually:

```bash
graphify update .
```

Use for codebase queries:

```bash
graphify query "<question>"
graphify path "<A>" "<B>"
graphify explain "<concept>"
```

### Contributing

1. Follow existing code conventions
2. All functions must have type hints
3. Write tests for new functionality
4. Run `mypy src/ && ruff check src/ && pytest` before committing
5. Ensure `entry_authorized = False` in all decision outputs (the graph enforces this)
6. Install pre-commit hooks to catch issues early

### Dependencies

**Core:**
- `instructor` — Structured LLM output
- `langgraph` — Workflow orchestration (LangGraph state machine)
- `pydantic-settings` — Configuration management with env prefix
- `openai` — LLM API client (also works with compatible providers)
- `mcp` — Model Context Protocol client
- `requests` + `beautifulsoup4` — Web scraping (ForexFactory)

**Dev:**
- `pytest` + `pytest-asyncio` + `pytest-cov` — Testing
- `mypy` — Static type checking (strict mode)
- `ruff` — Linter and formatter
- `responses` — HTTP request mocking
- `pre-commit` — Git hook framework

## License

MIT License
