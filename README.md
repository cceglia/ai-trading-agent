# Trading AI Agent

AI-powered trading agent for multi-timeframe market structure analysis, economic calendar monitoring, and trading decision-making.

## Overview

This agent combines deterministic technical analysis with LLM-based decision synthesis to provide advisory-only trading recommendations. It analyzes market structure across D1, H4, and H1 timeframes, evaluates economic calendar events, and produces structured trading decisions through a LangGraph orchestration pipeline with review loops.

**Key characteristics:**
- Advisory-only system (`entry_authorized` always false)
- Protocol-based dependency injection
- Deterministic market structure engine (16 modules)
- LLM-enhanced context synthesis and decision review
- Cost-controlled analysis (~$0.02 per symbol on GPT-4o)

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
┌───────────────┐  ┌─────────────────┐  ┌──────────────────┐
│  DataSource   │  │StructureAnalyzer│  │CalendarProvider  │
│  (Protocol)   │  │   (Protocol)    │  │   (Protocol)     │
└───────┬───────┘  └────────┬────────┘  └────────┬─────────┘
        │                   │                     │
┌───────▼───────┐  ┌────────▼────────┐  ┌────────▼─────────┐
│Mt5DataProvider│  │MarketStructure  │  │ForexFfactory     │
│               │  │    Engine       │  │   Calendar       │
└───────────────┘  └─────────────────┘  └──────────────────┘
```

### Design Principles

- **SOLID**: Single responsibility per module, open for extension via protocols
- **Dependency Injection**: All dependencies injected via protocol interfaces
- **Advisory-Only**: System never executes trades; `entry_authorized` always false
- **Cost Control**: Configurable limits on LLM calls per analysis

## Installation

### Prerequisites

- Python 3.11+
- MetaTrader 5 terminal running (for live data)
- MCP server for MT5 connectivity

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

# Edit .env with your settings
```

See [Configuration](#configuration) for available options.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `TRADING_MCP_SERVER_URL` | `http://localhost:8082` | MCP server URL for MT5 connectivity |
| `TRADING_OPENAI_API_KEY` | - | OpenAI API key for LLM calls |
| `TRADING_OPENAI_MODEL` | `gpt-4o` | LLM model to use |
| `TRADING_MAX_REVIEW_ATTEMPTS` | `2` | Maximum review retry attempts |
| `TRADING_COST_PER_SYMBOL_LIMIT` | `0.05` | Max cost per symbol analysis (USD) |
| `TRADING_CALENDAR_CACHE_HOURS` | `4` | Hours to cache calendar events |
| `TRADING_LOG_LEVEL` | `INFO` | Logging level |

### Cost Analysis

With default settings (`MAX_REVIEW_ATTEMPTS=2`):
- **LLM calls per symbol**: Up to 6 (synthesizer + decider + reviewer + retries)
- **Estimated cost per symbol**: ~$0.0225 (GPT-4o pricing)
- **Token usage**: ~5,000 input, ~1,000 output per symbol

## Usage

### CLI Commands

```bash
# Analyze a single symbol
python main.py EURUSD

# Specify model and log level
python main.py EURUSD --model gpt-4o --log-level DEBUG

# Custom MCP server URL
python main.py EURUSD --server-url http://localhost:8082
```

### Programmatic Usage

```python
from config.settings import Settings
from src.data.mt5_data_provider import Mt5DataProvider
from src.analysis.structure_analyzer import MarketStructureEngine
from src.calendar.forexfactory import ForexFactoryCalendar
from src.decision.agents import SynthesizerAgent, DeciderAgent, ReviewerAgent
from src.orchestrator.graph import TradingGraph

# Initialize settings
settings = Settings()

# Wire up dependencies
data_provider = Mt5DataProvider(settings.mcp_server_url)
structure_analyzer = MarketStructureEngine()
calendar_provider = ForexFactoryCalendar()
synthesizer = SynthesizerAgent(model=settings.openai_model)
decider = DeciderAgent(model=settings.openai_model)
reviewer = ReviewerAgent(model=settings.openai_model)

# Create and run graph
graph = TradingGraph(
    data_provider,
    structure_analyzer,
    calendar_provider,
    synthesizer,
    decider,
    reviewer
)

result = graph.run("EURUSD")
```

## Project Structure

```
├── main.py                    # CLI entry point
├── config/
│   ├── __init__.py
│   └── settings.py            # Pydantic settings with env vars
├── src/
│   ├── __init__.py
│   ├── logging_config.py      # Logging configuration
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── structure_analyzer.py
│   │   └── market_structure_engine/  # Deterministic analysis engine
│   │       ├── candles.py     # Candle data handling
│   │       ├── config.py      # Engine configuration
│   │       ├── context.py     # Analysis context
│   │       ├── engine.py      # Core engine
│   │       ├── errors.py      # Error definitions
│   │       ├── events.py      # BOS/CHoCH detection
│   │       ├── indicators.py  # Technical indicators
│   │       ├── levels.py      # Support/resistance
│   │       ├── liquidity.py   # Liquidity analysis
│   │       ├── review.py      # Analysis review
│   │       ├── scoring.py     # Confidence scoring
│   │       ├── structure.py   # Market structure
│   │       ├── swings.py      # Swing detection
│   │       ├── utils.py       # Utilities
│   │       └── validation.py  # Data validation
│   ├── decision/
│   │   ├── __init__.py
│   │   ├── protocols.py       # Protocol interfaces (DI)
│   │   ├── models.py          # Pydantic models
│   │   ├── agents.py          # LLM agents
│   │   └── prompts.py         # Agent prompts
│   ├── data/
│   │   ├── __init__.py
│   │   ├── mt5_data_provider.py  # MT5 via MCP
│   │   └── snapshot_builder.py   # Data snapshots
│   ├── calendar/
│   │   ├── __init__.py
│   │   ├── forexfactory.py    # ForexFactory scraper
│   │   └── evaluator.py       # Event evaluation
│   └── orchestrator/
│       ├── __init__.py
│       └── graph.py           # LangGraph workflow
├── tests/                     # 97 tests
├── rules.json                 # Bias calculation rules
├── pyproject.toml             # Project config
└── .env.template              # Environment template
```

## Components

### Data Layer (`src/data/`)

- **Mt5DataProvider**: Fetches OHLC candles, positions, and orders from MetaTrader 5 via MCP server. Implements `DataSource` protocol with retry logic and exponential backoff.
- **SnapshotBuilder**: Constructs multi-timeframe data snapshots for analysis.

### Analysis Layer (`src/analysis/`)

- **MarketStructureEngine**: 16-module deterministic engine for technical analysis:
  - Swing detection, BOS/CHoCH identification
  - Support/resistance level mapping
  - Liquidity analysis, confidence scoring
  - Multi-timeframe alignment checks

### Decision Layer (`src/decision/`)

- **Protocols**: `DataSource`, `CalendarProvider`, `StructureAnalyzer` interfaces for dependency injection
- **Models**: Pydantic models for `MarketContextSummary`, `DecisionOutput`, `ReviewVerdict`
- **Agents**: LLM-powered agents using Instructor for structured output:
  - `SynthesizerAgent`: Combines structure analysis + calendar into market context
  - `DeciderAgent`: Generates trading decisions based on context
  - `ReviewerAgent`: Independent review of decisions

### Calendar Layer (`src/calendar/`)

- **ForexFfactoryCalendar**: Scrapes ForexFactory economic calendar with 4-hour caching
- **Evaluator**: Filters events by currency and impact level

### Orchestrator (`src/orchestrator/`)

- **TradingGraph**: LangGraph state machine managing the analysis pipeline with conditional review loops

### Configuration (`config/`)

- **Settings**: Pydantic BaseSettings with environment variable binding and `.env` file support

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test directory
pytest tests/

# Run with verbose output
pytest -v
```

### Test Structure

The test suite contains 97 tests covering:
- Unit tests for all modules
- Protocol conformance tests
- Integration tests for the graph workflow
- Mock-based tests for external dependencies

## Development

### Code Quality

```bash
# Type checking
mypy src/

# Linting
ruff check src/

# Format code
ruff format src/
```

### Contributing

1. Follow existing code conventions
2. All functions must have type hints
3. Write tests for new functionality
4. Run `mypy` and `ruff` before committing
5. Keep `entry_authorized = False` in all decision outputs

### Dependencies

Core:
- `instructor` - Structured LLM output
- `langgraph` - Workflow orchestration
- `pydantic-settings` - Configuration management
- `openai` - LLM API client
- `mcp` - Model Context Protocol client
- `requests` + `beautifulsoup4` - Web scraping

Dev:
- `pytest` - Testing framework
- `mypy` - Static type checking
- `ruff` - Linter and formatter

## License

MIT License
