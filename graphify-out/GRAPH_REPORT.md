# Graph Report - Agent  (2026-08-01)

## Corpus Check
- 157 files · ~102,115 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3217 nodes · 7395 edges · 188 communities (158 shown, 30 thin omitted)
- Extraction: 64% EXTRACTED · 36% INFERRED · 0% AMBIGUOUS · INFERRED: 2648 edges (avg confidence: 0.64)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3931a88b`
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
- testget_cache_date_d1_after_close
- test_should_run_d1_without_cache
- test_cache_path_h1_includes_closing_hour
- triage-labels.md
- test_should_run_h4_with_cache
- TestDecisionOutput
- test_should_run_d1_before_close
- TestGradeSetupSchemaValidation
- _mock_analysis_result
- test_should_run_h1_with_cache
- test_should_run_h1_different_period
- reload_settings
- test_save_h1_creates_hour_suffixed_file
- .test_cost_limit_exceeded_is_exception
- _build_parser
- Domain Glossary
- Architecture
- 0001-reviewer-configuration-names.md
- TestArgparseMultiSymbol
- TestLogLlmCall

## God Nodes (most connected - your core abstractions)
1. `Settings` - 109 edges
2. `DecisionAction` - 94 edges
3. `AgentState` - 92 edges
4. `TradingGraph` - 91 edges
5. `CostTracker` - 88 edges
6. `RiskPolicyState` - 87 edges
7. `LLMUsage` - 87 edges
8. `TradeDirection` - 85 edges
9. `SetupGrade` - 75 edges
10. `ReviewStatus` - 75 edges

## Surprising Connections (you probably didn't know these)
- `TestCorsOrigins` --uses--> `Settings`  [INFERRED]
  server/tests/test_settings.py → analyzer/config/settings.py
- `TestResolvedCacheDir` --uses--> `Settings`  [INFERRED]
  server/tests/test_settings.py → analyzer/config/settings.py
- `test_settings_has_analysis_cache_dir()` --calls--> `Settings`  [INFERRED]
  analyzer/tests/analysis/test_candle_cache.py → analyzer/config/settings.py
- `test_settings_has_d1_close_time()` --calls--> `Settings`  [INFERRED]
  analyzer/tests/analysis/test_candle_cache.py → analyzer/config/settings.py
- `test_settings_has_h4_close_interval_hours()` --calls--> `Settings`  [INFERRED]
  analyzer/tests/analysis/test_candle_cache.py → analyzer/config/settings.py

## Import Cycles
- None detected.

## Communities (188 total, 30 thin omitted)

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
Cohesion: 0.05
Nodes (51): LangGraph orchestrator for trading analysis with multi-timeframe pipeline., TradingGraph, _directional_structure_analysis(), _make_tracking_side_effect(), mock_decider(), If get_broker_time() fails, _analyze_structure should set fatal_error., get_candles must be called with broker_time param., snapshot_builder.build must be called with broker_time. (+43 more)

### Community 4 - "SnapshotBuilder"
Cohesion: 0.07
Nodes (19): Evaluator, Any, datetime, Check if an event falls within the time window from now.          Returns False, Evaluate events for symbol with timeframe-dependent window.          Args:, Evaluates calendar events for trading symbols., High-impact event outside the window should NOT block., High-impact event within the window SHOULD block. (+11 more)

### Community 5 - "Evaluator"
Cohesion: 0.04
Nodes (44): At exact H4 boundary, the period starts at that boundary., H1 period is floored to the current hour., At exact H1 boundary, period starts at that time., Before D1 close, cache date is yesterday's date (from period_start)., H4 should skip analysis when cache file exists for that period., H4 should run analysis when no cache file exists., D1 before close should always run analysis (candle not closed)., D1 after close with existing cache should skip analysis. (+36 more)

### Community 6 - "Trading AI Agent"
Cohesion: 0.07
Nodes (21): emit, allDates, dateSourceRuns, days, filteredRuns, months, router, runCountBySymbol (+13 more)

### Community 7 - "TestSynthesizerPrompt"
Cohesion: 0.08
Nodes (19): CalendarProvider, DataSource, Any, datetime, Protocol, Analyze market structure from snapshots.          Args:             snapshots: D, Fetch OHLC candles as CSV string.          Args:             symbol: Trading sym, Get latest price info for a symbol.          Args:             symbol: Trading s (+11 more)

### Community 8 - "TestCostTracking"
Cohesion: 0.06
Nodes (42): _canonical_structure_analysis(), _directional_structure_analysis(), _make_cached_summary(), mock_decider(), datetime, Path, RED-first tests for orchestrator-level synthesizer cache integration.  Tests ver, Different H1 hour on same day → cache miss (different closing hours).          C (+34 more)

### Community 9 - "ForexFactoryCalendar"
Cohesion: 0.04
Nodes (44): Reviews trading decisions and provides feedback., ReviewerAgent, CostTracker, CostTracker — tracks LLM API call costs.  Exposes a single :class:`CostTracker`, Accumulated cost across all recorded calls., Number of calls recorded., Reset accumulated cost and call count to zero., Tracks LLM API call costs using per-model token pricing.      Each instance is i (+36 more)

### Community 10 - "orchestrator/test_synthesizer_cache.py"
Cohesion: 0.25
Nodes (14): EngineError, ExternalDerivedValuesError, InsufficientDataError, ParentContextError, Any, Exception, Base class for deterministic engine errors., TimeframeMismatchError (+6 more)

### Community 11 - "Agent Instructions"
Cohesion: 0.07
Nodes (18): main(), _parse_and_configure_settings(), Parse CLI args into a configured Settings instance.      Applies CLI overrides (, Main entry point.      Parses CLI arguments, initialises the analysis pipeline,, CaptureFixture, LogCaptureFixture, With --telegram, notification is NOT sent when action is no_trade., With --telegram, notification is NOT sent when review is not approved. (+10 more)

### Community 12 - "config/__init__.py"
Cohesion: 0.05
Nodes (40): autoprefixer, axios, echarts, postcss, tailwindcss, typescript, dependencies, axios (+32 more)

### Community 13 - "trading-ai-agent"
Cohesion: 0.05
Nodes (46): EnforcementViolation, EnforcementViolationCode, FinalDecisionState, Code identifying an enforcement violation in the setup., Status of the review process., An enforcement violation detected during setup validation.      Attributes:, Immutable state representing the final decision outcome.      Attributes:, ReviewStatus (+38 more)

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
Nodes (18): grade_setup(), Any, Grade a trading setup based on multi-timeframe structural analysis.      This fu, _d1_context(), _h1_context(), _h4_context(), Any, AAA grade when all three timeframes aligned: D1 directional,     H4 aligned cont (+10 more)

### Community 20 - "tests/data/__init__.py"
Cohesion: 0.33
Nodes (3): Configure structured logging for the trading agent., setup_logging(), TestSetupLogging

### Community 21 - "tests/decision/__init__.py"
Cohesion: 0.12
Nodes (25): _create_agents(), _format_field(), _format_field_int(), _get_decision_field(), _initialize_pipeline(), _print_summary(), _print_symbol_summary(), Any (+17 more)

### Community 22 - "tests/__init__.py"
Cohesion: 0.18
Nodes (9): calculate_entry_plan(), Calculate entry plan from raw setup data.      Accepts the raw entry data from t, calculate_entry_plan integration test., When geometry is invalid, status is TEMPORARILY_UNAVAILABLE., Entry calculator accepts TradeDirection as string., Entry calculator accepts TradeDirection as enum., Invalid trade direction returns rejected state, not NEUTRAL fallback., Non-string/enum trade direction returns rejected state. (+1 more)

### Community 23 - "tests/orchestrator/__init__.py"
Cohesion: 0.09
Nodes (47): BaseSettings, Parse JSON string env var and validate prices.          Accepts only the new for, Resolve ``analysis_cache_dir`` to an absolute path.          Both the analyzer a, Trading agent configuration., Settings, DeterministicEnforcementGate, Enforces deterministic invariants before a decision is finalised.      The gate, _calendar_blocker() (+39 more)

### Community 24 - "_make_mcp_tool_result"
Cohesion: 0.09
Nodes (22): DOM, DOM.Iterable, env.d.ts, ES2022, src/**/*.ts, src/**/*.vue, compilerOptions, baseUrl (+14 more)

### Community 25 - "TerminalApiError"
Cohesion: 0.07
Nodes (33): Walk the data directory tree, read/parse JSON result files,     filter/sort into, ResultScanner, Path, Unit tests for ResultScanner., Legacy fatal results must not make the run list endpoint fail., Helper to write a result JSON file., Files not in YYYY/MM/DD/SYMBOL/ pattern are skipped., When JSON has a 'symbol' field, it overrides the path-derived symbol. (+25 more)

### Community 26 - "test_terminal_data_provider.py"
Cohesion: 0.09
Nodes (14): _build_blockers(), Evaluate all blocker conditions and return the active blockers.      This is an, Immutable state for risk management policy evaluation.      Attributes:, Final risk percentage after grade multiplier is applied., Whether the estimated reward-to-risk meets the minimum threshold., RiskPolicyState, Deterministic risk policy creation for the multi-timeframe pipeline.  This modul, Risk information is output from RiskPolicyState. (+6 more)

### Community 27 - "TestGetCandlesBrokerNow"
Cohesion: 0.15
Nodes (15): Writes analysis results to JSON files in the data/ directory tree., ResultWriter, _make_analysis_result(), Path, SLTPOverlay, Tests for ResultWriter., When there are errors but no fatal_error, status should be 'partial'., OHLC bars appear in the output JSON under 'ohlc'. (+7 more)

### Community 28 - "TestGetPositions"
Cohesion: 0.24
Nodes (14): _make_decision(), _make_policy(), _make_review(), _make_risk_policy(), _make_setup(), ReviewStatus, Integration tests for the full pipeline: enforcement gate + output assembler.  T, Create a RiskPolicyState with sensible defaults. (+6 more)

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
Nodes (15): build_risk_policy(), Create a :class:`RiskPolicyState` from a setup grade and risk config.      The f, Tests for deterministic risk policy creation (Section 16.3).  Tests the build_ri, build_risk_policy computed fields work end-to-end., Missing R/R leads to risk_reward_ok=False even if minimum is technically met., Input validation for build_risk_policy., RiskPolicyState model validates estimated_reward_risk > 0 via gt=0 constraint., build_risk_policy() creates correct RiskPolicyState for each grade. (+7 more)

### Community 33 - "MarketContextSummary"
Cohesion: 0.16
Nodes (10): ForexFactoryCalendar, Any, Convert raw time text to ISO timestamp (best-effort)., Map raw impact text to standard impact level., Economic calendar provider via ForexFactory scraping., Initialize calendar provider.          Args:             cache_hours: Hours to c, Fetch upcoming economic calendar events.          Returns:             List of e, Check if cache is still valid. (+2 more)

### Community 34 - "setup_logging"
Cohesion: 0.23
Nodes (6): calculate_risk_reward(), Calculate the reward-to-risk ratio directionally.      For BULLISH: risk = entry, When validate_geometry returns False, R/R is None., R/R cannot be calculated when risk is zero., calculate_risk_reward computes directional R/R ratio., TestCalculateRiskReward

### Community 35 - "DecisionOutput"
Cohesion: 0.14
Nodes (8): useRun(), hasCompleteDeterministicSetup(), completeResult, FullResult, deterministicPlanComplete, { result, loading, error }, route, router

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
Cohesion: 0.18
Nodes (11): chartOption, props, AdvisoryLevels, Decision, MarketContext, OHLCBar, OHLCData, Review (+3 more)

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
Cohesion: 0.06
Nodes (15): Route-level tests with mocked scanner/runner., Tests for GET /api/runs/{symbol}/{year}/{month}/{day}/{file}., Tests for POST /api/run., Symbols must be 1-20 alphanumeric characters., CORS header verification tests., Issue an OPTIONS preflight request with standard CORS headers., OPTIONS preflight must return restricted allow-methods., OPTIONS preflight must return restricted allow-headers.          The middleware (+7 more)

### Community 54 - "main.py"
Cohesion: 0.05
Nodes (33): Retry reading result files with backoff.          After a subprocess completes t, Return the subset of *symbols* that have no run in the scanner., Walk the data directory via ResultScanner and return the         most recent res, Spawn Python subprocess to run analysis, enforce timeout,     capture stderr, an, Run analysis for the given symbols.          Spawns: python main.py [--model <m>, Spawn the Python process and wait for completion.          On timeout the proces, RunService, _make_run_summary() (+25 more)

### Community 55 - "test_result_pipeline_writes_json"
Cohesion: 0.05
Nodes (38): InvalidTradeDirectionError, Structure analysis missing required 'timeframes' schema., Trade direction string does not map to a valid TradeDirection., StructureSchemaError, AgentState, _deterministic_order_type(), _has_high_impact_calendar_event(), Any (+30 more)

### Community 56 - "TestSynthesizeContextCanonicalPrice"
Cohesion: 0.11
Nodes (11): evaluate_execution_policy(), Evaluate execution policy and return an :class:`ExecutionPolicyState`.      Cons, Self, Create an ExecutionPolicyState from a setup and blockers.          Extracts the, _make_risk_policy(), _make_setup(), Calendar has highest priority among non-execution blockers., When multiple blocker types present, status uses the highest priority. (+3 more)

### Community 57 - "TestOhlcCachePath"
Cohesion: 0.19
Nodes (12): OHLCBar, OHLCData, BaseModel, Single OHLC bar for chart rendering., OHLC data keyed by timeframe., Entry, stop-loss and take-profit overlay for charts., SLTPOverlay, Tests for output result models. (+4 more)

### Community 58 - "test_h4_candle_period_at_boundary"
Cohesion: 0.16
Nodes (8): parse_usage(), Extract an ``LLMUsage`` from a provider response.      Handles:     * ``None`` r, Tests for usage.py — LLMUsage, safe_non_negative_int, and parse_usage.  No exter, All token fields normalise negative values to 0., Booleans in usage fields are normalised to 0., TestParseUsageDict, TestParseUsageInvalidValues, TestParseUsageNoneOrMissing

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
Cohesion: 0.11
Nodes (20): DeciderAgent, Makes trading decisions based on market context., Record an LLM API call and return its usage with cost filled in.          Parame, LLMUsage, Immutable record of token usage for a single LLM API call.      Token fields are, _make_mock_client(), Tests for prompt usage in agents., SynthesizerAgent.synthesize must accept current_price/current_price_time kwargs. (+12 more)

### Community 81 - ".write"
Cohesion: 0.14
Nodes (19): get_cache_date(), Return the cache date for the given timeframes.      Returns a datetime whose da, load_ohlc_cache(), OHLCBar, Save OHLC bars to cache, same directory structure as analysis cache.      Args:, Load cached OHLC bars from disk if available.      Args:         timeframe: "D1", save_ohlc_cache(), D1 file path uses folder_date from get_cache_date, not raw broker_now. (+11 more)

### Community 82 - "test_should_run_d1_after_close_with_cache"
Cohesion: 0.33
Nodes (6): Development environment (Docker), Quick commands (run inside container), Running from Docker (host → container), Setup, Starting the container, Stopping

### Community 84 - "setup_logging"
Cohesion: 0.20
Nodes (7): make_raw_response(), Build a mock provider response with controlled usage fields.      The returned o, Primary field names: input_tokens / output_tokens., cached_input_tokens > input_tokens → clamped to input, uncached = 0., Fallback field names: prompt_tokens / completion_tokens., TestParseUsageChatCompletions, TestParseUsageResponsesApi

### Community 85 - "test_should_run_h1_different_period"
Cohesion: 0.11
Nodes (28): _cache_path(), _candle_period(), _get_settings(), load_cached_analysis(), Any, datetime, Determine if analysis should run for this timeframe.      Args:         timefram, Save analysis result to disk.      Args:         timeframe: "D1", "H4", or "H1" (+20 more)

### Community 86 - "TestAgentApiKey"
Cohesion: 0.15
Nodes (29): AdvisoryLevels, EntryType, Type of entry order for a trade setup., FinalOutputAssembler, Final decision output assembler.  This module implements :class:`FinalOutputAsse, Assembles a single :class:`AnalysisResult` from all pipeline states.      The as, _calendar_blocker(), _make_decision() (+21 more)

### Community 87 - "test_result_pipeline_writes_json"
Cohesion: 0.10
Nodes (17): AnthropicModelIdentityResolver, ModelIdentityResolver, OpenAIModelIdentityResolver, ProviderKind, Protocol, LLM model configuration and provider-aware identity resolution.  This module def, Protocol for provider-specific model identity resolvers.      Implementations mu, Return ``True`` if this resolver can handle *model*. (+9 more)

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
Cohesion: 0.10
Nodes (9): StrEnum, Outcome of a model identity resolution attempt., ResolutionStatus, Tests for LLM model configuration and identity resolution (Section 16.7).  Tests, GenericAliasModelIdentityResolver — always supports, resolves as fallback., ResolutionStatus values., TestGenericAliasModelIdentityResolver, TestProviderKind (+1 more)

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
Cohesion: 0.09
Nodes (18): create_llm_client(), LLMCommunicationClient, OpenAIProviderAdapter, LLM client protocol, provider adapters, and factory for structured LLM calls.  T, Raised when an unsupported LLM provider is requested., OpenAI provider adapter implementing ``LLMClientProtocol``.      Wraps an ``inst, The model identifier., Factory: create the right provider adapter for the given *provider*.      Args: (+10 more)

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
Cohesion: 0.14
Nodes (10): ExecutionMode, StrEnum, Deterministic enforcement gate for the trading pipeline.  This module implements, _get_settings(), ohlc_cache_path(), datetime, Compute OHLC cache file path, parallel to analysis cache.      Cache path conven, Tests for OHLC bar cache. (+2 more)

### Community 112 - "Usage"
Cohesion: 0.40
Nodes (5): Analyzer CLI, API Server, Programmatic Usage, UI Dashboard, Usage

### Community 113 - "Code Review Analysis"
Cohesion: 0.40
Nodes (5): Architecture Diagram, External Dependencies and I/O Boundaries, Project Facts and Conventions, Test Coverage — Analyzer, Testing

### Community 114 - "TestFatalError"
Cohesion: 0.12
Nodes (8): Compatibility field — canonical source is ``status``., Review verdict from reviewer agent.      The ``approved`` property derives from, ReviewVerdict, approved must appear in model_dump() via @computed_field., TestReviewVerdict, mock_reviewer(), TestReviewRouting, mock_reviewer()

### Community 115 - "Docker"
Cohesion: 0.25
Nodes (8): Development, Docker, First-time setup, Images, Migration from root-based setup, Prerequisites, Production, Running commands

### Community 116 - "TestGetRunIntegration"
Cohesion: 0.33
Nodes (5): emit, localDay, localMonth, localYear, props

### Community 117 - "Architecture"
Cohesion: 0.21
Nodes (12): Path, End-to-end integration test for the result JSON pipeline., Missing deterministic inputs remain explicitly non-actionable., Fatal pipeline failures are not persisted as unusable run results., Result with no OHLC data produces empty arrays., Full pipeline simulation writes valid JSON result., Success result without analysis_result raises contract error., test_empty_ohlc_defaults() (+4 more)

### Community 118 - "test_cache_path_mtf_uses_d1_date"
Cohesion: 0.08
Nodes (99): Entry plan calculation for the multi-timeframe pipeline.  This module implements, PolicySettings, Deterministic execution policy evaluation for the multi-timeframe pipeline.  Thi, Configuration for execution policy evaluation.      Attributes:         countert, Deterministic setup grading for the multi-timeframe pipeline.  This module imple, BlockerSeverity, DecisionAction, ExecutionBlocker (+91 more)

### Community 119 - "TestParseUsageChatCompletions"
Cohesion: 0.10
Nodes (15): OpenAIProviderAdapter, Any, T, OpenAI provider adapter — instructor-based structured output.  Wraps the ``instr, The provider this adapter handles., Resolved identity for the configured model., The underlying sync instructor-patched OpenAI client., The raw model identifier. (+7 more)

### Community 120 - ".get_run"
Cohesion: 0.25
Nodes (7): _canonical_structure_analysis(), Build a structure_analysis fixture whose H1 timeframe has the     most-recent cl, _synthesize_context must compute the canonical current price from         the pe, Even when the LLM-returned summary has current_price=None, the         orchestra, get_broker_time() should be called once in _analyze_structure and     reused in, test_get_broker_time_called_once_per_run(), TestSynthesizeContextCanonicalPrice

### Community 122 - "test_d1_candle_period_after_close"
Cohesion: 0.20
Nodes (5): Tests for CHoCH/BOS trigger classification (Section 16.5).  Tests the triggers.p, None trigger event handling., When multiple confirmation events are provided, any one path suffices., TestClassifyTriggerMultiplePaths, TestClassifyTriggerNull

### Community 124 - "test_h4_candle_period_at_boundary"
Cohesion: 0.16
Nodes (9): GenericAliasModelIdentityResolver, Fallback resolver that treats the entire model string as the family.      Used w, Resolve a model string to its provider-aware identity.      Iterates through reg, resolve_model_identity(), resolve_model_identity() orchestrates resolution through registered resolvers., Provider hint directs to the correct resolver., GENERIC provider hint bypasses provider-specific resolvers., resolve_model_identity never returns None — always falls back to generic. (+1 more)

### Community 125 - "testget_cache_date_d1_before_close"
Cohesion: 0.31
Nodes (10): _extract_int(), _extract_total_tokens(), _field_exists(), _get_field(), Any, LLM usage tracking — parse provider responses and extract token counts.  This mo, Return ``True`` if the nested attribute/dict path exists.      Works with object, Return the value at a nested attribute/dict path, or ``None``. (+2 more)

### Community 126 - "test_h1_candle_period_at_boundary"
Cohesion: 0.08
Nodes (16): LLMProviderAdapter, LLMProviderAdapterFactory, Any, Protocol, LLM provider adapter — base interface and factory.  Defines the abstract adapter, Register an adapter class for a provider.          Args:             provider: P, Create an adapter instance for the given config.          Args:             conf, Return the list of providers with registered adapters. (+8 more)

### Community 127 - "test_should_run_d1_after_close_without_cache"
Cohesion: 0.33
Nodes (4): _check_path_c_sweep_and_reclaim(), Path C: CHoCH is confirmed by a sweep-and-reclaim pattern.      A sweep-and-recl, Path C: CHoCH confirmed by a sweep-and-reclaim pattern., TestCheckPathCSweepAndReclaim

### Community 128 - "usage.py"
Cohesion: 0.33
Nodes (5): _calculate_entry_plan_inner(), _extract_entry_prices(), Any, Extract and normalize entry price data from setup context.      Args:         se, Inner implementation that may raise InvalidTradeDirectionError.

### Community 129 - "test_should_run_d1_after_close_with_cache"
Cohesion: 0.14
Nodes (10): derive_allowed_actions(), Derive the allowed actions based on trade direction and execution status.      R, Derive allowed actions from direction and execution status., Tests for enforcement logic and models (Section 16.6).  Tests the enforcement-re, Allowed actions based on status and direction., Tests for enforcement reviewer logic patterns., Non-executable actions (NO_TRADE, WAIT_FOR_SETUP) pass without         needing a, TestDeriveAllowedActions (+2 more)

### Community 130 - "_is_choch"
Cohesion: 0.43
Nodes (3): _is_choch(), Return ``True`` when the trigger is a Change-of-Character event., TestIsChoch

### Community 131 - "TestReviewerIndependenceLevel"
Cohesion: 0.16
Nodes (8): LLMModelConfig, Immutable configuration for an LLM endpoint.      Attributes:         model: Mod, Edge cases for LLM configuration., When provider is None, automatic detection kicks in., Model string with whitespace is treated literally (no stripping)., LLMModelConfig dataclass construction., TestLLMConfigEdgeCases, TestLLMModelConfig

### Community 132 - "TestCostTrackerWiring"
Cohesion: 0.18
Nodes (7): Return the resolved identity information about the configured LLM., Return identity information about the configured LLM., LLMModelIdentity, Human-readable model identity string for logging., Immutable, provider-aware identity for a resolved LLM model.      This is the ca, LLMModelIdentity dataclass and display_name., TestLLMModelIdentity

### Community 133 - ".invalidate_cache"
Cohesion: 0.19
Nodes (6): AnalysisResult, Top-level pipeline output serialized to JSON for the web viewer.      Fields are, Full-featured AnalysisResult with all optional fields set., rejection_codes must survive model_dump() round-trip., TestAnalysisResult, TestRejectionCodes

### Community 134 - "reload_settings"
Cohesion: 0.20
Nodes (6): Tests for the new terminal_server_url and terminal_api_key Settings fields., Settings().terminal_server_url returns the default MCP URL., Settings().terminal_api_key returns empty string by default., TRADING_TERMINAL_API_KEY env var overrides the default., TRADING_TERMINAL_SERVER_URL env var overrides the default., TestTerminalSettings

### Community 136 - ".test_empty_pricing_table"
Cohesion: 0.18
Nodes (8): Compute the project root from the test file location.          Mirror the same t, Default ``analysis_cache_dir="data"`` resolves to ``<project_root>/data``., A relative path resolves against the project root, not CWD., An absolute path is returned as-is., Setting ``TRADING_ANALYSIS_CACHE_DIR`` to an absolute value must         be retu, Analyzer and server must resolve the same default to the same path., Tests for the ``resolved_analysis_cache_dir`` property.      Both the analyzer a, TestResolvedAnalysisCacheDir

### Community 138 - ".test_cache_disabled_by_env"
Cohesion: 0.19
Nodes (9): Any, datetime, Exception, OHLCBar, Path, Compute data/YYYY/MM/DD/SYMBOL/result-HH.json path., Raised when ResultWriter receives an invalid or incomplete result., Write a successful or partial result JSON to disk.          Fatal pipeline failu (+1 more)

### Community 139 - "TestArgparseMultiSymbol"
Cohesion: 0.14
Nodes (12): CostLimitExceeded, Exception, Raised when per-symbol LLM cost exceeds the configured limit., Tests for ``except CostLimitExceeded: raise`` in every graph node.      Without, When ``SynthesizerAgent.synthesize`` raises ``CostLimitExceeded``,         it mu, When ``DeciderAgent.decide`` raises ``CostLimitExceeded``,         it must propa, When ``ReviewerAgent.review`` raises ``CostLimitExceeded``,         it must prop, When ``DataSource.get_positions`` raises ``CostLimitExceeded``,         it must (+4 more)

### Community 140 - "ResultWriterContractError"
Cohesion: 0.17
Nodes (7): Tests for the new synthesizer_cache_enabled Settings field.      RED phase: thes, synthesizer_cache_enabled defaults to True when no env var is set., TRADING_SYNTHESIZER_CACHE_ENABLED=true yields True., TRADING_SYNTHESIZER_CACHE_ENABLED=false yields False., TRADING_SYNTHESIZER_CACHE_ENABLED=0 yields False (bool coercion)., Invalid TRADING_SYNTHESIZER_CACHE_ENABLED value either raises or falls back to d, TestSynthesizerCacheEnabled

### Community 141 - "test_h1_candle_period"
Cohesion: 0.07
Nodes (28): Synthesizes market context from structure analysis and calendar., SynthesizerAgent, _mock_client(), Tests for LLM client injection in agents.  After refactoring, agent classes acce, Agent init logging still works with injected client., SynthesizerAgent must log model info at init., DeciderAgent must log model info at init., Build a minimal mock ``LLMClientProtocol``. (+20 more)

### Community 143 - "TestDetermineD1Directional"
Cohesion: 0.31
Nodes (3): _determine_d1_directional(), Determine if D1 shows clear directional bias.      Args:         d1_bias: D1 bia, TestDetermineD1Directional

### Community 144 - "test_grading.py"
Cohesion: 0.29
Nodes (4): Tests for the new openai_reasoning_effort Settings field.      These tests will, openai_reasoning_effort defaults to empty string (not set)., TRADING_OPENAI_REASONING_EFFORT env var overrides the default., TestReasoningEffortSettings

### Community 146 - "_mock_analysis_result"
Cohesion: 0.27
Nodes (6): Any, T, Synchronous variant of :meth:`generate_structured`.          Returns the respons, Send messages to the LLM and return a structured Pydantic model.          This m, Synchronous variant of :meth:`generate_structured`.          Returns ``(response, Send messages to the LLM and return a structured Pydantic model.          Args:

### Community 147 - "TestDetermineGeometryStatus"
Cohesion: 0.27
Nodes (4): _determine_geometry_status(), Determine geometry status based on entry plan validity.      Args:         h1_se, Tests for deterministic setup grading (Section 16.1).  Tests the grade_setup() f, TestDetermineGeometryStatus

### Community 148 - "TestDetermineH1ChochBased"
Cohesion: 0.36
Nodes (3): _determine_h1_choch_based(), Determine if H1 trigger is CHoCH-based.      Args:         h1_trigger_type: H1 t, TestDetermineH1ChochBased

### Community 149 - "TestDetermineH1TriggerConfirmed"
Cohesion: 0.36
Nodes (3): _determine_h1_trigger_confirmed(), Determine if H1 trigger is confirmed.      BOS triggers are considered confirmed, TestDetermineH1TriggerConfirmed

### Community 150 - "TestDetermineH4Aligned"
Cohesion: 0.36
Nodes (3): _determine_h4_aligned(), Determine if H4 is aligned with D1.      Args:         h4_alignment_status: H4 a, TestDetermineH4Aligned

### Community 151 - "derive_allowed_actions"
Cohesion: 0.33
Nodes (3): _determine_trade_direction(), Determine trade direction from D1 bias and H4 preferred direction.      Args:, TestDetermineTradeDirection

### Community 152 - "ExecutionStatus"
Cohesion: 0.17
Nodes (9): derive_execution_status(), Derive the execution status from a set of blockers.      Priority order (highest, _blocker(), REVIEW lowest priority — enforcement blockers take precedence., Deterministic violations (e.g., RISK_REWARD with INVALIDATES_GRADE)         shou, A review that is not APPROVED but has no deterministic violations         produc, For executable actions (BUY_SETUP/SELL_SETUP), if the status is         ACTIONAB, Status derivation with priority: CALENDAR > DATA_QUALITY > POLICY > ENFORCEMENT (+1 more)

### Community 153 - "TestSynthesizeContextCanonicalPrice"
Cohesion: 0.12
Nodes (11): BiasLevel, Structural bias levels., TestMaxReviewAttempts, TestTradingGraphInit, Multiple invocations within a day — only the first miss calls the LLM., 5 sequential runs on same symbol/day → exactly 1 LLM call.          First run: c, When ``state.fatal_error`` is set, ``_synthesize_context`` short-circuits., fatal_error set \u2192 returns {} without checking cache or calling LLM. (+3 more)

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
Cohesion: 0.14
Nodes (10): _dict_to_sns(), Recursively convert a dict to a SimpleNamespace., input_tokens_details = None must not crash., output_tokens_details = None must not crash., When primary field is 0 and fallback is non-zero, primary wins., Provider returned total_tokens=0 → keep 0, do not derive., No total_tokens field → derive as input + output., total_tokens = None → derive as input + output. (+2 more)

### Community 158 - "test_should_run_h4_with_cache"
Cohesion: 0.08
Nodes (18): DeterministicSetupState, Immutable state representing a classified trading setup.      Captures the full, Whether this setup qualifies as a candidate for decision.          A setup is a, Whether all canonical deterministic setup prices are available., Evaluate all enforcement checks and produce a final decision state.          Arg, CANDIDATE_NOT_GENERATED: executable action without classified candidate., EXECUTION_NOT_ACTIONABLE: executable action while not ACTIONABLE., DIRECTION_MISMATCH: decision contradicts deterministic direction. (+10 more)

### Community 159 - "test_d1_candle_period_after_close"
Cohesion: 0.33
Nodes (4): The removed reviewer prefix is not accepted as a compatibility alias., Tests for reviewer-specific environment variable names., Reviewer settings use the concise names while provider stays compatible., TestReviewerSettings

### Community 162 - "testget_cache_date_d1_after_close"
Cohesion: 0.17
Nodes (9): MonkeyPatch, Tests for the openai_temperature Settings field.      These tests verify that th, openai_temperature defaults to 0.0., TRADING_OPENAI_TEMPERATURE env var overrides the default., openai_temperature = 0.0 is valid (lower bound)., openai_temperature = 2.0 is valid (upper bound)., openai_temperature = 1.0 is valid (mid-range)., TRADING_MODEL_PRICING JSON env var overrides the default (new format). (+1 more)

### Community 170 - "test_cache_path_h1_includes_closing_hour"
Cohesion: 0.25
Nodes (7): Reset the _settings sentinel in candle_cache before each test.      Tests use mo, Reset the _settings sentinel in synthesizer_cache before each test.      Mirrors, reset_candle_cache_settings(), reset_synthesizer_cache_settings(), sample_decision(), sample_market_context(), sample_review()

### Community 173 - "TestDecisionOutput"
Cohesion: 0.15
Nodes (6): AdvisoryLevels, BaseModel, Optional LLM-proposed levels, never used for execution or chart overlays., DecisionOutput has no free-form price fields., Advisory prices are explicit fields and are absent by default., TestDecisionOutput

### Community 175 - "TestGradeSetupSchemaValidation"
Cohesion: 0.17
Nodes (7): Tests for _grade_setup schema validation (Phase 2.2)., Missing 'timeframes' key in structure analysis → INVALID_STRUCTURE_SCHEMA., Empty 'timeframes' dict → INVALID_STRUCTURE_SCHEMA., None value for 'timeframes' → INVALID_STRUCTURE_SCHEMA., Empty structure_analysis → INVALID_STRUCTURE_SCHEMA., _grade_setup returns empty dict when fatal_error is already set., TestGradeSetupSchemaValidation

### Community 176 - "_mock_analysis_result"
Cohesion: 0.22
Nodes (7): _mock_analysis_result(), SLTPOverlay, Create a mock AnalysisResult for test result dicts., Result file is always written to settings.analysis_cache_dir., When result has no broker_now, main() uses datetime.now() instead., With --telegram flag, notification is sent for approved buy/sell setups., TempPathFactory

### Community 179 - "reload_settings"
Cohesion: 0.33
Nodes (6): Force a fresh Settings() on the next _get_settings() call., reload_settings(), Fresh-fetch path must also save the MTF cache file., H1 analysis must now be saved to cache like D1/H4., test_analyze_structure_fresh_saves_mtf_cache(), test_analyze_structure_saves_h1_cache()

### Community 182 - "_build_parser"
Cohesion: 0.67
Nodes (3): _build_parser(), Build the CLI argument parser.      Returns:         Configured ArgumentParser i, ArgumentParser

### Community 183 - "Domain Glossary"
Cohesion: 0.29
Nodes (6): Analysis Runs, Design Decisions, Domain Glossary, LLM Agents, LLM Temperature, Trade Levels

### Community 184 - "Architecture"
Cohesion: 0.40
Nodes (5): Analysis Pipeline (LangGraph State Machine), Architecture, Deployment Architecture, Design Principles, Service Architecture

### Community 191 - "TestArgparseMultiSymbol"
Cohesion: 0.07
Nodes (20): Tests for multi-symbol support in main.py., Test that argparse accepts multiple symbols via _build_parser., Cost limit enforcement in the pipeline (TASK-3).      These tests verify that:, _build_parser accepts multiple symbols as nargs+., _build_parser is backward-compatible with single symbol., Verify cost_tracker.reset() is called before each symbol.          RED: ``_run_p, --model option is accepted., Verify set_limit() is called with settings.cost_per_symbol_limit.          RED: (+12 more)

### Community 192 - "TestLogLlmCall"
Cohesion: 0.09
Nodes (15): _log_llm_call(), Any, LLM agents for the trading pipeline.  Each agent owns a slice of the analysis pi, Record an LLM call and log its cost. Returns enriched usage with costs., MarketContextSummary, Summary of market context from synthesizer agent., Tests for agent cost-logging helper extraction., _log_llm_call extracts duplicated cost-logging from agents. (+7 more)

## Knowledge Gaps
- **176 isolated node(s):** `trading-ai-agent`, `create-user.sh script`, `start-dev.sh script`, `trading-server`, `*.vue` (+171 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **30 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `tests/orchestrator/__init__.py` to `Mt5DataProvider`, `DataSource`, `AgentState`, `Evaluator`, `reload_settings`, `.test_empty_pricing_table`, `.test_cache_disabled_by_env`, `Agent Instructions`, `ResultWriterContractError`, `test_grading.py`, `tests/decision/__init__.py`, `TestGetCandlesBrokerNow`, `._run_async`, `test_should_run_h4_with_cache`, `test_d1_candle_period_after_close`, `testget_cache_date_d1_after_close`, `test_should_run_d1_after_close_with_cache`, `test_result_pipeline_writes_json`, `test_should_run_h1_different_period`, `test_cache_path_mtf`, `test_cache_path_mtf_uses_d1_date`?**
  _High betweenness centrality (0.295) - this node is a cross-community bridge._
- **Why does `create_app()` connect `test_runner.py` to `server/tests/conftest.py`, `test_analyze_structure_fresh_saves_mtf_cache`, `src/data/__init__.py`, `main.py`, `TerminalApiError`, `test_result_pipeline_writes_json`, `._run_async`?**
  _High betweenness centrality (0.149) - this node is a cross-community bridge._
- **Why does `WebSettings` connect `._run_async` to `test_runner.py`?**
  _High betweenness centrality (0.146) - this node is a cross-community bridge._
- **Are the 94 inferred relationships involving `Settings` (e.g. with `ExecutionMode` and `DeterministicEnforcementGate`) actually correct?**
  _`Settings` has 94 INFERRED edges - model-reasoned connections that need verification._
- **Are the 85 inferred relationships involving `DecisionAction` (e.g. with `DeterministicEnforcementGate` and `AdvisoryLevels`) actually correct?**
  _`DecisionAction` has 85 INFERRED edges - model-reasoned connections that need verification._
- **Are the 71 inferred relationships involving `AgentState` (e.g. with `Settings` and `InvalidTradeDirectionError`) actually correct?**
  _`AgentState` has 71 INFERRED edges - model-reasoned connections that need verification._
- **Are the 71 inferred relationships involving `TradingGraph` (e.g. with `_initialize_pipeline()` and `Settings`) actually correct?**
  _`TradingGraph` has 71 INFERRED edges - model-reasoned connections that need verification._
