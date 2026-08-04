# Graph Report - Agent  (2026-08-04)

## Corpus Check
- 166 files · ~108,797 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3349 nodes · 7877 edges · 198 communities (164 shown, 34 thin omitted)
- Extraction: 63% EXTRACTED · 37% INFERRED · 0% AMBIGUOUS · INFERRED: 2911 edges (avg confidence: 0.63)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b253215a`
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
- TestOpenAIModelIdentityResolver
- .test_empty_pricing_table
- create-user.sh
- .test_cache_disabled_by_env
- TestArgparseMultiSymbol
- ResultWriterContractError
- test_h1_candle_period
- TestAnthropicModelIdentityResolver
- TestDetermineD1Directional
- test_grading.py
- TestTerminalSettings
- _mock_analysis_result
- TestDetermineGeometryStatus
- TestDetermineH1ChochBased
- TestDetermineH1TriggerConfirmed
- TestDetermineH4Aligned
- derive_allowed_actions
- ExecutionStatus
- TestSynthesizeContextCanonicalPrice
- Issue tracker: GitHub
- Domain Docs
- Agent skills
- testget_cache_date_h4_returns_closing_hour
- test_should_run_h4_with_cache
- test_d1_candle_period_after_close
- adapters/__init__.py
- test_should_run_h4_without_cache
- testget_cache_date_d1_after_close
- test_should_run_d1_after_close_with_cache
- test_h4_candle_period
- test_h1_candle_period_at_boundary
- test_h1_candle_period_midnight
- test_cache_path_d1_uses_folder_date_not_broker_now
- TestDeriveAllowedActions
- ResultWriterContractError
- test_cache_path_h1_includes_closing_hour
- triage-labels.md
- test_should_run_h4_with_cache
- TestDecisionOutput
- test_should_run_d1_before_close
- utils.py
- _mock_analysis_result
- test_should_run_h1_with_cache
- test_should_run_h1_different_period
- reload_settings
- test_save_h1_creates_hour_suffixed_file
- .test_cost_limit_exceeded_is_exception
- _build_parser
- Domain Glossary
- Architecture
- test_should_run_h4_without_cache
- testget_cache_date_d1_before_close
- testget_cache_date_d1_after_close
- test_should_run_d1_cache_in_wrong_folder
- 0001-reviewer-configuration-names.md
- test_should_run_h1_different_period
- TestArgparseMultiSymbol
- TestLogLlmCall
- test_load_returns_none_when_missing
- test_cache_path_h1_includes_closing_hour
- test_cache_path_zero_padded_hour
- test_cache_path_h4_hour_04_is_zero_padded
- reset_synthesizer_cache_settings

## God Nodes (most connected - your core abstractions)
1. `Settings` - 126 edges
2. `DecisionAction` - 112 edges
3. `TradeDirection` - 97 edges
4. `AgentState` - 94 edges
5. `CostTracker` - 93 edges
6. `TradingGraph` - 93 edges
7. `RiskPolicyState` - 88 edges
8. `LLMUsage` - 88 edges
9. `SetupGrade` - 85 edges
10. `DeterministicSetupState` - 85 edges

## Surprising Connections (you probably didn't know these)
- `TestCorsOrigins` --uses--> `Settings`  [INFERRED]
  server/tests/test_settings.py → analyzer/config/settings.py
- `TestResolvedCacheDir` --uses--> `Settings`  [INFERRED]
  server/tests/test_settings.py → analyzer/config/settings.py
- `test_settings_has_analysis_cache_dir()` --calls--> `Settings`  [INFERRED]
  analyzer/tests/analysis/test_candle_cache.py → analyzer/config/settings.py
- `test_settings_has_d1_close_time()` --calls--> `Settings`  [INFERRED]
  analyzer/tests/analysis/test_candle_cache.py → analyzer/config/settings.py
- `test_settings_has_h4_close_time()` --calls--> `Settings`  [INFERRED]
  analyzer/tests/analysis/test_candle_cache.py → analyzer/config/settings.py

## Import Cycles
- None detected.

## Communities (198 total, 34 thin omitted)

### Community 0 - "TestFatalError"
Cohesion: 0.27
Nodes (14): get_profile(), Any, TimeframeProfile, build_levels(), _cluster_side(), Any, analyze_liquidity(), _build_equal_pools() (+6 more)

### Community 1 - "Mt5DataProvider"
Cohesion: 0.12
Nodes (24): _make_summary(), datetime, MonkeyPatch, Path, Tests for synthesizer_cache — day-based synthesizer output caching.  ``src/decis, Fresh cache directory — should_run_synthesis returns True., After save — should_run_synthesis returns False., Corrupt JSON, pydantic validation failure, disk errors. (+16 more)

### Community 2 - "DataSource"
Cohesion: 0.06
Nodes (24): BaseSettings, Self, Parse JSON string env var and validate prices.          Accepts only the new for, Trading agent configuration., Reject unsupported instructor_mode values at Settings-parse time.          An in, Map an empty-string env var to ``None`` (inherit the primary timeout)., Resolve ``analysis_cache_dir`` to an absolute path.          Both the analyzer a, Validate execution policy settings based on execution mode.          Paper and L (+16 more)

### Community 3 - "AgentState"
Cohesion: 0.06
Nodes (27): mock_decider(), mock_synthesizer(), Corrupt per-TF cache file must not crash — fall back to fresh fetch., get_candles must be called with broker_time param., AgentState must NOT have 'account_info'; it must have 'symbol_price' instead., AgentState must NOT have 'market_data' — the dead field was removed.      This v, _analyze_structure must fetch all three timeframes fresh (no partial cache)., When no cache files exist, all 3 TFs must be fetched fresh. (+19 more)

### Community 4 - "SnapshotBuilder"
Cohesion: 0.07
Nodes (19): Evaluator, Any, datetime, Check if an event falls within the time window from now.          Returns False, Evaluate events for symbol with timeframe-dependent window.          Args:, Evaluates calendar events for trading symbols., High-impact event outside the window should NOT block., High-impact event within the window SHOULD block. (+11 more)

### Community 5 - "Evaluator"
Cohesion: 0.05
Nodes (43): After D1 close (17:00), the current candle is today's., At exact H1 boundary, period starts at that time., H4 cache date includes the closing hour in cache_date.hour., D1 should run analysis when no cache file exists., H4 should skip analysis when cache file exists for that period., D1 before close should always run analysis (candle not closed)., D1 after close with existing cache should skip analysis., D1 after close without cache should run analysis. (+35 more)

### Community 6 - "Trading AI Agent"
Cohesion: 0.07
Nodes (23): emit, startRun(), allDates, dateSourceRuns, days, filteredRuns, handleRunNow(), months (+15 more)

### Community 7 - "TestSynthesizerPrompt"
Cohesion: 0.08
Nodes (19): CalendarProvider, DataSource, Any, datetime, Protocol, Analyze market structure from snapshots.          Args:             snapshots: D, Fetch OHLC candles as CSV string.          Args:             symbol: Trading sym, Get latest price info for a symbol.          Args:             symbol: Trading s (+11 more)

### Community 8 - "TestCostTracking"
Cohesion: 0.10
Nodes (21): _canonical_structure_analysis(), _make_cached_summary(), datetime, Path, Different H1 hour on same day → cache miss (different closing hours).          C, Model changed across runs → cache hit (model version not in cache key)., Cache hit → cost_tracker.call_count == 0 (no LLM call recorded)., Build a ``MarketContextSummary`` that looks like it came from the cache. (+13 more)

### Community 9 - "ForexFactoryCalendar"
Cohesion: 0.04
Nodes (47): CostTracker, CostTracker — tracks LLM API call costs.  Exposes a single :class:`CostTracker`, Accumulated cost across all recorded calls., Number of calls recorded., Reset accumulated cost and call count to zero., Tracks LLM API call costs using per-model token pricing.      Each instance is i, Set a per-symbol cost limit.          When *limit* is ``<= 0`` or ``None`` the l, Set the current symbol for error context.          The symbol is used by :meth:` (+39 more)

### Community 10 - "orchestrator/test_synthesizer_cache.py"
Cohesion: 0.23
Nodes (15): EngineError, ExternalDerivedValuesError, InsufficientDataError, ParentContextError, Any, Exception, Structure analysis missing required 'timeframes' schema., Base class for deterministic engine errors. (+7 more)

### Community 11 - "Agent Instructions"
Cohesion: 0.08
Nodes (15): main(), Main entry point.      Parses CLI arguments, initialises the analysis pipeline,, CaptureFixture, LogCaptureFixture, With --telegram, notification is NOT sent when action is no_trade., With --telegram, notification is NOT sent when review is not approved., Verify main() calls graph.run() for each symbol., Warning is logged when --telegram is set but token/chat_id are empty. (+7 more)

### Community 12 - "config/__init__.py"
Cohesion: 0.05
Nodes (40): autoprefixer, axios, echarts, postcss, tailwindcss, typescript, dependencies, axios (+32 more)

### Community 13 - "trading-ai-agent"
Cohesion: 0.05
Nodes (40): EnforcementViolation, FinalDecisionState, An enforcement violation detected during setup validation.      Attributes:, Immutable state representing the final decision outcome.      Attributes:, Tests for output assembly logic (Section 16.9).  Tests how FinalDecisionState as, LLM output: action selection and reasoning. No deterministic fields., Enforcement violations are structured and carry code + reason., NOT_REQUIRED review status skips the reviewer for deterministic early exits. (+32 more)

### Community 14 - "src/calendar/__init__.py"
Cohesion: 0.37
Nodes (12): analyze_multi_timeframe(), analyze_snapshot(), _apply_structural_event_transition(), _check_same_market(), Any, Any, review_analysis(), review_multi_timeframe() (+4 more)

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
Nodes (16): grade_setup(), Any, Grade a trading setup based on multi-timeframe structural analysis.      This fu, _d1_context(), _h1_context(), _h4_context(), Any, AAA can be achieved with ALIGNED_PULLBACK as well. (+8 more)

### Community 20 - "tests/data/__init__.py"
Cohesion: 0.33
Nodes (3): Configure structured logging for the trading agent., setup_logging(), TestSetupLogging

### Community 21 - "tests/decision/__init__.py"
Cohesion: 0.10
Nodes (27): _build_parser(), _create_agents(), _get_decision_field(), _initialize_pipeline(), _model_or_dict(), _parse_and_configure_settings(), _print_summary(), Any (+19 more)

### Community 22 - "tests/__init__.py"
Cohesion: 0.14
Nodes (11): calculate_entry_plan(), Calculate entry plan from raw setup data.      Accepts the raw entry data from t, calculate_entry_plan integration test., When geometry is invalid, status is TEMPORARILY_UNAVAILABLE., NO_SETUP with missing prices must not be labelled INSUFFICIENT_DATA.          Th, A CLASSIFIED candidate with missing prices is genuinely INSUFFICIENT_DATA., Entry calculator accepts TradeDirection as string., Entry calculator accepts TradeDirection as enum. (+3 more)

### Community 23 - "tests/orchestrator/__init__.py"
Cohesion: 0.13
Nodes (28): DeterministicEnforcementGate, Enforces deterministic invariants before a decision is finalised.      The gate, _calendar_blocker(), _make_decision(), _make_policy(), _make_review(), _make_risk_policy(), _make_setup() (+20 more)

### Community 24 - "_make_mcp_tool_result"
Cohesion: 0.09
Nodes (22): DOM, DOM.Iterable, env.d.ts, ES2022, src/**/*.ts, src/**/*.vue, compilerOptions, baseUrl (+14 more)

### Community 25 - "TerminalApiError"
Cohesion: 0.07
Nodes (33): Walk the data directory tree, read/parse JSON result files,     filter/sort into, ResultScanner, Path, Unit tests for ResultScanner., Legacy fatal results must not make the run list endpoint fail., Helper to write a result JSON file., Files not in YYYY/MM/DD/SYMBOL/ pattern are skipped., When JSON has a 'symbol' field, it overrides the path-derived symbol. (+25 more)

### Community 26 - "test_terminal_data_provider.py"
Cohesion: 0.11
Nodes (11): Immutable state for risk management policy evaluation.      Attributes:, Final risk percentage after grade multiplier is applied., Whether the estimated reward-to-risk meets the minimum threshold., RiskPolicyState, Risk information is output from RiskPolicyState., TestRiskOutput, RiskPolicyState.risk_reward_ok computation., R/R of 0.0 is rejected by the model's gt=0 constraint. (+3 more)

### Community 27 - "TestGetCandlesBrokerNow"
Cohesion: 0.05
Nodes (39): InvalidTradeDirectionError, Trade direction string does not map to a valid TradeDirection., BiasLevel, Structural bias levels., CostLimitExceeded, Exception, Raised when per-symbol LLM cost exceeds the configured limit., AgentState (+31 more)

### Community 28 - "TestGetPositions"
Cohesion: 0.18
Nodes (16): _make_decision(), _make_policy(), _make_review(), _make_risk_policy(), _make_setup(), ReviewStatus, Integration tests for the full pipeline: enforcement gate + output assembler.  T, Create a RiskPolicyState with sensible defaults. (+8 more)

### Community 29 - "._run_async"
Cohesion: 0.06
Nodes (32): EnvSettingsSource, _CommaDelimitedEnvSource, Any, BaseSettings, Path, Server-specific settings using Pydantic BaseSettings., Env source that parses comma-separated values for list fields.      pydantic-set, Split comma-separated env values for known list fields. (+24 more)

### Community 30 - "TestGetPendingOrders"
Cohesion: 0.10
Nodes (3): TestDeciderPrompt, TestReviewerPrompt, TestSynthesizerPrompt

### Community 31 - "TestGetSymbolPrice"
Cohesion: 0.29
Nodes (6): calculate_score(), _directional_votes(), Any, clamp(), _directional_votes applies the structural bias bonus only in RANGE., TestDirectionalVotesStructuralBias

### Community 32 - "setup_logging"
Cohesion: 0.08
Nodes (16): build_risk_policy(), Create a :class:`RiskPolicyState` from a setup grade and risk config.      The f, Tests for deterministic risk policy creation (Section 16.3).  Tests the build_ri, build_risk_policy computed fields work end-to-end., Missing R/R leads to risk_reward_ok=False even if minimum is technically met., Input validation for build_risk_policy., build_risk_policy() creates correct RiskPolicyState for each grade., RiskPolicyState model validates estimated_reward_risk > 0 via gt=0 constraint. (+8 more)

### Community 33 - "MarketContextSummary"
Cohesion: 0.16
Nodes (10): ForexFactoryCalendar, Any, Convert raw time text to ISO timestamp (best-effort).          ForexFactory time, Map raw impact text to standard impact level., Economic calendar provider via ForexFactory scraping., Initialize calendar provider.          Args:             cache_hours: Hours to c, Fetch upcoming economic calendar events.          Returns:             List of e, Check if cache is still valid. (+2 more)

### Community 34 - "setup_logging"
Cohesion: 0.23
Nodes (6): calculate_risk_reward(), Calculate the reward-to-risk ratio directionally.      For BULLISH: risk = entry, When validate_geometry returns False, R/R is None., R/R cannot be calculated when risk is zero., calculate_risk_reward computes directional R/R ratio., TestCalculateRiskReward

### Community 35 - "DecisionOutput"
Cohesion: 0.13
Nodes (9): useRun(), hasCompleteDeterministicSetup(), fetchRunResult(), completeResult, FullResult, deterministicPlanComplete, { result, loading, error }, route (+1 more)

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
Cohesion: 0.05
Nodes (24): ModelIdentityResolutionStatus, Independence level of the reviewer., Status of model identity resolution., ReviewerIndependenceLevel, Tests for model identity resolution and execution mode validation (Section 16.7), Safe resolution: provide a function to resolve execution mode., Consistency checks between decision and engine models., DecisionAction should be importable from both engine models and decision models. (+16 more)

### Community 40 - "graph.py"
Cohesion: 0.17
Nodes (11): vite.config.ts, compilerOptions, allowImportingTsExtensions, composite, module, moduleResolution, skipLibCheck, strict (+3 more)

### Community 41 - "_canonical_structure_analysis"
Cohesion: 0.33
Nodes (6): RED-first tests for the canonical current-price selection helper (TASK-6).  Thes, Lazy-import the not-yet-existing helper so collection succeeds.      Raises ``Im, Build a single per-timeframe engine-output dict for the selector., _select_canonical_current_price(), TestSelectCanonicalCurrentPrice, _tf()

### Community 42 - "AgentState"
Cohesion: 0.11
Nodes (13): CaptureFixture, Tests for main.py entry point — Issue #13 error duplication., Duplicate error-printing blocks in main.py (Issue #13).      The first block (li, Tests that _create_agents wires temperature correctly to both LLM clients., Primary client gets openai_temperature as default_temperature., Reviewer client gets reviewer_temperature, independent of primary., Changing reviewer temperature does NOT affect primary client., main.py must not log 'Total LLM cost' — that's graph.run()'s job. (+5 more)

### Community 44 - "test_analyze_structure_fresh_saves_mtf_cache"
Cohesion: 0.11
Nodes (11): integration_client(), integration_data(), Path, Integration tests with real file I/O., Create a temporary data directory with fixture JSON files., Create app pointing at the mock data directory., Integration tests for GET /api/runs with real file I/O., Integration tests for GET /api/runs/{symbol}/{year}/{month}/{day}/{file}. (+3 more)

### Community 45 - "TestSettingsDescriptions"
Cohesion: 0.12
Nodes (15): chartOption, props, biasArrow, biasColor, emit, props, AdvisoryLevels, Decision (+7 more)

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
Cohesion: 0.30
Nodes (8): useRuns(), buildRequestURL(), capString(), extractErrorDetail(), formatApiError(), looksLikeHTML(), MinimalRequestConfig, safeStringify()

### Community 50 - "main.py"
Cohesion: 0.05
Nodes (17): client(), Route-level tests with mocked scanner/runner., Tests for GET /api/runs/{symbol}/{year}/{month}/{day}/{file}., Tests for POST /api/run., Symbols must be 1-20 alphanumeric characters., CORS header verification tests., Issue an OPTIONS preflight request with standard CORS headers., OPTIONS preflight must return restricted allow-methods. (+9 more)

### Community 54 - "main.py"
Cohesion: 0.05
Nodes (33): Retry reading result files with backoff.          After a subprocess completes t, Return the subset of *symbols* that have no run in the scanner., Walk the data directory via ResultScanner and return the         most recent res, Spawn Python subprocess to run analysis, enforce timeout,     capture stderr, an, Run analysis for the given symbols.          Spawns: python main.py [--model <m>, Spawn the Python process and wait for completion.          On timeout the proces, RunService, _make_run_summary() (+25 more)

### Community 55 - "test_result_pipeline_writes_json"
Cohesion: 0.09
Nodes (14): _has_high_impact_calendar_event(), Any, Deterministic early execution routing.          When the execution policy status, Validate the decision before it reaches the reviewer.          Ensures the decis, Run the deterministic enforcement gate.          The gate verifies that every ex, Run the trading graph for a symbol.          Args:             symbol: Trading s, Check if any calendar event has a high impact level., Build the LangGraph StateGraph with the multi-timeframe pipeline. (+6 more)

### Community 56 - "TestSynthesizeContextCanonicalPrice"
Cohesion: 0.08
Nodes (36): _build_blockers(), evaluate_execution_policy(), PolicySettings, Deterministic execution policy evaluation for the multi-timeframe pipeline.  Thi, Evaluate execution policy and return an :class:`ExecutionPolicyState`.      Cons, Configuration for execution policy evaluation.      Attributes:         countert, Evaluate all blocker conditions and return the active blockers.      This is an, ExecutionMode (+28 more)

### Community 57 - "TestOhlcCachePath"
Cohesion: 0.11
Nodes (16): AnalysisResult, OHLCBar, OHLCData, BaseModel, Single OHLC bar for chart rendering., OHLC data keyed by timeframe., Top-level pipeline output serialized to JSON for the web viewer.      Fields are, Tests for output result models. (+8 more)

### Community 58 - "test_h4_candle_period_at_boundary"
Cohesion: 0.17
Nodes (8): make_raw_response(), Build a mock provider response with controlled usage fields.      The returned o, Tests for usage.py — LLMUsage, safe_non_negative_int, and parse_usage.  No exter, Primary field names: input_tokens / output_tokens., cached_input_tokens > input_tokens → clamped to input, uncached = 0., Fallback field names: prompt_tokens / completion_tokens., TestParseUsageChatCompletions, TestParseUsageResponsesApi

### Community 59 - "AgentState"
Cohesion: 0.23
Nodes (4): _determine_entry_type(), Determine the entry type based on price relationship.      Args:         entry_p, _determine_entry_type classifies entry based on price relationship., TestDetermineEntryType

### Community 60 - "test_analyze_structure_uses_broker_time_not_utc"
Cohesion: 0.27
Nodes (4): Validate that geometry is correct for the trade direction.      For BULLISH: ent, validate_geometry(), validate_geometry checks entry/stop/target ordering by direction., TestValidateGeometry

### Community 76 - "DecisionOutput"
Cohesion: 0.57
Nodes (6): _canonicalize(), _event_type(), Any, _quality(), scan_events(), _scope()

### Community 80 - "test_cache_path_d1_uses_folder_date_not_broker_now"
Cohesion: 0.10
Nodes (17): MarketContextSummary, Summary of market context from synthesizer agent., _make_mock_client(), Tests for prompt usage in agents., SynthesizerAgent.synthesize must accept current_price/current_price_time kwargs., User prompt must render current_price and current_price_time values., When no price is supplied, the current-price line must state None., Build a mock ``LLMClientProtocol`` that returns a valid usage tuple. (+9 more)

### Community 81 - ".write"
Cohesion: 0.13
Nodes (16): _get_settings(), load_ohlc_cache(), ohlc_cache_path(), datetime, OHLCBar, Compute OHLC cache file path, parallel to analysis cache.      Cache path conven, Save OHLC bars to cache, same directory structure as analysis cache.      Args:, Load cached OHLC bars from disk if available.      Args:         timeframe: "D1" (+8 more)

### Community 82 - "test_should_run_d1_after_close_with_cache"
Cohesion: 0.33
Nodes (6): Development environment (Docker), Quick commands (run inside container), Running from Docker (host → container), Setup, Starting the container, Stopping

### Community 84 - "setup_logging"
Cohesion: 0.06
Nodes (25): MonkeyPatch, Tests for the new terminal_server_url and terminal_api_key Settings fields., Settings().terminal_server_url returns the default MCP URL., Settings().terminal_api_key returns empty string by default., TRADING_TERMINAL_API_KEY env var overrides the default., TRADING_TERMINAL_SERVER_URL env var overrides the default., Tests for the primary LLM instructor_mode and timeout Settings fields.      Thes, openai_instructor_mode defaults to 'json_mode'. (+17 more)

### Community 85 - "test_should_run_h1_different_period"
Cohesion: 0.13
Nodes (26): _cache_path(), _candle_period(), get_cache_date(), _get_settings(), load_cached_analysis(), Any, datetime, Return the cache date for the given timeframes.      Returns a datetime whose da (+18 more)

### Community 86 - "TestAgentApiKey"
Cohesion: 0.19
Nodes (19): AdvisoryLevels, FinalOutputAssembler, Final decision output assembler.  This module implements :class:`FinalOutputAsse, Assembles a single :class:`AnalysisResult` from all pipeline states.      The as, _calendar_blocker(), _make_decision(), _make_enforcement(), _make_policy() (+11 more)

### Community 87 - "test_result_pipeline_writes_json"
Cohesion: 0.08
Nodes (20): AnthropicModelIdentityResolver, ModelIdentityResolver, OpenAIModelIdentityResolver, Protocol, StrEnum, LLM model configuration and provider-aware identity resolution.  This module def, Protocol for provider-specific model identity resolvers.      Implementations mu, Resolver for OpenAI model identifiers.      Recognises patterns like ``gpt-4o-20 (+12 more)

### Community 88 - "send_trade_notification"
Cohesion: 0.07
Nodes (22): extract_trade_levels(), Any, Telegram notification sender — best-effort, never blocks the pipeline., Trade levels for Telegram notification., Extract trade levels from a pipeline result dict.      Reads from ``sl_tp_overla, Replace the bot token in a Telegram API URL with ``***``., Send a compact trade notification to Telegram.      Best-effort: logs warning on, _sanitize_url() (+14 more)

### Community 91 - "test_result_pipeline_writes_json"
Cohesion: 0.12
Nodes (15): FastAPI application entry point — port of the TypeScript Express server., BaseModel, Server-specific Pydantic models., Request body for POST /api/run., Summary of a single analysis run, matching Node.js RunSummary shape., RunRequest, RunSummary, RunService — port of the TypeScript runner service.  Spawns the Python analyzer (+7 more)

### Community 92 - "test_runner.py"
Cohesion: 0.14
Nodes (12): BaseHTTPMiddleware, FastAPI, Request, RequestResponseEndpoint, Response, create_app(), Create and configure the FastAPI application., AuthMiddleware (+4 more)

### Community 93 - "test_should_run_h1_different_period"
Cohesion: 0.25
Nodes (7): _format_field(), _format_field_int(), _print_symbol_summary(), Safely extract an attribute or dict key from an unknown object.      Handles bot, Safely extract an integer attribute or dict key., Print a compact analysis summary for one symbol to stdout., Compatibility field — canonical source is ``status``.

### Community 94 - "test_load_returns_none_when_missing"
Cohesion: 0.29
Nodes (4): _check_path_a_confirmed_retest(), Path A: CHoCH is confirmed by a retest of the broken level.      A confirmed ret, Path A: CHoCH confirmed by a retest of the broken level., TestCheckPathAConfirmedRetest

### Community 95 - "test_save_h1_creates_hour_suffixed_file"
Cohesion: 0.22
Nodes (9): Environment Configuration, Installation, License, Native Setup, Overview, Prerequisites, Project Structure, Services (+1 more)

### Community 96 - "test_save_h4_creates_hour_suffixed_file"
Cohesion: 0.67
Nodes (5): build_confluence(), build_timeframe_context(), _direction_from_bias(), Any, _require_parent()

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
Cohesion: 0.31
Nodes (3): _direction_matches(), Return ``True`` when the trigger direction matches the preferred direction., TestDirectionMatches

### Community 103 - "test_should_run_h1_without_cache"
Cohesion: 0.31
Nodes (3): Map a raw event-type string to the corresponding TriggerType enum.      Returns, _resolve_trigger_type(), TestResolveTriggerType

### Community 105 - "create_app"
Cohesion: 0.08
Nodes (19): create_llm_client(), LLMCommunicationClient, OpenAIProviderAdapter, LLM client protocol, provider adapters, and factory for structured LLM calls.  T, Raised when an unsupported LLM provider is requested., OpenAI provider adapter implementing ``LLMClientProtocol``.      Wraps an ``inst, The model identifier., Factory: create the right provider adapter for the given *provider*.      Args: (+11 more)

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
Cohesion: 0.15
Nodes (15): Writes analysis results to JSON files in the data/ directory tree., ResultWriter, _make_analysis_result(), Path, SLTPOverlay, Tests for ResultWriter., When there are errors but no fatal_error, status should be 'partial'., OHLC bars appear in the output JSON under 'ohlc'. (+7 more)

### Community 112 - "Usage"
Cohesion: 0.40
Nodes (5): Analyzer CLI, API Server, Programmatic Usage, UI Dashboard, Usage

### Community 113 - "Code Review Analysis"
Cohesion: 0.40
Nodes (5): Architecture Diagram, External Dependencies and I/O Boundaries, Project Facts and Conventions, Test Coverage — Analyzer, Testing

### Community 114 - "TestFatalError"
Cohesion: 0.16
Nodes (5): Review verdict from reviewer agent.      The ``approved`` property derives from, ReviewVerdict, approved must appear in model_dump() via @computed_field., TestReviewVerdict, mock_reviewer()

### Community 115 - "Docker"
Cohesion: 0.25
Nodes (8): Development, Docker, First-time setup, Images, Migration from root-based setup, Prerequisites, Production, Running commands

### Community 116 - "TestGetRunIntegration"
Cohesion: 0.33
Nodes (5): emit, localDay, localMonth, localYear, props

### Community 117 - "Architecture"
Cohesion: 0.26
Nodes (4): parse_usage(), Extract an ``LLMUsage`` from a provider response.      Handles:     * ``None`` r, TestParseUsageDict, TestParseUsageNoneOrMissing

### Community 118 - "test_cache_path_mtf_uses_d1_date"
Cohesion: 0.08
Nodes (111): Entry plan calculation for the multi-timeframe pipeline.  This module implements, Deterministic setup grading for the multi-timeframe pipeline.  This module imple, BlockerSeverity, DecisionAction, EnforcementViolationCode, EntryType, ExecutionBlockerCode, ExecutionBlockerType (+103 more)

### Community 119 - "TestParseUsageChatCompletions"
Cohesion: 0.31
Nodes (10): _extract_int(), _extract_total_tokens(), _field_exists(), _get_field(), Any, LLM usage tracking — parse provider responses and extract token counts.  This mo, Return ``True`` if the nested attribute/dict path exists.      Works with object, Return the value at a nested attribute/dict path, or ``None``. (+2 more)

### Community 120 - ".get_run"
Cohesion: 0.50
Nodes (4): _canonical_structure_analysis(), Build a structure_analysis fixture whose H1 timeframe has the     most-recent cl, get_broker_time() should be called once in _analyze_structure and     reused in, test_get_broker_time_called_once_per_run()

### Community 122 - "test_d1_candle_period_after_close"
Cohesion: 0.20
Nodes (5): Tests for CHoCH/BOS trigger classification (Section 16.5).  Tests the triggers.p, None trigger event handling., When multiple confirmation events are provided, any one path suffices., TestClassifyTriggerMultiplePaths, TestClassifyTriggerNull

### Community 124 - "test_h4_candle_period_at_boundary"
Cohesion: 0.12
Nodes (11): GenericAliasModelIdentityResolver, Fallback resolver that treats the entire model string as the family.      Used w, Resolve a model string to its provider-aware identity.      Iterates through reg, resolve_model_identity(), GenericAliasModelIdentityResolver — always supports, resolves as fallback., resolve_model_identity() orchestrates resolution through registered resolvers., Provider hint directs to the correct resolver., GENERIC provider hint bypasses provider-specific resolvers. (+3 more)

### Community 125 - "testget_cache_date_d1_before_close"
Cohesion: 0.25
Nodes (7): Reset the _settings sentinel in candle_cache before each test.      Tests use mo, Reset the _settings sentinel in synthesizer_cache before each test.      Mirrors, reset_candle_cache_settings(), reset_synthesizer_cache_settings(), sample_decision(), sample_market_context(), sample_review()

### Community 126 - "test_h1_candle_period_at_boundary"
Cohesion: 0.07
Nodes (21): The provider this adapter handles., ProviderKind, Return ``True`` if this resolver can handle *model*., Resolve *model* into an :class:`LLMModelIdentity`., Supported LLM provider identifiers., LLMProviderAdapter, LLMProviderAdapterFactory, Any (+13 more)

### Community 127 - "test_should_run_d1_after_close_without_cache"
Cohesion: 0.33
Nodes (4): _check_path_c_sweep_and_reclaim(), Path C: CHoCH is confirmed by a sweep-and-reclaim pattern.      A sweep-and-recl, Path C: CHoCH confirmed by a sweep-and-reclaim pattern., TestCheckPathCSweepAndReclaim

### Community 128 - "usage.py"
Cohesion: 0.22
Nodes (8): _calculate_entry_plan_inner(), _extract_entry_prices(), Any, Extract and normalize entry price data from setup context.      Args:         se, Inner implementation that may raise InvalidTradeDirectionError., Tests for entry plan calculation and geometry validation (Section 16.4).  Tests, _extract_entry_prices normalizes entry price data., TestExtractEntryPrices

### Community 129 - "test_should_run_d1_after_close_with_cache"
Cohesion: 0.29
Nodes (5): Any, T, The underlying sync instructor-patched OpenAI client., Send messages to the LLM and return a structured Pydantic model.          Runs t, Synchronous variant of :meth:`generate_structured`.          Returns ``(response

### Community 130 - "_is_choch"
Cohesion: 0.43
Nodes (3): _is_choch(), Return ``True`` when the trigger is a Change-of-Character event., TestIsChoch

### Community 131 - "TestReviewerIndependenceLevel"
Cohesion: 0.10
Nodes (13): OpenAIProviderAdapter, OpenAI provider adapter — instructor-based structured output.  Wraps the ``instr, The raw model identifier., Optional reasoning effort level., OpenAI provider adapter using ``instructor`` for structured output.      Conform, LLMModelConfig, Immutable configuration for an LLM endpoint.      Attributes:         model: Mod, Edge cases for LLM configuration. (+5 more)

### Community 132 - "TestCostTrackerWiring"
Cohesion: 0.15
Nodes (8): Resolved identity for the configured model., Return the resolved identity information about the configured LLM., Return identity information about the configured LLM., LLMModelIdentity, Human-readable model identity string for logging., Immutable, provider-aware identity for a resolved LLM model.      This is the ca, LLMModelIdentity dataclass and display_name., TestLLMModelIdentity

### Community 133 - ".invalidate_cache"
Cohesion: 0.17
Nodes (7): Tests for the openai_temperature Settings field.      These tests verify that th, openai_temperature defaults to 0.0., TRADING_OPENAI_TEMPERATURE env var overrides the default., openai_temperature = 0.0 is valid (lower bound)., openai_temperature = 2.0 is valid (upper bound)., openai_temperature = 1.0 is valid (mid-range)., TestOpenAITemperatureSettings

### Community 134 - "reload_settings"
Cohesion: 0.13
Nodes (23): _cache_path(), _get_cache_date(), _get_settings(), load_cached_synthesis(), Any, datetime, Path, File-based cache for SynthesizerAgent output, keyed by (symbol, day, H1-closing- (+15 more)

### Community 136 - ".test_empty_pricing_table"
Cohesion: 0.18
Nodes (8): Compute the project root from the test file location.          Mirror the same t, Default ``analysis_cache_dir="data"`` resolves to ``<project_root>/data``., A relative path resolves against the project root, not CWD., An absolute path is returned as-is., Setting ``TRADING_ANALYSIS_CACHE_DIR`` to an absolute value must         be retu, Analyzer and server must resolve the same default to the same path., Tests for the ``resolved_analysis_cache_dir`` property.      Both the analyzer a, TestResolvedAnalysisCacheDir

### Community 138 - ".test_cache_disabled_by_env"
Cohesion: 0.11
Nodes (13): _dict_to_sns(), Recursively convert a dict to a SimpleNamespace., input_tokens_details = None must not crash., output_tokens_details = None must not crash., When primary field is 0 and fallback is non-zero, primary wins., All token fields normalise negative values to 0., Booleans in usage fields are normalised to 0., Provider returned total_tokens=0 → keep 0, do not derive. (+5 more)

### Community 139 - "TestArgparseMultiSymbol"
Cohesion: 0.17
Nodes (7): Tests for the new synthesizer_cache_enabled Settings field.      RED phase: thes, synthesizer_cache_enabled defaults to True when no env var is set., TRADING_SYNTHESIZER_CACHE_ENABLED=true yields True., TRADING_SYNTHESIZER_CACHE_ENABLED=false yields False., TRADING_SYNTHESIZER_CACHE_ENABLED=0 yields False (bool coercion)., Invalid TRADING_SYNTHESIZER_CACHE_ENABLED value either raises or falls back to d, TestSynthesizerCacheEnabled

### Community 140 - "ResultWriterContractError"
Cohesion: 0.25
Nodes (8): Force a fresh Settings() on the next _get_settings() call., reload_settings(), reload_settings causes _get_settings to return a different object., test_reload_settings_creates_new_instance(), Fresh-fetch path must also save the MTF cache file., H1 analysis must now be saved to cache like D1/H4., test_analyze_structure_fresh_saves_mtf_cache(), test_analyze_structure_saves_h1_cache()

### Community 141 - "test_h1_candle_period"
Cohesion: 0.07
Nodes (39): DeciderAgent, LLM agents for the trading pipeline.  Each agent owns a slice of the analysis pi, Makes trading decisions based on market context., Reviews trading decisions and provides feedback., Synthesizes market context from structure analysis and calendar., ReviewerAgent, SynthesizerAgent, LLMClientProtocol (+31 more)

### Community 143 - "TestDetermineD1Directional"
Cohesion: 0.31
Nodes (3): _determine_d1_directional(), Determine if D1 shows clear directional bias.      Args:         d1_bias: D1 bia, TestDetermineD1Directional

### Community 144 - "test_grading.py"
Cohesion: 0.11
Nodes (11): ExecutionMode, StrEnum, Deterministic enforcement gate for the trading pipeline.  This module implements, The removed reviewer prefix is not accepted as a compatibility alias., Tests for the new openai_reasoning_effort Settings field.      These tests will, openai_reasoning_effort defaults to empty string (not set)., TRADING_OPENAI_REASONING_EFFORT env var overrides the default., Tests for reviewer-specific environment variable names. (+3 more)

### Community 146 - "_mock_analysis_result"
Cohesion: 0.08
Nodes (17): Route after early execution routing.          Returns:             - ``"determin, Route after the review node.          - ``"continue_enforcement"`` when review i, LangGraph orchestrator for trading analysis with multi-timeframe pipeline., TradingGraph, When only 2 of 3 TFs are cached, must fetch all fresh., If get_broker_time() fails, _analyze_structure should set fatal_error., snapshot_builder.build must be called with broker_time., Missing 'timeframes' key in structure analysis → INVALID_STRUCTURE_SCHEMA. (+9 more)

### Community 147 - "TestDetermineGeometryStatus"
Cohesion: 0.36
Nodes (3): _determine_geometry_status(), Determine geometry status based on entry plan validity.      Args:         h1_se, TestDetermineGeometryStatus

### Community 148 - "TestDetermineH1ChochBased"
Cohesion: 0.36
Nodes (3): _determine_h1_choch_based(), Determine if H1 trigger is CHoCH-based.      Args:         h1_trigger_type: H1 t, TestDetermineH1ChochBased

### Community 149 - "TestDetermineH1TriggerConfirmed"
Cohesion: 0.27
Nodes (4): _determine_h1_trigger_confirmed(), Determine if H1 trigger is confirmed.      BOS triggers are considered confirmed, Tests for deterministic setup grading (Section 16.1).  Tests the grade_setup() f, TestDetermineH1TriggerConfirmed

### Community 150 - "TestDetermineH4Aligned"
Cohesion: 0.36
Nodes (3): _determine_h4_aligned(), Determine if H4 is aligned with D1.      Args:         h4_alignment_status: H4 a, TestDetermineH4Aligned

### Community 151 - "derive_allowed_actions"
Cohesion: 0.33
Nodes (3): _determine_trade_direction(), Determine trade direction from D1 bias and H4 preferred direction.      Args:, TestDetermineTradeDirection

### Community 152 - "ExecutionStatus"
Cohesion: 0.12
Nodes (14): derive_execution_status(), Derive the execution status from a set of blockers.      Priority order (highest, _blocker(), Tests for enforcement logic and models (Section 16.6).  Tests the enforcement-re, REVIEW lowest priority — enforcement blockers take precedence., Tests for enforcement reviewer logic patterns., Deterministic violations (e.g., RISK_REWARD with INVALIDATES_GRADE)         shou, A review that is not APPROVED but has no deterministic violations         produc (+6 more)

### Community 153 - "TestSynthesizeContextCanonicalPrice"
Cohesion: 0.36
Nodes (10): dayFrom(), monthFrom(), padDay(), padMonth(), preferredOrFirst(), uniqueDays(), uniqueMonths(), uniqueYears() (+2 more)

### Community 154 - "Issue tracker: GitHub"
Cohesion: 0.29
Nodes (6): Conventions, Issue tracker: GitHub, Pull requests as a triage surface, Wayfinding operations, When a skill says "fetch the relevant ticket", When a skill says "publish to the issue tracker"

### Community 155 - "Domain Docs"
Cohesion: 0.33
Nodes (5): Before exploring, read these, Domain Docs, File structure, Flag ADR conflicts, Use the glossary's vocabulary

### Community 156 - "Agent skills"
Cohesion: 0.50
Nodes (4): Agent skills, Domain docs, Issue tracker, Triage labels

### Community 157 - "testget_cache_date_h4_returns_closing_hour"
Cohesion: 0.33
Nodes (6): api, createApiClient(), defaultBaseURL(), fetchRuns(), resolveApiBaseURL(), RunRequest

### Community 158 - "test_should_run_h4_with_cache"
Cohesion: 0.11
Nodes (15): _directional_structure_analysis(), _make_tracking_side_effect(), With max_review_attempts=2, decider.decide must be called exactly 3 times     (1, With max_review_attempts=2, feedback must be forwarded to decider.decide     on, The first call to decider.decide must have feedback=None.      This may already, Create a side effect that records an LLM call on the shared CostTracker.      Th, Run TradingGraph with mocked agents that have a shared CostTracker,         asse, Verify that a CostTracker instance can be shared across all 3 agents         and (+7 more)

### Community 159 - "test_d1_candle_period_after_close"
Cohesion: 0.09
Nodes (20): LLMClientError, Any, Exception, T, Synchronous variant of :meth:`generate_structured`.          Returns the respons, Raised when an LLM API call fails after all retries., Send messages to the LLM and return a structured Pydantic model.          This m, Synchronous variant of :meth:`generate_structured`.          Returns ``(response (+12 more)

### Community 161 - "test_should_run_h4_without_cache"
Cohesion: 0.12
Nodes (11): _directional_structure_analysis(), mock_decider(), mock_reviewer(), mock_synthesizer(), RED-first tests for orchestrator-level synthesizer cache integration.  Tests ver, Reset the ``_settings`` sentinel in ``synthesizer_cache`` before each test., Cache hit \u2192 the decide node must still run.          The cache should only, Return a multi-timeframe engine output that results in a CLASSIFIED     AAA-grad (+3 more)

### Community 162 - "testget_cache_date_d1_after_close"
Cohesion: 0.09
Nodes (18): DeterministicSetupState, ExecutionPolicyState, BaseModel, Immutable state representing a classified trading setup.      Captures the full, Whether this setup qualifies as a candidate for decision.          A setup is a, Whether all canonical deterministic setup prices are available., Immutable state for execution policy evaluation.      Attributes:         trade_, Derive execution status from blockers before review stage. (+10 more)

### Community 163 - "test_should_run_d1_after_close_with_cache"
Cohesion: 0.20
Nodes (8): ExecutionBlocker, Self, An execution blocker that prevents or delays trade execution.      Attributes:, Create an ExecutionPolicyState from a setup and blockers.          Extracts the, Key blocker codes are creatable and have expected properties., TestExecutionBlockerCodes, ExecutionPolicyState.create() factory method., TestExecutionPolicyStateCreate

### Community 164 - "test_h4_candle_period"
Cohesion: 0.40
Nodes (4): Consequences, Context, Decision, Default the structured output mode to `json_mode`

### Community 168 - "TestDeriveAllowedActions"
Cohesion: 0.18
Nodes (7): derive_allowed_actions(), Derive the allowed actions based on trade direction and execution status.      R, Derive allowed actions from direction and execution status., Allowed actions based on status and direction., TestDeriveAllowedActions, DeterministicSetupState holds prices, DecisionOutput holds action., LLM cannot select BUY_SETUP when deterministic says SELL_SETUP.

### Community 169 - "ResultWriterContractError"
Cohesion: 0.19
Nodes (9): Any, datetime, Exception, OHLCBar, Path, Compute data/YYYY/MM/DD/SYMBOL/result-HH.json path., Raised when ResultWriter receives an invalid or incomplete result., Write a successful or partial result JSON to disk.          Fatal pipeline failu (+1 more)

### Community 170 - "test_cache_path_h1_includes_closing_hour"
Cohesion: 0.21
Nodes (12): Path, End-to-end integration test for the result JSON pipeline., Missing deterministic inputs remain explicitly non-actionable., Fatal pipeline failures are not persisted as unusable run results., Result with no OHLC data produces empty arrays., Full pipeline simulation writes valid JSON result., Success result without analysis_result raises contract error., test_empty_ohlc_defaults() (+4 more)

### Community 172 - "test_should_run_h4_with_cache"
Cohesion: 0.25
Nodes (8): Select the canonical current price across timeframes.      The canonical current, Build a compact version of structure analysis suitable for LLM prompts.      The, Extract compact analytical fields from a single timeframe engine output.      Th, _select_canonical_current_price(), _summarize_structure_analysis(), _summarize_timeframe(), _summarize_timeframe should log a warning when nested fields     (events, levels, test_summarize_timeframe_logs_warning_on_non_dict()

### Community 173 - "TestDecisionOutput"
Cohesion: 0.14
Nodes (9): AdvisoryLevels, DecisionOutput, BaseModel, Optional LLM-proposed levels, never used for execution or chart overlays., Decision output from decider agent.      The LLM selects an action and explains, DecisionOutput does NOT contain deterministic fields like         entry_price, s, DecisionOutput has no free-form price fields., Advisory prices are explicit fields and are absent by default. (+1 more)

### Community 175 - "utils.py"
Cohesion: 0.38
Nodes (5): canonical_json(), finite_number(), parse_iso_timestamp(), Any, datetime

### Community 176 - "_mock_analysis_result"
Cohesion: 0.22
Nodes (7): _mock_analysis_result(), SLTPOverlay, Create a mock AnalysisResult for test result dicts., Result file is always written to settings.analysis_cache_dir., When result has no broker_now, main() uses datetime.now() instead., With --telegram flag, notification is sent for approved buy/sell setups., TempPathFactory

### Community 177 - "test_should_run_h1_with_cache"
Cohesion: 0.33
Nodes (4): _deterministic_order_type(), Return the canonical order type for LLM context, never an LLM value., Make trading decision., Review the decision.          If a review is already present in state (set by th

### Community 179 - "reload_settings"
Cohesion: 0.33
Nodes (4): Lazy sentinel initialisation and env-driven disable., _settings is lazy-initialised; second call returns same instance., Setting _settings = None re-reads Settings from env., TestSettingsSentinel

### Community 183 - "Domain Glossary"
Cohesion: 0.25
Nodes (7): Analysis Runs, Design Decisions, Domain Glossary, LLM Agents, LLM Temperature, Structured Output, Trade Levels

### Community 184 - "Architecture"
Cohesion: 0.40
Nodes (5): Analysis Pipeline (LangGraph State Machine), Architecture, Deployment Architecture, Design Principles, Service Architecture

### Community 191 - "TestArgparseMultiSymbol"
Cohesion: 0.08
Nodes (20): Entry, stop-loss and take-profit overlay for charts., SLTPOverlay, Tests for multi-symbol support in main.py., Test that argparse accepts multiple symbols via _build_parser., Cost limit enforcement in the pipeline (TASK-3).      These tests verify that:, _build_parser accepts multiple symbols as nargs+., _build_parser is backward-compatible with single symbol., --model option is accepted. (+12 more)

### Community 192 - "TestLogLlmCall"
Cohesion: 0.16
Nodes (9): _log_llm_call(), Any, Record an LLM call and log its cost. Returns enriched usage with costs., Tests for agent cost-logging helper extraction., _log_llm_call extracts duplicated cost-logging from agents., When usage is provided, logs cost details., When usage is all-zero (no usage data), logs zero cost., Records the call on the cost tracker when usage is provided. (+1 more)

## Knowledge Gaps
- **181 isolated node(s):** `trading-ai-agent`, `create-user.sh script`, `start-dev.sh script`, `trading-server`, `*.vue` (+176 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **34 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `DataSource` to `Evaluator`, `reload_settings`, `.invalidate_cache`, `.test_empty_pricing_table`, `TestArgparseMultiSymbol`, `test_grading.py`, `_mock_analysis_result`, `tests/decision/__init__.py`, `tests/orchestrator/__init__.py`, `TestGetCandlesBrokerNow`, `._run_async`, `testget_cache_date_d1_after_close`, `ResultWriterContractError`, `TestSynthesizeContextCanonicalPrice`, `.write`, `setup_logging`, `test_should_run_h1_different_period`, `test_cache_path_mtf`, `test_cache_path_mtf_uses_d1_date`?**
  _High betweenness centrality (0.321) - this node is a cross-community bridge._
- **Why does `create_app()` connect `test_runner.py` to `test_analyze_structure_fresh_saves_mtf_cache`, `src/data/__init__.py`, `main.py`, `main.py`, `TerminalApiError`, `test_result_pipeline_writes_json`, `._run_async`?**
  _High betweenness centrality (0.150) - this node is a cross-community bridge._
- **Why does `WebSettings` connect `._run_async` to `test_runner.py`?**
  _High betweenness centrality (0.147) - this node is a cross-community bridge._
- **Are the 109 inferred relationships involving `Settings` (e.g. with `ExecutionMode` and `DeterministicEnforcementGate`) actually correct?**
  _`Settings` has 109 INFERRED edges - model-reasoned connections that need verification._
- **Are the 103 inferred relationships involving `DecisionAction` (e.g. with `DeterministicEnforcementGate` and `AdvisoryLevels`) actually correct?**
  _`DecisionAction` has 103 INFERRED edges - model-reasoned connections that need verification._
- **Are the 77 inferred relationships involving `TradeDirection` (e.g. with `DeterministicEnforcementGate` and `TestDeriveAllowedActions`) actually correct?**
  _`TradeDirection` has 77 INFERRED edges - model-reasoned connections that need verification._
- **Are the 73 inferred relationships involving `AgentState` (e.g. with `Settings` and `InvalidTradeDirectionError`) actually correct?**
  _`AgentState` has 73 INFERRED edges - model-reasoned connections that need verification._
