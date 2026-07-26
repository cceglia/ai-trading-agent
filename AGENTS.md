# Agent Instructions

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

MUST use graphify for any codebase question before doing anything else. Do not skip it.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- Dirty graphify-out/ files are expected after hooks or incremental updates; dirty graph files are not a reason to skip graphify. Only skip graphify if the task is about stale or incorrect graph output, or the user explicitly says not to use it.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
- `.graphifyignore` excludes `__pycache__/`, `.venv/`, `.pytest_cache/`, `.opencode/`, `analysis/`, `.env`, and IDE files from extraction.

## Quick Commands

```bash
# Install (from analyzer/ directory)
cd analyzer && pip install -e ".[dev]"

# Type check → lint → test (run from analyzer/)
cd analyzer && mypy src/ && ruff check src/ && pytest

# Single test file
cd analyzer && pytest tests/decision/test_models.py -v

# Format
cd analyzer && ruff format src/
```

## Critical Invariants

- **Advisory-only**: `entry_authorized` must always be `False` in `DecisionOutput`. This system never executes trades.
- **Environment prefix**: All settings use `TRADING_` prefix (e.g., `TRADING_OPENAI_API_KEY`). See `config/settings.py` `model_config`.
- **Protocol DI**: All dependencies are injected via protocols in `analyzer/src/decision/protocols.py` (`DataSource`, `CalendarProvider`, `StructureAnalyzer`). Do not import concrete implementations in orchestration code.

## Architecture

Entry point: `analyzer/main.py` → `TradingGraph` (LangGraph state machine in `analyzer/src/orchestrator/graph.py`)

Pipeline: `fetch_data` → `analyze_structure` → `evaluate_calendar` → `synthesize_context` → `decide` → `review` → (retry or end)

Key modules:
- `analyzer/src/data/mt5_data_provider.py` — MT5 data via MCP server (has retry logic, async internals wrapped sync)
- `analyzer/src/analysis/structure_analyzer.py` — Delegates to `market_structure_engine/` (16-module deterministic engine)
- `analyzer/src/calendar/forexfactory.py` — ForexFactory scraper with 4h cache
- `analyzer/src/decision/agents.py` — LLM agents using `instructor` for structured output
- `rules.json` — Bias calculation rules and evidence hierarchy (loaded by analysis)

## Testing

- Framework: pytest with `asyncio_mode = "auto"`
- Fixtures in `tests/conftest.py`: `sample_market_context`, `sample_decision`, `sample_review`
- All external dependencies (MT5, LLM) are mocked in tests
- Run full suite: `pytest` (from analyzer/)

## Toolchain

- Python 3.11+ required
- `ruff` for lint + format (line-length 100, target py311)
- `mypy` strict mode
- No pre-commit hooks or CI configured
