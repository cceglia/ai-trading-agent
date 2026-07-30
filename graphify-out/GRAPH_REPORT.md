# Graph Report - Agent  (2026-07-30)

## Corpus Check
- 145 files · ~86,195 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2770 nodes · 5675 edges · 142 communities (128 shown, 14 thin omitted)
- Extraction: 68% EXTRACTED · 32% INFERRED · 0% AMBIGUOUS · INFERRED: 1844 edges (avg confidence: 0.66)
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
- _is_choch
- TestReviewerIndependenceLevel
- TestCostTrackerWiring
- .invalidate_cache
- reload_settings
- .test_empty_pricing_table
- create-user.sh
- .test_cache_disabled_by_env
- test_h1_candle_period
- derive_allowed_actions
- ExecutionStatus
- adapters/__init__.py

## God Nodes (most connected - your core abstractions)
1. `AgentState` - 88 edges
2. `LLMUsage` - 84 edges
3. `TradingGraph` - 82 edges
4. `CostTracker` - 81 edges
5. `DecisionAction` - 64 edges
6. `Settings` - 62 edges
7. `RiskPolicyState` - 58 edges
8. `ResultScanner` - 56 edges
9. `TradeDirection` - 55 edges
10. `ReviewStatus` - 54 edges

## Surprising Connections (you probably didn't know these)
- `TestCorsOrigins` --uses--> `Settings`  [INFERRED]
  server/tests/test_settings.py → analyzer/config/settings.py
- `TestResolvedCacheDir` --uses--> `Settings`  [INFERRED]
  server/tests/test_settings.py → analyzer/config/settings.py
- `sample_market_context()` --calls--> `MarketContextSummary`  [INFERRED]
  analyzer/tests/conftest.py → analyzer/src/decision/models.py
- `sample_decision()` --calls--> `DecisionOutput`  [INFERRED]
  analyzer/tests/conftest.py → analyzer/src/decision/models.py
- `sample_review()` --calls--> `ReviewVerdict`  [INFERRED]
  analyzer/tests/conftest.py → analyzer/src/decision/models.py

## Import Cycles
- None detected.

## Communities (142 total, 14 thin omitted)

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
Cohesion: 0.03
Nodes (109): Force a fresh Settings() on the next _get_settings() call., reload_settings(), CostLimitExceeded, Exception, Raised when per-symbol LLM cost exceeds the configured limit., AgentState, _has_high_impact_calendar_event(), Any (+101 more)

### Community 4 - "SnapshotBuilder"
Cohesion: 0.07
Nodes (19): Evaluator, Any, datetime, Check if an event falls within the time window from now.          Returns False, Evaluate events for symbol with timeframe-dependent window.          Args:, Evaluates calendar events for trading symbols., High-impact event outside the window should NOT block., High-impact event within the window SHOULD block. (+11 more)

### Community 5 - "Evaluator"
Cohesion: 0.07
Nodes (40): _cache_path(), _candle_period(), _get_settings(), load_cached_analysis(), Any, datetime, Determine if analysis should run for this timeframe.      Args:         timefram, Save analysis result to disk.      Args:         timeframe: "D1", "H4", or "H1" (+32 more)

### Community 6 - "Trading AI Agent"
Cohesion: 0.07
Nodes (20): allDates, dateSourceRuns, days, filteredRuns, months, router, runCountBySymbol, runNowError (+12 more)

### Community 7 - "TestSynthesizerPrompt"
Cohesion: 0.08
Nodes (19): CalendarProvider, DataSource, Any, datetime, Protocol, Analyze market structure from snapshots.          Args:             snapshots: D, Fetch OHLC candles as CSV string.          Args:             symbol: Trading sym, Get latest price info for a symbol.          Args:             symbol: Trading s (+11 more)

### Community 8 - "TestCostTracking"
Cohesion: 0.05
Nodes (50): _canonical_structure_analysis(), _directional_structure_analysis(), _make_cached_summary(), mock_reviewer(), mock_synthesizer(), datetime, Path, RED-first tests for orchestrator-level synthesizer cache integration.  Tests ver (+42 more)

### Community 9 - "ForexFactoryCalendar"
Cohesion: 0.04
Nodes (42): CostTracker, CostTracker — tracks LLM API call costs.  Exposes a single :class:`CostTracker`, Accumulated cost across all recorded calls., Number of calls recorded., Reset accumulated cost and call count to zero., Tracks LLM API call costs using per-model token pricing.      Each instance is i, Set a per-symbol cost limit.          When *limit* is ``<= 0`` or ``None`` the l, Set the current symbol for error context.          The symbol is used by :meth:` (+34 more)

### Community 10 - "orchestrator/test_synthesizer_cache.py"
Cohesion: 0.25
Nodes (14): EngineError, ExternalDerivedValuesError, InsufficientDataError, ParentContextError, Any, Exception, Base class for deterministic engine errors., TimeframeMismatchError (+6 more)

### Community 11 - "Agent Instructions"
Cohesion: 0.07
Nodes (21): _build_parser(), main(), _parse_and_configure_settings(), Build the CLI argument parser.      Returns:         Configured ArgumentParser i, Parse CLI args into a configured Settings instance.      Applies CLI overrides (, Main entry point.      Parses CLI arguments, initialises the analysis pipeline,, CaptureFixture, LogCaptureFixture (+13 more)

### Community 12 - "config/__init__.py"
Cohesion: 0.05
Nodes (40): autoprefixer, axios, echarts, postcss, tailwindcss, typescript, dependencies, axios (+32 more)

### Community 13 - "trading-ai-agent"
Cohesion: 0.05
Nodes (48): DecisionAction, EnforcementViolation, EnforcementViolationCode, ExecutionStatus, FinalDecisionState, Code identifying an enforcement violation in the setup., Decision action taken by the decision agent., An enforcement violation detected during setup validation.      Attributes: (+40 more)

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
Cohesion: 0.09
Nodes (20): _determine_d1_directional(), _determine_h1_trigger_confirmed(), grade_setup(), Any, Grade a trading setup based on multi-timeframe structural analysis.      This fu, Determine if D1 shows clear directional bias.      Args:         d1_bias: D1 bia, Determine if H1 trigger is confirmed.      Args:         h1_setup_status: H1 set, _d1_context() (+12 more)

### Community 20 - "tests/data/__init__.py"
Cohesion: 0.33
Nodes (3): Configure structured logging for the trading agent., setup_logging(), TestSetupLogging

### Community 21 - "tests/decision/__init__.py"
Cohesion: 0.11
Nodes (26): _create_agents(), _format_field(), _format_field_int(), _get_decision_field(), _initialize_pipeline(), _print_summary(), _print_symbol_summary(), Any (+18 more)

### Community 22 - "tests/__init__.py"
Cohesion: 0.16
Nodes (9): _log_llm_call(), Any, Record an LLM call and log its cost. Returns enriched usage with costs., Tests for agent cost-logging helper extraction., _log_llm_call extracts duplicated cost-logging from agents., When usage is provided, logs cost details., When usage is all-zero (no usage data), logs zero cost., Records the call on the cost tracker when usage is provided. (+1 more)

### Community 23 - "tests/orchestrator/__init__.py"
Cohesion: 0.16
Nodes (11): _build_blockers(), Evaluate all blocker conditions and return the active blockers.      This is an, ExecutionBlocker, BaseModel, Self, An execution blocker that prevents or delays trade execution.      Attributes:, Create an ExecutionPolicyState from a setup and blockers.          Extracts the, Key blocker codes are creatable and have expected properties. (+3 more)

### Community 24 - "_make_mcp_tool_result"
Cohesion: 0.09
Nodes (22): DOM, DOM.Iterable, env.d.ts, ES2022, src/**/*.ts, src/**/*.vue, compilerOptions, baseUrl (+14 more)

### Community 25 - "TerminalApiError"
Cohesion: 0.09
Nodes (25): Walk the data directory tree, read/parse JSON result files,     filter/sort into, ResultScanner, Path, Unit tests for ResultScanner., Helper to write a result JSON file., Files not in YYYY/MM/DD/SYMBOL/ pattern are skipped., When JSON has a 'symbol' field, it overrides the path-derived symbol., Tests for ResultScanner.get_run(). (+17 more)

### Community 26 - "test_terminal_data_provider.py"
Cohesion: 0.09
Nodes (15): Immutable state for risk management policy evaluation.      Attributes:, Final risk percentage after grade multiplier is applied., Whether the estimated reward-to-risk meets the minimum threshold., RiskPolicyState, FinalOutputAssembler, Final decision output assembler.  This module implements :class:`FinalOutputAsse, Assembles a single :class:`AnalysisResult` from all pipeline states.      The as, Map all pipeline states into a unified :class:`AnalysisResult`.          Paramet (+7 more)

### Community 27 - "TestGetCandlesBrokerNow"
Cohesion: 0.11
Nodes (17): Any, datetime, OHLCBar, Path, Writes analysis results to JSON files in the data/ directory tree., Write result JSON to disk. Returns the file path written.          Args:, Compute data/YYYY/MM/DD/SYMBOL/result-HH.json path., ResultWriter (+9 more)

### Community 28 - "TestGetPositions"
Cohesion: 0.06
Nodes (19): BiasLevel, Structural bias levels., Status of the review process., ReviewStatus, DecisionOutput, BaseModel, Whether the review outcome is approved., Decision output from decider agent.      The LLM selects an action and explains (+11 more)

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
Cohesion: 0.09
Nodes (15): build_risk_policy(), Create a :class:`RiskPolicyState` from a setup grade and risk config.      The f, Tests for deterministic risk policy creation (Section 16.3).  Tests the build_ri, build_risk_policy computed fields work end-to-end., Missing R/R leads to risk_reward_ok=False even if minimum is technically met., Input validation for build_risk_policy., RiskPolicyState model validates estimated_reward_risk > 0 via gt=0 constraint., Edge cases for risk policy creation. (+7 more)

### Community 33 - "MarketContextSummary"
Cohesion: 0.16
Nodes (10): ForexFactoryCalendar, Any, Convert raw time text to ISO timestamp (best-effort)., Map raw impact text to standard impact level., Economic calendar provider via ForexFactory scraping., Initialize calendar provider.          Args:             cache_hours: Hours to c, Fetch upcoming economic calendar events.          Returns:             List of e, Check if cache is still valid. (+2 more)

### Community 34 - "setup_logging"
Cohesion: 0.05
Nodes (25): calculate_entry_plan(), calculate_risk_reward(), _determine_entry_type(), _extract_entry_prices(), Any, Extract and normalize entry price data from setup context.      Args:         se, Determine the entry type based on price relationship.      Args:         entry_p, Calculate entry plan from raw setup data.      Accepts the raw entry data from t (+17 more)

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
Cohesion: 0.11
Nodes (11): classify_trigger(), Classify a price-action trigger event and determine its confirmation status., CHoCH classification with all confirmation paths., CHoCH without any confirmation path → PENDING_CONFIRMATION., CHoCH + retest (Path A) → CONFIRMED., CHoCH + continuation BOS (Path B) → CONFIRMED., CHoCH + sweep-and-reclaim (Path C) → CONFIRMED., RECLAIM and RETEST trigger types. (+3 more)

### Community 39 - "test_should_run_h1_different_period"
Cohesion: 0.06
Nodes (23): Tests for multi-symbol support in main.py., Test that argparse accepts multiple symbols via _build_parser., _build_parser accepts multiple symbols as nargs+., _build_parser is backward-compatible with single symbol., Cost limit enforcement in the pipeline (TASK-3).      These tests verify that:, Verify sys.exit(1) when CostLimitExceeded is raised mid-run.          RED: curre, --model option is accepted., Verify the error log includes limit/cost details.          RED: CostLimitExceede (+15 more)

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
Cohesion: 0.27
Nodes (6): Type of price action trigger for a setup., TriggerType, _is_bos(), CHoCH/BOS trigger classification for the H1 timeframe.  This module implements `, Return ``True`` when the trigger is a Break-of-Structure event., TestIsBos

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
Cohesion: 0.05
Nodes (23): BaseModel, Server-specific Pydantic models., Request body for POST /api/run., Summary of a single analysis run, matching Node.js RunSummary shape., RunRequest, RunSummary, Route-level tests with mocked scanner/runner., Tests for GET /api/runs/{symbol}/{year}/{month}/{day}/{file}. (+15 more)

### Community 54 - "main.py"
Cohesion: 0.08
Nodes (18): Retry reading result files with backoff.          After a subprocess completes t, Return the subset of *symbols* that have no run in the scanner., Walk the data directory via ResultScanner and return the         most recent res, Spawn Python subprocess to run analysis, enforce timeout,     capture stderr, an, Run analysis for the given symbols.          Spawns: python main.py [--model <m>, Spawn the Python process and wait for completion.          On timeout the proces, RunService, Verify --model flag is absent when model is None. (+10 more)

### Community 55 - "test_result_pipeline_writes_json"
Cohesion: 0.09
Nodes (46): evaluate_execution_policy(), PolicySettings, Deterministic execution policy evaluation for the multi-timeframe pipeline.  Thi, Evaluate execution policy and return an :class:`ExecutionPolicyState`.      Cons, Configuration for execution policy evaluation.      Attributes:         countert, BlockerSeverity, ExecutionBlockerCode, ExecutionBlockerType (+38 more)

### Community 56 - "TestSynthesizeContextCanonicalPrice"
Cohesion: 0.10
Nodes (15): MonkeyPatch, Settings().terminal_server_url returns the default MCP URL., Settings().terminal_api_key returns empty string by default., TRADING_TERMINAL_API_KEY env var overrides the default., TRADING_TERMINAL_SERVER_URL env var overrides the default., Invalid JSON raises a validation error., Tests for the new synthesizer_cache_enabled Settings field.      RED phase: thes, synthesizer_cache_enabled defaults to True when no env var is set. (+7 more)

### Community 57 - "TestOhlcCachePath"
Cohesion: 0.08
Nodes (14): Tests for model identity resolution and execution mode validation (Section 16.7), Backtest modes don't require STRONG independence., Safe resolution: provide a function to resolve execution mode., Consistency checks between decision and engine models., DecisionAction should be importable from both engine models and decision models., BiasLevel should be importable from both engine models and decision models., ReviewStatus should be importable from both., ExecutionMode validation requirements. (+6 more)

### Community 58 - "test_h4_candle_period_at_boundary"
Cohesion: 0.15
Nodes (8): derive_allowed_actions(), Derive the allowed actions based on trade direction and execution status.      R, Derive allowed actions from direction and execution status., Allowed actions based on status and direction., Non-executable actions (NO_TRADE, WAIT_FOR_SETUP) pass without         needing a, TestDeriveAllowedActions, DeterministicSetupState holds prices, DecisionOutput holds action., LLM cannot select BUY_SETUP when deterministic says SELL_SETUP.

### Community 59 - "AgentState"
Cohesion: 0.17
Nodes (12): Entry plan calculation for the multi-timeframe pipeline.  This module implements, EntryType, InvalidationReason, ModelIdentityResolutionStatus, StrEnum, Shared domain enums and data models for the market structure engine.  This modul, Reason a setup was invalidated., Type of entry order for a trade setup. (+4 more)

### Community 60 - "test_analyze_structure_uses_broker_time_not_utc"
Cohesion: 0.20
Nodes (9): _dict_to_sns(), Reset the _settings sentinel in candle_cache before each test.      Tests use mo, Recursively convert a dict to a SimpleNamespace., Reset the _settings sentinel in synthesizer_cache before each test.      Mirrors, reset_candle_cache_settings(), reset_synthesizer_cache_settings(), sample_decision(), sample_market_context() (+1 more)

### Community 76 - "DecisionOutput"
Cohesion: 0.57
Nodes (6): _canonicalize(), _event_type(), Any, _quality(), scan_events(), _scope()

### Community 80 - "test_cache_path_d1_uses_folder_date_not_broker_now"
Cohesion: 0.12
Nodes (13): DeterministicSetupState, Immutable state representing a classified trading setup.      Captures the full, Whether this setup qualifies as a candidate for decision.          A setup is a, DeterministicEnforcementGate, Evaluate all enforcement checks and produce a final decision state.          Arg, CANDIDATE_NOT_GENERATED: executable action without classified candidate., EXECUTION_NOT_ACTIONABLE: executable action while not ACTIONABLE., DIRECTION_MISMATCH: decision contradicts deterministic direction. (+5 more)

### Community 81 - ".write"
Cohesion: 0.13
Nodes (18): get_cache_date(), Return the cache date for the given timeframes.      Returns a datetime whose da, _get_settings(), load_ohlc_cache(), ohlc_cache_path(), datetime, OHLCBar, Compute OHLC cache file path, parallel to analysis cache.      Cache path conven (+10 more)

### Community 82 - "test_should_run_d1_after_close_with_cache"
Cohesion: 0.33
Nodes (6): Development environment (Docker), Quick commands (run inside container), Running from Docker (host → container), Setup, Starting the container, Stopping

### Community 84 - "setup_logging"
Cohesion: 0.13
Nodes (16): AnalysisResult, OHLCBar, OHLCData, BaseModel, Single OHLC bar for chart rendering., OHLC data keyed by timeframe., Entry, stop-loss and take-profit overlay for charts., Top-level pipeline output serialized to JSON for the web viewer.      Fields are (+8 more)

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
Cohesion: 0.11
Nodes (15): BaseHTTPMiddleware, FastAPI, Request, RequestResponseEndpoint, Response, create_app(), FastAPI application entry point — port of the TypeScript Express server., Create and configure the FastAPI application. (+7 more)

### Community 93 - "test_should_run_h1_different_period"
Cohesion: 0.28
Nodes (8): Path, End-to-end integration test for the result JSON pipeline., Pipeline with fatal error produces valid error result., Result with no OHLC data produces empty arrays., Full pipeline simulation writes valid JSON result., test_empty_ohlc_defaults(), test_result_pipeline_writes_json(), test_result_with_fatal_error()

### Community 94 - "test_load_returns_none_when_missing"
Cohesion: 0.29
Nodes (4): _check_path_a_confirmed_retest(), Path A: CHoCH is confirmed by a retest of the broken level.      A confirmed ret, Path A: CHoCH confirmed by a retest of the broken level., TestCheckPathAConfirmedRetest

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
Cohesion: 0.10
Nodes (18): client(), client_with_auth(), mock_data_dir(), Any, Path, RunSummary, Shared fixtures for server tests., Create a temporary data directory with fixture JSON files. (+10 more)

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
Cohesion: 0.31
Nodes (3): _direction_matches(), Return ``True`` when the trigger direction matches the preferred direction., TestDirectionMatches

### Community 103 - "test_should_run_h1_without_cache"
Cohesion: 0.31
Nodes (3): Map a raw event-type string to the corresponding TriggerType enum.      Returns, _resolve_trigger_type(), TestResolveTriggerType

### Community 105 - "create_app"
Cohesion: 0.18
Nodes (6): LLMCommunicationClient, LLM client protocol and communication client for structured LLM calls.  This mod, Concrete LLM client implementing ``LLMClientProtocol``.      Wraps an ``instruct, Return identity information about the configured LLM., The model identifier., BaseException

### Community 106 - "TestListRunsPruning"
Cohesion: 0.33
Nodes (3): _determine_lifecycle_status(), Determine lifecycle status based on trigger confirmation.      Args:         h1_, TestDetermineLifecycleStatus

### Community 107 - "TestListRunsIntegration"
Cohesion: 0.29
Nodes (5): _check_path_b_continuation_bos(), Any, Path B: CHoCH is confirmed by a continuation BOS in the same direction.      A c, Path B: CHoCH confirmed by a continuation BOS in the same direction., TestCheckPathBContinuationBos

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
Cohesion: 0.22
Nodes (8): Any, T, The underlying sync instructor-patched OpenAI client., Send messages to the LLM and return a structured Pydantic model.          Runs t, Synchronous variant of :meth:`generate_structured`.          Returns ``(response, LLMClientError, Exception, Raised when an LLM API call fails after all retries.

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
Cohesion: 0.27
Nodes (6): Any, T, Synchronous variant of :meth:`generate_structured`.          Returns the respons, Send messages to the LLM and return a structured Pydantic model.          This m, Synchronous variant of :meth:`generate_structured`.          Returns ``(response, Send messages to the LLM and return a structured Pydantic model.          Args:

### Community 119 - "TestParseUsageChatCompletions"
Cohesion: 0.17
Nodes (8): OpenAIProviderAdapter, OpenAI provider adapter — instructor-based structured output.  Wraps the ``instr, The provider this adapter handles., The raw model identifier., Optional reasoning effort level., OpenAI provider adapter using ``instructor`` for structured output.      Conform, LLMModelConfig, Immutable configuration for an LLM endpoint.      Attributes:         model: Mod

### Community 122 - "test_d1_candle_period_after_close"
Cohesion: 0.20
Nodes (5): Tests for CHoCH/BOS trigger classification (Section 16.5).  Tests the triggers.p, None trigger event handling., When multiple confirmation events are provided, any one path suffices., TestClassifyTriggerMultiplePaths, TestClassifyTriggerNull

### Community 124 - "test_h4_candle_period_at_boundary"
Cohesion: 0.18
Nodes (7): LLMProviderAdapter, Protocol, Abstract protocol for LLM provider adapters.      An adapter encapsulates the pr, The provider this adapter handles., Resolved identity for the configured model., The raw model identifier., Optional reasoning effort level.

### Community 125 - "testget_cache_date_d1_before_close"
Cohesion: 0.03
Nodes (58): After D1 close (17:00), the current candle is today's., H4 period containing the given time, anchored at 00:00., At exact H1 boundary, period starts at that time., H1 period crossing midnight boundary works correctly., D1 file path uses folder_date from get_cache_date, not raw broker_now., Before D1 close, cache date is yesterday's date (from period_start)., After D1 close, cache date is today's date (from period_start)., H4 cache date includes the closing hour in cache_date.hour. (+50 more)

### Community 126 - "test_h1_candle_period_at_boundary"
Cohesion: 0.14
Nodes (9): LLMProviderAdapterFactory, Any, LLM provider adapter — base interface and factory.  Defines the abstract adapter, Register an adapter class for a provider.          Args:             provider: P, Create an adapter instance for the given config.          Args:             conf, Return the list of providers with registered adapters., Clear all registered adapters.  Intended for testing only., The underlying instructor-patched client.          The concrete type depends on (+1 more)

### Community 127 - "test_should_run_d1_after_close_without_cache"
Cohesion: 0.33
Nodes (4): _check_path_c_sweep_and_reclaim(), Path C: CHoCH is confirmed by a sweep-and-reclaim pattern.      A sweep-and-recl, Path C: CHoCH confirmed by a sweep-and-reclaim pattern., TestCheckPathCSweepAndReclaim

### Community 128 - "usage.py"
Cohesion: 0.31
Nodes (10): _extract_int(), _extract_total_tokens(), _field_exists(), _get_field(), Any, LLM usage tracking — parse provider responses and extract token counts.  This mo, Return ``True`` if the nested attribute/dict path exists.      Works with object, Return the value at a nested attribute/dict path, or ``None``. (+2 more)

### Community 129 - "test_should_run_d1_after_close_with_cache"
Cohesion: 0.25
Nodes (3): ModelIdentityResolutionStatus has three states with expected semantics., Semantic: RESOLVED means a clear model was identified., TestModelIdentityResolutionStatus

### Community 130 - "_is_choch"
Cohesion: 0.43
Nodes (3): _is_choch(), Return ``True`` when the trigger is a Change-of-Character event., TestIsChoch

### Community 131 - "TestReviewerIndependenceLevel"
Cohesion: 0.29
Nodes (3): ReviewerIndependenceLevel has three levels of independence., STRONG, WEAK, NONE each have different string values., TestReviewerIndependenceLevel

### Community 132 - "TestCostTrackerWiring"
Cohesion: 0.25
Nodes (5): Resolved identity for the configured model., Return identity information about the configured LLM., LLMModelIdentity, Human-readable model identity string for logging., Immutable, provider-aware identity for a resolved LLM model.      This is the ca

### Community 134 - "reload_settings"
Cohesion: 0.29
Nodes (5): ModelIdentityResolver, Protocol, Protocol for provider-specific model identity resolvers.      Implementations mu, Return ``True`` if this resolver can handle *model*., Resolve *model* into an :class:`LLMModelIdentity`.

### Community 138 - ".test_cache_disabled_by_env"
Cohesion: 0.17
Nodes (7): ExecutionMode, StrEnum, Deterministic enforcement gate for the trading pipeline.  This module implements, Tests for the new openai_reasoning_effort Settings field.      These tests will, openai_reasoning_effort defaults to empty string (not set)., TRADING_OPENAI_REASONING_EFFORT env var overrides the default., TestReasoningEffortSettings

### Community 141 - "test_h1_candle_period"
Cohesion: 0.05
Nodes (56): DeciderAgent, LLM agents for the trading pipeline.  Each agent owns a slice of the analysis pi, Makes trading decisions based on market context., Reviews trading decisions and provides feedback., Synthesizes market context from structure analysis and calendar., ReviewerAgent, SynthesizerAgent, LLMClientProtocol (+48 more)

### Community 151 - "derive_allowed_actions"
Cohesion: 0.07
Nodes (36): _determine_geometry_status(), _determine_h1_choch_based(), _determine_h4_aligned(), _determine_trade_direction(), Deterministic setup grading for the multi-timeframe pipeline.  This module imple, Determine if H1 trigger is CHoCH-based.      Args:         h1_trigger_type: H1 t, Determine geometry status based on entry plan validity.      Args:         h1_se, Determine trade direction from D1 bias and H4 preferred direction.      Args: (+28 more)

### Community 152 - "ExecutionStatus"
Cohesion: 0.13
Nodes (13): derive_execution_status(), Derive the execution status from a set of blockers.      Priority order (highest, Derive execution status from blockers before review stage., _blocker(), Tests for enforcement logic and models (Section 16.6).  Tests the enforcement-re, Tests for enforcement reviewer logic patterns., Deterministic violations (e.g., RISK_REWARD with INVALIDATES_GRADE)         shou, A review that is not APPROVED but has no deterministic violations         produc (+5 more)

## Knowledge Gaps
- **152 isolated node(s):** `trading-ai-agent`, `create-user.sh script`, `start-dev.sh script`, `trading-server`, `*.vue` (+147 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `DataSource` to `Mt5DataProvider`, `AgentState`, `Evaluator`, `.test_cache_disabled_by_env`, `Agent Instructions`, `test_cache_path_mtf`, `test_cache_path_d1_uses_folder_date_not_broker_now`, `.write`, `tests/decision/__init__.py`, `test_result_pipeline_writes_json`, `TestSynthesizeContextCanonicalPrice`, `TestGetCandlesBrokerNow`, `._run_async`?**
  _High betweenness centrality (0.274) - this node is a cross-community bridge._
- **Why does `TradingGraph` connect `AgentState` to `DataSource`, `Evaluator`, `TestCostTracking`, `trading-ai-agent`, `test_cache_path_d1_uses_folder_date_not_broker_now`, `setup_logging`, `tests/decision/__init__.py`, `test_result_pipeline_writes_json`, `derive_allowed_actions`, `test_terminal_data_provider.py`, `TestGetPositions`?**
  _High betweenness centrality (0.166) - this node is a cross-community bridge._
- **Why does `create_app()` connect `test_runner.py` to `server/tests/conftest.py`, `test_analyze_structure_fresh_saves_mtf_cache`, `src/data/__init__.py`, `main.py`, `TerminalApiError`, `._run_async`?**
  _High betweenness centrality (0.154) - this node is a cross-community bridge._
- **Are the 68 inferred relationships involving `AgentState` (e.g. with `Settings` and `PolicySettings`) actually correct?**
  _`AgentState` has 68 INFERRED edges - model-reasoned connections that need verification._
- **Are the 75 inferred relationships involving `LLMUsage` (e.g. with `OpenAIProviderAdapter` and `DeciderAgent`) actually correct?**
  _`LLMUsage` has 75 INFERRED edges - model-reasoned connections that need verification._
- **Are the 62 inferred relationships involving `TradingGraph` (e.g. with `_initialize_pipeline()` and `Settings`) actually correct?**
  _`TradingGraph` has 62 INFERRED edges - model-reasoned connections that need verification._
- **Are the 62 inferred relationships involving `CostTracker` (e.g. with `DeciderAgent` and `ReviewerAgent`) actually correct?**
  _`CostTracker` has 62 INFERRED edges - model-reasoned connections that need verification._
