# Trading AI Agent

AI-powered trading agent for multi-timeframe market structure analysis, economic calendar
monitoring, and advisory-only trading decision-making. The full stack comprises a Python
analysis engine, a Python FastAPI REST API server, and a Vue 3 terminal-themed dashboard.

## Overview

The agent combines a **16-module deterministic market structure engine** with **LLM-based
decision synthesis** to provide advisory-only trading recommendations. It analyzes market
structure across D1, H4, and H1 timeframes, evaluates economic calendar events, and produces
structured trading decisions through a LangGraph orchestration pipeline with automated review
loops.

Results are written as JSON files to a versioned directory tree and served through a REST API
with a corresponding web UI.

**Key characteristics:**

- **Advisory-only** — The system never executes trades. Enforced at four layers:
  the deterministic engine hardcodes `entry_authorized = False` at every output level;
  the structure analyzer adapter validates this on every read; the LLM prompts instruct
  the model (instructional, not enforceable); and the `DeterministicEnforcementGate`
  blocks any executable action that fails invariant checks post-hoc.
- **Protocol-based dependency injection** — all dependencies wired via `DataSource`,
  `CalendarProvider`, and `StructureAnalyzer` protocols
- **Deterministic market structure engine** — 16 self-contained modules for swing detection,
  BOS/CHoCH, liquidity, support/resistance, and confidence scoring
- **LLM-enhanced synthesis** — context synthesis, decision generation, and independent review
  via structured output (Instructor + OpenAI)
- **Cost-controlled** — `CostTracker` tracks per-symbol spend against configurable limits using
  model-specific pricing tables; raises `CostLimitExceeded` to halt mid-pipeline
- **Synthesizer caching** — content-addressable cache eliminates redundant LLM calls for
  identical analysis inputs
- **MTF candle caching** — disk-backed cache keyed by symbol/timeframe/close-time for faster
  re-analysis
- **Knowledge graph** — persistent dependency graph at `graphify-out/` supports codebase
  queries and cross-file navigation
- **Two-LLM-instance architecture** — reviewer can use an independent model, API key, base URL,
  and reasoning effort from the primary synthesizer/decider
- **Deterministic enforcement gate** — 5 invariant checks block any action that contradicts
  deterministic pipeline outputs

## Architecture

### Analysis Pipeline (LangGraph State Machine)

```
┌────────────────────────────────────────────────────────────────────────────────────────────┐
│                                  Trading Graph (14 nodes)                                  │
│                              LangGraph StateGraph Orchestrator                             │
├────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                            │
│  ┌───────────┐   ┌───────────────┐   ┌────────────────┐   ┌──────────────────┐            │
│  │ fetch_data │──▶│analyze_struct │──▶│evaluate_calendar│──▶│synthesize_context│            │
│  └───────────┘   └───────────────┘   └────────────────┘   └────────┬─────────┘            │
│                                                                    │                       │
│                                             ┌──────────────────────▼──────────────────┐    │
│                                             │        Deterministic Pipeline           │    │
│                                             │  grade_setup → build_risk_policy →     │    │
│                                             │  evaluate_execution_policy →           │    │
│                                             │  early_execution_routing               │    │
│                                             └──────────────────────┬──────────────────┘    │
│                                                                    │                       │
│                                             ┌──────────────────────▼──────────────────┐    │
│                                             │      early_execution_routing           │    │
│                                             │                                        │    │
│                                             │  ┌──────────────────┐ ┌──────────────┐ │    │
│                                             │  │deterministic_con │ │  llm_decide  │ │    │
│                                             │  │tinue (NO_TRADE   │ │  (proceed    │ │    │
│                                             │  │ bypass LLM)      │ │  to LLM)    │ │    │
│                                             │  └────────┬─────────┘ └──────┬───────┘ │    │
│                                             └───────────┼──────────────────┼──────────┘    │
│                                                         │                  │               │
│                               ┌─────────────────────────┘                  │               │
│                               ▼                                            ▼               │
│  ┌──────────────────────────────┐                          ┌──────────────────────────┐    │
│  │pre_review_decision_validation│                          │         decide           │    │
│  └──────────────┬───────────────┘                          └────────────┬─────────────┘    │
│                 │                                                       │                  │
│                 └──────────────────┬────────────────────────────────────┘                  │
│                                    ▼                                                        │
│                         ┌──────────────────────┐                                            │
│                         │        review         │                                            │
│                         └──────────┬───────────┘                                            │
│                                    │                                                        │
│                     ┌──────────────┴──────────────┐                                         │
│                     │                             │                                         │
│             ┌───────▼────────┐           ┌────────▼───────┐                                 │
│             │   enforcement  │           │  retry_decide  │                                 │
│             │ (approved /    │           │ (rejected,     │                                 │
│             │  NOT_REQUIRED  │           │  attempts      │                                 │
│             │  / max retry)  │           │  remaining)    │                                 │
│             └───────┬────────┘           └────────┬───────┘                                 │
│                     │                             │                                         │
│                     │                             └── back to decide ───────────────────────┤
│                     ▼                                                                      │
│             ┌────────────────┐                                                              │
│             │ final_enforce- │                                                              │
│             │ ment           │                                                              │
│             └───────┬────────┘                                                              │
│                     ▼                                                                       │
│             ┌────────────────┐                                                              │
│             │ assemble_output│                                                              │
│             └───────┬────────┘                                                              │
│                     ▼                                                                       │
│                     END                                                                     │
└────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Pipeline flow (14 nodes):**

| Phase | Nodes | Description |
|---|---|---|
| **Data pipeline** | `fetch_data` → `analyze_structure` → `evaluate_calendar` | Sequential: fetches MT5 candles/positions via MCP, runs 16-module deterministic market structure engine (D1/H4/H1), scrapes ForexFactory calendar |
| **LLM synthesis** | `synthesize_context` | One LLM call combining summarised structure analysis + calendar events → `MarketContextSummary`. Content-addressable caching skips redundant calls. |
| **Deterministic pipeline** | `grade_setup` → `build_risk_policy` → `evaluate_execution_policy` → `early_execution_routing` | Pure deterministic: grades the setup (AAA/AA/COUNTERTREND/REJECTED), maps grade → risk multiplier + min R/R, evaluates execution blockers (policy/calendar/geometry/data-quality), then routes |
| **LLM decision** | `decide` | LLM generates a trading decision (action + reasoning). Price levels come from the deterministic engine — never from the LLM. |
| **Validation** | `pre_review_decision_validation` | Validates decision presence and symbol match before review. Logs advisory warnings for unexpected NO_TRADE without deterministic early-exit reason. |
| **Review** | `review` → conditional retry to `decide` | Independent LLM review verdict; if `REVISION_REQUIRED` and attempts remain, loops back to `decide` with feedback (up to `MAX_REVIEW_ATTEMPTS`). Deterministic early-exit bypasses the LLM reviewer entirely. |
| **Enforcement + output** | `final_enforcement` → `assemble_output` | `DeterministicEnforcementGate` (5 invariant checks) blocks any action violating deterministic invariants. Assembles final `AnalysisResult` with SL/TP overlay, execution blockers, enforcement violations. |

**Conditional routing:**

- `early_execution_routing → {deterministic_continue, llm_decide}` — when execution status is `NON_EXECUTABLE` or `BLOCKED_BY_DATA_QUALITY`, the LLM is bypassed entirely. A deterministic `NO_TRADE` decision and `NOT_REQUIRED` review verdict are injected directly, flowing to `pre_review_decision_validation` → `review` (pass-through) → `final_enforcement` → `assemble_output`.
- `review → {continue_enforcement, retry_decide}` — when review is `APPROVED`, `NOT_REQUIRED`, or max attempts reached, proceeds to enforcement. When `REVISION_REQUIRED` and attempts remain, retries the `decide` node with structured reviewer feedback injected into the prompt.

### Service Architecture

```
┌──────────┐     MCP over HTTP   ┌──────────┐     spawns child     ┌──────────────┐
│  MT5 MCP │◄───────────────────►│ Analyzer │◄────────────────────►│   Server     │
│ Terminal │  req/res + notify   │ (Python) │   python main.py     │ (Python /    │
│(host:22346)│                   │  (CLI)   │                      │  FastAPI)    │
└──────────┘                     └────┬─────┘                      │ (port 3000)  │
                                      │                            └──────▲───────┘
                                      │ reads/writes                     │ reads
                                      ▼                                  │
                              ┌──────────────┐                          │
                              │    data/      │◄─────────────────────────┘
                              │  (JSON files) │    filesystem via ResultScanner
                              └──────────────┘
                                      ▲
                                      │ HTTP (axios)
                                      │
                              ┌───────┴────────┐     ┌──────────────────┐
                              │  UI (Vue 3)    │     │   Telegram Bot   │
                              │  Vite dev:5173 │     │  (notifications) │
                              │  Prod: served  │     │                  │
                              │  by FastAPI    │     │  ◄────────────── │
                              └────────────────┘     │  analyzer sends  │
                                                     │  approved setups │
                                                     └──────────────────┘
```

### Design Principles

- **SOLID**: Single responsibility per module, open for extension via protocols
- **Dependency Injection**: All dependencies injected via protocol interfaces; orchestration
  code never imports concrete implementations
- **Advisory-Only**: System never executes trades. Enforced at four layers: engine
  hardcodes `entry_authorized = False` (context.py, engine.py, review.py); structure
  analyzer adapter validates on read; LLM prompts instruct the model; enforcement gate
  blocks post-hoc.
- **Cost Control**: Configurable per-symbol spend limits with model-specific token pricing
- **Cache-Heavy**: Multi-level caching (candle data + synthesizer output) reduces redundant
  computation and LLM calls
- **Broker-Local Time**: All time-sensitive operations align to broker/server time, not local
  wall clock

### Deployment Architecture

**Development (`docker-compose.devel.yml`):**

```
┌─────────────────────────────────────────────────────────────────┐
│                        trading-agent:devel                        │
│                                                                   │
│  ┌────────────┐  ┌────────────┐  ┌────────┐  ┌──────┐  ┌──────┐ │
│  │ analyzer/  │  │  server/   │  │  ui/   │  │data/ │  │scripts│ │
│  │ (bind:rw)  │  │ (bind:rw)  │  │(bind:rw)│  │:rw   │  │:rw   │ │
│  └────────────┘  └────────────┘  └────────┘  └──────┘  └──────┘ │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │              Auto-starts on boot:                        │    │
│  │  ┌─────────────────┐          ┌───────────────────┐     │    │
│  │  │ FastAPI (reload) │          │ Vite (HMR)        │     │    │
│  │  │ :3000 (internal) │          │ :5173 → host:5173 │     │    │
│  │  └─────────────────┘          └───────────────────┘     │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                   │
│  Ports: 5173:5173    Env: .env    Volumes: node_modules (named)  │
└─────────────────────────────────────────────────────────────────┘
```

**Production (`docker-compose.prod.yml`):**

```
┌─────────────────────────────────────────────────────────────────┐
│                       trading-agent:prod                          │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │              All deps baked in at build time             │    │
│  │  ┌─────────────────┐    ┌───────────────────┐           │    │
│  │  │  FastAPI         │    │  Vue UI (built)   │           │    │
│  │  │  :3000 → host:  │    │  served by FastAPI│           │    │
│  │  │  3000            │    │  from ui/dist/    │           │    │
│  │  └─────────────────┘    └───────────────────┘           │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                   │
│  Bind mount: ./data:/app/data (persisted)                        │
│  Ports: 3000:3000    Env: .env    No source bind mounts          │
└─────────────────────────────────────────────────────────────────┘
```

## Services

| Service | Language | Directory | Purpose |
|---|---|---|---|---|
| **Analyzer** (core) | Python 3.11+ | `analyzer/` | CLI-based trading analysis engine. Fetches MT5 data via MCP, runs 16-module deterministic market structure engine, synthesizes context via LLM, makes advisory decisions, and reviews them. |
| **Server** (API) | Python 3.11+ (FastAPI) | `server/` | FastAPI REST API that serves analysis results from the filesystem and can trigger new analyses by spawning the Python analyzer as a child process. |
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

# --- Analyzer & Server ---
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Install analyzer + dev dependencies
pip install -e ".[dev]"

# Install server
cd server
pip install -e .
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
| **LLM — Primary** | | |
| `TRADING_PRIMARY_LLM_PROVIDER` | `openai` | Provider for the primary LLM (currently only `openai`) |
| `TRADING_OPENAI_API_KEY` | — | OpenAI API key (or compatible provider) |
| `TRADING_OPENAI_MODEL` | `gpt-4o` | LLM model identifier |
| `TRADING_OPENAI_BASE_URL` | `""` | OpenAI-compatible base URL (e.g. Ollama `http://localhost:11434/v1`, Groq, etc.); empty = `https://api.openai.com/v1` |
| `TRADING_OPENAI_REASONING_EFFORT` | `""` | Reasoning effort level (`low`, `medium`, `high`); empty = model default |
| `TRADING_OPENAI_MODEL_FAMILY_OVERRIDE` | — | Override detected model family for the primary LLM |
| `TRADING_OPENAI_MODEL_VERSION_OVERRIDE` | — | Override detected model version for the primary LLM |
| **LLM — Reviewer (independent)** | | |
| `TRADING_REVIEWER_LLM_PROVIDER` | `openai` | Provider for the reviewer LLM |
| `TRADING_REVIEWER_MODEL` | `""` | Model identifier (empty = use primary model) |
| `TRADING_REVIEWER_API_KEY` | `""` | API key (empty = use primary API key) |
| `TRADING_REVIEWER_BASE_URL` | `""` | Base URL (empty = default for provider) |
| `TRADING_REVIEWER_REASONING_EFFORT` | `""` | Reasoning effort for reviewer |
| `TRADING_REVIEWER_TEMPERATURE` | `0.0` | Temperature for the reviewer LLM |
| `TRADING_REVIEWER_MODEL_FAMILY_OVERRIDE` | — | Override detected model family for reviewer |
| `TRADING_REVIEWER_MODEL_VERSION_OVERRIDE` | — | Override detected model version for reviewer |
| **Review Policy** | | |
| `TRADING_REQUIRE_REVIEWER` | `True` | Require independent reviewer for executable decisions |
| `TRADING_ALLOW_UNREVIEWED_DECISIONS` | `False` | Allow decisions without review (forbidden in paper/live) |
| `TRADING_ALLOW_SAME_MODEL_DIFFERENT_DEPLOYMENT` | `False` | Allow reviewer to use same model family with different deployment |
| `TRADING_MAX_REVIEW_ATTEMPTS` | `2` | Maximum review retry attempts per symbol |
| **Cost** | | |
| `TRADING_COST_PER_SYMBOL_LIMIT` | `0.05` | Maximum allowed LLM cost per symbol (USD) |
| `TRADING_MODEL_PRICING` | *(see below)* | JSON dict of per-model token prices: `{"model": {"input_per_million": $/M, "cached_input_per_million": $/M, "output_per_million": $/M}}` |
| **Setup Policy** | | |
| `TRADING_ENABLE_COUNTERTREND` | `False` | Allow countertrend setups |
| `TRADING_MIN_RR_AAA` | `2.0` | Minimum reward-to-risk ratio for AAA-grade setups |
| `TRADING_MIN_RR_AA` | `2.0` | Minimum reward-to-risk ratio for AA-grade setups |
| `TRADING_MIN_RR_COUNTERTREND` | `2.5` | Minimum reward-to-risk ratio for countertrend setups |
| `TRADING_RISK_MULTIPLIER_AAA` | `1.0` | Risk multiplier for AAA-grade setups |
| `TRADING_RISK_MULTIPLIER_AA` | `0.5` | Risk multiplier for AA-grade setups |
| `TRADING_RISK_MULTIPLIER_COUNTERTREND` | `0.25` | Risk multiplier for countertrend setups |
| `TRADING_SETUP_EXPIRATION_H1_BARS` | `3` | Number of H1 bars before a setup expires |
| **Execution Mode** | | |
| `TRADING_EXECUTION_MODE` | `PAPER` | Execution mode: `DETERMINISTIC_BACKTEST`, `FULL_CHAIN_BACKTEST`, `DEVELOPMENT`, `SHADOW`, `PAPER`, `LIVE` |
| **Caching & Calendar** | | |
| `TRADING_CALENDAR_CACHE_HOURS` | `4` | Hours to cache ForexFactory calendar events |
| `TRADING_SYNTHESIZER_CACHE_ENABLED` | `True` | Enable LLM synthesizer output caching |
| `TRADING_ANALYSIS_CACHE_DIR` | `data` | Base directory for analysis disk cache and run results |
| **Candle Close Times** | | |
| `TRADING_D1_CLOSE_TIME` | `17:00` | D1 candle close time (`HH:MM` in broker time) |
| `TRADING_H4_CLOSE_TIME` | `00:00` | H4 anchor time (`HH:MM` in broker time); H4 length is fixed at 4 hours |
| **Telegram Notifications** | | |
| `TRADING_TELEGRAM_BOT_TOKEN` | `""` | Telegram bot token for trade notifications |
| `TRADING_TELEGRAM_CHAT_ID` | `""` | Telegram chat ID for notifications |
| `TRADING_WEB_UI_BASE_URL` | `http://localhost:3000` | Web UI base URL for notification links |
| **Logging** | | |
| `TRADING_LOG_LEVEL` | `INFO` | Logging level |

### Environment Variables — Server

Loaded from the environment (or a `.env` file) by the FastAPI server via `WebSettings`.
Uses backward-compatible unprefixed aliases for most vars; only `TRADING_ANALYSIS_CACHE_DIR`
retains its prefix since it is shared with the analyzer.

| Variable | Default | Description |
|---|---|---|
| `HOST` | `0.0.0.0` | HTTP listen address |
| `PORT` | `3000` | HTTP listen port |
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated allowed CORS origins |
| `PYTHON_CMD` | `python` | Python executable for spawning the analyzer |
| `TRADING_ANALYSIS_CACHE_DIR` | `data` | Base directory for analysis disk cache (shared with analyzer) |
| `TRADING_API_KEY` | — | API key for authenticated endpoints |
| `TRADING_RATE_LIMIT_MAX` | `20` | Max requests per rate-limit window |
| `TRADING_RATE_LIMIT_WINDOW` | `60` | Rate-limit window in seconds |

### Default Model Pricing

Prices are in **dollars per million tokens**. `cached_input_per_million` is set to `0.0`
when the provider does not offer a verified cached-input discount.

```json
{
  "gpt-4o":        {"input_per_million": 2.50, "cached_input_per_million": 1.25, "output_per_million": 10.00},
  "gpt-4o-mini":   {"input_per_million": 0.15, "cached_input_per_million": 0.075, "output_per_million": 0.60},
  "gpt-4":         {"input_per_million": 30.00, "cached_input_per_million": 0.0,  "output_per_million": 60.00},
  "gpt-3.5-turbo": {"input_per_million": 0.50, "cached_input_per_million": 0.0,  "output_per_million": 1.50}
}
```

Override via `TRADING_MODEL_PRICING` as a JSON environment variable. Only models with
verified official pricing are included by default; add additional models via the env var.
Any price set to `0.0` logs a warning — cost tracking will undercount.

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

# Send Telegram notifications for approved trade setups
python main.py EURUSD --telegram
```

### API Server

```bash
# Must use -m flag so src/ is resolved as a package
cd server && python -m src.main     # Runs uvicorn on port 3000
```

Or with hot-reload:

```bash
pip install watchfiles
uvicorn src.main:app --reload --port 3000
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

In production the FastAPI server serves the built UI files from `ui/dist/`.

### Programmatic Usage

```python
from config.settings import Settings
from src.data.terminal_data_provider import TerminalDataProvider
from src.analysis.structure_analyzer import MarketStructureEngine
from src.calendar.forexfactory import ForexFactoryCalendar
from src.decision.agents import SynthesizerAgent, DeciderAgent, ReviewerAgent
from src.decision.cost_tracker import CostTracker
from src.decision.llm_client import create_llm_client
from src.decision.llm_config import ProviderKind
from src.orchestrator.graph import TradingGraph

# Initialize settings (loads from .env / environment)
settings = Settings()

# Cost tracking with model-specific pricing
cost_tracker = CostTracker(pricing=settings.model_pricing)
cost_tracker.set_limit(settings.cost_per_symbol_limit)

# Wire up data provider
data_provider = TerminalDataProvider(
    server_url=settings.terminal_server_url,
    api_key=settings.terminal_api_key,
)

# Wire up analysis and calendar
structure_analyzer = MarketStructureEngine()
calendar_provider = ForexFactoryCalendar()

# Create LLM clients via factory
# Synthesizer and decider share the primary client; reviewer gets its own
api_key = settings.openai_api_key or ""
base_url = settings.openai_base_url or None
model = settings.openai_model
reasoning_effort = settings.openai_reasoning_effort or None

primary_client = create_llm_client(
    provider=ProviderKind(settings.primary_llm_provider),
    api_key=api_key,
    base_url=base_url,
    model=model,
    reasoning_effort=reasoning_effort,
)

# Reviewer can use a different model
reviewer_client = create_llm_client(
    provider=ProviderKind(settings.reviewer_llm_provider),
    api_key=settings.reviewer_api_key or api_key,
    base_url=settings.reviewer_base_url or base_url,
    model=settings.reviewer_model or model,
    reasoning_effort=settings.reviewer_reasoning_effort or reasoning_effort,
)

# Wire up LLM agents with their respective clients
synthesizer = SynthesizerAgent(
    llm_client=primary_client,
    cost_tracker=cost_tracker,
)
decider = DeciderAgent(
    llm_client=primary_client,
    cost_tracker=cost_tracker,
)
reviewer = ReviewerAgent(
    llm_client=reviewer_client,
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
│
├── scripts/                                 # Dev / CI helper scripts
│   ├── create-user.sh                       # Non-root user creation
│   └── start-dev.sh                         # Auto-starts FastAPI + Vite
│
├── analyzer/                                # Python analysis engine
│   ├── main.py                              # CLI entry point
│   ├── pyproject.toml
│   ├── config/
│   │   └── settings.py                      # Pydantic BaseSettings
│   ├── src/
│   │   ├── logging_config.py                # Logging setup
│   │   ├── analysis/                        # Market structure engine (16 modules)
│   │   │   └── market_structure_engine/
│   │   ├── calendar/                        # ForexFactory scraper + evaluator
│   │   ├── data/                            # MT5 data provider + snapshot builder
│   │   ├── decision/                        # LLM agents + protocols + cost tracker + LLM client
│   │   │   └── adapters/                    # Provider adapters (OpenAI, etc.)
│   │   ├── notification/                    # Telegram trade notifications
│   │   │   └── telegram_sender.py
│   │   ├── orchestrator/                    # LangGraph state machine
│   │   └── output/                          # Result models + JSON writer + OHLC cache
│   │       ├── result_models.py
│   │       ├── result_writer.py
│   │       ├── ohlc_cache.py
│   │       └── ohlc_extractor.py
│   └── tests/                               # 1001 tests
│
├── server/                                  # Python FastAPI
│   ├── pyproject.toml
│   ├── .env.example
│   ├── src/
│   │   ├── main.py                          # FastAPI app (port 3000)
│   │   ├── models.py                        # Pydantic DTOs
│   │   ├── runner.py                        # Spawns Python analyzer
│   │   ├── scanner.py                       # Reads result JSON files
│   │   ├── settings.py                      # WebSettings (pydantic-settings)
│   │   ├── middleware/
│   │   │   ├── auth.py                      # API key auth
│   │   │   └── ratelimit.py                 # Sliding window rate limiter
│   │   └── __init__.py
│   └── tests/                               # 104 tests
│       ├── conftest.py
│       ├── test_main.py
│       ├── test_routes.py
│       ├── test_runner.py
│       ├── test_scanner.py
│       └── test_settings.py
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
- **Structure Analyzer Adapter** (`src/analysis/structure_analyzer.py`): Wraps the engine
  output and validates the advisory-only invariant on every read — raises `ValueError` if
  `confluence.entry_authorized` is not `False`.

### Decision Layer (`analyzer/src/decision/`)

- **Protocols** (`protocols.py`): `DataSource`, `CalendarProvider`, `StructureAnalyzer` —
  runtime-checkable `typing.Protocol` interfaces for dependency injection.
- **LLM Client Architecture** (`llm_client.py`):
  - `LLMClientProtocol` — abstract protocol (structural typing via `@runtime_checkable`)
    defining `generate_structured()` (async) and `generate_structured_sync()` (sync) methods.
    Both return Pydantic models validated by `instructor`, with the sync variant also
    returning an `LLMUsage` tuple for cost tracking.
  - `OpenAIProviderAdapter` — concrete implementation wrapping an `instructor`-patched OpenAI
    client. Supports configurable `max_retries`, `temperature`, `reasoning_effort`, custom
    `base_url`, and model identity overrides. Both async and sync variants catch provider
    errors and re-raise as `LLMClientError`.
  - `create_llm_client()` — factory function dispatching by `ProviderKind` enum. Currently
    only `OPENAI` is registered; `ANTHROPIC` and `GENERIC` are gated. Raises
    `UnsupportedLLMProviderError` for unregistered providers.
- **Model Identity Resolution** (`llm_config.py`):
  - `LLMModelIdentity` — frozen dataclass carrying `provider`, `raw_model_identifier`,
    `model_family`, `model_version`, and `resolution_status`. Provides a `display_name`
    property for logging (e.g. `openai/gpt-4o/2024-08-06`).
  - `ModelIdentityResolver` — protocol for provider-specific resolvers. Implementations:
    `OpenAIModelIdentityResolver` (pattern: `gpt-{family}-{version}` / `o{family}-{version}`),
    `AnthropicModelIdentityResolver` (pattern: `claude-{version}-{variant}-{date}`),
    `GenericAliasModelIdentityResolver` (fallback — treats entire model string as family).
  - `resolve_model_identity()` — iterates registered resolvers in order, applies optional
    `family_override` / `version_override`, and returns the resolved identity.
  - `ProviderKind` — `StrEnum` with `OPENAI`, `ANTHROPIC`, `GENERIC` values.
  - `LLMModelConfig` — frozen dataclass bundling model, api_key, base_url, provider, and
    reasoning_effort for end-to-end configuration.
- **Usage Tracking** (`usage.py`):
  - `LLMUsage` — frozen dataclass with `input_tokens`, `cached_input_tokens`,
    `uncached_input_tokens`, `output_tokens`, `reasoning_tokens`, `total_tokens`, and
    corresponding cost fields (filled in by `CostTracker`).
  - `parse_usage()` — parses raw provider responses extracting token counts from either
    Responses API or Chat Completions field names. Handles partial/missing data gracefully
    — all fields default to `0`.
- **Models** (`models.py`): Pydantic models for `MarketContextSummary` (bias, confidence,
  reasoning, key levels, structural events, calendar context, canonical current price),
  `DecisionOutput` (symbol, action, reasoning — no `entry_authorized` field), and
  `ReviewVerdict` (status, reasoning, concerns, suggested improvements, plus six
  deterministic compliance flags). `DecisionAction` and `ReviewStatus` enums are re-exported
  from the engine.
- **Agents** (`agents.py`): Three LLM agents, each accepting an `LLMClientProtocol` instance
  and optional `CostTracker`:
  - `SynthesizerAgent` — combines structure analysis + calendar events → `MarketContextSummary`
  - `DeciderAgent` — generates trading decision (action + reasoning) from context + positions
  - `ReviewerAgent` — independent quality review of the decision with structured verdict
  - All agents log call-level cost via `_log_llm_call()` using the injected cost tracker.
- **Two-LLM-Instance Architecture** (`main.py:_create_agents`): The synthesizer and decider
  share a **primary** LLM client. The reviewer receives its own **reviewer** client, which
  can use a different model, API key, base URL, reasoning effort, and model family/version
  overrides — all configured via environment variables (`TRADING_REVIEWER_MODEL`,
  `TRADING_REVIEWER_API_KEY`, etc.).
- **CostTracker** (`cost_tracker.py`): Tracks cumulative token usage and USD cost per symbol
  using per-model pricing tables (`input_per_million`, `cached_input_per_million`,
  `output_per_million`). Raises `CostLimitExceeded` when `cost_per_symbol_limit` is exceeded
  — this exception propagates up through the LangGraph pipeline and is caught by the CLI
  entry point, halting the run for that symbol.
- **Enforcement Gate** (`enforcement.py`): `DeterministicEnforcementGate` — purely
  deterministic (no LLM calls, no I/O). The `enforce()` method runs five invariant checks
  against the full pipeline state (setup, policy, risk, decision, review):
  1. `CANDIDATE_NOT_GENERATED` — executable action without a classified candidate
  2. `EXECUTION_NOT_ACTIONABLE` — executable action while execution status is not `ACTIONABLE`
  3. `DIRECTION_MISMATCH` — decision action contradicts deterministic trade direction
  4. `INVALID_GEOMETRY` — executable action while entry geometry is not `VALID`
  5. `ACTION_NOT_ALLOWED` — decision action not in the derived allowed actions set
  - If any violation is found: `final_action = NO_TRADE`, `status = BLOCKED_BY_ENFORCEMENT`
  - If action is executable but review not approved: `status = BLOCKED_BY_REVIEW`
  - Otherwise: pass-through of pre-review execution status and decision action.
- **SynthesizerCache** (`synthesizer_cache.py`): Content-addressable cache for synthesizer
  outputs, keyed by `symbol / calendar-date / H1-closing-hour`. Day boundaries align with
  calendar midnight (not D1 candle close). When identical analysis inputs are re-encountered
  (same symbol, same day, same H1 hour), the cached `MarketContextSummary` is returned,
  saving both time and cost. Best-effort writes — failures log a warning and do not raise.
  Legacy cache files (pre-H1-hour-suffix format) are cleaned up automatically.
- **Output Assembler** (`output_assembler.py`): `FinalOutputAssembler` — stateless mapper
  collecting structured state from every pipeline stage into a single `AnalysisResult`.
  Deterministic values (enforcement action, SL/TP from engine) always override LLM-produced
  values. Produces a JSON-serialisable result for the web dashboard.

### Calendar Layer (`analyzer/src/calendar/`)

- **ForexFactoryCalendar** (`CalendarProvider` protocol): Scrapes ForexFactory economic
  calendar with 4-hour in-memory caching. Filters by upcoming events.
- **Evaluator**: Filters events by relevant currencies and impact level (high/medium/low) for
  the analyzed symbol.

### Orchestrator (`analyzer/src/orchestrator/`)

- **TradingGraph**: LangGraph state machine with 13 nodes (plus END). Manages the full
  14-node pipeline with two conditional routing branches:
  - `early_execution_routing` bypasses the LLM entirely when the deterministic engine
    classifies the setup as `NON_EXECUTABLE` or `BLOCKED_BY_DATA_QUALITY`
  - `review` routes to `retry_decide` when `REVISION_REQUIRED` and attempts remain, or to
    `continue_enforcement` when approved/maxed out
  - State is modelled as a `TypedDict` (`AgentState`) with typed fields grouped by
    provenance (market data, structure analysis, deterministic pipeline, LLM agents,
    enforcement, output).

### Configuration (`analyzer/config/`)

- **Settings**: Pydantic `BaseSettings` class binding all environment variables (`TRADING_`
  prefix). Supports `.env` file loading, field validation, and complex types like
  `dict[str, dict[str, float]]` for model pricing (auto-parsed from JSON env var).
  Includes execution-mode validation (paper/live modes require reviewer enforcement).
  Provides `resolved_analysis_cache_dir` property that resolves relative paths against the
  project root.

### Server (`server/`)

- **FastAPI app** (`src/main.py`): CORS-configured REST API that serves result JSON files
  from the filesystem and proxies new analysis runs to the Python CLI.
- **ResultScanner** (`src/scanner.py`): Walks the `data/` directory tree, parses
  result JSON files, and returns typed `RunSummary` or `FullResult` objects.
- **RunService** (`src/runner.py`): Spawns `python main.py` as a child process with
  the requested symbols and optional model override. Enforces a 10-minute timeout.
- **Routes**: `GET /api/runs` (list with filters), `GET /api/runs/:symbol/:year/:month/:day/:file`
  (detail), `POST /api/run` (trigger).
- **Middleware**: API key authentication (`middleware/auth.py`) and sliding-window rate
  limiting (`middleware/ratelimit.py`).

### UI (`ui/`)

- **Dashboard view** (`Dashboard.vue`): Lists all analysis runs with symbol, bias, confidence,
  action, review status, and current price. Includes filters and a symbol sidebar.
- **Detail view** (`Detail.vue`): Full analysis breakdown for a single symbol — OHLC chart
  with SL/TP overlay, decision reasoning, review verdict, and calendar context.
- **Components**: `OhlcChart.vue` (echarts candle chart), `RunCard.vue` (run summary card),
  `SymbolSidebar.vue` (symbol filter), `TimelineBar.vue` (time-based run navigation).
- **API client** (`lib/api.ts`): Axios-based client communicating with the FastAPI server.

## Docker

The project includes Docker support for both development and production environments.

### Prerequisites

- Docker Engine 24+
- Docker Compose v2+

### Development

The dev container runs as a non-root user matching your host UID/GID (set in `.env` as
`UID`/`GID`). This avoids root-owned files in bind-mounted directories. Set `UID` and `GID`
to your user's values (`id -u` and `id -g`) before building.

#### First-time setup

```bash
# 1. Build the image and start the container
docker compose -f docker-compose.devel.yml up -d --build

# 2. Install all Python dependencies (analyzer + server share the same venv)
docker compose -f docker-compose.devel.yml exec trading-agent bash \
  -c "cd /app/analyzer && pip install -e '.[dev]' && cd /app/server && pip install -e ."

# 3. (Optional) Install UI dependencies for frontend development
docker compose -f docker-compose.devel.yml exec trading-agent bash \
  -c "cd /app/ui && npm install"
```

The dev container uses bind mounts for all source directories, so code changes on the host
are immediately visible inside the container. The container stays alive with `sleep infinity` —
use `docker compose exec` to run commands.

#### Running commands

**Development** — run the API server and the Vite dev server in separate shells.
The Vite dev server (port 5173) proxies `/api` requests to the API (port 3000)
and provides hot-reload. No UI rebuild is needed during development.

```bash
# Shell 1 — start the API server (port 3000)
docker compose -f docker-compose.devel.yml exec trading-agent bash \
  -c "cd /app/server && python -m src.main"

# Shell 2 — start the Vite dev server (port 5173, proxies /api → :3000)
docker compose -f docker-compose.devel.yml exec trading-agent bash \
  -c "cd /app/ui && npm run dev"
```

**Testing the production build locally** — build the UI first, then start the
server. The FastAPI server serves the built files from `ui/dist/` when they exist.

```bash
# 1. Build the UI (outputs to ui/dist/)
docker compose -f docker-compose.devel.yml exec trading-agent bash \
  -c "cd /app/ui && npm run build"

# 2. Start the server — now serves both API and UI on port 3000
docker compose -f docker-compose.devel.yml exec trading-agent bash \
  -c "cd /app/server && python -m src.main"
```

**Other commands**

```bash
# Run the analyzer
docker compose -f docker-compose.devel.yml exec trading-agent bash \
  -c "cd /app/analyzer && python main.py XAUUSD"

# Run analyzer tests
docker compose -f docker-compose.devel.yml exec trading-agent bash \
  -c "cd /app/analyzer && pytest"

# Run server tests
docker compose -f docker-compose.devel.yml exec trading-agent bash \
  -c "cd /app/server && python -m pytest"

# Run UI tests
docker compose -f docker-compose.devel.yml exec trading-agent bash \
  -c "cd /app/ui && npm run test"

# Open a shell inside the container
docker compose -f docker-compose.devel.yml exec trading-agent bash
```

#### Migration from root-based setup

If you were running the container before the non-root user change, remove the old
named volume first — it still contains root-owned files:

```bash
docker compose -f docker-compose.devel.yml down
docker volume rm agent_trading_node_modules
docker compose -f docker-compose.devel.yml up -d
```

Then re-run the first-time setup commands above.

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

- All dependencies are installed at build time (`pip install`, `npm ci`)
- The Vue UI is built into static files (`ui/dist/`)
- The FastAPI server serves both the REST API and the built UI on port 3000
- Only the `data/` directory is persisted via bind mount

### Images

| Image | Base | Size | Purpose |
|---|---|---|---|
| `trading-agent:devel` | Ubuntu 26.04 | ~270 MB content | Development with bind mounts, Python venv, Node.js (for UI toolchain) |
| `trading-agent:prod` | Ubuntu 26.04 | ~400 MB content | Production with all deps baked in, UI built |

## Testing

```bash
# Analyzer (Python) — run from analyzer/
cd analyzer

# Run all tests (1001 tests)
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run a specific test file
pytest tests/decision/test_cost_tracker.py -v

# Run tests matching a keyword
pytest -k "cache"

# Server (Python)
cd server && python -m pytest

# UI type checking
cd ui && npm run typecheck   # vue-tsc
```

### Test Coverage — Analyzer

The test suite contains **1001 tests** covering:

- **Analysis**: Candle cache engine fields, market structure engine modules
- **Calendar**: Event evaluator logic
- **Config**: Settings loading, env prefix, validation, model pricing, execution policy
- **Data**: Snapshot builder, terminal data provider (retry, auth, broker time)
- **Decision**: Agents (API key handling, prompt rendering), cost tracker, models, protocols,
  synthesizer cache, LLM client, LLM config, enforcement gate
- **Notification**: Telegram sender
- **Output**: Result writer, OHLC cache, result models
- **Orchestrator**: Full graph pipeline, canonical price handling, synthesizer cache integration
- **Main**: CLI entry point argument handling
- **Integration**: End-to-end pipeline integration

All external dependencies (MT5 terminal, LLM API, ForexFactory) are mocked in tests.

**Server** has **104 tests** covering routes, runner, scanner, settings, and integration.

### Project Facts and Conventions

- **Two-package monorepo**: `analyzer/` (trading-ai-agent, pip-installable) + `server/` (trading-server, pip-installable)
- **Advisory-only**: `entry_authorized` is hardcoded `False` in the engine, validated by the structure analyzer adapter, instructed in LLM prompts, and enforced post-hoc by `DeterministicEnforcementGate` — the system never executes trades
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
│  │  src/logging_config.py │     │  src/runner.py — spawns       │   │
│  │  src/decision/         │ ◄──│  analyzer as subprocess       │   │
│  │  src/orchestrator/      │sub │  src/scanner.py — reads       │   │
│  │  src/analysis/          │pr  │  result files from disk        │   │
│  │  src/calendar/          │ocess│  src/settings.py — WebSettings │   │
│  │  src/data/              │     │  src/models.py — Pydantic dtos │   │
│  │  src/notification/      │     │  src/middleware/              │   │
│  │  src/output/            │     │  tests/                       │   │
│  │  config/settings.py ◄───┼─────┤                               │   │
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
python -m src.main          # uvicorn (port 3000) — -m flag required for src/ package
python -m pytest            # run tests
uvicorn src.main:app --reload --port 3000  # hot-reload (requires watchfiles)

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
5. Ensure `entry_authorized = False` in all engine confluence outputs (the structure analyzer adapter and enforcement gate enforce this)
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
- `fastapi` — HTTP framework
- `uvicorn[standard]` — ASGI server
- `pydantic` + `pydantic-settings` — Data validation and configuration
- `pytest` — Testing

**UI:**
- `vue` + `vue-router` — Frontend framework
- `vue-echarts` + `echarts` — OHLC chart rendering
- `axios` — HTTP client
- `vite`, `vue-tsc`, `tailwindcss` — Dev toolchain

## License

MIT License
