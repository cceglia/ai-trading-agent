# Graph Report - Agent  (2026-07-30)

## Corpus Check
- 122 files · ~66,666 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2010 nodes · 3807 edges · 143 communities (106 shown, 37 thin omitted)
- Extraction: 71% EXTRACTED · 29% INFERRED · 0% AMBIGUOUS · INFERRED: 1110 edges (avg confidence: 0.7)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7118c16d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- TestFatalError
- Mt5DataProvider
- DataSource
- AgentState
- SnapshotBuilder
- Evaluator
- Trading AI Agent
- TestSynthesizerPrompt
- TestCostTracking
- ForexFactoryCalendar
- orchestrator/test_synthesizer_cache.py
- Agent Instructions
- config/__init__.py
- trading-ai-agent
- src/calendar/__init__.py
- src/data/__init__.py
- src/decision/__init__.py
- src/__init__.py
- src/orchestrator/__init__.py
- tests/calendar/__init__.py
- tests/data/__init__.py
- tests/decision/__init__.py
- tests/__init__.py
- tests/orchestrator/__init__.py
- _make_mcp_tool_result
- TerminalApiError
- test_terminal_data_provider.py
- TestGetCandlesBrokerNow
- TestGetPositions
- ._run_async
- TestGetPendingOrders
- TestGetSymbolPrice
- setup_logging
- MarketContextSummary
- setup_logging
- DecisionOutput
- TestRepeatedRuns
- _select_canonical_current_price
- AgentState
- test_should_run_h1_different_period
- graph.py
- _canonical_structure_analysis
- AgentState
- TradingGraph
- test_analyze_structure_fresh_saves_mtf_cache
- TestSettingsDescriptions
- BiasLevel
- test_analyze_structure_passes_broker_time_to_snapshot_builder
- test_analyze_structure_fetches_all_timeframes
- test_analyze_structure_full_cache_hit
- main.py
- BiasLevel
- conftest.py
- .write
- main.py
- test_result_pipeline_writes_json
- TestSynthesizeContextCanonicalPrice
- TestOhlcCachePath
- test_h4_candle_period_at_boundary
- AgentState
- test_analyze_structure_uses_broker_time_not_utc
- _make_tracking_side_effect
- PriceCard.vue
- DecisionOutput
- test_cache_path_d1_uses_folder_date_not_broker_now
- .write
- test_should_run_d1_after_close_with_cache
- setup_logging
- test_should_run_h1_different_period
- TestAgentApiKey
- test_result_pipeline_writes_json
- send_trade_notification
- trading-server
- test_result_pipeline_writes_json
- test_runner.py
- test_should_run_h1_different_period
- test_load_returns_none_when_missing
- test_save_h1_creates_hour_suffixed_file
- test_save_h4_creates_hour_suffixed_file
- test_load_handles_corrupt_json
- server/tests/conftest.py
- test_cache_path_d1_no_hour_suffix
- context.py
- structure.py
- _log_llm_call
- test_should_run_h1_without_cache
- create_app
- TestListRunsPruning
- TestListRunsIntegration
- test_d1_candle_period_after_close
- Development
- test_cache_path_mtf
- Usage
- Code Review Analysis
- TestFatalError
- Docker
- TestGetRunIntegration
- Architecture
- test_cache_path_mtf_uses_d1_date
- TestParseUsageChatCompletions
- .get_run
- test_d1_candle_period_after_close
- test_h4_candle_period
- test_h4_candle_period_at_boundary
- testget_cache_date_d1_before_close
- test_h1_candle_period_at_boundary
- testget_cache_date_d1_after_close
- test_should_run_d1_without_cache
- test_should_run_d1_after_close_with_cache
- test_cache_path_h4_hour_04_is_zero_padded
- .invalidate_cache
- .test_zero_tokens_zero_cost
- .test_empty_pricing_table
- create-user.sh
- .test_multiple_calls_accumulate
- .test_missing_output_price
- .test_record_call_does_not_raise_when_equal_to_limit
- .test_record_call_does_not_raise_when_below_limit
- .test_zero_limit_disables_enforcement
- .test_negative_limit_disables_enforcement
- .test_no_limit_set_does_not_raise
- .test_set_limit_none_disables_enforcement

## God Nodes (most connected - your core abstractions)
1. `MarketContextSummary` - 89 edges
2. `CostTracker` - 87 edges
3. `AgentState` - 71 edges
4. `DecisionOutput` - 68 edges
5. `TradingGraph` - 65 edges
6. `ReviewVerdict` - 61 edges
7. `Settings` - 58 edges
8. `ResultScanner` - 56 edges
9. `SynthesizerAgent` - 53 edges
10. `LLMUsage` - 52 edges

## Surprising Connections (you probably didn't know these)
- `TestCorsOrigins` --uses--> `Settings`  [INFERRED]
  server/tests/test_settings.py → analyzer/config/settings.py
- `TestResolvedCacheDir` --uses--> `Settings`  [INFERRED]
  server/tests/test_settings.py → analyzer/config/settings.py
- `sample_market_context()` --calls--> `MarketContextSummary`  [INFERRED]
  analyzer/tests/conftest.py → analyzer/src/decision/models.py
- `sample_decision()` --calls--> `DecisionOutput`  [INFERRED]
  analyzer/tests/conftest.py → analyzer/src/decision/models.py
- `mock_decider()` --calls--> `DecisionOutput`  [INFERRED]
  analyzer/tests/orchestrator/test_synthesizer_cache.py → analyzer/src/decision/models.py

## Import Cycles
- None detected.

## Communities (143 total, 37 thin omitted)

### Community 0 - "TestFatalError"
Cohesion: 0.27
Nodes (14): get_profile(), Any, TimeframeProfile, build_levels(), _cluster_side(), Any, analyze_liquidity(), _build_equal_pools() (+6 more)

### Community 1 - "Mt5DataProvider"
Cohesion: 0.07
Nodes (52): _cache_path(), _get_cache_date(), _get_settings(), load_cached_synthesis(), Any, datetime, Path, File-based cache for SynthesizerAgent output, keyed by (symbol, day, H1-closing- (+44 more)

### Community 2 - "DataSource"
Cohesion: 0.09
Nodes (12): Tests for the new model_pricing Settings field.      These tests will fail RED (, model_pricing defaults to a non-empty dict., Default model_pricing contains 'gpt-4o' with new format keys., Invalid JSON raises a validation error., All price values in model_pricing are >= 0., Price of exactly 0.0 is accepted silently (valid configuration)., Boolean as a price value is rejected., Negative price is rejected. (+4 more)

### Community 3 - "AgentState"
Cohesion: 0.03
Nodes (82): Force a fresh Settings() on the next _get_settings() call., reload_settings(), AgentState, Any, Select the canonical current price across timeframes.      The canonical current, Build a compact version of structure analysis suitable for LLM prompts.      The, State for the trading graph., LangGraph orchestrator for trading analysis. (+74 more)

### Community 4 - "SnapshotBuilder"
Cohesion: 0.07
Nodes (19): Evaluator, Any, datetime, Check if an event falls within the time window from now.          Returns False, Evaluate events for symbol with timeframe-dependent window.          Args:, Evaluates calendar events for trading symbols., High-impact event outside the window should NOT block., High-impact event within the window SHOULD block. (+11 more)

### Community 5 - "Evaluator"
Cohesion: 0.12
Nodes (24): _cache_path(), _candle_period(), get_cache_date(), _get_settings(), datetime, Determine if analysis should run for this timeframe.      Args:         timefram, Save analysis result to disk.      Args:         timeframe: "D1", "H4", or "H1", Compute cache file path.      Args:         timeframe: "D1", "H4", or "H1" (+16 more)

### Community 6 - "Trading AI Agent"
Cohesion: 0.11
Nodes (12): emit, emit, dates, filteredRuns, router, runCountBySymbol, runNowError, runNowLoading (+4 more)

### Community 7 - "TestSynthesizerPrompt"
Cohesion: 0.08
Nodes (19): CalendarProvider, DataSource, Any, datetime, Analyze market structure from snapshots.          Args:             snapshots: D, Fetch OHLC candles as CSV string.          Args:             symbol: Trading sym, Get latest price info for a symbol.          Args:             symbol: Trading s, Get open positions.          Args:             symbol: Optional symbol filter (+11 more)

### Community 8 - "TestCostTracking"
Cohesion: 0.06
Nodes (41): _canonical_structure_analysis(), _make_cached_summary(), mock_decider(), mock_reviewer(), mock_synthesizer(), datetime, Path, RED-first tests for orchestrator-level synthesizer cache integration.  Tests ver (+33 more)

### Community 9 - "ForexFactoryCalendar"
Cohesion: 0.12
Nodes (9): Tests for CostTracker — tracks LLM API call costs.  CostTracker lives in ``src/d, CostTracker: tracks LLM API call costs., CostLimitExceeded is a subclass of Exception., After set_limit(0.05), internal _limit reflects the value., Exception string representation includes limit, total_cost, and symbol., set_symbol('XAUUSD') stores symbol internally., set_symbol('B') after set_symbol('A') overwrites symbol., total_cost=0.0, call_count=0 on fresh instance. (+1 more)

### Community 10 - "orchestrator/test_synthesizer_cache.py"
Cohesion: 0.25
Nodes (14): EngineError, ExternalDerivedValuesError, InsufficientDataError, ParentContextError, Any, Exception, Base class for deterministic engine errors., TimeframeMismatchError (+6 more)

### Community 11 - "Agent Instructions"
Cohesion: 0.11
Nodes (17): _build_parser(), main(), _parse_and_configure_settings(), Build the CLI argument parser.      Returns:         Configured ArgumentParser i, Parse CLI args into a configured Settings instance.      Applies CLI overrides (, Main entry point.      Parses CLI arguments, initialises the analysis pipeline,, LogCaptureFixture, With --telegram, notification is NOT sent when review is not approved. (+9 more)

### Community 12 - "config/__init__.py"
Cohesion: 0.05
Nodes (40): autoprefixer, axios, echarts, postcss, tailwindcss, typescript, dependencies, axios (+32 more)

### Community 13 - "trading-ai-agent"
Cohesion: 0.10
Nodes (18): MarketContextSummary, Summary of market context from synthesizer agent., _make_raw_response(), Tests for prompt usage in agents., SynthesizerAgent.synthesize must accept current_price/current_price_time kwargs., User prompt must render current_price and current_price_time values., Build a mock raw_response with a usable .usage attribute., When no price is supplied, the current-price line must state None. (+10 more)

### Community 14 - "src/calendar/__init__.py"
Cohesion: 0.31
Nodes (14): analyze_multi_timeframe(), analyze_snapshot(), _apply_structural_event_transition(), _check_same_market(), Any, Any, review_analysis(), review_multi_timeframe() (+6 more)

### Community 15 - "src/data/__init__.py"
Cohesion: 0.05
Nodes (23): Sliding-window rate limiter — in-memory, pure Python., Return ``True`` if the client may proceed, ``False`` if rate-limited., Remove all expired buckets to free memory., In-memory sliding-window rate limiter.      Tracks request timestamps per client, SlidingWindowRateLimiter, Tests for authentication and rate-limiting middleware., Integration tests: rate limiter wired into POST /api/run., After max_requests POSTs, the next one returns 429. (+15 more)

### Community 16 - "src/decision/__init__.py"
Cohesion: 0.22
Nodes (9): Analysis Layer (`analyzer/src/analysis/`), Calendar Layer (`analyzer/src/calendar/`), Components, Configuration (`analyzer/config/`), Data Layer (`analyzer/src/data/`), Decision Layer (`analyzer/src/decision/`), Orchestrator (`analyzer/src/orchestrator/`), Server (`server/`) (+1 more)

### Community 17 - "src/__init__.py"
Cohesion: 0.10
Nodes (15): extract_ohlc_from_all_timeframes(), extract_ohlc_from_csv(), OHLCBar, OHLC data extractor — parses CSV candle data into structured OHLCBar objects.  P, Parse CSV candle data into a list of OHLCBar objects.      Uses the shared :func, Extract OHLC bars for all timeframes from a mapping of CSV strings.      Args:, Tests for OHLC extractor., An empty CSV in any timeframe propagates ValueError. (+7 more)

### Community 18 - "src/orchestrator/__init__.py"
Cohesion: 0.28
Nodes (14): analyze_candles(), _classify_engulfing(), Any, adx(), calculate_indicators(), ema(), macd(), Any (+6 more)

### Community 19 - "tests/calendar/__init__.py"
Cohesion: 0.06
Nodes (23): CostLimitExceeded, CostTracker, Exception, CostTracker — tracks LLM API call costs.  Exposes a single :class:`CostTracker`, Accumulated cost across all recorded calls., Number of calls recorded., Reset accumulated cost and call count to zero., Raised when per-symbol LLM cost exceeds the configured limit. (+15 more)

### Community 20 - "tests/data/__init__.py"
Cohesion: 0.33
Nodes (3): Configure structured logging for the trading agent., setup_logging(), TestSetupLogging

### Community 21 - "tests/decision/__init__.py"
Cohesion: 0.13
Nodes (24): _create_agents(), _format_field(), _format_field_int(), _get_decision_field(), _initialize_pipeline(), _print_summary(), _print_symbol_summary(), Any (+16 more)

### Community 22 - "tests/__init__.py"
Cohesion: 0.03
Nodes (68): DeciderAgent, _log_llm_call(), Any, Makes trading decisions based on market context., Reviews trading decisions and provides feedback., Record an LLM call and log its cost. Returns enriched usage with costs., Synthesizes market context from structure analysis and calendar., ReviewerAgent (+60 more)

### Community 23 - "tests/orchestrator/__init__.py"
Cohesion: 0.22
Nodes (7): _get_settings(), ohlc_cache_path(), datetime, Compute OHLC cache file path, parallel to analysis cache.      Cache path conven, Tests for OHLC bar cache., Full path follows analysis/YYYY/MM/DD/SYMBOL/ pattern., TestOhlcCachePath

### Community 24 - "_make_mcp_tool_result"
Cohesion: 0.09
Nodes (22): DOM, DOM.Iterable, env.d.ts, ES2022, src/**/*.ts, src/**/*.vue, compilerOptions, baseUrl (+14 more)

### Community 25 - "TerminalApiError"
Cohesion: 0.10
Nodes (22): Walk the data directory tree, read/parse JSON result files,     filter/sort into, ResultScanner, Path, Helper to write a result JSON file., Files not in YYYY/MM/DD/SYMBOL/ pattern are skipped., When JSON has a 'symbol' field, it overrides the path-derived symbol., Directory pruning: when symbol is provided only matching dirs are walked., EURUSD must NOT be discovered when scanning for XAUUSD. (+14 more)

### Community 26 - "test_terminal_data_provider.py"
Cohesion: 0.20
Nodes (6): Tests for agent cost-logging helper extraction., _log_llm_call extracts duplicated cost-logging from agents., When usage is provided, logs cost details., When usage is all-zero (no usage data), logs zero cost., Records the call on the cost tracker when usage is provided., TestLogLlmCall

### Community 27 - "TestGetCandlesBrokerNow"
Cohesion: 0.05
Nodes (37): AnalysisResult, OHLCData, BaseModel, OHLC data keyed by timeframe., Entry, stop-loss and take-profit overlay for charts., Top-level pipeline output serialized to JSON for the web viewer., SLTPOverlay, Any (+29 more)

### Community 28 - "TestGetPositions"
Cohesion: 0.33
Nodes (3): Tests for the new openai_reasoning_effort Settings field.      These tests will, openai_reasoning_effort defaults to empty string (not set)., TestReasoningEffortSettings

### Community 29 - "._run_async"
Cohesion: 0.06
Nodes (32): EnvSettingsSource, _CommaDelimitedEnvSource, Any, BaseSettings, Path, Server-specific settings using Pydantic BaseSettings., Env source that parses comma-separated values for list fields.      pydantic-set, Split comma-separated env values for known list fields. (+24 more)

### Community 30 - "TestGetPendingOrders"
Cohesion: 0.10
Nodes (3): TestDeciderPrompt, TestReviewerPrompt, TestSynthesizerPrompt

### Community 31 - "TestGetSymbolPrice"
Cohesion: 0.21
Nodes (8): calculate_score(), _directional_votes(), Any, clamp(), parse_iso_timestamp(), datetime, _directional_votes applies the structural bias bonus only in RANGE., TestDirectionalVotesStructuralBias

### Community 32 - "setup_logging"
Cohesion: 0.11
Nodes (16): parse_usage(), Extract an ``LLMUsage`` from a provider response.      Handles:     * ``None`` r, Primary field names: input_tokens / output_tokens., input_tokens_details = None must not crash., output_tokens_details = None must not crash., cached_input_tokens > input_tokens → clamped to input, uncached = 0., When primary field is 0 and fallback is non-zero, primary wins., All token fields normalise negative values to 0. (+8 more)

### Community 33 - "MarketContextSummary"
Cohesion: 0.16
Nodes (10): ForexFactoryCalendar, Any, Convert raw time text to ISO timestamp (best-effort)., Map raw impact text to standard impact level., Economic calendar provider via ForexFactory scraping., Initialize calendar provider.          Args:             cache_hours: Hours to c, Fetch upcoming economic calendar events.          Returns:             List of e, Check if cache is still valid. (+2 more)

### Community 34 - "setup_logging"
Cohesion: 0.25
Nodes (5): End-to-end cost limit abort integration tests (TASK-4).      These tests exercis, 3 symbols: first two succeed, third exceeds limit → sys.exit(1).          Verifi, First symbol exceeds limit → sys.exit(1), no subsequent symbols.          Verifi, Real CostTracker wired through _run_pipeline with a very low limit.          Use, TestMainIntegrationCostLimit

### Community 35 - "DecisionOutput"
Cohesion: 0.17
Nodes (5): useRun(), FullResult, { result, loading, error }, route, router

### Community 36 - "TestRepeatedRuns"
Cohesion: 0.14
Nodes (13): Tests for engine field rename (no _utc suffix) and engine deepcopy behavior., analyze_snapshot must NOT deepcopy the input snapshot before passing to validate, _ALLOWED_BAR must accept open_time, not open_time_utc., Swing dataclass must have timestamp, not timestamp_utc., Engine source_audit must use latest_closed_candle_time, not _utc., _ALLOWED_TOP_LEVEL must accept retrieved_at, not retrieved_at_utc., Engine must export scoring.latest_close, matching technical_context.close., test_analyze_snapshot_does_not_deepcopy_input() (+5 more)

### Community 37 - "_select_canonical_current_price"
Cohesion: 0.26
Nodes (7): MarketStructureEngine, Any, Concrete adapter implementing StructureAnalyzer.      Wraps the module-level ana, Analyze market structure from snapshots.          Args:             snapshots: D, Build engine request from snapshots., Delegate analysis to the engine., Validate engine output.

### Community 38 - "AgentState"
Cohesion: 0.15
Nodes (9): CaptureFixture, Tests for multi-symbol support in main.py., When one symbol fails, main() continues with remaining symbols., Result file is always written to settings.analysis_cache_dir., When result has no broker_now, main() uses datetime.now() instead., Test that main() loops over all symbols correctly., Verify main() calls graph.run() for each symbol., TestMainMultiSymbolExecution (+1 more)

### Community 39 - "test_should_run_h1_different_period"
Cohesion: 0.14
Nodes (8): Test that argparse accepts multiple symbols via _build_parser., _build_parser accepts multiple symbols as nargs+., _build_parser is backward-compatible with single symbol., --model option is accepted., --base-url option is accepted., --log-level option defaults to INFO., Calling without any symbols should raise a SystemExit., TestArgparseMultiSymbol

### Community 40 - "graph.py"
Cohesion: 0.17
Nodes (11): vite.config.ts, compilerOptions, allowImportingTsExtensions, composite, module, moduleResolution, skipLibCheck, strict (+3 more)

### Community 41 - "_canonical_structure_analysis"
Cohesion: 0.33
Nodes (6): RED-first tests for the canonical current-price selection helper (TASK-6).  Thes, Lazy-import the not-yet-existing helper so collection succeeds.      Raises ``Im, Build a single per-timeframe engine-output dict for the selector., _select_canonical_current_price(), TestSelectCanonicalCurrentPrice, _tf()

### Community 42 - "AgentState"
Cohesion: 0.18
Nodes (8): CaptureFixture, Tests for main.py entry point — Issue #13 error duplication., Duplicate error-printing blocks in main.py (Issue #13).      The first block (li, main.py should not log 'Total LLM cost' — graph.run() already does., Verify errors are printed exactly once, not twice.          mocks:         - Set, main.py must not log 'Total LLM cost' — that's graph.run()'s job., TestMainCostLogging, TestMainErrorDuplication

### Community 44 - "test_analyze_structure_fresh_saves_mtf_cache"
Cohesion: 0.12
Nodes (10): integration_client(), integration_data(), Path, Integration tests with real file I/O., Create a temporary data directory with fixture JSON files., Create app pointing at the mock data directory., Integration tests for GET /api/runs with real file I/O., Integration tests for GET /api/runs/{symbol}/{year}/{month}/{day}/{file}. (+2 more)

### Community 45 - "TestSettingsDescriptions"
Cohesion: 0.22
Nodes (9): chartOption, props, Decision, MarketContext, OHLCBar, OHLCData, Review, RunRequest (+1 more)

### Community 46 - "BiasLevel"
Cohesion: 0.08
Nodes (26): BiasLevel, DecisionAction, DecisionOutput, BaseModel, Structural bias levels., Decision output from decider agent., Review verdict from reviewer agent., ReviewVerdict (+18 more)

### Community 47 - "test_analyze_structure_passes_broker_time_to_snapshot_builder"
Cohesion: 0.20
Nodes (8): Agent Instructions, Architectural notes, Architecture, Critical invariants, Graphify first, Pre-commit hooks, Testing, Toolchain

### Community 48 - "test_analyze_structure_fetches_all_timeframes"
Cohesion: 0.51
Nodes (8): _assign_status(), _candidate_indexes(), detect_swings(), _group_local_plateaus(), _prominence(), Any, _representative(), Swing

### Community 49 - "test_analyze_structure_full_cache_hit"
Cohesion: 0.22
Nodes (6): biasArrow, biasColor, emit, props, useRuns(), RunSummary

### Community 50 - "main.py"
Cohesion: 0.12
Nodes (5): Route-level tests with mocked scanner/runner., Tests for GET /api/runs/{symbol}/{year}/{month}/{day}/{file}., Tests for GET /api/runs., TestGetRun, TestListRuns

### Community 54 - "main.py"
Cohesion: 0.08
Nodes (18): Retry reading result files with backoff.          After a subprocess completes t, Return the subset of *symbols* that have no run in the scanner., Walk the data directory via ResultScanner and return the         most recent res, Spawn Python subprocess to run analysis, enforce timeout,     capture stderr, an, Run analysis for the given symbols.          Spawns: python main.py [--model <m>, Spawn the Python process and wait for completion.          On timeout the proces, RunService, Verify --model flag is absent when model is None. (+10 more)

### Community 55 - "test_result_pipeline_writes_json"
Cohesion: 0.25
Nodes (6): BaseHTTPMiddleware, Request, RequestResponseEndpoint, Response, AuthMiddleware, Validates the ``X-API-Key`` header against a configured API key.      When ``api

### Community 56 - "TestSynthesizeContextCanonicalPrice"
Cohesion: 0.16
Nodes (9): MonkeyPatch, Settings().terminal_server_url returns the default MCP URL., Settings().terminal_api_key returns empty string by default., TRADING_TERMINAL_API_KEY env var overrides the default., TRADING_TERMINAL_SERVER_URL env var overrides the default., TRADING_MODEL_PRICING JSON env var overrides the default (new format)., TRADING_OPENAI_REASONING_EFFORT env var overrides the default., Tests for the new terminal_server_url and terminal_api_key Settings fields. (+1 more)

### Community 57 - "TestOhlcCachePath"
Cohesion: 0.17
Nodes (3): Tests for POST /api/run., Symbols must be 1-20 alphanumeric characters., TestPostRun

### Community 58 - "test_h4_candle_period_at_boundary"
Cohesion: 0.14
Nodes (7): Unknown model logs warning, preserves token fields, cost fields zero., Missing input_per_million → input_cost = 0.0., record_call raises CostLimitExceeded when total_cost > limit., Build an LLMUsage with computed uncached and total., Cached input tokens are priced at cached_input_per_million., record_call returns the per-call cost in LLMUsage.total_cost., record_call accumulates total_cost across calls.

### Community 59 - "AgentState"
Cohesion: 0.23
Nodes (7): CORS header verification tests., Issue an OPTIONS preflight request with standard CORS headers., OPTIONS preflight must return restricted allow-methods., OPTIONS preflight must return restricted allow-headers.          The middleware, OPTIONS preflight from a configured origin should echo it back., OPTIONS preflight must include allow-credentials: true., TestCORS

### Community 60 - "test_analyze_structure_uses_broker_time_not_utc"
Cohesion: 0.20
Nodes (9): _dict_to_sns(), Reset the _settings sentinel in candle_cache before each test.      Tests use mo, Recursively convert a dict to a SimpleNamespace., Reset the _settings sentinel in synthesizer_cache before each test.      Mirrors, reset_candle_cache_settings(), reset_synthesizer_cache_settings(), sample_decision(), sample_market_context() (+1 more)

### Community 76 - "DecisionOutput"
Cohesion: 0.57
Nodes (6): _canonicalize(), _event_type(), Any, _quality(), scan_events(), _scope()

### Community 80 - "test_cache_path_d1_uses_folder_date_not_broker_now"
Cohesion: 0.25
Nodes (8): BaseModel, Server-specific Pydantic models., Request body for POST /api/run., Summary of a single analysis run, matching Node.js RunSummary shape., RunRequest, RunSummary, Sample RunSummary for route tests., sample_summary()

### Community 81 - ".write"
Cohesion: 0.20
Nodes (12): Analyze market structure with candle-aligned caching.          The multi-timefra, load_ohlc_cache(), OHLCBar, Save OHLC bars to cache, same directory structure as analysis cache.      Args:, Load cached OHLC bars from disk if available.      Args:         timeframe: "D1", save_ohlc_cache(), OHLCBar, Single OHLC bar for chart rendering. (+4 more)

### Community 82 - "test_should_run_d1_after_close_with_cache"
Cohesion: 0.33
Nodes (6): Development environment (Docker), Quick commands (run inside container), Running from Docker (host → container), Setup, Starting the container, Stopping

### Community 84 - "setup_logging"
Cohesion: 0.17
Nodes (10): FastAPI, create_app(), FastAPI application entry point — port of the TypeScript Express server., Create and configure the FastAPI application., Authentication middleware — validates X-API-Key header., RunService — port of the TypeScript runner service.  Spawns the Python analyzer, client(), Create a test client with mocked scanner and runner (no API key). (+2 more)

### Community 85 - "test_should_run_h1_different_period"
Cohesion: 0.67
Nodes (5): build_confluence(), build_timeframe_context(), _direction_from_bias(), Any, _require_parent()

### Community 88 - "send_trade_notification"
Cohesion: 0.11
Nodes (11): Any, Telegram notification sender — best-effort, never blocks the pipeline., Replace the bot token in a Telegram API URL with ``***``., Send a compact trade notification to Telegram.      Best-effort: logs warning on, _sanitize_url(), send_trade_notification(), Tests for telegram_sender module., Return *True* when the token (``test-token``) does **not**         appear in *pa (+3 more)

### Community 91 - "test_result_pipeline_writes_json"
Cohesion: 0.17
Nodes (7): Cost limit enforcement in the pipeline (TASK-3).      These tests verify that:, Verify sys.exit(1) when CostLimitExceeded is raised mid-run.          RED: curre, Verify cost_tracker.reset() is called before each symbol.          RED: ``_run_p, Verify set_limit() is called with settings.cost_per_symbol_limit.          RED:, Verify CostLimitExceeded propagates out of _run_single_symbol.          RED: ``_, cost_per_symbol_limit=0 disables enforcement — all symbols process.          RED, TestMainCostLimit

### Community 93 - "test_should_run_h1_different_period"
Cohesion: 0.17
Nodes (7): Tests for the new synthesizer_cache_enabled Settings field.      RED phase: thes, synthesizer_cache_enabled defaults to True when no env var is set., TRADING_SYNTHESIZER_CACHE_ENABLED=true yields True., TRADING_SYNTHESIZER_CACHE_ENABLED=false yields False., TRADING_SYNTHESIZER_CACHE_ENABLED=0 yields False (bool coercion)., Invalid TRADING_SYNTHESIZER_CACHE_ENABLED value either raises or falls back to d, TestSynthesizerCacheEnabled

### Community 94 - "test_load_returns_none_when_missing"
Cohesion: 0.10
Nodes (15): _make_run_summary(), _mock_process(), Unit tests for RunService., Create a RunService with test defaults., Tests for RunService._wait_for_results()., Create a mock asyncio subprocess., RunService with minimal retry delays for fast tests., Scanner returns empty on first N-1 calls, then succeeds. (+7 more)

### Community 95 - "test_save_h1_creates_hour_suffixed_file"
Cohesion: 0.22
Nodes (9): Environment Configuration, Installation, License, Native Setup, Overview, Prerequisites, Project Structure, Services (+1 more)

### Community 96 - "test_save_h4_creates_hour_suffixed_file"
Cohesion: 0.20
Nodes (6): LLMUsage, Immutable record of token usage for a single LLM API call.      Token fields are, Tests for usage.py — LLMUsage, safe_non_negative_int, and parse_usage.  No exter, TestLLMUsageDefaults, TestParseUsageDict, TestParseUsageNoneOrMissing

### Community 97 - "test_load_handles_corrupt_json"
Cohesion: 0.29
Nodes (7): Configuration, Cost Analysis, Cost Estimate (GPT-4o), Default Model Pricing, Environment Variables — Analyzer, Environment Variables — Server, Token Estimates (GPT-4o)

### Community 98 - "server/tests/conftest.py"
Cohesion: 0.11
Nodes (16): client_with_auth(), mock_data_dir(), Any, Path, RunSummary, Shared fixtures for server tests., Create a temporary data directory with fixture JSON files., Create a ResultScanner pointing at the mock data directory. (+8 more)

### Community 99 - "test_cache_path_d1_no_hour_suffix"
Cohesion: 0.24
Nodes (4): Return a non-negative ``int`` or ``0`` for invalid/missing values.      Handles, safe_non_negative_int(), LogCaptureFixture, TestSafeNonNegativeInt

### Community 100 - "context.py"
Cohesion: 0.22
Nodes (6): Path, RunSummary, Full directory walk (fallback when no symbol is specified)., Walk only directories that match *symbol_upper*.          Directory layout:  dat, Parse a result JSON file into a RunSummary.          Path convention: data/YYYY/, List all runs, optionally filtered by symbol and date range.          Returns so

### Community 101 - "structure.py"
Cohesion: 0.08
Nodes (29): _alternating_major(), _can_classify_sequence(), classify_structure(), _coarse_fallback(), _compute_structural_bias(), Any, Map local structure + broader bias into a human-readable context label.      Ret, Require a complete 3-high/3-low window for previous-regime analysis.      ``_seq (+21 more)

### Community 102 - "_log_llm_call"
Cohesion: 0.18
Nodes (9): BaseSettings, Trading agent configuration., Resolve ``analysis_cache_dir`` to an absolute path.          Both the analyzer a, Parse JSON string env var and validate prices.          Accepts only the new for, Settings, test_settings_has_analysis_cache_dir(), test_settings_has_d1_close_time(), test_settings_has_h4_close_interval_hours() (+1 more)

### Community 103 - "test_should_run_h1_without_cache"
Cohesion: 0.31
Nodes (10): _extract_int(), _extract_total_tokens(), _field_exists(), _get_field(), Any, LLM usage tracking — parse provider responses and extract token counts.  This mo, Return ``True`` if the nested attribute/dict path exists.      Works with object, Return the value at a nested attribute/dict path, or ``None``. (+2 more)

### Community 105 - "create_app"
Cohesion: 0.22
Nodes (4): ResultScanner — port of the TypeScript scanner service., Unit tests for ResultScanner., Tests for ResultScanner.get_run()., TestGetRun

### Community 109 - "Development"
Cohesion: 0.33
Nodes (6): Commands, Contributing, Dependencies, Development, Knowledge Graph, Pre-commit Hooks

### Community 111 - "test_cache_path_mtf"
Cohesion: 0.18
Nodes (8): Compute the project root from the test file location.          Mirror the same t, Default ``analysis_cache_dir="data"`` resolves to ``<project_root>/data``., A relative path resolves against the project root, not CWD., An absolute path is returned as-is., Setting ``TRADING_ANALYSIS_CACHE_DIR`` to an absolute value must         be retu, Analyzer and server must resolve the same default to the same path., Tests for the ``resolved_analysis_cache_dir`` property.      Both the analyzer a, TestResolvedAnalysisCacheDir

### Community 112 - "Usage"
Cohesion: 0.40
Nodes (5): Analyzer CLI, API Server, Programmatic Usage, UI Dashboard, Usage

### Community 113 - "Code Review Analysis"
Cohesion: 0.40
Nodes (5): Architecture Diagram, External Dependencies and I/O Boundaries, Project Facts and Conventions, Test Coverage — Analyzer, Testing

### Community 115 - "Docker"
Cohesion: 0.25
Nodes (8): Development, Docker, First-time setup, Images, Migration from root-based setup, Prerequisites, Production, Running commands

### Community 117 - "Architecture"
Cohesion: 0.50
Nodes (4): Analysis Pipeline (LangGraph State Machine), Architecture, Design Principles, Service Architecture

### Community 123 - "test_h4_candle_period"
Cohesion: 0.12
Nodes (17): load_cached_analysis(), Any, Load cached analysis from disk if available.      Args:         timeframe: "D1",, D1 save then load returns identical dict (round-trip fidelity)., H4 save then load returns identical dict., H1 save then load returns identical dict., Load returns None when no cache file exists., Load returns None for corrupt JSON (does not raise). (+9 more)

### Community 125 - "testget_cache_date_d1_before_close"
Cohesion: 0.05
Nodes (40): At exact H4 boundary, the period starts at that boundary., At exact H1 boundary, period starts at that time., H1 period crossing midnight boundary works correctly., D1 file path uses folder_date from get_cache_date, not raw broker_now., After D1 close, cache date is today's date (from period_start)., H4 cache date includes the closing hour in cache_date.hour., H4 should skip analysis when cache file exists for that period., D1 before close should always run analysis (candle not closed). (+32 more)

## Knowledge Gaps
- **137 isolated node(s):** `trading-ai-agent`, `create-user.sh script`, `trading-server`, `*.vue`, `name` (+132 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **37 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `_log_llm_call` to `Mt5DataProvider`, `DataSource`, `AgentState`, `Evaluator`, `Agent Instructions`, `test_cache_path_mtf`, `._run_async`, `tests/decision/__init__.py`, `tests/orchestrator/__init__.py`, `TestSynthesizeContextCanonicalPrice`, `TestGetCandlesBrokerNow`, `TestGetPositions`, `test_should_run_h1_different_period`?**
  _High betweenness centrality (0.278) - this node is a cross-community bridge._
- **Why does `create_app()` connect `setup_logging` to `test_analyze_structure_fresh_saves_mtf_cache`, `src/data/__init__.py`, `main.py`, `test_result_pipeline_writes_json`, `TerminalApiError`, `._run_async`?**
  _High betweenness centrality (0.166) - this node is a cross-community bridge._
- **Why does `WebSettings` connect `._run_async` to `setup_logging`?**
  _High betweenness centrality (0.162) - this node is a cross-community bridge._
- **Are the 78 inferred relationships involving `MarketContextSummary` (e.g. with `DeciderAgent` and `ReviewerAgent`) actually correct?**
  _`MarketContextSummary` has 78 INFERRED edges - model-reasoned connections that need verification._
- **Are the 68 inferred relationships involving `CostTracker` (e.g. with `DeciderAgent` and `ReviewerAgent`) actually correct?**
  _`CostTracker` has 68 INFERRED edges - model-reasoned connections that need verification._
- **Are the 59 inferred relationships involving `AgentState` (e.g. with `Settings` and `CostLimitExceeded`) actually correct?**
  _`AgentState` has 59 INFERRED edges - model-reasoned connections that need verification._
- **Are the 62 inferred relationships involving `DecisionOutput` (e.g. with `DeciderAgent` and `ReviewerAgent`) actually correct?**
  _`DecisionOutput` has 62 INFERRED edges - model-reasoned connections that need verification._
