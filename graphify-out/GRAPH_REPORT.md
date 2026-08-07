# Graph Report - Agent  (2026-08-07)

## Corpus Check
- 169 files · ~90,285 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2724 nodes · 5614 edges · 185 communities (150 shown, 35 thin omitted)
- Extraction: 70% EXTRACTED · 30% INFERRED · 0% AMBIGUOUS · INFERRED: 1694 edges (avg confidence: 0.67)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `95c6e479`
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
- usage.py
- TestSynthesizeContextCanonicalPrice
- Issue tracker: GitHub
- Domain Docs
- Agent skills
- testget_cache_date_h4_returns_closing_hour
- test_routes.py
- test_d1_candle_period_after_close
- adapters/__init__.py
- .run_analysis
- test_load_returns_none_when_missing
- test_save_analysis_creates_directories
- test_h4_candle_period
- test_cache_path_h4_includes_closing_hour
- .candidate_generated
- TestListRuns
- test_routes.py
- test_should_run_d1_before_close
- triage-labels.md
- test_should_run_d1_after_close_with_cache
- test_cache_path_mtf_uses_d1_date
- test_cache_path_zero_padded_hour
- test_should_run_d1_cache_in_wrong_folder
- test_d1_candle_period_before_close
- .test_missing_output_price
- test_load_returns_none_when_missing
- .test_set_limit_none_disables_enforcement
- .test_reset_zeroes_state
- Domain Glossary
- Architecture
- 0001-reviewer-configuration-names.md
- .invalidate_cache
- TestLogLlmCall

## God Nodes (most connected - your core abstractions)
1. `Settings` - 76 edges
2. `ResultScanner` - 63 edges
3. `DecisionAction` - 52 edges
4. `TradeDirection` - 52 edges
5. `RiskPolicyState` - 50 edges
6. `DeterministicValidator` - 49 edges
7. `CostTracker` - 49 edges
8. `DeterministicSetupState` - 48 edges
9. `SetupGrade` - 43 edges
10. `ExecutionPolicyState` - 43 edges

## Surprising Connections (you probably didn't know these)
- `TestCorsOrigins` --uses--> `Settings`  [INFERRED]
  server/tests/test_settings.py → analyzer/config/settings.py
- `TestResolvedCacheDir` --uses--> `Settings`  [INFERRED]
  server/tests/test_settings.py → analyzer/config/settings.py
- `sample_market_context()` --calls--> `MarketContextSummary`  [INFERRED]
  analyzer/tests/conftest.py → analyzer/src/decision/models.py
- `sample_decision()` --calls--> `DecisionOutput`  [INFERRED]
  analyzer/tests/conftest.py → analyzer/src/decision/models.py
- `ExecutionMode` --uses--> `ExecutionMode`  [INFERRED]
  analyzer/config/settings.py → analyzer/src/analysis/market_structure_engine/models.py

## Import Cycles
- None detected.

## Communities (185 total, 35 thin omitted)

### Community 0 - "TestFatalError"
Cohesion: 0.29
Nodes (12): _canonicalize(), _event_type(), Any, _quality(), _scope(), analyze_liquidity(), _build_equal_pools(), _dedupe_pools() (+4 more)

### Community 1 - "Mt5DataProvider"
Cohesion: 0.12
Nodes (19): datetime, Path, Tests for synthesizer_cache — day-based synthesizer output caching.  ``src/decis, Fresh cache directory — should_run_synthesis returns True., After save — should_run_synthesis returns False., Corrupt JSON, pydantic validation failure, disk errors., Write invalid JSON to cache file — load returns None (not crash)., Write dict missing required fields — load returns None (not crash). (+11 more)

### Community 2 - "DataSource"
Cohesion: 0.08
Nodes (21): BaseSettings, Parse JSON string env var and validate prices.          Accepts only the new for, Reject unsupported instructor_mode values at Settings-parse time.          An in, Resolve ``analysis_cache_dir`` to an absolute path.          Both the analyzer a, Trading agent configuration., Settings, test_settings_has_analysis_cache_dir(), test_settings_has_d1_close_time() (+13 more)

### Community 3 - "AgentState"
Cohesion: 0.33
Nodes (6): Force a fresh Settings() on the next _get_settings() call., reload_settings(), reload_settings causes _get_settings to return a different object., After reload_settings, _get_settings picks up new env var values., test_reload_settings_creates_new_instance(), test_reload_settings_updates_values()

### Community 4 - "SnapshotBuilder"
Cohesion: 0.07
Nodes (19): Evaluator, Any, datetime, Check if an event falls within the time window from now.          Returns False, Evaluate events for symbol with timeframe-dependent window.          Args:, Evaluates calendar events for trading symbols., High-impact event outside the window should NOT block., High-impact event within the window SHOULD block. (+11 more)

### Community 5 - "Evaluator"
Cohesion: 0.09
Nodes (63): _build_blockers(), PolicySettings, Deterministic execution policy evaluation for the multi-timeframe pipeline.  Thi, Configuration for execution policy evaluation.      Attributes:         countert, Evaluate all blocker conditions and return the active blockers.      This is an, BlockerSeverity, derive_execution_status(), DeterministicSetupState (+55 more)

### Community 6 - "Trading AI Agent"
Cohesion: 0.07
Nodes (23): emit, startRun(), allDates, dateSourceRuns, days, filteredRuns, handleRunNow(), months (+15 more)

### Community 7 - "TestSynthesizerPrompt"
Cohesion: 0.08
Nodes (19): CalendarProvider, DataSource, Any, datetime, Protocol, Analyze market structure from snapshots.          Args:             snapshots: D, Fetch OHLC candles as CSV string.          Args:             symbol: Trading sym, Get latest price info for a symbol.          Args:             symbol: Trading s (+11 more)

### Community 8 - "TestCostTracking"
Cohesion: 0.06
Nodes (32): EnvSettingsSource, _CommaDelimitedEnvSource, Any, BaseSettings, Path, Server-specific settings using Pydantic BaseSettings., Env source that parses comma-separated values for list fields.      pydantic-set, Split comma-separated env values for known list fields. (+24 more)

### Community 9 - "ForexFactoryCalendar"
Cohesion: 0.07
Nodes (21): Tests for CostTracker — tracks LLM API call costs.  CostTracker lives in ``src/d, Unknown model logs warning, preserves token fields, cost fields zero., Missing cached_input_per_million → cached_input_cost = 0.0., Missing input_per_million → input_cost = 0.0., CostTracker: tracks LLM API call costs., Zero tokens result in zero cost but call IS counted., CostTracker(pricing={}) — record_call warns and returns zero costs., Many calls accumulate total_cost correctly. (+13 more)

### Community 10 - "orchestrator/test_synthesizer_cache.py"
Cohesion: 0.12
Nodes (32): analyze_multi_timeframe(), analyze_snapshot(), _apply_structural_event_transition(), _check_same_market(), Any, EngineError, ExternalDerivedValuesError, InsufficientDataError (+24 more)

### Community 11 - "Agent Instructions"
Cohesion: 0.15
Nodes (8): _normalize_legacy_result(), Any, ResultScanner — port of the TypeScript scanner service., Get a single run's full result. Returns None if not found., Normalize legacy result JSON to current schema.      - Derive ``review.status``, Unit tests for ResultScanner., Tests for ResultScanner.get_run()., TestGetRun

### Community 12 - "config/__init__.py"
Cohesion: 0.05
Nodes (40): autoprefixer, axios, echarts, postcss, tailwindcss, typescript, dependencies, axios (+32 more)

### Community 13 - "trading-ai-agent"
Cohesion: 0.11
Nodes (13): _dict_to_sns(), Recursively convert a dict to a SimpleNamespace., input_tokens_details = None must not crash., output_tokens_details = None must not crash., When primary field is 0 and fallback is non-zero, primary wins., All token fields normalise negative values to 0., Booleans in usage fields are normalised to 0., Provider returned total_tokens=0 → keep 0, do not derive. (+5 more)

### Community 14 - "src/calendar/__init__.py"
Cohesion: 0.05
Nodes (42): H4 period containing the given time, anchored at 00:00., H1 period is floored to the current hour., At exact H1 boundary, period starts at that time., H1 period crossing midnight boundary works correctly., After D1 close, cache date is today's date (from period_start)., D1 should run analysis when no cache file exists., H4 should skip analysis when cache file exists for that period., H4 should run analysis when no cache file exists. (+34 more)

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
Cohesion: 0.22
Nodes (19): analyze_candles(), _classify_engulfing(), Any, adx(), calculate_indicators(), ema(), macd(), Any (+11 more)

### Community 19 - "tests/calendar/__init__.py"
Cohesion: 0.15
Nodes (14): grade_setup(), Any, Grade a trading setup based on multi-timeframe structural analysis.      This fu, _d1_context(), _h1_context(), _h4_context(), Any, AAA can be achieved with ALIGNED_PULLBACK as well. (+6 more)

### Community 20 - "tests/data/__init__.py"
Cohesion: 0.33
Nodes (3): Configure structured logging for the trading agent., setup_logging(), TestSetupLogging

### Community 21 - "tests/decision/__init__.py"
Cohesion: 0.12
Nodes (26): _create_agents(), _format_field(), _format_field_int(), _get_decision_field(), _initialize_pipeline(), _model_or_dict(), _print_summary(), _print_symbol_summary() (+18 more)

### Community 22 - "tests/__init__.py"
Cohesion: 0.14
Nodes (11): calculate_entry_plan(), Calculate entry plan from raw setup data.      Accepts the raw entry data from t, calculate_entry_plan integration test., When geometry is invalid, status is TEMPORARILY_UNAVAILABLE., NO_SETUP with missing prices must not be labelled INSUFFICIENT_DATA.          Th, A CLASSIFIED candidate with missing prices is genuinely INSUFFICIENT_DATA., Entry calculator accepts TradeDirection as string., Entry calculator accepts TradeDirection as enum. (+3 more)

### Community 23 - "tests/orchestrator/__init__.py"
Cohesion: 0.11
Nodes (11): evaluate_execution_policy(), Evaluate execution policy and return an :class:`ExecutionPolicyState`.      Cons, Self, Create an ExecutionPolicyState from a setup and blockers.          Extracts the, _make_risk_policy(), _make_setup(), Calendar has highest priority among non-execution blockers., When multiple blocker types present, status uses the highest priority. (+3 more)

### Community 24 - "_make_mcp_tool_result"
Cohesion: 0.09
Nodes (22): DOM, DOM.Iterable, env.d.ts, ES2022, src/**/*.ts, src/**/*.vue, compilerOptions, baseUrl (+14 more)

### Community 25 - "TerminalApiError"
Cohesion: 0.08
Nodes (30): Walk the data directory tree, read/parse JSON result files,     filter/sort into, ResultScanner, Path, Legacy fatal results must not make the run list endpoint fail., Helper to write a result JSON file., Files not in YYYY/MM/DD/SYMBOL/ pattern are skipped., When JSON has a 'symbol' field, it overrides the path-derived symbol., Tests for legacy result normalization in get_run(). (+22 more)

### Community 26 - "test_terminal_data_provider.py"
Cohesion: 0.12
Nodes (10): Immutable state for risk management policy evaluation.      Attributes:, Final risk percentage after grade multiplier is applied., Whether the estimated reward-to-risk meets the minimum threshold., RiskPolicyState, Deterministic risk policy creation for the multi-timeframe pipeline.  This modul, RiskPolicyState.risk_reward_ok computation., R/R of 0.0 is rejected by the model's gt=0 constraint., RiskPolicyState.final_risk_percentage computation. (+2 more)

### Community 27 - "TestGetCandlesBrokerNow"
Cohesion: 0.10
Nodes (11): CostLimitExceeded, Exception, CostTracker — tracks LLM API call costs.  Exposes a single :class:`CostTracker`, Raised when per-symbol LLM cost exceeds the configured limit., Record an LLM API call and return its usage with cost filled in.          Parame, CostLimitExceeded is a subclass of Exception., record_call raises CostLimitExceeded when total_cost > limit., set_limit() after calls already recorded does not retroactively raise. (+3 more)

### Community 28 - "TestGetPositions"
Cohesion: 0.12
Nodes (44): _action_value(), _blockers(), DeterministicValidator, _finite_number(), _non_negative_integer(), _parse_timestamp(), Any, datetime (+36 more)

### Community 29 - "._run_async"
Cohesion: 0.09
Nodes (24): AgentState, _has_high_impact_calendar_event(), Any, Reject missing or malformed interpretive output without retrying., Run the deterministic enforcement gate.          The gate verifies that every ex, Assemble the final AnalysisResult from all pipeline states., Run the trading graph for a symbol.          Args:             symbol: Trading s, Select the canonical current price across timeframes.      The canonical current (+16 more)

### Community 31 - "TestGetSymbolPrice"
Cohesion: 0.23
Nodes (8): calculate_score(), _directional_votes(), Any, clamp(), test_confidence_uses_required_component_weights(), test_failed_breakout_evidence_is_scored_when_confirmation_is_latest(), _directional_votes applies the structural bias bonus only in RANGE., TestDirectionalVotesStructuralBias

### Community 32 - "setup_logging"
Cohesion: 0.08
Nodes (16): build_risk_policy(), Create a :class:`RiskPolicyState` from a setup grade and risk config.      The f, Tests for deterministic risk policy creation (Section 16.3).  Tests the build_ri, build_risk_policy computed fields work end-to-end., Missing R/R leads to risk_reward_ok=False even if minimum is technically met., Input validation for build_risk_policy., build_risk_policy() creates correct RiskPolicyState for each grade., RiskPolicyState model validates estimated_reward_risk > 0 via gt=0 constraint. (+8 more)

### Community 33 - "MarketContextSummary"
Cohesion: 0.16
Nodes (10): ForexFactoryCalendar, Any, Convert raw time text to ISO timestamp (best-effort).          ForexFactory time, Map raw impact text to standard impact level., Economic calendar provider via ForexFactory scraping., Initialize calendar provider.          Args:             cache_hours: Hours to c, Fetch upcoming economic calendar events.          Returns:             List of e, Check if cache is still valid. (+2 more)

### Community 34 - "setup_logging"
Cohesion: 0.21
Nodes (7): calculate_risk_reward(), Calculate the reward-to-risk ratio directionally.      For BULLISH: risk = entry, When validate_geometry returns False, R/R is None., R/R cannot be calculated when risk is zero., calculate_risk_reward computes directional R/R ratio., TestCalculateRiskReward, test_directional_rr_uses_canonical_boundary()

### Community 35 - "DecisionOutput"
Cohesion: 0.13
Nodes (9): useRun(), hasCompleteDeterministicSetup(), fetchRunResult(), completeResult, FullResult, deterministicPlanComplete, { result, loading, error }, route (+1 more)

### Community 36 - "TestRepeatedRuns"
Cohesion: 0.17
Nodes (11): Tests for engine field rename (no _utc suffix) and engine deepcopy behavior., _ALLOWED_BAR must accept open_time, not open_time_utc., Swing dataclass must have timestamp, not timestamp_utc., Engine source_audit must use latest_closed_candle_time, not _utc., _ALLOWED_TOP_LEVEL must accept retrieved_at, not retrieved_at_utc., Engine must export scoring.latest_close, matching technical_context.close., test_engine_export_includes_latest_close(), test_engine_source_audit_no_utc() (+3 more)

### Community 37 - "_select_canonical_current_price"
Cohesion: 0.26
Nodes (7): MarketStructureEngine, Any, Concrete adapter implementing StructureAnalyzer.      Wraps the module-level ana, Analyze market structure from snapshots.          Args:             snapshots: D, Build engine request from snapshots., Delegate analysis to the engine., Validate engine output.

### Community 38 - "AgentState"
Cohesion: 0.11
Nodes (11): classify_trigger(), Classify a price-action trigger event and determine its confirmation status., CHoCH classification with all confirmation paths., CHoCH without any confirmation path → PENDING_CONFIRMATION., CHoCH + retest (Path A) → CONFIRMED., CHoCH + continuation BOS (Path B) → CONFIRMED., CHoCH + sweep-and-reclaim (Path C) → CONFIRMED., RECLAIM and RETEST trigger types. (+3 more)

### Community 40 - "graph.py"
Cohesion: 0.17
Nodes (11): vite.config.ts, compilerOptions, allowImportingTsExtensions, composite, module, moduleResolution, skipLibCheck, strict (+3 more)

### Community 41 - "_canonical_structure_analysis"
Cohesion: 0.33
Nodes (6): RED-first tests for the canonical current-price selection helper (TASK-6).  Thes, Lazy-import the not-yet-existing helper so collection succeeds.      Raises ``Im, Build a single per-timeframe engine-output dict for the selector., _select_canonical_current_price(), TestSelectCanonicalCurrentPrice, _tf()

### Community 42 - "AgentState"
Cohesion: 0.15
Nodes (7): OpenAIProviderAdapter, OpenAI provider adapter — instructor-based structured output.  Wraps the ``instr, The provider this adapter handles., Resolved identity for the configured model., The raw model identifier., Optional reasoning effort level., OpenAI provider adapter using ``instructor`` for structured output.      Conform

### Community 44 - "test_analyze_structure_fresh_saves_mtf_cache"
Cohesion: 0.11
Nodes (11): integration_client(), integration_data(), Path, Integration tests with real file I/O., Create a temporary data directory with fixture JSON files., Create app pointing at the mock data directory., Integration tests for GET /api/runs with real file I/O., Integration tests for GET /api/runs/{symbol}/{year}/{month}/{day}/{file}. (+3 more)

### Community 45 - "TestSettingsDescriptions"
Cohesion: 0.13
Nodes (14): chartOption, props, biasArrow, biasColor, emit, props, AdvisoryLevels, Decision (+6 more)

### Community 46 - "BiasLevel"
Cohesion: 0.27
Nodes (6): Type of price action trigger for a setup., TriggerType, _is_bos(), CHoCH/BOS trigger classification for the H1 timeframe.  This module implements `, Return ``True`` when the trigger is a Break-of-Structure event., TestIsBos

### Community 47 - "test_analyze_structure_passes_broker_time_to_snapshot_builder"
Cohesion: 0.20
Nodes (8): Agent Instructions, Architectural notes, Architecture, Critical invariants, Graphify first, Pre-commit hooks, Testing, Toolchain

### Community 48 - "test_analyze_structure_fetches_all_timeframes"
Cohesion: 0.31
Nodes (10): Any, TimeframeProfile, _assign_status(), _candidate_indexes(), detect_swings(), _group_local_plateaus(), _prominence(), Any (+2 more)

### Community 49 - "test_analyze_structure_full_cache_hit"
Cohesion: 0.30
Nodes (8): useRuns(), buildRequestURL(), capString(), extractErrorDetail(), formatApiError(), looksLikeHTML(), MinimalRequestConfig, safeStringify()

### Community 50 - "main.py"
Cohesion: 0.25
Nodes (8): BaseModel, Server-specific Pydantic models., Request body for POST /api/run., Summary of a single analysis run, matching Node.js RunSummary shape., RunRequest, RunSummary, Sample RunSummary for route tests., sample_summary()

### Community 54 - "main.py"
Cohesion: 0.05
Nodes (34): RunService — port of the TypeScript runner service.  Spawns the Python analyzer, Retry reading result files with backoff.          After a subprocess completes t, Return the subset of *symbols* that have no run in the scanner., Walk the data directory via ResultScanner and return the         most recent res, Spawn Python subprocess to run analysis, enforce timeout,     capture stderr, an, Run analysis for the given symbols.          Spawns: python main.py [--model <m>, Spawn the Python process and wait for completion.          On timeout the proces, RunService (+26 more)

### Community 55 - "test_result_pipeline_writes_json"
Cohesion: 0.15
Nodes (20): _cache_path(), _get_cache_date(), _get_settings(), load_cached_synthesis(), Any, datetime, Path, File-based cache for SynthesizerAgent output, keyed by (symbol, day, H1-closing- (+12 more)

### Community 56 - "TestSynthesizeContextCanonicalPrice"
Cohesion: 0.17
Nodes (9): ExecutionMode, StrEnum, _get_settings(), ohlc_cache_path(), datetime, Compute OHLC cache file path, parallel to analysis cache.      Cache path conven, Tests for OHLC bar cache., Full path follows analysis/YYYY/MM/DD/SYMBOL/ pattern. (+1 more)

### Community 57 - "TestOhlcCachePath"
Cohesion: 0.31
Nodes (3): _determine_d1_directional(), Determine if D1 shows clear directional bias.      Args:         d1_bias: D1 bia, TestDetermineD1Directional

### Community 58 - "test_h4_candle_period_at_boundary"
Cohesion: 0.36
Nodes (8): build_confluence(), build_timeframe_context(), _direction_from_bias(), Any, _require_parent(), test_h1_context_does_not_fallback_to_historical_invalidation_level(), test_reclaim_evidence_is_consumed_by_context_and_scoring(), test_unclassified_structural_break_does_not_trigger_h1_setup()

### Community 59 - "AgentState"
Cohesion: 0.23
Nodes (4): _determine_entry_type(), Determine the entry type based on price relationship.      Args:         entry_p, _determine_entry_type classifies entry based on price relationship., TestDetermineEntryType

### Community 60 - "test_analyze_structure_uses_broker_time_not_utc"
Cohesion: 0.27
Nodes (4): Validate that geometry is correct for the trade direction.      For BULLISH: ent, validate_geometry(), validate_geometry checks entry/stop/target ordering by direction., TestValidateGeometry

### Community 76 - "DecisionOutput"
Cohesion: 0.17
Nodes (10): MarketContextSummary, Summary of market context from synthesizer agent., _make_summary(), save_synthesis should NOT catch errors that aren't OSError or         pydantic V, Cache scoped by (symbol, day)., Save at 23:59 → load at 00:01 next day ⇒ miss., File path includes H1 closing hour: ``…/synthesizer-h1-13.json``., After save, next should_run for same symbol+day returns False. (+2 more)

### Community 80 - "test_cache_path_d1_uses_folder_date_not_broker_now"
Cohesion: 0.08
Nodes (44): ValidationStatus, Entry plan calculation for the multi-timeframe pipeline.  This module implements, _determine_geometry_status(), _determine_h4_aligned(), Deterministic setup grading for the multi-timeframe pipeline.  This module imple, Determine geometry status based on entry plan validity.      Args:         h1_se, Determine if H4 is aligned with D1.      Args:         h4_alignment_status: H4 a, DecisionAction (+36 more)

### Community 81 - ".write"
Cohesion: 0.14
Nodes (19): get_cache_date(), Return the cache date for the given timeframes.      Returns a datetime whose da, load_ohlc_cache(), OHLCBar, Save OHLC bars to cache, same directory structure as analysis cache.      Args:, Load cached OHLC bars from disk if available.      Args:         timeframe: "D1", save_ohlc_cache(), D1 file path uses folder_date from get_cache_date, not raw broker_now. (+11 more)

### Community 82 - "test_should_run_d1_after_close_with_cache"
Cohesion: 0.33
Nodes (6): Development environment (Docker), Quick commands (run inside container), Running from Docker (host → container), Setup, Starting the container, Stopping

### Community 84 - "setup_logging"
Cohesion: 0.13
Nodes (12): MonkeyPatch, Invalid JSON raises a validation error., Tests for the primary LLM instructor_mode and timeout Settings fields.      Thes, openai_instructor_mode defaults to 'json_mode'., json_mode' is a valid value., tool_call' is a valid value., An unsupported instructor_mode value is rejected at parse time., An empty primary instructor_mode is a misconfiguration and is rejected. (+4 more)

### Community 85 - "test_should_run_h1_different_period"
Cohesion: 0.13
Nodes (24): _cache_path(), _candle_period(), _get_settings(), load_cached_analysis(), Any, datetime, Determine if analysis should run for this timeframe.      Args:         timefram, Save analysis result to disk.      Args:         timeframe: "D1", "H4", or "H1" (+16 more)

### Community 86 - "TestAgentApiKey"
Cohesion: 0.05
Nodes (46): DeterministicValidation, BaseModel, Result of validating deterministic facts., BiasLevel, EnforcementViolation, EnforcementViolationCode, FinalDecisionState, Code identifying an enforcement violation in the setup. (+38 more)

### Community 87 - "test_result_pipeline_writes_json"
Cohesion: 0.11
Nodes (10): CostTracker, Accumulated cost across all recorded calls., Number of calls recorded., Reset accumulated cost and call count to zero., Tracks LLM API call costs using per-model token pricing.      Each instance is i, Set a per-symbol cost limit.          When *limit* is ``<= 0`` or ``None`` the l, Set the current symbol for error context.          The symbol is used by :meth:`, CostTracker() with no args uses empty pricing → zero costs. (+2 more)

### Community 88 - "send_trade_notification"
Cohesion: 0.07
Nodes (22): extract_trade_levels(), Any, Telegram notification sender — best-effort, never blocks the pipeline., Trade levels for Telegram notification., Extract trade levels from a pipeline result dict.      Reads from ``sl_tp_overla, Replace the bot token in a Telegram API URL with ``***``., Send a compact trade notification to Telegram.      Best-effort: logs warning on, _sanitize_url() (+14 more)

### Community 91 - "test_result_pipeline_writes_json"
Cohesion: 0.24
Nodes (7): LLMUsage, parse_usage(), Extract an ``LLMUsage`` from a provider response.      Handles:     * ``None`` r, Immutable record of token usage for a single LLM API call.      Token fields are, TestLLMUsageDefaults, TestParseUsageDict, TestParseUsageNoneOrMissing

### Community 92 - "test_runner.py"
Cohesion: 0.15
Nodes (11): BaseHTTPMiddleware, FastAPI, Request, RequestResponseEndpoint, Response, create_app(), FastAPI application entry point — port of the TypeScript Express server., Create and configure the FastAPI application. (+3 more)

### Community 94 - "test_load_returns_none_when_missing"
Cohesion: 0.29
Nodes (4): _check_path_a_confirmed_retest(), Path A: CHoCH is confirmed by a retest of the broken level.      A confirmed ret, Path A: CHoCH confirmed by a retest of the broken level., TestCheckPathAConfirmedRetest

### Community 95 - "test_save_h1_creates_hour_suffixed_file"
Cohesion: 0.22
Nodes (9): Environment Configuration, Installation, License, Native Setup, Overview, Prerequisites, Project Structure, Services (+1 more)

### Community 96 - "test_save_h4_creates_hour_suffixed_file"
Cohesion: 0.25
Nodes (4): Synthesizes market context from structure analysis and calendar., SynthesizerAgent, test_synthesizer_uses_injected_client_once(), test_synthesizer_prompt_treats_deterministic_facts_as_authoritative()

### Community 97 - "test_load_handles_corrupt_json"
Cohesion: 0.29
Nodes (7): Configuration, Cost Analysis, Cost Estimate (GPT-4o), Default Model Pricing, Environment Variables — Analyzer, Environment Variables — Server, Token Estimates (GPT-4o)

### Community 98 - "server/tests/conftest.py"
Cohesion: 0.10
Nodes (18): client(), client_with_auth(), mock_data_dir(), Any, Path, RunSummary, Shared fixtures for server tests., Create a temporary data directory with fixture JSON files. (+10 more)

### Community 99 - "test_cache_path_d1_no_hour_suffix"
Cohesion: 0.24
Nodes (4): Return a non-negative ``int`` or ``0`` for invalid/missing values.      Handles, safe_non_negative_int(), TestSafeNonNegativeInt, LogCaptureFixture

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
Cohesion: 0.07
Nodes (25): create_llm_client(), LLMClientProtocol, LLMCommunicationClient, OpenAIProviderAdapter, Protocol, LLM client protocol, provider adapters, and factory for structured LLM calls.  T, Raised when an unsupported LLM provider is requested., OpenAI provider adapter implementing ``LLMClientProtocol``.      Wraps an ``inst (+17 more)

### Community 107 - "TestListRunsIntegration"
Cohesion: 0.29
Nodes (5): _check_path_b_continuation_bos(), Any, Path B: CHoCH is confirmed by a continuation BOS in the same direction.      A c, Path B: CHoCH confirmed by a continuation BOS in the same direction., TestCheckPathBContinuationBos

### Community 109 - "Development"
Cohesion: 0.33
Nodes (6): Commands, Contributing, Dependencies, Development, Knowledge Graph, Pre-commit Hooks

### Community 111 - "test_cache_path_mtf"
Cohesion: 0.05
Nodes (44): AnalysisResult, OHLCBar, OHLCData, BaseModel, Single OHLC bar for chart rendering., OHLC data keyed by timeframe., Entry, stop-loss and take-profit overlay for charts., Top-level pipeline output serialized to JSON for the web viewer.      Fields are (+36 more)

### Community 112 - "Usage"
Cohesion: 0.40
Nodes (5): Analyzer CLI, API Server, Programmatic Usage, UI Dashboard, Usage

### Community 113 - "Code Review Analysis"
Cohesion: 0.40
Nodes (5): Architecture Diagram, External Dependencies and I/O Boundaries, Project Facts and Conventions, Test Coverage — Analyzer, Testing

### Community 114 - "TestFatalError"
Cohesion: 0.17
Nodes (3): Tests for POST /api/run., Symbols must be 1-20 alphanumeric characters., TestPostRun

### Community 115 - "Docker"
Cohesion: 0.25
Nodes (8): Development, Docker, First-time setup, Images, Migration from root-based setup, Prerequisites, Production, Running commands

### Community 116 - "TestGetRunIntegration"
Cohesion: 0.33
Nodes (5): emit, localDay, localMonth, localYear, props

### Community 117 - "Architecture"
Cohesion: 0.23
Nodes (7): CORS header verification tests., Issue an OPTIONS preflight request with standard CORS headers., OPTIONS preflight must return restricted allow-methods., OPTIONS preflight must return restricted allow-headers.          The middleware, OPTIONS preflight from a configured origin should echo it back., OPTIONS preflight must include allow-credentials: true., TestCORS

### Community 118 - "test_cache_path_mtf_uses_d1_date"
Cohesion: 0.36
Nodes (3): _determine_h1_choch_based(), Determine if H1 trigger is CHoCH-based.      Args:         h1_trigger_type: H1 t, TestDetermineH1ChochBased

### Community 119 - "TestParseUsageChatCompletions"
Cohesion: 0.17
Nodes (7): openai_temperature defaults to 0.0., TRADING_OPENAI_TEMPERATURE env var overrides the default., openai_temperature = 0.0 is valid (lower bound)., openai_temperature = 2.0 is valid (upper bound)., openai_temperature = 1.0 is valid (mid-range)., Tests for the openai_temperature Settings field.      These tests verify that th, TestOpenAITemperatureSettings

### Community 120 - ".get_run"
Cohesion: 0.33
Nodes (3): _determine_lifecycle_status(), Determine lifecycle status based on trigger confirmation.      Args:         h1_, TestDetermineLifecycleStatus

### Community 122 - "test_d1_candle_period_after_close"
Cohesion: 0.20
Nodes (5): Tests for CHoCH/BOS trigger classification (Section 16.5).  Tests the triggers.p, None trigger event handling., When multiple confirmation events are provided, any one path suffices., TestClassifyTriggerMultiplePaths, TestClassifyTriggerNull

### Community 124 - "test_h4_candle_period_at_boundary"
Cohesion: 0.16
Nodes (9): GenericAliasModelIdentityResolver, Fallback resolver that treats the entire model string as the family.      Used w, Resolve a model string to its provider-aware identity.      Iterates through reg, resolve_model_identity(), resolve_model_identity() orchestrates resolution through registered resolvers., Provider hint directs to the correct resolver., GENERIC provider hint bypasses provider-specific resolvers., resolve_model_identity never returns None — always falls back to generic. (+1 more)

### Community 125 - "testget_cache_date_d1_before_close"
Cohesion: 0.18
Nodes (9): _build_parser(), main(), _parse_and_configure_settings(), Build the CLI argument parser.      Returns:         Configured ArgumentParser i, Parse CLI args into a configured Settings instance.      Applies CLI overrides (, Main entry point.      Parses CLI arguments, initialises the analysis pipeline,, test_initialize_pipeline_passes_only_synthesizer_to_graph(), ArgumentParser (+1 more)

### Community 126 - "test_h1_candle_period_at_boundary"
Cohesion: 0.08
Nodes (19): ProviderKind, Return ``True`` if this resolver can handle *model*., Supported LLM provider identifiers., LLMProviderAdapter, LLMProviderAdapterFactory, Any, Protocol, LLM provider adapter — base interface and factory.  Defines the abstract adapter (+11 more)

### Community 127 - "test_should_run_d1_after_close_without_cache"
Cohesion: 0.33
Nodes (4): _check_path_c_sweep_and_reclaim(), Path C: CHoCH is confirmed by a sweep-and-reclaim pattern.      A sweep-and-recl, Path C: CHoCH confirmed by a sweep-and-reclaim pattern., TestCheckPathCSweepAndReclaim

### Community 128 - "usage.py"
Cohesion: 0.22
Nodes (8): _calculate_entry_plan_inner(), _extract_entry_prices(), Any, Extract and normalize entry price data from setup context.      Args:         se, Inner implementation that may raise InvalidTradeDirectionError., Tests for entry plan calculation and geometry validation (Section 16.4).  Tests, _extract_entry_prices normalizes entry price data., TestExtractEntryPrices

### Community 129 - "test_should_run_d1_after_close_with_cache"
Cohesion: 0.12
Nodes (13): AnthropicModelIdentityResolver, ModelIdentityResolver, OpenAIModelIdentityResolver, Protocol, LLM model configuration and provider-aware identity resolution.  This module def, Protocol for provider-specific model identity resolvers.      Implementations mu, Resolver for OpenAI model identifiers.      Recognises patterns like ``gpt-4o-20, Resolver for Anthropic model identifiers.      Recognises patterns like ``claude (+5 more)

### Community 130 - "_is_choch"
Cohesion: 0.43
Nodes (3): _is_choch(), Return ``True`` when the trigger is a Change-of-Character event., TestIsChoch

### Community 131 - "TestReviewerIndependenceLevel"
Cohesion: 0.33
Nodes (3): _determine_trade_direction(), Determine trade direction from D1 bias and H4 preferred direction.      Args:, TestDetermineTradeDirection

### Community 132 - "TestCostTrackerWiring"
Cohesion: 0.44
Nodes (8): _decision(), _enforce(), _policy(), Deterministic enforcement assertions; no approval or retry stage exists., _setup(), test_actionable_deterministic_policy_passes(), test_missing_candidate_is_blocked_by_enforcement(), test_policy_blocker_is_enforced_without_second_llm_decision()

### Community 134 - "reload_settings"
Cohesion: 0.30
Nodes (19): get_profile(), scan_events(), _bar(), Any, _swing(), test_available_real_h1_fixture_runs_with_configured_formulas(), test_combined_event_history_applies_limit_after_merging_event_categories(), test_direct_reclaim_is_distinct_from_reclaim_after_acceptance() (+11 more)

### Community 135 - "TestOpenAIModelIdentityResolver"
Cohesion: 0.17
Nodes (8): make_raw_response(), Build a mock provider response with controlled usage fields.      The returned o, Tests for usage.py — LLMUsage, safe_non_negative_int, and parse_usage.  No exter, Primary field names: input_tokens / output_tokens., cached_input_tokens > input_tokens → clamped to input, uncached = 0., Fallback field names: prompt_tokens / completion_tokens., TestParseUsageChatCompletions, TestParseUsageResponsesApi

### Community 136 - ".test_empty_pricing_table"
Cohesion: 0.18
Nodes (8): Compute the project root from the test file location.          Mirror the same t, Default ``analysis_cache_dir="data"`` resolves to ``<project_root>/data``., A relative path resolves against the project root, not CWD., An absolute path is returned as-is., Setting ``TRADING_ANALYSIS_CACHE_DIR`` to an absolute value must         be retu, Analyzer and server must resolve the same default to the same path., Tests for the ``resolved_analysis_cache_dir`` property.      Both the analyzer a, TestResolvedAnalysisCacheDir

### Community 138 - ".test_cache_disabled_by_env"
Cohesion: 0.16
Nodes (8): LLMModelConfig, Immutable configuration for an LLM endpoint.      Attributes:         model: Mod, Edge cases for LLM configuration., When provider is None, automatic detection kicks in., Model string with whitespace is treated literally (no stripping)., LLMModelConfig dataclass construction., TestLLMConfigEdgeCases, TestLLMModelConfig

### Community 139 - "TestArgparseMultiSymbol"
Cohesion: 0.17
Nodes (7): Tests for the new synthesizer_cache_enabled Settings field.      RED phase: thes, synthesizer_cache_enabled defaults to True when no env var is set., TRADING_SYNTHESIZER_CACHE_ENABLED=true yields True., TRADING_SYNTHESIZER_CACHE_ENABLED=false yields False., TRADING_SYNTHESIZER_CACHE_ENABLED=0 yields False (bool coercion)., Invalid TRADING_SYNTHESIZER_CACHE_ENABLED value either raises or falls back to d, TestSynthesizerCacheEnabled

### Community 141 - "test_h1_candle_period"
Cohesion: 0.60
Nodes (4): _graph(), The synthesizer is the only optional LLM call in the graph., test_deterministic_decision_does_not_call_synthesizer(), test_synthesis_makes_at_most_one_llm_call()

### Community 142 - "TestAnthropicModelIdentityResolver"
Cohesion: 0.33
Nodes (5): Consequences, Context, Decision, Deterministic decision, validation, and single Synthesizer, Status

### Community 143 - "TestDetermineD1Directional"
Cohesion: 0.27
Nodes (17): _bar(), _level(), Any, _swing(), test_clustered_level_id_uses_serialized_rounded_price(), test_level_lifecycle_precedence_and_accepted_beyond_block(), test_levels_block_when_only_one_directional_candidate_is_eligible(), test_validator_accepts_no_setup_with_over_age_historical_level() (+9 more)

### Community 144 - "test_grading.py"
Cohesion: 0.29
Nodes (4): Tests for the new openai_reasoning_effort Settings field.      These tests will, openai_reasoning_effort defaults to empty string (not set)., TRADING_OPENAI_REASONING_EFFORT env var overrides the default., TestReasoningEffortSettings

### Community 146 - "_mock_analysis_result"
Cohesion: 0.20
Nodes (6): Tests for the new terminal_server_url and terminal_api_key Settings fields., Settings().terminal_server_url returns the default MCP URL., Settings().terminal_api_key returns empty string by default., TRADING_TERMINAL_API_KEY env var overrides the default., TRADING_TERMINAL_SERVER_URL env var overrides the default., TestTerminalSettings

### Community 147 - "TestDetermineGeometryStatus"
Cohesion: 0.22
Nodes (6): LLMModelIdentity, Human-readable model identity string for logging., Resolve *model* into an :class:`LLMModelIdentity`., Immutable, provider-aware identity for a resolved LLM model.      This is the ca, LLMModelIdentity dataclass and display_name., TestLLMModelIdentity

### Community 149 - "TestDetermineH1TriggerConfirmed"
Cohesion: 0.27
Nodes (6): Any, T, Synchronous variant of :meth:`generate_structured`.          Returns the respons, Send messages to the LLM and return a structured Pydantic model.          This m, Synchronous variant of :meth:`generate_structured`.          Returns ``(response, Send messages to the LLM and return a structured Pydantic model.          Args:

### Community 150 - "TestDetermineH4Aligned"
Cohesion: 0.10
Nodes (9): StrEnum, Outcome of a model identity resolution attempt., ResolutionStatus, Tests for LLM model configuration and identity resolution (Section 16.7).  Tests, GenericAliasModelIdentityResolver — always supports, resolves as fallback., ResolutionStatus values., TestGenericAliasModelIdentityResolver, TestProviderKind (+1 more)

### Community 151 - "derive_allowed_actions"
Cohesion: 0.36
Nodes (3): _determine_h1_trigger_confirmed(), Determine if H1 trigger is confirmed.      BOS triggers are considered confirmed, TestDetermineH1TriggerConfirmed

### Community 152 - "usage.py"
Cohesion: 0.31
Nodes (10): _extract_int(), _extract_total_tokens(), _field_exists(), _get_field(), Any, LLM usage tracking — parse provider responses and extract token counts.  This mo, Return ``True`` if the nested attribute/dict path exists.      Works with object, Return the value at a nested attribute/dict path, or ``None``. (+2 more)

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
Cohesion: 0.39
Nodes (5): api, createApiClient(), defaultBaseURL(), fetchRuns(), resolveApiBaseURL()

### Community 158 - "test_routes.py"
Cohesion: 0.28
Nodes (6): MonkeyPatch, Lazy sentinel initialisation and env-driven disable., _settings is lazy-initialised; second call returns same instance., Setting _settings = None re-reads Settings from env., Env false → should_run_synthesis returns True even after save., TestSettingsSentinel

### Community 159 - "test_d1_candle_period_after_close"
Cohesion: 0.15
Nodes (13): LLMClientError, Exception, Raised when an LLM API call fails after all retries., _Echo, hanging_server(), _HangingServer, Any, BaseModel (+5 more)

### Community 161 - ".run_analysis"
Cohesion: 0.29
Nodes (6): Reset the _settings sentinel in candle_cache before each test.      Tests use mo, Reset the _settings sentinel in synthesizer_cache before each test.      Mirrors, reset_candle_cache_settings(), reset_synthesizer_cache_settings(), sample_decision(), sample_market_context()

### Community 162 - "test_load_returns_none_when_missing"
Cohesion: 0.23
Nodes (12): Build a compact version of structure analysis suitable for LLM prompts.      The, Extract compact analytical fields from a single timeframe engine output.      Th, _summarize_structure_analysis(), _summarize_timeframe(), _graph(), test_deterministic_decision_defaults_to_no_trade_when_policy_blocks(), test_deterministic_decision_uses_policy_action_without_llm(), test_graph_has_no_secondary_llm_nodes() (+4 more)

### Community 163 - "test_save_analysis_creates_directories"
Cohesion: 0.33
Nodes (3): client(), Route-level tests with mocked scanner/runner., Create a test client with mocked scanner and runner.

### Community 164 - "test_h4_candle_period"
Cohesion: 0.40
Nodes (4): Consequences, Context, Decision, Superseded: default the structured output mode to `json_mode`

### Community 165 - "test_cache_path_h4_includes_closing_hour"
Cohesion: 0.29
Nodes (5): Any, T, The underlying sync instructor-patched OpenAI client., Send messages to the LLM and return a structured Pydantic model.          Runs t, Synchronous variant of :meth:`generate_structured`.          Returns ``(response

### Community 183 - "Domain Glossary"
Cohesion: 0.25
Nodes (7): Analysis Pipeline, Analysis Runs, Domain Glossary, Liquidity and Levels, Risk and LLM Boundary, Setup and Decision, Structural Events

### Community 184 - "Architecture"
Cohesion: 0.40
Nodes (5): Analysis Pipeline (LangGraph State Machine), Architecture, Deployment Architecture, Design Principles, Service Architecture

### Community 192 - "TestLogLlmCall"
Cohesion: 0.14
Nodes (10): _log_llm_call(), Any, LLM agents for the trading pipeline.  The synthesizer is the only LLM integratio, Record an LLM call and log its cost. Returns enriched usage with costs., Tests for agent cost-logging helper extraction., _log_llm_call extracts duplicated cost-logging from agents., When usage is provided, logs cost details., When usage is all-zero (no usage data), logs zero cost. (+2 more)

## Knowledge Gaps
- **183 isolated node(s):** `trading-ai-agent`, `create-user.sh script`, `start-dev.sh script`, `trading-server`, `*.vue` (+178 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **35 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `DataSource` to `Evaluator`, `.test_empty_pricing_table`, `TestCostTracking`, `TestArgparseMultiSymbol`, `test_cache_path_mtf`, `test_grading.py`, `._run_async`, `_mock_analysis_result`, `TestDetermineH1ChochBased`, `tests/decision/__init__.py`, `test_should_run_h1_different_period`, `test_result_pipeline_writes_json`, `TestSynthesizeContextCanonicalPrice`, `setup_logging`, `TestParseUsageChatCompletions`, `testget_cache_date_d1_before_close`?**
  _High betweenness centrality (0.313) - this node is a cross-community bridge._
- **Why does `TradingGraph` connect `._run_async` to `DataSource`, `test_load_returns_none_when_missing`, `Evaluator`, `orchestrator/test_synthesizer_cache.py`, `test_h1_candle_period`, `test_cache_path_mtf`, `test_cache_path_d1_uses_folder_date_not_broker_now`, `tests/decision/__init__.py`, `TestAgentApiKey`, `test_should_run_h1_different_period`, `test_result_pipeline_writes_json`, `test_terminal_data_provider.py`, `TestGetCandlesBrokerNow`, `TestGetPositions`?**
  _High betweenness centrality (0.144) - this node is a cross-community bridge._
- **Why does `create_app()` connect `test_runner.py` to `server/tests/conftest.py`, `test_save_analysis_creates_directories`, `TestCostTracking`, `test_analyze_structure_fresh_saves_mtf_cache`, `src/data/__init__.py`, `main.py`, `TerminalApiError`?**
  _High betweenness centrality (0.136) - this node is a cross-community bridge._
- **Are the 61 inferred relationships involving `Settings` (e.g. with `ExecutionMode` and `_get_settings()`) actually correct?**
  _`Settings` has 61 INFERRED edges - model-reasoned connections that need verification._
- **Are the 49 inferred relationships involving `ResultScanner` (e.g. with `create_app()` and `RunService`) actually correct?**
  _`ResultScanner` has 49 INFERRED edges - model-reasoned connections that need verification._
- **Are the 44 inferred relationships involving `DecisionAction` (e.g. with `DeterministicValidation` and `DeterministicValidator`) actually correct?**
  _`DecisionAction` has 44 INFERRED edges - model-reasoned connections that need verification._
- **Are the 36 inferred relationships involving `TradeDirection` (e.g. with `DeterministicValidation` and `DeterministicValidator`) actually correct?**
  _`TradeDirection` has 36 INFERRED edges - model-reasoned connections that need verification._
