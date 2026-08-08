# Agent Instructions

## Graphify first

This project has a persistent knowledge graph at `graphify-out/`. Run `graphify query "<question>"` for any codebase question before grepping or reading source. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused explanations. If `graphify-out/wiki/index.md` exists, use it for broad navigation.

Dirty graph files after hooks/incremental updates are normal — not a reason to skip.

After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).

## Architecture

**Monorepo with three packages:**

| Directory | Language | Role |
|---|---|---|
| `analyzer/` | Python 3.11+ | CLI trading analysis engine. Entry: `main.py`. LangGraph state machine in `src/orchestrator/graph.py`. |
| `server/` | Python 3.11+ (FastAPI) | REST API serving analysis results + triggering new runs. Entry: `src/main.py`. |
| `ui/` | Vue 3 + Vite | Dark-terminal web dashboard. |

**Pipeline (per symbol):** `fetch_data` → `analyze_structure` → `evaluate_calendar` → `synthesize_context` → `grade_setup` → `build_risk_policy` → `evaluate_execution_policy` → `early_execution_routing` → (`decide` | deterministic NO_TRADE) → `pre_review_decision_validation` → `review` → (retry to `decide` | `final_enforcement`) → `assemble_output` → END

**Key modules:**
- `analyzer/src/data/terminal_data_provider.py` — MT5 data via MCP server (retry logic, async wrapped sync)
- `analyzer/src/analysis/structure_analyzer.py` — Delegates to `market_structure_engine/` (16-module deterministic engine)
- `analyzer/src/calendar/forexfactory.py` — ForexFactory scraper with 4h cache
- `analyzer/src/decision/agents.py` — LLM agents using `instructor` for structured output

## Critical invariants

- **Advisory-only**: `entry_authorized` must always be `False`. Enforced at four layers: the deterministic engine hardcodes it; the structure analyzer adapter validates on read; the LLM prompts instruct the model; and the `DeterministicEnforcementGate` blocks post-hoc.
- **Environment prefix**: Analyzer settings use `TRADING_` prefix via `pydantic-settings` (`config/settings.py`). Server `WebSettings` (`server/src/settings.py`) uses **unprefixed aliases** for most vars (`HOST`, `PORT`, `CORS_ORIGINS`, `PYTHON_CMD`) for backward compatibility; only `TRADING_ANALYSIS_CACHE_DIR`, `TRADING_API_KEY`, `TRADING_RATE_LIMIT_MAX`, `TRADING_RATE_LIMIT_WINDOW`, `TRADING_TERMINAL_SERVER_URL` keep the prefix (all shared with the analyzer). `TRADING_TRUSTED_PROXY_CIDRS` also keeps the prefix — it is spec-mandated by DEC-008/FR-036 even though it is server-only (reverse-proxy source networks for the `X-Authenticated-User` marker). The server reads `TRADING_TERMINAL_SERVER_URL` for its readiness MCP probe (ticket 08).
- **Protocol DI**: Dependencies injected via protocols in `analyzer/src/decision/protocols.py` (`DataSource`, `CalendarProvider`, `StructureAnalyzer`). Orchestration code never imports concrete implementations.

## Development environment (Docker)

All commands below **must be run inside the developer Docker container**. The container runs as
a non-root user matching your host UID/GID (set in `.env` as `UID`/`GID`). The container
provides Ubuntu 26.04 with Node.js, Python 3, and a virtual environment at `/app/.venv`
(auto-activated by the startup script). Source code is mounted live from the host so changes
take effect immediately.

### Setup

See the [Docker Development section in README.md](./README.md#development) for a complete
first-time setup guide (build, start, install dependencies).

### Starting the container

```bash
# Build (first time or after dependency changes)
docker compose -f docker-compose.devel.yml build

# Start the container — auto-launches FastAPI (reload) + Vite (HMR)
docker compose -f docker-compose.devel.yml up -d

# Open a shell inside the running container
docker compose -f docker-compose.devel.yml exec trading-agent bash
```

### Stopping

```bash
docker compose -f docker-compose.devel.yml down
```

### Quick commands (run inside container)

```bash
# Analyzer — run everything
cd analyzer && mypy src/ && ruff check src/ && pytest

# Single test
cd analyzer && pytest tests/decision/test_models.py -v

# Server tests
cd server && python -m pytest

# UI typecheck and build
cd ui && npm run typecheck               # vue-tsc --noEmit
cd ui && npm run build                   # Vite build → ui/dist/
```

> **Note:** FastAPI and the Vite dev server **auto-start** when the container boots.
> Access the dev UI at **http://localhost:5173**.
> FastAPI runs internally on port 3000 — Vite proxies `/api/*` requests to it.
> Editing `.py` files auto-reloads FastAPI; editing `.vue`/`.ts` files triggers Vite HMR.

### Running from Docker (host → container)

```bash
# Start the API server (FastAPI auto-starts, this is for manual restart)
docker compose -f docker-compose.devel.yml exec trading-agent bash \
  -c "pkill -f 'python -m src.main' 2>/dev/null; sleep 1; cd /app/server && python -m uvicorn src.main:app --host 0.0.0.0 --port 3000 --reload"

# Run the analyzer CLI
docker compose -f docker-compose.devel.yml exec trading-agent bash \
  -c "cd /app/analyzer && python main.py XAUUSD"
```

## Testing

- **Analyzer**: 1001 tests, pytest with `asyncio_mode = "auto"`. Fixtures in `tests/conftest.py`: `sample_market_context`, `sample_decision`, `sample_review`.
- **Server**: 104 tests, pytest with `asyncio_mode = "auto"`. Client fixtures in `server/tests/conftest.py` mock scanner+runner.
- All external dependencies (MT5 terminal, LLM API, ForexFactory) are mocked.
- **Quirk**: Module-level `_settings` singleton in `candle_cache.py` and `synthesizer_cache.py` must be manually invalidated in tests — no refresh mechanism.

## Pre-commit hooks

`.pre-commit-config.yaml` is active (install with `pre-commit install`). Hooks: `ruff` (lint+fix, blocks on unfixed), `ruff-format`, `mypy` (`analyzer/src/` only), trailing-whitespace, end-of-file-fixer, check-yaml, check-added-large-files (excludes `graphify-out/`), check-merge-conflict, debug-statements. The graphify-update hook was removed to avoid infinite loops on graphify-out/ changes.

## Toolchain

- **ruff** for lint + format (line-length 100, target py311). Select rules: `E`, `F`, `I`, `N`, `W`, `UP`.
- **mypy** strict mode, Python 3.12 target in config (runtime is 3.14).
- **Server**: FastAPI + uvicorn. Auth via `X-API-Key` header (`TRADING_API_KEY`). Rate limiting via `TRADING_RATE_LIMIT_MAX`/`TRADING_RATE_LIMIT_WINDOW`. Spawns analyzer as subprocess with 10-minute timeout and result-polling with retry.
- No CI is configured.

## Architectural notes

- The server was ported **from Node.js/Express to Python/FastAPI**. All `.ts` files were removed.
- `analyzer/main.py` is a 492-line CLI entry point accepting symbols, `--model`, `--base-url`, `--log-level`, `--telegram`.
- Synthesizer caching is content-addressable: identical structure analysis + calendar events skip the LLM call.
- Candle caching is disk-backed, keyed by `symbol/timeframe/candle_close_time`, with broker-local time alignment.
- The `/data/` directory tree stores versioned JSON results (`<symbol>/<year>/<month>/<day>/result-<time>.json`).

## Agent skills

### Issue tracker

Issues are tracked on GitHub Issues for this repo. See `docs/agents/issue-tracker.md`.

### Triage labels

Five canonical triage labels, each matching its name. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout — one `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.
