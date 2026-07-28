# Trading AI Agent

AI-powered trading agent for multi-timeframe market structure analysis, economic calendar
monitoring, and advisory-only trading decision-making. The full stack comprises a Python
analysis engine, a Node.js REST API server, and a Vue 3 terminal-themed dashboard.

## Overview

The agent combines a **16-module deterministic market structure engine** with **LLM-based
decision synthesis** to provide advisory-only trading recommendations. It analyzes market
structure across D1, H4, and H1 timeframes, evaluates economic calendar events, and produces
structured trading decisions through a LangGraph orchestration pipeline with automated review
loops.

Results are written as JSON files to a versioned directory tree and served through a REST API
with a corresponding web UI.

**Key characteristics:**

- **Advisory-only** — `entry_authorized` is always `False`; the system never executes trades
- **Protocol-based dependency injection** — all dependencies wired via `DataSource`,
  `CalendarProvider`, and `StructureAnalyzer` protocols
- **Deterministic market structure engine** — 16 self-contained modules for swing detection,
  BOS/CHoCH, liquidity, support/resistance, and confidence scoring
- **LLM-enhanced synthesis** — context synthesis, decision generation, and independent review
  via structured output (Instructor + OpenAI)
- **Cost-controlled** — `CostTracker` tracks per-symbol spend against configurable limits using
  model-specific pricing tables
- **Synthesizer caching** — caches identical analysis inputs to eliminate redundant LLM calls
- **MTF candle caching** — disk-backed cache keyed by symbol/timeframe/close-time for faster
  re-analysis
- **Knowledge graph** — graphify-updated dependency graph supports codebase queries and
  cross-file navigation
- **Pre-commit hooks** — automated `ruff` lint+format, `mypy` static checks, and graphify
  update on commit

## Architecture

### Analysis Pipeline (LangGraph State Machine)

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
```

### Service Architecture

```
┌──────────┐     HTTP/API      ┌──────────┐     spawns child     ┌──────────┐
│  MT5 MCP │◄─────────────────►│ Analyzer │◄────────────────────►│  Server  │
│ Terminal │  MCP Streamable   │ (Python) │   python main.py     │  (Node)  │
│(host:22346)│                 │  (CLI)   │                      │(port 3000)│
└──────────┘                   └────┬─────┘                      └────▲─────┘
                                    │                                 │
                                    │ reads/writes                    │ reads
                                    ▼                                 │
                            ┌──────────────┐                         │
                            │    data/      │◄────────────────────────┘
                            │  (JSON files) │    filesystem via ResultScanner
                            └──────────────┘
                                    ▲
                                    │ HTTP (axios)
                                    │
                            ┌───────┴────────┐
                            │  UI (Vue 3)    │
                            │  Vite dev:5173 │
                            │  Prod: served  │
                            │  by Express    │
                            └────────────────┘
```

### Design Principles

- **SOLID**: Single responsibility per module, open for extension via protocols
- **Dependency Injection**: All dependencies injected via protocol interfaces; orchestration
  code never imports concrete implementations
- **Advisory-Only**: System never executes trades; `entry_authorized` is always `False`
  (enforced via invariant check)
- **Cost Control**: Configurable per-symbol spend limits with model-specific token pricing
- **Cache-Heavy**: Multi-level caching (candle data + synthesizer output) reduces redundant
  computation and LLM calls
- **Broker-Local Time**: All time-sensitive operations align to broker/server time, not local
  wall clock

## Services

| Service | Language | Directory | Purpose |
|---|---|---|---|
| **Analyzer** (core) | Python 3.14+ | `analyzer/` | CLI-based trading analysis engine. Fetches MT5 data via MCP, runs 16-module deterministic market structure engine, synthesizes context via LLM, makes advisory decisions, and reviews them. |
| **Server** (API) | Node.js/TypeScript | `server/` | Express REST API that serves analysis results from the filesystem and can trigger new analyses by spawning the Python analyzer as a child process. |
| **UI** (frontend) | Vue 3 + Vite | `ui/` | Dark-terminal-themed web dashboard displaying analysis results, OHLC charts, run history, and a detail view for individual symbol analyses. |

## Installation

### Prerequisites

- Python 3.11+
- Node.js 20+
- MetaTrader 5 terminal running (for live data) with a matching MCP server
- OpenAI API key or compatible LLM endpoint

### Native Setup

```bash
# Clone the repository
git clone <repository-url>
cd Agent

# --- Analyzer ---
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -e .

# Install dev dependencies (optional)
pip install -e ".[dev]"

# --- Server ---
cd server
npm install
cd ..

# --- UI ---
cd ui
npm install
cd ..
```

### Environment Configuration

```bash
# Copy environment template
cp .env.template .env

# Edit .env with your settings (see configuration table below)
```

## Configuration

### Environment Variables — Analyzer

All settings use the `TRADING_` prefix and are loaded via `pydantic-settings` from `.env` or
the environment.

| Variable | Default | Description |
|---|---|---|
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

### Environment Variables — Server

These are loaded from the environment (or a `.env` file in `server/`) by the Express server.

| Variable | Default | Description |
|---|---|---|
| `PORT` | `3000` | HTTP listen port |
| `DATA_DIR` | `../data/runs` | Path to analysis result files (relative to `server/`) |
| `PYTHON_CMD` | `python` | Python executable for spawning the analyzer |
| `ANALYZER_DIR` | `.` | Working directory for the Python analyzer process |
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated allowed CORS origins |

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

Override via `TRADING_MODEL_PRICING` as a JSON environment variable. Any price set to `0` logs
a warning — cost tracking will undercount.

### Cost Analysis

LLM calls per symbol pipeline:

| Step | Calls | Description |
|---|---|---|
| 1. Synthesizer | 1 | Structure analysis + calendar → market context |
| 2. Decider | 1 | Context + positions → decision |
| 3. Reviewer | 1 | Context + decision → verdict |
| 4. Decider retry | up to `MAX_REVIEW_ATTEMPTS` | Revised decision with reviewer feedback |
| 5. Reviewer retry | up to `MAX_REVIEW_ATTEMPTS` | Re-review of revised decision |

**Total: up to `(2 + 2 x MAX_REVIEW_ATTEMPTS)` LLM calls per symbol**

With default `MAX_REVIEW_ATTEMPTS=2`: **up to 6 calls per symbol**

#### Token Estimates (GPT-4o)

| Agent | Input tokens | Output tokens |
|---|---|---|
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

### Analyzer CLI

```bash
# Analyze a single symbol
python main.py EURUSD

# Specify model and base URL (e.g., for local Ollama)
python main.py EURUSD --model DeepSeek-V4-Flash --base-url http://localhost:11434/v1

# Override log level
python main.py EURUSD --log-level DEBUG
```

### API Server

```bash
cd server
npm run dev      # Development with hot-reload (tsx watch)
npm run build    # TypeScript compile
npm start        # Run compiled server (port 3000)
```

The server exposes:

- `GET /api/runs` — List analysis runs (optional query params: `symbol`, `from`, `to`)
- `GET /api/runs/:symbol/:year/:month/:day/:file` — Get a specific run result
- `POST /api/run` — Trigger a new analysis (body: `{"symbols": ["EURUSD"], "model": "gpt-4o"}`)

### UI Dashboard

```bash
cd ui
npm run dev    # Vite dev server (port 5173, proxies /api to :3000)
npm run build  # Production build → ui/dist/
```

In production the Express server serves the built UI files from `ui/dist/`.

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
├── .dockerignore                            # Docker build exclusions
├── .env.template                            # Environment variables template
├── .pre-commit-config.yaml                  # Pre-commit hooks
├── AGENTS.md                                # Agent instructions
├── Dockerfile.dev                           # Development Docker image
├── Dockerfile.prod                          # Production Docker image
├── README.md
├── docker-compose.devel.yml                 # Development Compose
├── docker-compose.prod.yml                  # Production Compose
├── rules.json                               # Bias calculation rules
│
├── analyzer/                                # Python analysis engine
│   ├── main.py                              # CLI entry point
│   ├── pyproject.toml
│   ├── config/
│   │   └── settings.py                      # Pydantic BaseSettings
│   ├── src/
│   │   ├── analysis/                        # Market structure engine (16 modules)
│   │   │   └── market_structure_engine/
│   │   ├── calendar/                        # ForexFactory scraper + evaluator
│   │   ├── data/                            # MT5 data provider + snapshot builder
│   │   ├── decision/                        # LLM agents + protocols + cost tracker
│   │   ├── orchestrator/                    # LangGraph state machine
│   │   └── output/                          # Result models + JSON writer
│   └── tests/                               # 356 tests
│
├── server/                                  # Node.js Express API
│   ├── package.json
│   ├── tsconfig.json
│   ├── vitest.config.ts
│   ├── .env.example
│   └── src/
│       ├── index.ts                         # Express app (port 3000)
│       ├── types.ts                         # TypeScript interfaces
│       ├── routes/
│       │   ├── run.ts                       # POST /api/run
│       │   └── runs.ts                      # GET /api/runs
│       ├── services/
│       │   ├── runner.ts                    # Spawns Python analyzer
│       │   └── scanner.ts                   # Reads result JSON files
│       └── __tests__/
│
├── ui/                                      # Vue 3 frontend
│   ├── package.json
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── src/
│       ├── main.ts
│       ├── App.vue
│       ├── router.ts                        # Dashboard + Detail views
│       ├── lib/api.ts                       # Axios API client
│       ├── composables/                     # useRuns, useRun
│       ├── components/                      # OhlcChart, RunCard, etc.
│       └── views/                           # Dashboard.vue, Detail.vue
│
├── data/                                    # Runtime data (git-ignored)
└── graphify-out/                            # Knowledge graph
```

## Components

### Data Layer (`analyzer/src/data/`)

- **TerminalDataProvider** (`DataSource` protocol): Fetches OHLC candles, positions, pending
  orders, and broker-local time from MetaTrader 5 via an MCP server. Implements retry logic
  with exponential backoff and optional bearer-token authentication.
- **SnapshotBuilder** (`src/data/snapshot_builder.py`): Constructs multi-timeframe (D1/H4/H1)
  data snapshots enriched with current price, structure analysis results, and calendar events.

### Analysis Layer (`analyzer/src/analysis/`)

- **MarketStructureEngine** (`StructureAnalyzer` protocol): 16-module deterministic engine for
  technical analysis. Operates on OHLC data without any stochastic or LLM components:
  - Swing detection and classification
  - BOS (Break of Structure) and CHoCH (Change of Character) identification
  - Support/resistance level mapping (swing highs/lows, structural levels)
  - Liquidity analysis (stop-run clusters, order-block detection)
  - Multi-timeframe alignment and confidence scoring
  - All outputs are deterministic — same input always produces same result
- **Candle Cache** (`src/analysis/candle_cache.py`): Disk-backed cache for MTF analysis
  results, keyed by `symbol/timeframe/candle_close_time`. Determines when re-analysis is
  needed based on broker-local time and cached candle periods. Reduces MCP server round-trips
  on repeated analysis of the same closed candles.

### Decision Layer (`analyzer/src/decision/`)

- **Protocols** (`protocols.py`): `DataSource`, `CalendarProvider`, `StructureAnalyzer` —
  runtime-checkable `typing.Protocol` interfaces for dependency injection.
- **Models** (`models.py`): Pydantic models for `MarketContextSummary`, `DecisionOutput`
  (with `entry_authorized: bool = False`), `ReviewVerdict`, and supporting types.
- **Agents** (`agents.py`): LLM-powered agents using Instructor for structured JSON output:
  - `SynthesizerAgent` — combines structure analysis + calendar events → market context summary
  - `DeciderAgent` — generates trading decision (direction, entry, SL, TP, risk-reward)
  - `ReviewerAgent` — independent quality review of the decision with veto power
- **CostTracker** (`cost_tracker.py`): Tracks cumulative token usage and USD cost per analysis
  run using model-specific pricing tables. Raises a `CostLimitExceeded` error when
  `cost_per_symbol_limit` is reached.
- **SynthesizerCache** (`synthesizer_cache.py`): Content-addressable cache for synthesizer
  outputs. When identical analysis inputs are re-encountered (same structure state + calendar
  events), the cached LLM response is returned, saving both time and cost.

### Calendar Layer (`analyzer/src/calendar/`)

- **ForexFactoryCalendar** (`CalendarProvider` protocol): Scrapes ForexFactory economic
  calendar with 4-hour in-memory caching. Filters by upcoming events.
- **Evaluator**: Filters events by relevant currencies and impact level (high/medium/low) for
  the analyzed symbol.

### Orchestrator (`analyzer/src/orchestrator/`)

- **TradingGraph**: LangGraph state machine managing the 6-node analysis pipeline:
  1. `fetch_data` — retrieves candles, positions, and broker time
  2. `analyze_structure` — runs the deterministic market structure engine
  3. `evaluate_calendar` — fetches and filters economic events
  4. `synthesize_context` — LLM combines structure + calendar into a narrative context
  5. `decide` — LLM generates a trading decision with specific levels
  6. `review` — LLM independently reviews the decision; if rejected, loops back to `decide`
     (up to `MAX_REVIEW_ATTEMPTS`)
  - The advisory-only invariant is enforced at the model layer: `DecisionOutput.entry_authorized`
    defaults to `False` and its Pydantic validator forces it to `False` regardless of LLM output;
    the structure analyzer also rejects any engine result where `entry_authorized` is not `False`.

### Configuration (`analyzer/config/`)

- **Settings**: Pydantic `BaseSettings` class binding all environment variables (`TRADING_*`
  prefix). Supports `.env` file loading, field validation, and complex types like
  `dict[str, dict[str, float]]` for model pricing (auto-parsed from JSON env var).

### Server (`server/`)

- **Express app** (`src/index.ts`): CORS-configured REST API that serves result JSON files
  from the filesystem and proxies new analysis runs to the Python CLI.
- **ResultScanner** (`src/services/scanner.ts`): Walks the `data/` directory tree, parses
  result JSON files, and returns typed `RunSummary` or `FullResult` objects.
- **RunService** (`src/services/runner.ts`): Spawns `python main.py` as a child process with
  the requested symbols and optional model override. Enforces a 10-minute timeout.
- **Routes**: `GET /api/runs` (list with filters), `GET /api/runs/:symbol/:year/:month/:day/:file`
  (detail), `POST /api/run` (trigger).

### UI (`ui/`)

- **Dashboard view** (`Dashboard.vue`): Lists all analysis runs with symbol, bias, confidence,
  action, review status, and current price. Includes filters and a symbol sidebar.
- **Detail view** (`Detail.vue`): Full analysis breakdown for a single symbol — OHLC chart
  with SL/TP overlay, decision reasoning, review verdict, and calendar context.
- **Components**: `OhlcChart.vue` (echarts candle chart), `RunCard.vue` (run summary card),
  `SymbolSidebar.vue` (symbol filter), `TimelineBar.vue` (time-based run navigation).
- **API client** (`lib/api.ts`): Axios-based client communicating with the Express server.

## Docker

The project includes Docker support for both development and production environments.

### Prerequisites

- Docker Engine 24+
- Docker Compose v2+

### Development

```bash
# Build and start the dev container
docker compose -f docker-compose.devel.yml up -d --build

# First-time: install dependencies inside the container
docker compose -f docker-compose.devel.yml exec trading-agent bash \
  -c "cd /app/analyzer && pip install -e '.[dev]' && cd /app/server && npm install"

# Run the analyzer
docker compose -f docker-compose.devel.yml exec trading-agent bash \
  -c "cd /app/analyzer && python main.py XAUUSD"

# Start the API server (port 3000)
docker compose -f docker-compose.devel.yml exec trading-agent bash \
  -c "cd /app/server && npm run dev"
```

The dev container uses bind mounts for all source directories, so code changes on the host
are immediately visible inside the container. The container stays alive with `sleep infinity` —
use `docker compose exec` to run commands.

### Production

```bash
# Build and start
docker compose -f docker-compose.prod.yml up -d --build

# Check logs
docker compose -f docker-compose.prod.yml logs -f

# Stop
docker compose -f docker-compose.prod.yml down
```

The production image is self-contained:

- All dependencies are installed at build time (`npm ci`, `pip install`)
- The Vue UI is built into static files (`ui/dist/`)
- The TypeScript server is compiled (`server/dist/`)
- The Express server serves both the REST API and the built UI on port 3000
- Only the `data/` directory is persisted via bind mount

### Images

| Image | Base | Size | Purpose |
|---|---|---|---|
| `trading-agent:devel` | Ubuntu 26.04 | ~270 MB content | Development with bind mounts, Python venv, Node 22, tsx |
| `trading-agent:prod` | Ubuntu 26.04 | ~400 MB content | Production with all deps baked in, UI built |

## Testing

```bash
# Analyzer (Python) — run from analyzer/
cd analyzer

# Run all tests (356 tests)
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run a specific test file
pytest tests/decision/test_cost_tracker.py -v

# Run tests matching a keyword
pytest -k "cache"

# Server (Node)
cd server && npm test        # vitest

# UI type checking
cd ui && npm run typecheck   # vue-tsc
```

### Test Coverage — Analyzer

The test suite contains **356 tests** covering:

- **Analysis**: Candle cache engine fields
- **Calendar**: Event evaluator logic
- **Config**: Settings loading, env prefix, validation, model pricing
- **Data**: Snapshot builder, terminal data provider (retry, auth, broker time)
- **Decision**: Agents (API key handling, prompt rendering), cost tracker, models, protocols,
  synthesizer cache
- **Orchestrator**: Full graph pipeline, canonical price handling, synthesizer cache integration
- **Main**: CLI entry point argument handling

All external dependencies (MT5 terminal, LLM API, ForexFactory) are mocked in tests.

## Code Review Analysis

A comprehensive code review identified **17 issues** across the two-package monorepo —
`analyzer/` (trading pipeline) and `server/` (FastAPI web API) — plus Dockerfile.prod and
test files. Issues span security, performance, correctness, and maintainability. No feature
additions.

### Issues Summary

| # | Severity | Issue |
|---|---|---|
| 1 | Critical | **Missing Server Dependencies** — `server/pyproject.toml` lists only fastapi and uvicorn; pydantic imports fail without analyzer's transitive install |
| 2 | Critical | **No Authentication or Rate Limiting on POST /api/run** — open spending endpoint; each invocation triggers up to 6 LLM calls per symbol |
| 3 | Critical | **Token Leakage Risk in Telegram URL** — bot token embedded in URL string passed to `requests.post`; could appear in debug logs |
| 4 | High | **Post-Analysis Race Condition on File Read** — `_read_results` immediately reads result files after subprocess exits; no filesystem flush guarantee |
| 5 | High | **os.walk Scans Entire Directory on Every Request** — `list_runs()` traverses full data tree and parses every `.json` before applying filters |
| 6 | High | **Broad Exception Catching Obscures Real Errors** — bare `except Exception` raises generic `RuntimeError` with no diagnostic detail |
| 7 | Medium | **CORS Configuration Too Permissive** — allows all methods (`["*"]`) and headers (`["*"]`) |
| 8 | Medium | **Runner Creates Scanner Instance on Every Call** — `_read_results` allocates a new `ResultScanner` each time, triggering a full directory walk |
| 9 | Medium | **Settings Duplication Between Analyzer and Server** — `analysis_cache_dir` defined in both packages with different path-resolution behavior |
| 10 | Medium | **_normalize_cors Validator Duplicates _CommaDelimitedEnvSource Logic** — comma-splitting implemented in both places; validator is redundant |
| 11 | Medium | **Permanent Settings() Singleton in candle_cache** — module-level `_settings` singleton must be manually invalidated in tests; no refresh mechanism |
| 12 | Medium | **Inconsistent Exception Chaining in POST /api/run** — three overlapping branches all produce `RuntimeError`; needlessly complex |
| 13 | Low | **Long main() Function** — 165 lines handling argument parsing, initialization, per-symbol orchestration, output writing, Telegram notifications |
| 14 | Low | **Unused request Parameter in Exception Handler** — `request` parameter unused in `http_exception_handler` |
| 15 | Low | **Deferred Imports Make Dependency Errors Opaque** — imports inside try block cause `ImportError` to be caught by same handler as runtime failures |
| 16 | Low | **Type Hint: sample_full_result Fixture Returns dict Without Generic** — should be `dict[str, Any]` |
| 17 | Low | **Test Naming Inconsistency** — `test_sellsend_message` missing underscore vs `test_sends_buy_message` |

### Project Facts and Conventions

- **Two-package monorepo**: `analyzer/` (trading-ai-agent, pip-installable) + `server/` (trading-server, pip-installable)
- **Advisory-only**: `entry_authorized` must always be `False` — never executes trades
- **TRADING_ env prefix**: All settings use `TRADING_` prefix via `pydantic-settings`
- **Protocol DI**: Dependencies injected via protocols in `analyzer/src/decision/protocols.py`
- **pytest** with `asyncio_mode = "auto"` (both packages)
- **mypy strict mode** for analyzer, **ruff** lint+format (line-length 100, target py311)
- **Python 3.11+ required**
- **Module-level `_settings` singleton pattern** in `candle_cache.py` and `synthesizer_cache.py` — requires manual reset in tests

### Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                          Project Root                                │
│                                                                      │
│  ┌─────────────────────────┐     ┌───────────────────────────────┐   │
│  │       analyzer/          │     │         server/                │   │
│  │  (trading-ai-agent)      │     │  (trading-server, FastAPI)     │   │
│  │                         │     │                               │   │
│  │  main.py — CLI entry    │     │  src/main.py — FastAPI app    │   │
│  │  src/decision/agents.py │ ◄── │  src/runner.py — spawns       │   │
│  │  src/orchestrator/      │subpr │  analyzer as subprocess       │   │
│  │  src/analysis/          │cess  │  src/scanner.py — reads       │   │
│  │  src/calendar/          │     │  result files from disk        │   │
│  │  src/data/              │     │  src/settings.py — WebSettings │   │
│  │  src/notification/      │     │  src/models.py — Pydantic dtos │   │
│  │  config/settings.py ◄───┼─────┤  tests/                       │   │
│  │  tests/                 │shared│                               │   │
│  └─────────────────────────┘ env  └───────────────────────────────┘   │
│                                   var                                │
│  ┌──────────────────────┐     ┌──────────────────────────────┐      │
│  │    Dockerfile.prod   │─────│  ui/ (Vue 3 SPA, static)     │      │
│  └──────────────────────┘     └──────────────────────────────┘      │
└──────────────────────────────────────────────────────────────────────┘
```

- **Dependency direction**: `server/` depends on `analyzer/` at runtime (spawns subprocess, reads its output). No import dependency.
- **Shared config surface**: `TRADING_ANALYSIS_CACHE_DIR` is the single shared env var between both packages.
- **Runner is the bridge**: `RunService._spawn_process` → analyzer subprocess → `_read_results` → `ResultScanner` to return results to API caller.

### External Dependencies and I/O Boundaries

| Dependency | Used By | Type |
|---|---|---|
| OpenAI API | `analyzer/src/decision/agents.py` | Network (HTTPS) |
| MetaTrader 5 MCP server | `analyzer/src/data/terminal_data_provider.py` | Local network (MCP over HTTP) |
| ForexFactory (BeautifulSoup) | `analyzer/src/calendar/forexfactory.py` | Network (HTTPS, web scraping) |
| Telegram Bot API | `analyzer/src/notification/telegram_sender.py` | Network (HTTPS) |
| Filesystem (result cache) | `analyzer/src/output/result_writer.py`, `analyzer/src/analysis/candle_cache.py`, `server/src/scanner.py` | Local disk |
| Python subprocess | `server/src/runner.py` | OS process spawn |
| FastAPI / Uvicorn | `server/src/main.py` | Web server |
| LLM (instructor + openai) | `analyzer/src/decision/agents.py` | Network (HTTPS) |

## Development

### Commands

```bash
# --- Analyzer ---
cd analyzer
mypy src/              # Static type checking (strict mode)
ruff check src/        # Linting
ruff format src/       # Auto-format
pytest                 # Run all tests

# --- Server ---
cd server
npm run dev            # tsx watch (hot-reload)
npm run build          # tsc compile
npm test               # vitest
npm run typecheck      # tsc --noEmit

# --- UI ---
cd ui
npm run dev            # Vite dev server (port 5173)
npm run build          # Vite build → ui/dist/
npm run typecheck      # vue-tsc --noEmit
```

### Pre-commit Hooks

The repository includes a `.pre-commit-config.yaml` that runs automatically on `git commit`:

| Hook | Action |
|---|---|
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

A persistent knowledge graph is maintained at `graphify-out/` with god nodes, community
structure, and cross-file relationships. It auto-updates on commit via pre-commit hook, or
can be rebuilt manually:

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
4. Run `mypy src/ && ruff check src/ && pytest` before committing (Analyzer)
5. Ensure `entry_authorized = False` in all decision outputs (the graph enforces this)
6. Install pre-commit hooks to catch issues early

### Dependencies

**Analyzer core:**
- `instructor` — Structured LLM output
- `langgraph` — Workflow orchestration (LangGraph state machine)
- `pydantic-settings` — Configuration management with env prefix
- `openai` — LLM API client (also works with compatible providers)
- `mcp` — Model Context Protocol client
- `requests` + `beautifulsoup4` — Web scraping (ForexFactory)

**Analyzer dev:**
- `pytest` + `pytest-asyncio` + `pytest-cov` — Testing
- `mypy` — Static type checking (strict mode)
- `ruff` — Linter and formatter
- `responses` — HTTP request mocking
- `pre-commit` — Git hook framework

**Server:**
- `express` — HTTP framework
- `cors` — Cross-origin resource sharing
- `dotenv` — Environment variable loading
- `typescript`, `tsx`, `vitest`, `supertest` — Dev toolchain

**UI:**
- `vue` + `vue-router` — Frontend framework
- `vue-echarts` + `echarts` — OHLC chart rendering
- `axios` — HTTP client
- `vite`, `vue-tsc`, `tailwindcss` — Dev toolchain

## License

MIT License
