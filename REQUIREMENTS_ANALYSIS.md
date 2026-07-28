## REQUIREMENTS_ANALYSIS

### Normalized Feature Request
Fix 17 code review findings (3 Critical, 3 High, 6 Medium, 5 Low) across the two-package monorepo — analyzer (trading pipeline) and server (FastAPI web API) — plus Dockerfile.prod and test files. Issues span security (missing deps, no auth, token leakage), performance (os.walk on every request, scanner re-creation), correctness (race condition, exception chaining), and maintainability (settings duplication, long functions, naming). No feature additions.

### Included Scope

1. **Missing Server Dependencies (Critical)** — server/pyproject.toml lists only fastapi and uvicorn; imports pydantic and pydantic_settings fail without analyzer's transitive install.
2. **No Authentication or Rate Limiting on POST /api/run (Critical)** — open spending endpoint; each invocation triggers up to 6 LLM calls per symbol (~$0.02/symbol with GPT-4o).
3. **Token Leakage Risk in Telegram URL (Critical)** — bot token embedded in URL string passed to requests.post; could appear in debug logs or error tracking on network failure.
4. **Post-Analysis Race Condition on File Read (High)** — `_read_results` immediately reads result files after `_spawn_process` returns; no guarantee filesystem flush under NFS/heavy I/O.
5. **os.walk Scans Entire Directory on Every Request (High)** — `list_runs()` traverses full data tree and parses every .json before applying filters.
6. **Broad Exception Catching Obscures Real Errors (High)** — bare `except Exception` in list_runs/get_run raises generic RuntimeError with no diagnostic detail.
7. **CORS Configuration Too Permissive (Medium)** — allows all methods (["*"]) and headers (["*"]).
8. **Runner Creates Scanner Instance on Every Call (Medium)** — `_read_results` allocates a new ResultScanner each time, triggering a full directory walk.
9. **Settings Duplication Between Analyzer and Server (Medium)** — `TRADING_ANALYSIS_CACHE_DIR` / `analysis_cache_dir` defined in both `Settings` and `WebSettings` with different path-resolution behavior.
10. **_normalize_cors Validator Duplicates _CommaDelimitedEnvSource Logic (Medium)** — comma-splitting implemented in both custom EnvSettingsSource and model_validator; validator is redundant for env-based usage.
11. **Permanent Settings() Singleton in candle_cache Cannot Be Refreshed (Medium)** — module-level `_settings` singleton must be manually invalidated in tests; no refresh mechanism without process restart.
12. **Inconsistent Exception Chaining in POST /api/run (Medium)** — three overlapping branches (TimeoutError→RuntimeError, RuntimeError→pass-through, Exception→RuntimeError) all produce RuntimeError; needlessly complex.
13. **Long main() Function (Low)** — 165 lines handling argument parsing, initialization, per-symbol orchestration, output writing, Telegram notifications.
14. **Unused request Parameter in Exception Handler (Low)** — `request` parameter unused in `http_exception_handler`.
15. **Deferred Imports Make Dependency Errors Opaque (Low)** — imports inside try block cause ImportError to be caught by same handler as runtime failures.
16. **Type Hint: sample_full_result Fixture Returns dict Without Generic (Low)** — should be `dict[str, Any]`.
17. **Test Naming Inconsistency (Low)** — `test_sellsend_message` missing underscore vs `test_sends_buy_message`.

### Excluded Scope

- No changes to the analyzer pipeline business logic (decision flow, LangGraph state machine, agent models, protocol interfaces).
- No changes to the Vue 3 UI (`ui/` directory).
- No real trade execution; `entry_authorized` remains `False`.
- No changes to Dockerfile.dev or docker-compose.devel.yml.
- No changes to `.graphifyignore`.
- No introduction of new external dependencies beyond what's needed for the fixes (pydantic, pydantic-settings in server/pyproject.toml).
- No Telegram bot interactivity (one-way outbound only; no webhooks, no command handling).

### Project Facts (with file paths)

- **Two-package monorepo**: `analyzer/` (trading-ai-agent, pip-installable) + `server/` (trading-server, pip-installable).
- **analyzer/pyproject.toml**: depends on `pydantic-settings>=2.0.0`, `openai`, `instructor`, `langgraph`, `requests`, `beautifulsoup4`, `mcp`, `fastapi`, `uvicorn`. Dev deps: `pytest`, `pytest-asyncio`, `pytest-cov`, `mypy`, `ruff`, `responses`, `httpx`.
- **server/pyproject.toml**: depends on `fastapi>=0.115.0`, `uvicorn[standard]>=0.32.0`. Only. Missing `pydantic>=2.0.0` and `pydantic-settings>=2.0.0`. Uses `asyncio_mode = "auto"`.
- **Dockerfile.prod:17-18**: `COPY server/pyproject.toml ./server/ && pip install "."` — server installed first, analyzer second. Server works only because analyzer pulls in pydantic transitively.
- **analyzer/config/settings.py:104-106**: `analysis_cache_dir: str = Field(default="data")` with `model_config = {"env_prefix": "TRADING_"}` → env var `TRADING_ANALYSIS_CACHE_DIR`.
- **server/src/settings.py:50**: `analysis_cache_dir: str = Field(default="data", alias="TRADING_ANALYSIS_CACHE_DIR")` with `resolved_cache_dir` property resolving relative to project root → `analyzer/`.
- **server/src/main.py:86-111**: POST /api/run — no auth middleware, no rate limiting. Calls `runner.run_analysis()` which spawns analyzer subprocess.
- **server/src/runner.py:87-90**: `_read_results` creates `ResultScanner(self.data_dir)` on every call.
- **server/src/runner.py:46-47**: `await self._spawn_process(args)` then immediately `return self._read_results(symbols)` — no filesystem sync guarantee.
- **analyzer/src/notification/telegram_sender.py:56**: `f"https://api.telegram.org/bot{bot_token}/sendMessage"` — token in URL string.
- **analyzer/src/analysis/candle_cache.py:12-21**: Module-level `_settings: Settings | None = None` singleton created by `_get_settings()` — no refresh mechanism.
- **analyzer/main.py:167-217**: All imports (`MarketStructureEngine`, `ForexFactoryCalendar`, `TerminalDataProvider`, agents, `TradingGraph`, `ResultWriter`) inside `try` block at line 166.
- **server/src/main.py:118-120**: `async def http_exception_handler(request, exc):` — `request` parameter unused.
- **server/tests/conftest.py:32**: `def sample_full_result() -> dict:` — missing generic `dict[str, Any]`.
- **analyzer/tests/notification/test_telegram_sender.py:36**: `def test_sellsend_message` — missing underscore vs `test_sends_buy_message` at line 11.
- **analyzer/tests/conftest.py:13-25**: `reset_candle_cache_settings` autouse fixture manually resets `candle_cache._settings = None` — this is the workaround for Issue #11.
- **analyzer/tests/notification/conftest.py**: Separate fixtures (`sample_decision` returns dict, `sample_context`, `sample_review`) for telegram tests.
- **Previous plans exist** at `.opencode/plans/` covering related but distinct code review fix sets (code-review-fixes-plan.md, phase2-review-fixes-plan.md, post-review-fixes-plan.md, review-fixes-plan.md). Some issues overlap thematically but the specific file versions and exact findings differ.

### Project Conventions and Constraints

1. **Advisory-only**: `entry_authorized` must always be `False` in `DecisionOutput` — never executes trades (AGENTS.md Critical Invariant #1).
2. **TRADING_ env prefix**: All settings use `TRADING_` prefix (AGENTS.md Critical Invariant #2, analyzer/config/settings.py:111).
3. **Protocol DI**: Dependencies injected via protocols in `analyzer/src/decision/protocols.py` — never import concrete implementations in orchestration code (AGENTS.md Critical Invariant #3).
4. **pytest** with `asyncio_mode = "auto"` (both analyzer/pyproject.toml:35 and server/pyproject.toml:13).
5. **mypy strict mode** (analyzer/pyproject.toml:38-39).
6. **ruff** lint+format: line-length 100, target py311 (analyzer/pyproject.toml:42-43).
7. **Python 3.11+ required**.
8. **No pre-commit hooks or CI configured** (AGENTS.md).
9. **Module-level `_settings` singleton pattern** in `candle_cache.py` and `synthesizer_cache.py` — requires manual `_settings = None` reset in tests (established pattern, considered known limitation).
10. **After modifying code**, run `graphify update .` to keep the knowledge graph current (AGENTS.md).
11. **All external dependencies (MT5, LLM) are mocked in tests** (AGENTS.md).

### Existing Architecture and Responsibility Boundaries

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
- **Shared config surface**: `TRADING_ANALYSIS_CACHE_DIR` is the single shared env var between `analyzer/config/settings.py` and `server/src/settings.py`.
- **Server uses aliases for env vars** (e.g., `HOST`, `PORT`, `PYTHON_CMD`) — these do NOT use `TRADING_` prefix. Only `TRADING_ANALYSIS_CACHE_DIR` retains its prefix.
- **Scanner reads disk data** — no direct analyzer dependency. `ResultScanner` walks the directory tree written by analyzer's `ResultWriter`.
- **Runner is the bridge**: `RunService._spawn_process` → analyzer subprocess → `_read_results` → `ResultScanner` to return results to API caller.

### External Dependencies and I/O Boundaries

| Dependency | Used By | Type |
|---|---|---|
| OpenAI API | analyzer/src/decision/agents.py | Network (HTTPS) |
| MetaTrader 5 MCP server | analyzer/src/data/terminal_data_provider.py | Local network (MCP over HTTP) |
| ForexFactory (via BeautifulSoup) | analyzer/src/calendar/forexfactory.py | Network (HTTPS, web scraping) |
| Telegram Bot API | analyzer/src/notification/telegram_sender.py | Network (HTTPS) |
| Filesystem (result cache) | analyzer/src/output/result_writer.py, analyzer/src/analysis/candle_cache.py, server/src/scanner.py | Local disk |
| Python subprocess | server/src/runner.py | OS process spawn |
| FastAPI / Uvicorn | server/src/main.py | Web server |
| LLM (via `instructor` + `openai`) | analyzer/src/decision/agents.py | Network (HTTPS) |

### Likely Production Files to Modify

1. `server/pyproject.toml` — add pydantic dependencies (#1)
2. `Dockerfile.prod` — may need layer reordering if dependency order matters (#1)
3. `server/src/main.py` — add auth middleware, rate limiting (#2); fix exception error logging (#6); tighten CORS (#7); simplify exception chaining (#12); prefix unused param (#14)
4. `server/src/settings.py` — remove duplicate _normalize_cors validator (#10)
5. `server/src/runner.py` — add filesystem flush/retry loop after subprocess (#4); make scanner a lazy instance attribute (#8)
6. `server/src/scanner.py` — add directory-based pruning for symbol filter (#5); add LRU caching (#5)
7. `analyzer/src/notification/telegram_sender.py` — sanitize token from URL/error logs (#3)
8. `analyzer/main.py` — split main() into smaller functions (#13); move imports outside try block (#15)
9. `analyzer/config/settings.py` — possibly extract shared settings base class (#9)
10. `analyzer/src/analysis/candle_cache.py` — possibly refactor _settings singleton; or document as known limitation (#11; may be excluded)
11. `server/tests/conftest.py` — fix type hint (#16)

### Likely Test Files to Modify

1. `analyzer/tests/notification/test_telegram_sender.py` — fix test_sellsend_message naming (#17)
2. `server/tests/test_scanner.py` — new tests for directory-based pruning and caching (#5)
3. `server/tests/test_runner.py` — new tests for retry loop (#4) and scanner reuse (#8)
4. `server/tests/test_main.py` — new tests for auth/rate limiting (#2), CORS restriction (#7), exception logging (#6/#12), unused param (#14)
5. `server/tests/test_settings.py` — new tests for _normalize_cors removal (#10)
6. `server/tests/conftest.py` — fix sample_full_result type hint (#16)
7. `analyzer/tests/conftest.py` — may need updates if _settings singleton is refactored (#11)
8. `analyzer/tests/notification/test_telegram_sender.py` — verify token sanitization behavior (#3)

### Detected Test Engine and Commands

- **Framework**: pytest with `asyncio_mode = "auto"` (both analyzer/pyproject.toml and server/pyproject.toml).
- **Analyzer tests**: `cd analyzer && pytest` (347+ existing tests per phase2-review-fixes-plan).
- **Server tests**: `cd server && pytest` (likely small or none yet — need to verify).
- **Full check**: `cd analyzer && mypy src/ && ruff check src/ && pytest`.
- **Formatter**: `cd analyzer && ruff format src/`.
- **Test fixtures**:
  - `analyzer/tests/conftest.py`: `sample_market_context` (MarketContextSummary), `sample_decision` (DecisionOutput), `sample_review` (ReviewVerdict), plus `reset_candle_cache_settings` and `reset_synthesizer_cache_settings` autouse fixtures.
  - `analyzer/tests/notification/conftest.py`: `sample_decision` (dict), `sample_context` (dict), `sample_review` (dict).
  - `server/tests/conftest.py`: `sample_run_summary` (RunSummary), `sample_full_result` (dict), `mock_data_dir` (tmp_path with fixture JSON), `scanner` (ResultScanner), `runner` (RunService).

### Safe Assumptions

- The server (`server/src/main.py`) is a Python FastAPI application; the Node.js Express server has been fully migrated.
- All analyzer tests run under `analyzer/` directory with `analyzer/` on `PYTHONPATH` (implied by pip install -e .).
- Server tests run under `server/` directory with `server/` on `PYTHONPATH` (implied by Dockerfile.prod ENV PYTHONPATH).
- The `_settings` module-level singleton in `candle_cache.py` is an established pattern; if refactored, tests in `analyzer/tests/conftest.py:13-25` that reset it must be updated.
- `pydantic` and `pydantic_settings` are already transitive dependencies via `analyzer/pyproject.toml` — adding them to `server/pyproject.toml` will not introduce conflicts.
- The `RunService` is instantiated once at server startup (server/src/main.py:46) and used for all POST /api/run calls.
- No changes to the analyzer's public API are required — all fixes are either server-side or localized refactors in the analyzer module.

### Unresolved External Blockers

- **Issue #2 (auth/rate limiting)**: No existing auth infrastructure in the project. Requires either a new middleware (`fastapi.Security` / API key header check) or a lightweight solution (static API key from env var). Rate limiting may need an in-memory store or a package like `slowapi`. The choice of approach is not specified by the code review.
- **Issue #5 (os.walk caching)**: `list_runs()` is called from both the API handler and `_read_results()`. Adding caching must ensure invalidation when new runs complete (POST /api/run). Cache TTL or write-triggered invalidation strategy is unspecified.
- **Issue #4 (race condition)**: The exact filesystem flush behavior of the spawned analyzer subprocess is unknown. The fix requires empirical understanding of whether the subprocess's `ResultWriter` has fully flushed to disk before the parent reads. Adding a retry loop with stat() check is safe but the optimal retry delay is unspecified.
- **Issue #9 (settings duplication)**: Extracting a shared settings mixin would require moving code between packages, which may break the `server/` → no-import-from-analyzer boundary. The review doesn't specify whether a shared package or simple import from analyzer is preferred.

### Likely Acceptance Criteria

1. `server/pyproject.toml` lists `pydantic>=2.0.0` and `pydantic-settings>=2.0.0`; Docker layer `pip install` for server succeeds without analyzer pre-installed.
2. POST /api/run requires a valid API key (via header); requests without it return 401. Rate limiting returns 429 after N requests/minute.
3. Telegram bot token is never written to logs; network error logs show sanitized URL or no URL.
4. `_read_results` retries on empty/missing files after subprocess exits; integration test verifies eventual consistency.
5. `list_runs()` with symbol filter prunes directory traversal; GET /api/runs with filter completes in <500ms for directories with 500+ result files.
6. Exception handlers in main.py log the original exception before raising RuntimeError.
7. CORS middleware restricted to methods `["GET", "POST", "OPTIONS"]` and headers `["Content-Type", "Authorization"]`.
8. `_read_results` uses a cached/lazy `ResultScanner` instance instead of creating a new one per call.
9. `WebSettings` and `Settings` share consistent `analysis_cache_dir` resolution; documented behavior for relative vs absolute paths.
10. `_normalize_cors` model_validator removed from `WebSettings` (redundant with `_CommaDelimitedEnvSource`).
11. `candle_cache._settings` singleton is either refactored (with lru_cache or explicit reload) or documented as a known limitation.
12. POST /api/run exception handling simplified to a single branch.
13. `analyzer/main.py` `main()` function split into smaller named functions (argument parsing, initialization, per-symbol loop, output).
14. Unused `request` parameter prefixed with `_` in `http_exception_handler`.
15. Top-level imports moved outside the try block in `analyzer/main.py`.
16. `sample_full_result` return type is `dict[str, Any]`.
17. `test_sellsend_message` renamed to `test_sends_sell_message`.
18. `cd analyzer && mypy src/ && ruff check src/ && pytest` passes.
19. `cd server && pytest` passes (or server test suite is created and passes).
20. `graphify update .` succeeds after all changes (AST-only, no API cost).

### Existing .opencode/plans/ Naming Pattern

**Pattern**: `{kebab-case-description}-plan.md`

All 24 plan files use lowercase kebab-case with a single `-plan` suffix before `.md`:
- `broker-time-unification-plan.md`
- `candle-aligned-cache-plan.md`
- `code-review-fixes-plan.md`
- `phase2-review-fixes-plan.md`
- `fastapi-migration-and-telegram-notifications-plan.md`

No numbering, no prefixes like `TASK-`, no date stamps. Descriptions range from 2 to 6 hyphen-separated words. The pattern is consistent: `<hyphenated-brief>-plan.md`.
