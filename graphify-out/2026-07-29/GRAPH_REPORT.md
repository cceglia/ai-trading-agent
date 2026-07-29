# Graph Report - Agent  (2026-07-29)

## Corpus Check
- 119 files · ~60,833 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1834 nodes · 3386 edges · 138 communities (107 shown, 31 thin omitted)
- Extraction: 72% EXTRACTED · 28% INFERRED · 0% AMBIGUOUS · INFERRED: 940 edges (avg confidence: 0.69)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9f0db53d`
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
- TestProjectFiles
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
- test_h1_candle_period
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
- TestPostRun
- context.py
- structure.py
- _log_llm_call
- test_d1_candle_period_before_close
- create_app
- .test_read_results_retries_on_empty_read
- TestListRunsIntegration
- test_d1_candle_period_after_close
- Development
- _build_parser
- Usage
- Code Review Analysis
- TestFatalError
- Docker
- test_d1_candle_period_after_close
- Architecture
- Installation
- test_h4_candle_period
- test_h4_candle_period_at_boundary
- test_h1_candle_period
- test_h1_candle_period_at_boundary
- test_h1_candle_period_midnight
- testget_cache_date_d1_before_close
- test_save_h1_creates_hour_suffixed_file
- testget_cache_date_h4_returns_closing_hour
- test_should_run_d1_after_close_with_cache
- test_cache_path_d1_no_hour_suffix
- test_should_run_h4_without_cache
- test_should_run_d1_cache_in_wrong_folder
- test_should_run_h1_with_cache
- test_cache_path_h4_includes_closing_hour
- test_cache_path_mtf
- test_cache_path_mtf_uses_d1_date
- test_d1_candle_period_before_close
- create-user.sh

## God Nodes (most connected - your core abstractions)
1. `MarketContextSummary` - 86 edges
2. `CostTracker` - 82 edges
3. `AgentState` - 71 edges
4. `DecisionOutput` - 68 edges
5. `TradingGraph` - 65 edges
6. `ReviewVerdict` - 61 edges
7. `ResultScanner` - 56 edges
8. `SynthesizerAgent` - 49 edges
9. `Settings` - 44 edges
10. `CostLimitExceeded` - 38 edges

## Surprising Connections (you probably didn't know these)
- `sample_market_context()` --calls--> `MarketContextSummary`  [INFERRED]
  analyzer/tests/conftest.py → analyzer/src/decision/models.py
- `sample_decision()` --calls--> `DecisionOutput`  [INFERRED]
  analyzer/tests/conftest.py → analyzer/src/decision/models.py
- `mock_decider()` --calls--> `DecisionOutput`  [INFERRED]
  analyzer/tests/orchestrator/test_synthesizer_cache.py → analyzer/src/decision/models.py
- `sample_review()` --calls--> `ReviewVerdict`  [INFERRED]
  analyzer/tests/conftest.py → analyzer/src/decision/models.py
- `mock_reviewer()` --calls--> `ReviewVerdict`  [INFERRED]
  analyzer/tests/orchestrator/test_synthesizer_cache.py → analyzer/src/decision/models.py

## Import Cycles
- None detected.

## Communities (138 total, 31 thin omitted)

### Community 0 - "TestFatalError"
Cohesion: 0.27
Nodes (14): get_profile(), Any, TimeframeProfile, build_levels(), _cluster_side(), Any, analyze_liquidity(), _build_equal_pools() (+6 more)

### Community 1 - "Mt5DataProvider"
Cohesion: 0.07
Nodes (52): _cache_path(), _get_cache_date(), _get_settings(), load_cached_synthesis(), Any, datetime, Path, File-based cache for SynthesizerAgent output, keyed by (symbol, day, H1-closing- (+44 more)

### Community 2 - "DataSource"
Cohesion: 0.06
Nodes (35): BaseSettings, Trading agent configuration., Parse JSON string env var and validate all prices are non-negative., Settings, test_settings_has_analysis_cache_dir(), test_settings_has_d1_close_time(), test_settings_has_h4_close_interval_hours(), test_settings_has_h4_close_time() (+27 more)

### Community 3 - "AgentState"
Cohesion: 0.05
Nodes (49): Force a fresh Settings() on the next _get_settings() call., reload_settings(), LangGraph orchestrator for trading analysis., TradingGraph, H1 analysis must now be saved to cache like D1/H4., If get_broker_time() fails, _analyze_structure should set fatal_error., get_candles must be called with broker_time param., snapshot_builder.build must be called with broker_time. (+41 more)

### Community 4 - "SnapshotBuilder"
Cohesion: 0.07
Nodes (19): Evaluator, Any, datetime, Check if an event falls within the time window from now.          Returns False, Evaluate events for symbol with timeframe-dependent window.          Args:, Evaluates calendar events for trading symbols., High-impact event outside the window should NOT block., High-impact event within the window SHOULD block. (+11 more)

### Community 5 - "Evaluator"
Cohesion: 0.09
Nodes (26): load_cached_analysis(), Any, Save analysis result to disk.      Args:         timeframe: "D1", "H4", or "H1", Load cached analysis from disk if available.      Args:         timeframe: "D1",, save_analysis(), Analyze market structure with candle-aligned caching.          The multi-timefra, D1 save then load returns identical dict (round-trip fidelity)., H4 save then load returns identical dict. (+18 more)

### Community 6 - "Trading AI Agent"
Cohesion: 0.11
Nodes (12): emit, emit, dates, filteredRuns, router, runCountBySymbol, runNowError, runNowLoading (+4 more)

### Community 7 - "TestSynthesizerPrompt"
Cohesion: 0.08
Nodes (19): CalendarProvider, DataSource, Any, datetime, Analyze market structure from snapshots.          Args:             snapshots: D, Fetch OHLC candles as CSV string.          Args:             symbol: Trading sym, Get latest price info for a symbol.          Args:             symbol: Trading s, Get open positions.          Args:             symbol: Optional symbol filter (+11 more)

### Community 8 - "TestCostTracking"
Cohesion: 0.07
Nodes (30): _canonical_structure_analysis(), _make_cached_summary(), datetime, Path, Model changed across runs → cache hit (model version not in cache key)., Cache hit → cost_tracker.call_count == 0 (no LLM call recorded)., Cache miss → cost_tracker.call_count == 1 (one LLM call recorded)., 5 sequential runs on same symbol/day → exactly 1 LLM call.          First run: c (+22 more)

### Community 9 - "ForexFactoryCalendar"
Cohesion: 0.04
Nodes (34): CostTracker, Accumulated cost across all recorded calls., Number of calls recorded., Reset accumulated cost and call count to zero., Tracks LLM API call costs using per-model token pricing.      Each instance is i, Set a per-symbol cost limit.          When *limit* is ``<= 0`` the limit check i, Set the current symbol for error context.          The symbol is used by :meth:`, Tests for CostTracker — tracks LLM API call costs.  CostTracker lives in ``src/d (+26 more)

### Community 10 - "TestProjectFiles"
Cohesion: 0.25
Nodes (3): Tests for OHLC bar cache., Full path follows analysis/YYYY/MM/DD/SYMBOL/ pattern., TestOhlcCachePath

### Community 11 - "Agent Instructions"
Cohesion: 0.07
Nodes (26): _build_parser(), main(), _parse_and_configure_settings(), Build the CLI argument parser.      Returns:         Configured ArgumentParser i, Parse CLI args into a configured Settings instance.      Applies CLI overrides (, Main entry point.      Parses CLI arguments, initialises the analysis pipeline,, CaptureFixture, Tests for multi-symbol support in main.py. (+18 more)

### Community 12 - "config/__init__.py"
Cohesion: 0.05
Nodes (36): autoprefixer, axios, echarts, postcss, tailwindcss, typescript, dependencies, axios (+28 more)

### Community 13 - "trading-ai-agent"
Cohesion: 0.10
Nodes (18): MarketContextSummary, Summary of market context from synthesizer agent., _make_raw_response(), Tests for prompt usage in agents., SynthesizerAgent.synthesize must accept current_price/current_price_time kwargs., User prompt must render current_price and current_price_time values., Build a mock raw_response with a usable .usage attribute., When no price is supplied, the current-price line must state None. (+10 more)

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
Cohesion: 0.19
Nodes (12): OHLCBar, OHLCData, BaseModel, Single OHLC bar for chart rendering., OHLC data keyed by timeframe., Entry, stop-loss and take-profit overlay for charts., SLTPOverlay, Tests for output result models. (+4 more)

### Community 19 - "tests/calendar/__init__.py"
Cohesion: 0.07
Nodes (21): CostLimitExceeded, Exception, CostTracker — tracks LLM API call costs.  Exposes a single :class:`CostTracker`, Raised when per-symbol LLM cost exceeds the configured limit., Record an LLM API call and return its cost.          Parameters         --------, CostLimitExceeded is a subclass of Exception., Exception string representation includes limit, total_cost, and symbol., Tests for ``except CostLimitExceeded: raise`` in every graph node.      Without (+13 more)

### Community 20 - "tests/data/__init__.py"
Cohesion: 0.33
Nodes (3): Configure structured logging for the trading agent., setup_logging(), TestSetupLogging

### Community 21 - "tests/decision/__init__.py"
Cohesion: 0.13
Nodes (24): _create_agents(), _format_field(), _format_field_int(), _get_decision_field(), _initialize_pipeline(), _print_summary(), _print_symbol_summary(), Any (+16 more)

### Community 22 - "tests/__init__.py"
Cohesion: 0.09
Nodes (19): Synthesizes market context from structure analysis and calendar., SynthesizerAgent, Tests for API key and base_url passthrough in agents., When a pre-built client is provided, base_url must be ignored., SynthesizerAgent must pass both api_key and base_url when provided., Empty string → None conversion in main.py (same pattern as api_key/base_url)., Agent must accept None reasoning_effort without error., Agent must accept empty string reasoning_effort (though main.py converts it). (+11 more)

### Community 23 - "tests/orchestrator/__init__.py"
Cohesion: 0.12
Nodes (13): Per-call cost logging for synthesizer, decider, and reviewer agents.      These, Build a mock raw_response with a usable .usage attribute., Build a mock raw_response with usage set to None., SynthesizerAgent must log prompt_tokens, completion_tokens and total_tokens., SynthesizerAgent must log cost=$ with a numeric value., DeciderAgent must log token usage after decide()., ReviewerAgent must log token usage after review()., Agents must call create_with_completion, not create. (+5 more)

### Community 24 - "_make_mcp_tool_result"
Cohesion: 0.09
Nodes (22): DOM, DOM.Iterable, env.d.ts, ES2022, src/**/*.ts, src/**/*.vue, compilerOptions, baseUrl (+14 more)

### Community 25 - "TerminalApiError"
Cohesion: 0.12
Nodes (19): Walk the data directory tree, read/parse JSON result files,     filter/sort into, ResultScanner, Path, Helper to write a result JSON file., Files not in YYYY/MM/DD/SYMBOL/ pattern are skipped., When JSON has a 'symbol' field, it overrides the path-derived symbol., Tests for ResultScanner.get_run()., Tests for ResultScanner.list_runs(). (+11 more)

### Community 26 - "test_terminal_data_provider.py"
Cohesion: 0.08
Nodes (24): D1 file path uses folder_date from get_cache_date, not raw broker_now., D1 before close should always run analysis (candle not closed)., D1 after close without cache should run analysis., H1 should run analysis when no H1 cache file exists., H1 should run when cache exists for a different period., H1 filename includes the closing hour (e.g. h1-14-analysis.json)., _get_settings must return the same Settings instance on every call., After clearing _settings sentinel, _get_settings must reflect env var changes. (+16 more)

### Community 27 - "TestGetCandlesBrokerNow"
Cohesion: 0.18
Nodes (10): Writes analysis results to JSON files in the data/ directory tree., ResultWriter, Path, Tests for ResultWriter., When there are errors but no fatal_error, status should be 'partial'., OHLC bars appear in the output JSON under 'ohlc'., SL/TP overlay is populated from decision when available., SL/TP overlay fields are None when there is no decision. (+2 more)

### Community 28 - "TestGetPositions"
Cohesion: 0.08
Nodes (22): AgentState, Any, Select the canonical current price across timeframes.      The canonical current, Build a compact version of structure analysis suitable for LLM prompts.      The, State for the trading graph., Initialize trading graph with dependencies.          Args:             data_prov, Build the LangGraph StateGraph., Fetch market data from MT5. (+14 more)

### Community 29 - "._run_async"
Cohesion: 0.06
Nodes (30): EnvSettingsSource, _CommaDelimitedEnvSource, Any, BaseSettings, Path, Server-specific settings using Pydantic BaseSettings., Env source that parses comma-separated values for list fields.      pydantic-set, Split comma-separated env values for known list fields. (+22 more)

### Community 30 - "TestGetPendingOrders"
Cohesion: 0.10
Nodes (3): TestDeciderPrompt, TestReviewerPrompt, TestSynthesizerPrompt

### Community 31 - "TestGetSymbolPrice"
Cohesion: 0.28
Nodes (14): analyze_candles(), _classify_engulfing(), Any, adx(), calculate_indicators(), ema(), macd(), Any (+6 more)

### Community 32 - "setup_logging"
Cohesion: 0.08
Nodes (17): DeciderAgent, Makes trading decisions based on market context., Reviews trading decisions and provides feedback., ReviewerAgent, SynthesizerAgent must accept reasoning_effort param., When not specified, reasoning_effort defaults to None., DeciderAgent must accept reasoning_effort param., ReviewerAgent must accept reasoning_effort param. (+9 more)

### Community 33 - "MarketContextSummary"
Cohesion: 0.16
Nodes (10): ForexFactoryCalendar, Any, Convert raw time text to ISO timestamp (best-effort)., Map raw impact text to standard impact level., Economic calendar provider via ForexFactory scraping., Initialize calendar provider.          Args:             cache_hours: Hours to c, Fetch upcoming economic calendar events.          Returns:             List of e, Check if cache is still valid. (+2 more)

### Community 34 - "setup_logging"
Cohesion: 0.20
Nodes (6): Tests for agent cost-logging helper extraction., _log_llm_call extracts duplicated cost-logging from agents., When usage is provided, logs cost details., When usage is None, logs N/A., Records the call on the cost tracker when usage is provided., TestLogLlmCall

### Community 35 - "DecisionOutput"
Cohesion: 0.17
Nodes (5): useRun(), FullResult, { result, loading, error }, route, router

### Community 36 - "TestRepeatedRuns"
Cohesion: 0.37
Nodes (12): analyze_multi_timeframe(), analyze_snapshot(), _apply_structural_event_transition(), _check_same_market(), Any, Any, review_analysis(), review_multi_timeframe() (+4 more)

### Community 37 - "_select_canonical_current_price"
Cohesion: 0.26
Nodes (7): MarketStructureEngine, Any, Concrete adapter implementing StructureAnalyzer.      Wraps the module-level ana, Analyze market structure from snapshots.          Args:             snapshots: D, Build engine request from snapshots., Delegate analysis to the engine., Validate engine output.

### Community 38 - "AgentState"
Cohesion: 0.14
Nodes (13): Tests for engine field rename (no _utc suffix) and engine deepcopy behavior., analyze_snapshot must NOT deepcopy the input snapshot before passing to validate, _ALLOWED_BAR must accept open_time, not open_time_utc., Swing dataclass must have timestamp, not timestamp_utc., Engine source_audit must use latest_closed_candle_time, not _utc., _ALLOWED_TOP_LEVEL must accept retrieved_at, not retrieved_at_utc., Engine must export scoring.latest_close, matching technical_context.close., test_analyze_snapshot_does_not_deepcopy_input() (+5 more)

### Community 39 - "test_should_run_h1_different_period"
Cohesion: 0.11
Nodes (10): Test that argparse accepts multiple symbols via _build_parser., _build_parser accepts multiple symbols as nargs+., _build_parser is backward-compatible with single symbol., --output-dir option is accepted., --output-dir defaults to None., --model option is accepted., --base-url option is accepted., --log-level option defaults to INFO. (+2 more)

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
Cohesion: 0.18
Nodes (8): integration_client(), integration_data(), Path, Integration tests with real file I/O., Create a temporary data directory with fixture JSON files., Create app pointing at the mock data directory., Integration tests for GET /api/runs with real file I/O., TestListRunsIntegration

### Community 45 - "TestSettingsDescriptions"
Cohesion: 0.22
Nodes (9): chartOption, props, Decision, MarketContext, OHLCBar, OHLCData, Review, RunRequest (+1 more)

### Community 46 - "BiasLevel"
Cohesion: 0.08
Nodes (25): BiasLevel, DecisionAction, Structural bias levels., TestMaxReviewAttempts, TestTradingGraphInit, mock_decider(), mock_reviewer(), mock_synthesizer() (+17 more)

### Community 47 - "test_analyze_structure_passes_broker_time_to_snapshot_builder"
Cohesion: 0.15
Nodes (12): Agent Instructions, Architectural notes, Architecture, Critical invariants, Development environment (Docker), Graphify first, Pre-commit hooks, Quick commands (run inside container) (+4 more)

### Community 48 - "test_analyze_structure_fetches_all_timeframes"
Cohesion: 0.53
Nodes (3): _log_llm_call(), Any, Record an LLM call and log its cost. Returns cost or None if no usage.

### Community 49 - "test_analyze_structure_full_cache_hit"
Cohesion: 0.22
Nodes (6): biasArrow, biasColor, emit, props, useRuns(), RunSummary

### Community 50 - "main.py"
Cohesion: 0.23
Nodes (7): CORS header verification tests., Issue an OPTIONS preflight request with standard CORS headers., OPTIONS preflight must return restricted allow-methods., OPTIONS preflight must return restricted allow-headers.          The middleware, OPTIONS preflight from a configured origin should echo it back., OPTIONS preflight must include allow-credentials: true., TestCORS

### Community 54 - "main.py"
Cohesion: 0.08
Nodes (18): Retry reading result files with backoff.          After a subprocess completes t, Return the subset of *symbols* that have no run in the scanner., Walk the data directory via ResultScanner and return the         most recent res, Spawn Python subprocess to run analysis, enforce timeout,     capture stderr, an, Run analysis for the given symbols.          Spawns: python main.py --output-dir, Spawn the Python process and wait for completion.          On timeout the proces, RunService, Verify --model flag is absent when model is None. (+10 more)

### Community 55 - "test_result_pipeline_writes_json"
Cohesion: 0.17
Nodes (3): Tests for POST /api/run., Symbols must be 1-20 alphanumeric characters., TestPostRun

### Community 56 - "TestSynthesizeContextCanonicalPrice"
Cohesion: 0.17
Nodes (7): reasoning_effort is a create()-level kwarg, not an OpenAI() constructor arg., When reasoning_effort is set, it must appear in client.create() kwargs., When reasoning_effort is None, the key must be absent from create() kwargs., When reasoning_effort is explicitly None, key absent from create() kwargs., DeciderAgent passes reasoning_effort to create()., ReviewerAgent passes reasoning_effort to create()., TestReasoningEffortPassthrough

### Community 57 - "TestOhlcCachePath"
Cohesion: 0.10
Nodes (15): _make_run_summary(), _mock_process(), Unit tests for RunService., Create a RunService with test defaults., Create a mock asyncio subprocess., Tests for RunService._wait_for_results()., RunService with minimal retry delays for fast tests., Scanner returns empty on first N-1 calls, then succeeds. (+7 more)

### Community 58 - "test_h4_candle_period_at_boundary"
Cohesion: 0.29
Nodes (6): _make_tracking_side_effect(), Create a side effect that records an LLM call on the shared CostTracker.      Th, Tests for CostTracker wiring in TradingGraph.run().      These tests verify that, Run TradingGraph with mocked agents that have a shared CostTracker,         asse, Verify that a CostTracker instance can be shared across all 3 agents         and, TestCostTrackerWiring

### Community 59 - "AgentState"
Cohesion: 0.22
Nodes (6): Path, RunSummary, Full directory walk (fallback when no symbol is specified)., Walk only directories that match *symbol_upper*.          Directory layout:  dat, Parse a result JSON file into a RunSummary.          Path convention: data/YYYY/, List all runs, optionally filtered by symbol and date range.          Returns so

### Community 60 - "test_analyze_structure_uses_broker_time_not_utc"
Cohesion: 0.25
Nodes (7): Reset the _settings sentinel in candle_cache before each test.      Tests use mo, Reset the _settings sentinel in synthesizer_cache before each test.      Mirrors, reset_candle_cache_settings(), reset_synthesizer_cache_settings(), sample_decision(), sample_market_context(), sample_review()

### Community 76 - "DecisionOutput"
Cohesion: 0.51
Nodes (8): _assign_status(), _candidate_indexes(), detect_swings(), _group_local_plateaus(), _prominence(), Any, _representative(), Swing

### Community 81 - ".write"
Cohesion: 0.19
Nodes (13): _get_settings(), load_ohlc_cache(), ohlc_cache_path(), datetime, OHLCBar, Compute OHLC cache file path, parallel to analysis cache.      Cache path conven, Save OHLC bars to cache, same directory structure as analysis cache.      Args:, Load cached OHLC bars from disk if available.      Args:         timeframe: "D1" (+5 more)

### Community 82 - "test_should_run_d1_after_close_with_cache"
Cohesion: 0.17
Nodes (7): End-to-end: reasoning_effort flows from constructor → create() kwargs., synthesize() must include reasoning_effort in create_with_completion kwargs when, Must NOT include reasoning_effort in create_with_completion kwargs when None., decide() must include reasoning_effort in create_with_completion() kwargs when s, review() must include reasoning_effort in create_with_completion() kwargs when s, Pre-built client: reasoning_effort still flows to create_with_completion()., TestReasoningEffortIntegration

### Community 84 - "setup_logging"
Cohesion: 0.22
Nodes (5): Directory pruning: when symbol is provided only matching dirs are walked., EURUSD must NOT be discovered when scanning for XAUUSD., The pruned path does *not* call os.walk., Date ranges narrow the walked directories., TestListRunsPruning

### Community 85 - "test_h1_candle_period"
Cohesion: 0.12
Nodes (10): DecisionOutput, BaseModel, Decision output from decider agent., Review verdict from reviewer agent., ReviewVerdict, TestDecisionOutput, TestReviewVerdict, mock_decider() (+2 more)

### Community 87 - "test_result_pipeline_writes_json"
Cohesion: 0.36
Nodes (6): calculate_score(), _directional_votes(), Any, clamp(), parse_iso_timestamp(), datetime

### Community 88 - "send_trade_notification"
Cohesion: 0.11
Nodes (11): Any, Telegram notification sender — best-effort, never blocks the pipeline., Replace the bot token in a Telegram API URL with ``***``., Send a compact trade notification to Telegram.      Best-effort: logs warning on, _sanitize_url(), send_trade_notification(), Tests for telegram_sender module., Return *True* when the token (``test-token``) does **not**         appear in *pa (+3 more)

### Community 91 - "test_result_pipeline_writes_json"
Cohesion: 0.17
Nodes (7): Cost limit enforcement in the pipeline (TASK-3).      These tests verify that:, Verify sys.exit(1) when CostLimitExceeded is raised mid-run.          RED: curre, Verify cost_tracker.reset() is called before each symbol.          RED: ``_run_p, Verify set_limit() is called with settings.cost_per_symbol_limit.          RED:, Verify CostLimitExceeded propagates out of _run_single_symbol.          RED: ``_, cost_per_symbol_limit=0 disables enforcement — all symbols process.          RED, TestMainCostLimit

### Community 92 - "test_runner.py"
Cohesion: 0.33
Nodes (3): RunService — port of the TypeScript runner service.  Spawns the Python analyzer, ResultScanner — port of the TypeScript scanner service., Unit tests for ResultScanner.

### Community 93 - "test_should_run_h1_different_period"
Cohesion: 0.22
Nodes (14): _cache_path(), _candle_period(), get_cache_date(), _get_settings(), datetime, Determine if analysis should run for this timeframe.      Args:         timefram, Compute cache file path.      Args:         timeframe: "D1", "H4", or "H1", Compute the start and end of a candle period.      Args:         timeframe: "D1" (+6 more)

### Community 94 - "test_load_returns_none_when_missing"
Cohesion: 0.25
Nodes (8): BaseModel, Server-specific Pydantic models., Request body for POST /api/run., Summary of a single analysis run, matching Node.js RunSummary shape., RunRequest, RunSummary, Sample RunSummary for route tests., sample_summary()

### Community 95 - "test_save_h1_creates_hour_suffixed_file"
Cohesion: 0.25
Nodes (7): License, Overview, Project Structure, Services, Test Coverage — Analyzer, Testing, Trading AI Agent

### Community 96 - "test_save_h4_creates_hour_suffixed_file"
Cohesion: 0.57
Nodes (6): _canonicalize(), _event_type(), Any, _quality(), scan_events(), _scope()

### Community 97 - "test_load_handles_corrupt_json"
Cohesion: 0.29
Nodes (7): Configuration, Cost Analysis, Cost Estimate (GPT-4o), Default Model Pricing, Environment Variables — Analyzer, Environment Variables — Server, Token Estimates (GPT-4o)

### Community 98 - "server/tests/conftest.py"
Cohesion: 0.10
Nodes (18): client(), client_with_auth(), mock_data_dir(), Any, Path, RunSummary, Shared fixtures for server tests., Create a temporary data directory with fixture JSON files. (+10 more)

### Community 99 - "TestPostRun"
Cohesion: 0.15
Nodes (5): client(), Route-level tests with mocked scanner/runner., Create a test client with mocked scanner and runner., Tests for GET /api/runs., TestListRuns

### Community 100 - "context.py"
Cohesion: 0.67
Nodes (5): build_confluence(), build_timeframe_context(), _direction_from_bias(), Any, _require_parent()

### Community 101 - "structure.py"
Cohesion: 0.80
Nodes (5): _alternating_major(), classify_structure(), _coarse_fallback(), Any, _sequence_classification()

### Community 102 - "_log_llm_call"
Cohesion: 0.23
Nodes (5): AnalysisResult, Top-level pipeline output serialized to JSON for the web viewer., Critical invariant: entry_authorized must always be False., Full-featured AnalysisResult with all optional fields set., TestAnalysisResult

### Community 105 - "create_app"
Cohesion: 0.15
Nodes (11): BaseHTTPMiddleware, FastAPI, Request, RequestResponseEndpoint, Response, create_app(), FastAPI application entry point — port of the TypeScript Express server., Create and configure the FastAPI application. (+3 more)

### Community 106 - ".test_read_results_retries_on_empty_read"
Cohesion: 0.24
Nodes (6): Any, datetime, OHLCBar, Path, Write result JSON to disk. Returns the file path written.          Args:, Compute data/YYYY/MM/DD/SYMBOL/result-HH-MM.json path.

### Community 107 - "TestListRunsIntegration"
Cohesion: 0.25
Nodes (14): EngineError, ExternalDerivedValuesError, InsufficientDataError, ParentContextError, Any, Exception, Base class for deterministic engine errors., TimeframeMismatchError (+6 more)

### Community 109 - "Development"
Cohesion: 0.33
Nodes (6): Commands, Contributing, Dependencies, Development, Knowledge Graph, Pre-commit Hooks

### Community 112 - "Usage"
Cohesion: 0.40
Nodes (5): Analyzer CLI, API Server, Programmatic Usage, UI Dashboard, Usage

### Community 113 - "Code Review Analysis"
Cohesion: 0.40
Nodes (5): Architecture Diagram, Code Review Analysis, External Dependencies and I/O Boundaries, Issues Summary, Project Facts and Conventions

### Community 114 - "TestFatalError"
Cohesion: 0.33
Nodes (5): _canonical_structure_analysis(), Build a structure_analysis fixture whose H1 timeframe has the     most-recent cl, _synthesize_context must compute the canonical current price from         the pe, Even when the LLM-returned summary has current_price=None, the         orchestra, TestSynthesizeContextCanonicalPrice

### Community 115 - "Docker"
Cohesion: 0.40
Nodes (5): Development, Docker, Images, Prerequisites, Production

### Community 116 - "test_d1_candle_period_after_close"
Cohesion: 0.28
Nodes (8): Path, End-to-end integration test for the result JSON pipeline., Pipeline with fatal error produces valid error result., Result with no OHLC data produces empty arrays., Full pipeline simulation writes valid JSON result., test_empty_ohlc_defaults(), test_result_pipeline_writes_json(), test_result_with_fatal_error()

### Community 117 - "Architecture"
Cohesion: 0.50
Nodes (4): Analysis Pipeline (LangGraph State Machine), Architecture, Design Principles, Service Architecture

### Community 118 - "Installation"
Cohesion: 0.50
Nodes (4): Environment Configuration, Installation, Native Setup, Prerequisites

## Knowledge Gaps
- **131 isolated node(s):** `trading-ai-agent`, `create-user.sh script`, `trading-server`, `*.vue`, `name` (+126 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **31 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `CostTracker` connect `ForexFactoryCalendar` to `setup_logging`, `setup_logging`, `test_should_run_h1_different_period`, `TestCostTracking`, `Agent Instructions`, `BiasLevel`, `test_analyze_structure_fetches_all_timeframes`, `test_should_run_d1_after_close_with_cache`, `tests/calendar/__init__.py`, `TestFatalError`, `tests/decision/__init__.py`, `tests/__init__.py`, `tests/orchestrator/__init__.py`, `TestSynthesizeContextCanonicalPrice`, `test_h1_candle_period`, `test_h4_candle_period_at_boundary`, `test_result_pipeline_writes_json`, `TestGetPositions`?**
  _High betweenness centrality (0.089) - this node is a cross-community bridge._
- **Why does `Settings` connect `DataSource` to `Mt5DataProvider`, `AgentState`, `.test_read_results_retries_on_empty_read`, `Agent Instructions`, `.write`, `tests/decision/__init__.py`, `TestGetCandlesBrokerNow`, `TestGetPositions`, `test_should_run_h1_different_period`?**
  _High betweenness centrality (0.088) - this node is a cross-community bridge._
- **Why does `TradingGraph` connect `AgentState` to `DataSource`, `Evaluator`, `TestCostTracking`, `trading-ai-agent`, `BiasLevel`, `src/orchestrator/__init__.py`, `tests/calendar/__init__.py`, `TestFatalError`, `test_h1_candle_period`, `tests/decision/__init__.py`, `test_h4_candle_period_at_boundary`, `TestGetPositions`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **Are the 75 inferred relationships involving `MarketContextSummary` (e.g. with `DeciderAgent` and `ReviewerAgent`) actually correct?**
  _`MarketContextSummary` has 75 INFERRED edges - model-reasoned connections that need verification._
- **Are the 63 inferred relationships involving `CostTracker` (e.g. with `DeciderAgent` and `ReviewerAgent`) actually correct?**
  _`CostTracker` has 63 INFERRED edges - model-reasoned connections that need verification._
- **Are the 59 inferred relationships involving `AgentState` (e.g. with `Settings` and `CostLimitExceeded`) actually correct?**
  _`AgentState` has 59 INFERRED edges - model-reasoned connections that need verification._
- **Are the 62 inferred relationships involving `DecisionOutput` (e.g. with `DeciderAgent` and `ReviewerAgent`) actually correct?**
  _`DecisionOutput` has 62 INFERRED edges - model-reasoned connections that need verification._
