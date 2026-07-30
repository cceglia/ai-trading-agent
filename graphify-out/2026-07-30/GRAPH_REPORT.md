# Graph Report - Agent  (2026-07-30)

## Corpus Check
- 136 files · ~78,451 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2273 nodes · 4276 edges · 141 communities (124 shown, 17 thin omitted)
- Extraction: 75% EXTRACTED · 25% INFERRED · 0% AMBIGUOUS · INFERRED: 1087 edges (avg confidence: 0.7)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6f123d5a`
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
- test_should_run_d1_after_close_without_cache
- usage.py
- test_should_run_d1_after_close_with_cache
- TestCostTrackerWiring
- .invalidate_cache
- reload_settings
- .test_empty_pricing_table
- create-user.sh
- .test_cache_disabled_by_env
- test_h1_candle_period
- .test_pipeline_resets_cost_tracker_per_symbol
- derive_allowed_actions
- ExecutionStatus
- adapters/__init__.py

## God Nodes (most connected - your core abstractions)
1. `AgentState` - 88 edges
2. `LLMUsage` - 84 edges
3. `TradingGraph` - 82 edges
4. `CostTracker` - 81 edges
5. `Settings` - 62 edges
6. `ResultScanner` - 56 edges
7. `MarketContextSummary` - 50 edges
8. `CostLimitExceeded` - 39 edges
9. `DecisionOutput` - 36 edges
10. `ReviewVerdict` - 35 edges

## Surprising Connections (you probably didn't know these)
- `TestCorsOrigins` --uses--> `Settings`  [INFERRED]
  server/tests/test_settings.py → analyzer/config/settings.py
- `TestResolvedCacheDir` --uses--> `Settings`  [INFERRED]
  server/tests/test_settings.py → analyzer/config/settings.py
- `test_settings_has_h4_close_interval_hours()` --calls--> `Settings`  [INFERRED]
  analyzer/tests/analysis/test_candle_cache.py → analyzer/config/settings.py
- `sample_market_context()` --calls--> `MarketContextSummary`  [INFERRED]
  analyzer/tests/conftest.py → analyzer/src/decision/models.py
- `sample_decision()` --calls--> `DecisionOutput`  [INFERRED]
  analyzer/tests/conftest.py → analyzer/src/decision/models.py

## Import Cycles
- None detected.

## Communities (141 total, 17 thin omitted)

### Community 0 - "TestFatalError"
Cohesion: 0.27
Nodes (14): get_profile(), Any, TimeframeProfile, build_levels(), _cluster_side(), Any, analyze_liquidity(), _build_equal_pools() (+6 more)

### Community 1 - "Mt5DataProvider"
Cohesion: 0.07
Nodes (52): _cache_path(), _get_cache_date(), _get_settings(), load_cached_synthesis(), Any, datetime, Path, File-based cache for SynthesizerAgent output, keyed by (symbol, day, H1-closing- (+44 more)

### Community 2 - "DataSource"
Cohesion: 0.07
Nodes (23): BaseSettings, Self, Parse JSON string env var and validate prices.          Accepts only the new for, Resolve ``analysis_cache_dir`` to an absolute path.          Both the analyzer a, Trading agent configuration., Validate execution policy settings based on execution mode.          Paper and L, Settings, test_settings_has_analysis_cache_dir() (+15 more)

### Community 3 - "AgentState"
Cohesion: 0.05
Nodes (50): Force a fresh Settings() on the next _get_settings() call., reload_settings(), AgentState, State for the trading graph.      Fields are grouped by their provenance within, _canonical_structure_analysis(), Fresh-fetch path must also save the MTF cache file., H1 analysis must now be saved to cache like D1/H4., If get_broker_time() fails, _analyze_structure should set fatal_error. (+42 more)

### Community 4 - "SnapshotBuilder"
Cohesion: 0.07
Nodes (19): Evaluator, Any, datetime, Check if an event falls within the time window from now.          Returns False, Evaluate events for symbol with timeframe-dependent window.          Args:, Evaluates calendar events for trading symbols., High-impact event outside the window should NOT block., High-impact event within the window SHOULD block. (+11 more)

### Community 5 - "Evaluator"
Cohesion: 0.09
Nodes (36): _cache_path(), _candle_period(), get_cache_date(), _get_settings(), load_cached_analysis(), Any, datetime, Determine if analysis should run for this timeframe.      Args:         timefram (+28 more)

### Community 6 - "Trading AI Agent"
Cohesion: 0.07
Nodes (20): allDates, dateSourceRuns, days, filteredRuns, months, router, runCountBySymbol, runNowError (+12 more)

### Community 7 - "TestSynthesizerPrompt"
Cohesion: 0.08
Nodes (19): CalendarProvider, DataSource, Any, datetime, Protocol, Analyze market structure from snapshots.          Args:             snapshots: D, Fetch OHLC candles as CSV string.          Args:             symbol: Trading sym, Get latest price info for a symbol.          Args:             symbol: Trading s (+11 more)

### Community 8 - "TestCostTracking"
Cohesion: 0.06
Nodes (41): _canonical_structure_analysis(), _directional_structure_analysis(), _make_cached_summary(), mock_reviewer(), datetime, Path, RED-first tests for orchestrator-level synthesizer cache integration.  Tests ver, Different H1 hour on same day → cache miss (different closing hours).          C (+33 more)

### Community 9 - "ForexFactoryCalendar"
Cohesion: 0.04
Nodes (33): Tests for CostTracker — tracks LLM API call costs.  CostTracker lives in ``src/d, Unknown model logs warning, preserves token fields, cost fields zero., Missing cached_input_per_million → cached_input_cost = 0.0., Missing input_per_million → input_cost = 0.0., CostTracker: tracks LLM API call costs., Zero tokens result in zero cost but call IS counted., CostTracker(pricing={}) — record_call warns and returns zero costs., Many calls accumulate total_cost correctly. (+25 more)

### Community 10 - "orchestrator/test_synthesizer_cache.py"
Cohesion: 0.25
Nodes (14): EngineError, ExternalDerivedValuesError, InsufficientDataError, ParentContextError, Any, Exception, Base class for deterministic engine errors., TimeframeMismatchError (+6 more)

### Community 11 - "Agent Instructions"
Cohesion: 0.09
Nodes (19): _build_parser(), main(), _parse_and_configure_settings(), Build the CLI argument parser.      Returns:         Configured ArgumentParser i, Parse CLI args into a configured Settings instance.      Applies CLI overrides (, Main entry point.      Parses CLI arguments, initialises the analysis pipeline,, LogCaptureFixture, With --telegram, notification is NOT sent when review is not approved. (+11 more)

### Community 12 - "config/__init__.py"
Cohesion: 0.05
Nodes (40): autoprefixer, axios, echarts, postcss, tailwindcss, typescript, dependencies, axios (+32 more)

### Community 13 - "trading-ai-agent"
Cohesion: 0.11
Nodes (18): Record an LLM API call and return its usage with cost filled in.          Parame, LLMUsage, Immutable record of token usage for a single LLM API call.      Token fields are, _make_mock_client(), Tests for prompt usage in agents., SynthesizerAgent.synthesize must accept current_price/current_price_time kwargs., User prompt must render current_price and current_price_time values., When no price is supplied, the current-price line must state None. (+10 more)

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
Cohesion: 0.14
Nodes (12): CostLimitExceeded, Exception, Raised when per-symbol LLM cost exceeds the configured limit., Tests for ``except CostLimitExceeded: raise`` in every graph node.      Without, When ``SynthesizerAgent.synthesize`` raises ``CostLimitExceeded``,         it mu, When ``DeciderAgent.decide`` raises ``CostLimitExceeded``,         it must propa, When ``ReviewerAgent.review`` raises ``CostLimitExceeded``,         it must prop, When ``DataSource.get_positions`` raises ``CostLimitExceeded``,         it must (+4 more)

### Community 20 - "tests/data/__init__.py"
Cohesion: 0.33
Nodes (3): Configure structured logging for the trading agent., setup_logging(), TestSetupLogging

### Community 21 - "tests/decision/__init__.py"
Cohesion: 0.14
Nodes (22): _format_field(), _format_field_int(), _get_decision_field(), _initialize_pipeline(), _print_summary(), _print_symbol_summary(), Any, Trading AI Agent - CLI Entry Point. (+14 more)

### Community 22 - "tests/__init__.py"
Cohesion: 0.10
Nodes (14): _log_llm_call(), Any, Record an LLM call and log its cost. Returns enriched usage with costs., MarketContextSummary, Summary of market context from synthesizer agent., Tests for agent cost-logging helper extraction., _log_llm_call extracts duplicated cost-logging from agents., When usage is provided, logs cost details. (+6 more)

### Community 23 - "tests/orchestrator/__init__.py"
Cohesion: 0.12
Nodes (16): _build_blockers(), evaluate_execution_policy(), Evaluate execution policy and return an :class:`ExecutionPolicyState`.      Cons, Evaluate all blocker conditions and return the active blockers.      This is an, ExecutionBlocker, Self, An execution blocker that prevents or delays trade execution.      Attributes:, Immutable state for risk management policy evaluation.      Attributes: (+8 more)

### Community 24 - "_make_mcp_tool_result"
Cohesion: 0.09
Nodes (22): DOM, DOM.Iterable, env.d.ts, ES2022, src/**/*.ts, src/**/*.vue, compilerOptions, baseUrl (+14 more)

### Community 25 - "TerminalApiError"
Cohesion: 0.10
Nodes (22): Walk the data directory tree, read/parse JSON result files,     filter/sort into, ResultScanner, Path, Helper to write a result JSON file., Files not in YYYY/MM/DD/SYMBOL/ pattern are skipped., When JSON has a 'symbol' field, it overrides the path-derived symbol., Directory pruning: when symbol is provided only matching dirs are walked., EURUSD must NOT be discovered when scanning for XAUUSD. (+14 more)

### Community 26 - "test_terminal_data_provider.py"
Cohesion: 0.22
Nodes (7): _get_settings(), ohlc_cache_path(), datetime, Compute OHLC cache file path, parallel to analysis cache.      Cache path conven, Tests for OHLC bar cache., Full path follows analysis/YYYY/MM/DD/SYMBOL/ pattern., TestOhlcCachePath

### Community 27 - "TestGetCandlesBrokerNow"
Cohesion: 0.17
Nodes (11): Writes analysis results to JSON files in the data/ directory tree., ResultWriter, Path, Tests for ResultWriter., When there are errors but no fatal_error, status should be 'partial'., OHLC bars appear in the output JSON under 'ohlc'., SL/TP overlay fields are None when there is no decision., SL/TP overlay fields are None when DecisionOutput has no price fields. (+3 more)

### Community 28 - "TestGetPositions"
Cohesion: 0.07
Nodes (21): BiasLevel, DecisionAction, Decision action taken by the decision agent., Structural bias levels., Status of the review process., ReviewStatus, BaseModel, Whether the review outcome is approved. (+13 more)

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
Cohesion: 0.17
Nodes (3): Tests for POST /api/run., Symbols must be 1-20 alphanumeric characters., TestPostRun

### Community 33 - "MarketContextSummary"
Cohesion: 0.16
Nodes (10): ForexFactoryCalendar, Any, Convert raw time text to ISO timestamp (best-effort)., Map raw impact text to standard impact level., Economic calendar provider via ForexFactory scraping., Initialize calendar provider.          Args:             cache_hours: Hours to c, Fetch upcoming economic calendar events.          Returns:             List of e, Check if cache is still valid. (+2 more)

### Community 34 - "setup_logging"
Cohesion: 0.19
Nodes (16): calculate_entry_plan(), calculate_risk_reward(), _determine_entry_type(), _extract_entry_prices(), Any, Entry plan calculation for the multi-timeframe pipeline.  This module implements, Extract and normalize entry price data from setup context.      Args:         se, Determine the entry type based on price relationship.      Args:         entry_p (+8 more)

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
Nodes (8): CaptureFixture, Tests for main.py entry point — Issue #13 error duplication., Duplicate error-printing blocks in main.py (Issue #13).      The first block (li, main.py must not log 'Total LLM cost' — that's graph.run()'s job., main.py should not log 'Total LLM cost' — graph.run() already does., Verify errors are printed exactly once, not twice.          mocks:         - Set, TestMainCostLogging, TestMainErrorDuplication

### Community 44 - "test_analyze_structure_fresh_saves_mtf_cache"
Cohesion: 0.12
Nodes (10): integration_client(), integration_data(), Path, Integration tests with real file I/O., Create a temporary data directory with fixture JSON files., Create app pointing at the mock data directory., Integration tests for GET /api/runs with real file I/O., Integration tests for GET /api/runs/{symbol}/{year}/{month}/{day}/{file}. (+2 more)

### Community 45 - "TestSettingsDescriptions"
Cohesion: 0.22
Nodes (9): chartOption, props, Decision, MarketContext, OHLCBar, OHLCData, Review, RunRequest (+1 more)

### Community 46 - "BiasLevel"
Cohesion: 0.16
Nodes (22): Type of price action trigger for a setup., Status of the trigger confirmation process., TriggerStatus, TriggerType, _check_path_a_confirmed_retest(), _check_path_b_continuation_bos(), _check_path_c_sweep_and_reclaim(), classify_trigger() (+14 more)

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
Cohesion: 0.12
Nodes (27): PolicySettings, Deterministic execution policy evaluation for the multi-timeframe pipeline.  Thi, Configuration for execution policy evaluation.      Attributes:         countert, BlockerSeverity, EnforcementViolationCode, ExecutionBlockerCode, ExecutionBlockerType, ExecutionMode (+19 more)

### Community 56 - "TestSynthesizeContextCanonicalPrice"
Cohesion: 0.09
Nodes (18): MonkeyPatch, Settings().terminal_server_url returns the default MCP URL., Settings().terminal_api_key returns empty string by default., TRADING_TERMINAL_API_KEY env var overrides the default., TRADING_TERMINAL_SERVER_URL env var overrides the default., Tests for the new synthesizer_cache_enabled Settings field.      RED phase: thes, synthesizer_cache_enabled defaults to True when no env var is set., TRADING_SYNTHESIZER_CACHE_ENABLED=true yields True. (+10 more)

### Community 57 - "TestOhlcCachePath"
Cohesion: 0.23
Nodes (7): CORS header verification tests., Issue an OPTIONS preflight request with standard CORS headers., OPTIONS preflight must return restricted allow-methods., OPTIONS preflight must return restricted allow-headers.          The middleware, OPTIONS preflight from a configured origin should echo it back., OPTIONS preflight must include allow-credentials: true., TestCORS

### Community 58 - "test_h4_candle_period_at_boundary"
Cohesion: 0.33
Nodes (4): When ``state.fatal_error`` is set, ``_synthesize_context`` short-circuits., fatal_error set \u2192 returns {} without checking cache or calling LLM., fatal_error set \u2192 cache is NOT written even if synthesizer runs.          N, TestFatalError

### Community 59 - "AgentState"
Cohesion: 0.06
Nodes (30): _has_high_impact_calendar_event(), Any, Route after the review node.          - ``"continue_enforcement"`` when review i, Run the deterministic enforcement gate.          The gate verifies that every ex, Run the trading graph for a symbol.          Args:             symbol: Trading s, Select the canonical current price across timeframes.      The canonical current, Build a compact version of structure analysis suitable for LLM prompts.      The, Check if any calendar event has a high impact level. (+22 more)

### Community 60 - "test_analyze_structure_uses_broker_time_not_utc"
Cohesion: 0.20
Nodes (9): _dict_to_sns(), Reset the _settings sentinel in candle_cache before each test.      Tests use mo, Recursively convert a dict to a SimpleNamespace., Reset the _settings sentinel in synthesizer_cache before each test.      Mirrors, reset_candle_cache_settings(), reset_synthesizer_cache_settings(), sample_decision(), sample_market_context() (+1 more)

### Community 76 - "DecisionOutput"
Cohesion: 0.57
Nodes (6): _canonicalize(), _event_type(), Any, _quality(), scan_events(), _scope()

### Community 80 - "test_cache_path_d1_uses_folder_date_not_broker_now"
Cohesion: 0.11
Nodes (27): DeterministicSetupState, EnforcementViolation, ExecutionPolicyState, FinalDecisionState, BaseModel, An enforcement violation detected during setup validation.      Attributes:, Immutable state representing a classified trading setup.      Captures the full, Whether this setup qualifies as a candidate for decision.          A setup is a (+19 more)

### Community 81 - ".write"
Cohesion: 0.24
Nodes (9): load_ohlc_cache(), OHLCBar, Save OHLC bars to cache, same directory structure as analysis cache.      Args:, Load cached OHLC bars from disk if available.      Args:         timeframe: "D1", save_ohlc_cache(), Path, Saved JSON file contains exactly the expected data., Saving an empty bar list should produce an empty JSON array. (+1 more)

### Community 82 - "test_should_run_d1_after_close_with_cache"
Cohesion: 0.33
Nodes (6): Development environment (Docker), Quick commands (run inside container), Running from Docker (host → container), Setup, Starting the container, Stopping

### Community 84 - "setup_logging"
Cohesion: 0.19
Nodes (12): OHLCBar, OHLCData, BaseModel, Single OHLC bar for chart rendering., OHLC data keyed by timeframe., Entry, stop-loss and take-profit overlay for charts., SLTPOverlay, Tests for output result models. (+4 more)

### Community 85 - "test_should_run_h1_different_period"
Cohesion: 0.67
Nodes (5): build_confluence(), build_timeframe_context(), _direction_from_bias(), Any, _require_parent()

### Community 86 - "TestAgentApiKey"
Cohesion: 0.10
Nodes (15): _make_run_summary(), _mock_process(), Unit tests for RunService., Create a RunService with test defaults., Tests for RunService._wait_for_results()., Create a mock asyncio subprocess., RunService with minimal retry delays for fast tests., Scanner returns empty on first N-1 calls, then succeeds. (+7 more)

### Community 87 - "test_result_pipeline_writes_json"
Cohesion: 0.15
Nodes (14): AnthropicModelIdentityResolver, GenericAliasModelIdentityResolver, OpenAIModelIdentityResolver, ProviderKind, StrEnum, LLM model configuration and provider-aware identity resolution.  This module def, Resolver for OpenAI model identifiers.      Recognises patterns like ``gpt-4o-20, Resolver for Anthropic model identifiers.      Recognises patterns like ``claude (+6 more)

### Community 88 - "send_trade_notification"
Cohesion: 0.11
Nodes (11): Any, Telegram notification sender — best-effort, never blocks the pipeline., Replace the bot token in a Telegram API URL with ``***``., Send a compact trade notification to Telegram.      Best-effort: logs warning on, _sanitize_url(), send_trade_notification(), Tests for telegram_sender module., Return *True* when the token (``test-token``) does **not**         appear in *pa (+3 more)

### Community 91 - "test_result_pipeline_writes_json"
Cohesion: 0.12
Nodes (11): input_tokens_details = None must not crash., output_tokens_details = None must not crash., When primary field is 0 and fallback is non-zero, primary wins., All token fields normalise negative values to 0., Booleans in usage fields are normalised to 0., Provider returned total_tokens=0 → keep 0, do not derive., No total_tokens field → derive as input + output., total_tokens = None → derive as input + output. (+3 more)

### Community 92 - "test_runner.py"
Cohesion: 0.17
Nodes (10): FastAPI, create_app(), FastAPI application entry point — port of the TypeScript Express server., Create and configure the FastAPI application., Authentication middleware — validates X-API-Key header., RunService — port of the TypeScript runner service.  Spawns the Python analyzer, client(), Create a test client with mocked scanner and runner (no API key). (+2 more)

### Community 93 - "test_should_run_h1_different_period"
Cohesion: 0.28
Nodes (8): Path, End-to-end integration test for the result JSON pipeline., Pipeline with fatal error produces valid error result., Result with no OHLC data produces empty arrays., Full pipeline simulation writes valid JSON result., test_empty_ohlc_defaults(), test_result_pipeline_writes_json(), test_result_with_fatal_error()

### Community 94 - "test_load_returns_none_when_missing"
Cohesion: 0.22
Nodes (4): ResultScanner — port of the TypeScript scanner service., Unit tests for ResultScanner., Tests for ResultScanner.get_run()., TestGetRun

### Community 95 - "test_save_h1_creates_hour_suffixed_file"
Cohesion: 0.22
Nodes (9): Environment Configuration, Installation, License, Native Setup, Overview, Prerequisites, Project Structure, Services (+1 more)

### Community 96 - "test_save_h4_creates_hour_suffixed_file"
Cohesion: 0.13
Nodes (12): parse_usage(), Extract an ``LLMUsage`` from a provider response.      Handles:     * ``None`` r, make_raw_response(), Build a mock provider response with controlled usage fields.      The returned o, Tests for usage.py — LLMUsage, safe_non_negative_int, and parse_usage.  No exter, Primary field names: input_tokens / output_tokens., cached_input_tokens > input_tokens → clamped to input, uncached = 0., Fallback field names: prompt_tokens / completion_tokens. (+4 more)

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
Cohesion: 0.25
Nodes (8): BaseModel, Server-specific Pydantic models., Request body for POST /api/run., Summary of a single analysis run, matching Node.js RunSummary shape., RunRequest, RunSummary, Sample RunSummary for route tests., sample_summary()

### Community 103 - "test_should_run_h1_without_cache"
Cohesion: 0.27
Nodes (4): AnalysisResult, Top-level pipeline output serialized to JSON for the web viewer.      Fields are, Full-featured AnalysisResult with all optional fields set., TestAnalysisResult

### Community 105 - "create_app"
Cohesion: 0.25
Nodes (6): BaseHTTPMiddleware, Request, RequestResponseEndpoint, Response, AuthMiddleware, Validates the ``X-API-Key`` header against a configured API key.      When ``api

### Community 106 - "TestListRunsPruning"
Cohesion: 0.24
Nodes (6): Any, datetime, OHLCBar, Path, Write result JSON to disk. Returns the file path written.          Args:, Compute data/YYYY/MM/DD/SYMBOL/result-HH.json path.

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

### Community 114 - "TestFatalError"
Cohesion: 0.09
Nodes (19): Any, T, The underlying sync instructor-patched OpenAI client., Send messages to the LLM and return a structured Pydantic model.          Runs t, Synchronous variant of :meth:`generate_structured`.          Returns ``(response, LLMClientError, LLMCommunicationClient, Any (+11 more)

### Community 115 - "Docker"
Cohesion: 0.25
Nodes (8): Development, Docker, First-time setup, Images, Migration from root-based setup, Prerequisites, Production, Running commands

### Community 116 - "TestGetRunIntegration"
Cohesion: 0.33
Nodes (5): emit, localDay, localMonth, localYear, props

### Community 117 - "Architecture"
Cohesion: 0.50
Nodes (4): Analysis Pipeline (LangGraph State Machine), Architecture, Design Principles, Service Architecture

### Community 118 - "test_cache_path_mtf_uses_d1_date"
Cohesion: 0.13
Nodes (14): _directional_structure_analysis(), _make_tracking_side_effect(), With max_review_attempts=2, decider.decide must be called exactly 3 times     (1, With max_review_attempts=2, feedback must be forwarded to decider.decide     on, The first call to decider.decide must have feedback=None.      This may already, Create a side effect that records an LLM call on the shared CostTracker.      Th, Tests for CostTracker wiring in TradingGraph.run().      These tests verify that, Run TradingGraph with mocked agents that have a shared CostTracker,         asse (+6 more)

### Community 119 - "TestParseUsageChatCompletions"
Cohesion: 0.17
Nodes (8): OpenAIProviderAdapter, OpenAI provider adapter — instructor-based structured output.  Wraps the ``instr, The provider this adapter handles., The raw model identifier., Optional reasoning effort level., OpenAI provider adapter using ``instructor`` for structured output.      Conform, LLMModelConfig, Immutable configuration for an LLM endpoint.      Attributes:         model: Mod

### Community 124 - "test_h4_candle_period_at_boundary"
Cohesion: 0.18
Nodes (7): LLMProviderAdapter, Protocol, Abstract protocol for LLM provider adapters.      An adapter encapsulates the pr, The provider this adapter handles., Resolved identity for the configured model., The raw model identifier., Optional reasoning effort level.

### Community 125 - "testget_cache_date_d1_before_close"
Cohesion: 0.03
Nodes (59): At exact H4 boundary, the period starts at that boundary., H1 period is floored to the current hour., At exact H1 boundary, period starts at that time., H1 period crossing midnight boundary works correctly., D1 file path uses folder_date from get_cache_date, not raw broker_now., Before D1 close, cache date is yesterday's date (from period_start)., H4 cache date includes the closing hour in cache_date.hour., H4 should skip analysis when cache file exists for that period. (+51 more)

### Community 126 - "test_h1_candle_period_at_boundary"
Cohesion: 0.14
Nodes (9): LLMProviderAdapterFactory, Any, LLM provider adapter — base interface and factory.  Defines the abstract adapter, Register an adapter class for a provider.          Args:             provider: P, Create an adapter instance for the given config.          Args:             conf, Return the list of providers with registered adapters., Clear all registered adapters.  Intended for testing only., The underlying instructor-patched client.          The concrete type depends on (+1 more)

### Community 128 - "usage.py"
Cohesion: 0.31
Nodes (10): _extract_int(), _extract_total_tokens(), _field_exists(), _get_field(), Any, LLM usage tracking — parse provider responses and extract token counts.  This mo, Return ``True`` if the nested attribute/dict path exists.      Works with object, Return the value at a nested attribute/dict path, or ``None``. (+2 more)

### Community 129 - "test_should_run_d1_after_close_with_cache"
Cohesion: 0.07
Nodes (25): _create_agents(), Create the three LLM agents used in the pipeline.      Each agent receives its o, DeciderAgent, LLM agents for the trading pipeline.  Each agent owns a slice of the analysis pi, Makes trading decisions based on market context., Reviews trading decisions and provides feedback., ReviewerAgent, CostTracker (+17 more)

### Community 132 - "TestCostTrackerWiring"
Cohesion: 0.20
Nodes (6): Resolved identity for the configured model., Return identity information about the configured LLM., Return identity information about the configured LLM., LLMModelIdentity, Human-readable model identity string for logging., Immutable, provider-aware identity for a resolved LLM model.      This is the ca

### Community 134 - "reload_settings"
Cohesion: 0.29
Nodes (5): ModelIdentityResolver, Protocol, Protocol for provider-specific model identity resolvers.      Implementations mu, Return ``True`` if this resolver can handle *model*., Resolve *model* into an :class:`LLMModelIdentity`.

### Community 138 - ".test_cache_disabled_by_env"
Cohesion: 0.40
Nodes (3): ExecutionMode, StrEnum, Deterministic enforcement gate for the trading pipeline.  This module implements

### Community 141 - "test_h1_candle_period"
Cohesion: 0.08
Nodes (24): Synthesizes market context from structure analysis and calendar., SynthesizerAgent, _mock_client(), Tests for LLM client injection in agents.  After refactoring, agent classes acce, SynthesizerAgent must log model info at init., Build a minimal mock ``LLMClientProtocol``., Cost logging tests that verify generate_structured_sync is used correctly., SynthesizerAgent must log input, output and total_tokens. (+16 more)

### Community 145 - ".test_pipeline_resets_cost_tracker_per_symbol"
Cohesion: 0.17
Nodes (7): Cost limit enforcement in the pipeline (TASK-3).      These tests verify that:, Verify sys.exit(1) when CostLimitExceeded is raised mid-run.          RED: curre, Verify cost_tracker.reset() is called before each symbol.          RED: ``_run_p, Verify set_limit() is called with settings.cost_per_symbol_limit.          RED:, Verify CostLimitExceeded propagates out of _run_single_symbol.          RED: ``_, cost_per_symbol_limit=0 disables enforcement — all symbols process.          RED, TestMainCostLimit

### Community 151 - "derive_allowed_actions"
Cohesion: 0.13
Nodes (20): _determine_d1_directional(), _determine_geometry_status(), _determine_h1_choch_based(), _determine_h1_trigger_confirmed(), _determine_h4_aligned(), _determine_lifecycle_status(), _determine_trade_direction(), grade_setup() (+12 more)

### Community 152 - "ExecutionStatus"
Cohesion: 0.22
Nodes (8): derive_allowed_actions(), derive_execution_status(), ExecutionStatus, Derive the execution status from a set of blockers.      Priority order (highest, Derive the allowed actions based on trade direction and execution status.      R, Status of the execution pipeline for a setup., Derive execution status from blockers before review stage., Derive allowed actions from direction and execution status.

## Knowledge Gaps
- **152 isolated node(s):** `trading-ai-agent`, `create-user.sh script`, `start-dev.sh script`, `trading-server`, `*.vue` (+147 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `DataSource` to `test_should_run_d1_after_close_with_cache`, `Mt5DataProvider`, `AgentState`, `Evaluator`, `TestGetCandlesBrokerNow`, `.test_cache_disabled_by_env`, `Agent Instructions`, `TestListRunsPruning`, `test_cache_path_mtf`, `test_cache_path_d1_uses_folder_date_not_broker_now`, `._run_async`, `tests/decision/__init__.py`, `test_result_pipeline_writes_json`, `TestSynthesizeContextCanonicalPrice`, `test_terminal_data_provider.py`, `AgentState`, `testget_cache_date_d1_before_close`?**
  _High betweenness centrality (0.310) - this node is a cross-community bridge._
- **Why does `create_app()` connect `test_runner.py` to `create_app`, `test_analyze_structure_fresh_saves_mtf_cache`, `src/data/__init__.py`, `main.py`, `TerminalApiError`, `._run_async`?**
  _High betweenness centrality (0.143) - this node is a cross-community bridge._
- **Why does `TradingGraph` connect `AgentState` to `DataSource`, `AgentState`, `Evaluator`, `test_should_run_h1_without_cache`, `TestCostTracking`, `test_cache_path_d1_uses_folder_date_not_broker_now`, `tests/calendar/__init__.py`, `tests/orchestrator/__init__.py`, `tests/decision/__init__.py`, `setup_logging`, `test_result_pipeline_writes_json`, `ExecutionStatus`, `test_cache_path_mtf_uses_d1_date`, `test_h4_candle_period_at_boundary`, `TestGetPositions`?**
  _High betweenness centrality (0.140) - this node is a cross-community bridge._
- **Are the 68 inferred relationships involving `AgentState` (e.g. with `Settings` and `PolicySettings`) actually correct?**
  _`AgentState` has 68 INFERRED edges - model-reasoned connections that need verification._
- **Are the 75 inferred relationships involving `LLMUsage` (e.g. with `OpenAIProviderAdapter` and `DeciderAgent`) actually correct?**
  _`LLMUsage` has 75 INFERRED edges - model-reasoned connections that need verification._
- **Are the 62 inferred relationships involving `TradingGraph` (e.g. with `_initialize_pipeline()` and `Settings`) actually correct?**
  _`TradingGraph` has 62 INFERRED edges - model-reasoned connections that need verification._
- **Are the 62 inferred relationships involving `CostTracker` (e.g. with `DeciderAgent` and `ReviewerAgent`) actually correct?**
  _`CostTracker` has 62 INFERRED edges - model-reasoned connections that need verification._
