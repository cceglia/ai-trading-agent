# Graph Report - Agent  (2026-08-08)

## Corpus Check
- 187 files · ~113,616 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3305 nodes · 6845 edges · 215 communities (187 shown, 28 thin omitted)
- Extraction: 71% EXTRACTED · 29% INFERRED · 0% AMBIGUOUS · INFERRED: 2016 edges (avg confidence: 0.66)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5dc10793`
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
- TestCORS
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
- _print_symbol_summary
- .test_empty_pricing_table
- create-user.sh
- .test_cache_disabled_by_env
- TestArgparseMultiSymbol
- TestDetermineLifecycleStatus
- test_h1_candle_period
- TestAnthropicModelIdentityResolver
- TestDetermineD1Directional
- test_grading.py
- src/models.py
- _mock_analysis_result
- TestDetermineGeometryStatus
- TestDetermineH1ChochBased
- TestDetermineH1TriggerConfirmed
- TestListRuns
- derive_allowed_actions
- test_routes.py
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
- SecretRedactionFilter
- create_app
- test_h4_candle_period_at_boundary
- server/tests/test_main.py
- TestProxyMarkerAuthentication
- TestDetermineGeometryStatus
- triage-labels.md
- TestDetermineH4Aligned
- test_save_h4_creates_hour_suffixed_file
- test_cache_path_zero_padded_hour
- test_get_settings_respects_monkeypatch
- orchestrator/test_synthesizer_cache.py
- .test_record_call_does_not_raise_when_below_limit
- .test_multiple_calls_accumulate
- _CommaDelimitedEnvSource
- WebSettings
- secretScan.test.ts
- main
- Domain Glossary
- Architecture
- .generate_structured_sync
- TestAuthMiddleware
- .test_cache_disabled_by_env
- EngineError
- 0001-reviewer-configuration-names.md
- TestGenericAliasModelIdentityResolver
- .invalidate_cache
- TestLogLlmCall
- BiasLevel
- test_result_pipeline_writes_canonical_json
- .validate_execution_policy
- test_should_run_h4_with_cache
- _get_decision_field
- test_should_run_d1_after_close_with_cache
- test_load_handles_corrupt_json
- .test_set_limit_none_disables_enforcement
- .test_reset_zeroes_state
- reset_synthesizer_cache_settings
- .generate_structured_sync
- test_scanner.py
- RunCard.vue
- analyzer/tests/conftest.py
- main
- testget_cache_date_d1_before_close
- test_should_run_h4_with_cache
- test_should_run_d1_before_close
- test_should_run_d1_cache_in_wrong_folder
- test_load_handles_corrupt_json
- test_cache_path_mtf_uses_d1_date
- .test_empty_pricing_table

## God Nodes (most connected - your core abstractions)
1. `Settings` - 80 edges
2. `ResultScanner` - 77 edges
3. `TradeDirection` - 71 edges
4. `DecisionAction` - 61 edges
5. `SetupGrade` - 60 edges
6. `ResultWriter` - 60 edges
7. `SetupClassificationStatus` - 59 edges
8. `SetupLifecycleStatus` - 54 edges
9. `RiskPolicyState` - 52 edges
10. `DeterministicSetupState` - 50 edges

## Surprising Connections (you probably didn't know these)
- `TestCorsOrigins` --uses--> `Settings`  [INFERRED]
  server/tests/test_settings.py → analyzer/config/settings.py
- `TestProviderConfig` --uses--> `Settings`  [INFERRED]
  server/tests/test_settings.py → analyzer/config/settings.py
- `TestResolvedCacheDir` --uses--> `Settings`  [INFERRED]
  server/tests/test_settings.py → analyzer/config/settings.py
- `TestTrustedProxyCidrs` --uses--> `Settings`  [INFERRED]
  server/tests/test_settings.py → analyzer/config/settings.py
- `TestTrustedProxyCidrValidation` --uses--> `Settings`  [INFERRED]
  server/tests/test_settings.py → analyzer/config/settings.py

## Import Cycles
- None detected.

## Communities (215 total, 28 thin omitted)

### Community 0 - "TestFatalError"
Cohesion: 0.64
Nodes (7): analyze_liquidity(), _build_equal_pools(), _dedupe_pools(), _pool_status(), Any, _single_swing_pools(), stable_id()

### Community 1 - "Mt5DataProvider"
Cohesion: 0.06
Nodes (19): BatchResult, Per-symbol terminal outcomes for one batch run (FR-033 / INV-014).      ``result, Batch status per FR-033: success / partial / error.          ``success`` when al, Tests for POST /api/run — batch envelope (FR-033, AC-016/020)., Symbols are normalized once for request keys and analyzer args., NFR-006: xauusd + XAUUSD are the same symbol and run once., Dedup preserves first-occurrence order., FR-033a/AC-020: >20 symbols returns 422 and never spawns the runner. (+11 more)

### Community 2 - "DataSource"
Cohesion: 0.07
Nodes (23): BaseSettings, Self, Parse JSON string env var and validate prices.          Accepts only the new for, Reject unsupported instructor_mode values at Settings-parse time.          An in, Resolve ``analysis_cache_dir`` to an absolute path.          Both the analyzer a, Trading agent configuration., Validate execution policy settings based on execution mode.          Paper and L, Settings (+15 more)

### Community 3 - "AgentState"
Cohesion: 0.25
Nodes (8): Force a fresh Settings() on the next _get_settings() call., reload_settings(), reload_settings causes _get_settings to return a different object., After reload_settings, _get_settings picks up new env var values., test_reload_settings_creates_new_instance(), test_reload_settings_updates_values(), Reset the _settings sentinel in candle_cache before each test.      Tests use mo, reset_candle_cache_settings()

### Community 4 - "SnapshotBuilder"
Cohesion: 0.07
Nodes (19): Evaluator, Any, datetime, Check if an event falls within the time window from now.          Returns False, Evaluate events for symbol with timeframe-dependent window.          Args:, Evaluates calendar events for trading symbols., High-impact event outside the window should NOT block., High-impact event within the window SHOULD block. (+11 more)

### Community 5 - "Evaluator"
Cohesion: 0.13
Nodes (24): load_cached_synthesis(), Load a cached ``MarketContextSummary`` for *symbol* at the current H1 hour., datetime, MonkeyPatch, Path, Tests for synthesizer_cache — day-based synthesizer output caching.  ``src/decis, Fresh cache directory — should_run_synthesis returns True., After save — should_run_synthesis returns False. (+16 more)

### Community 6 - "Trading AI Agent"
Cohesion: 0.08
Nodes (31): emit, dayFrom(), monthFrom(), padDay(), padMonth(), preferredOrFirst(), uniqueDays(), uniqueMonths() (+23 more)

### Community 7 - "TestSynthesizerPrompt"
Cohesion: 0.08
Nodes (19): CalendarProvider, DataSource, Any, datetime, Protocol, Analyze market structure from snapshots.          Args:             snapshots: D, Fetch OHLC candles as CSV string.          Args:             symbol: Trading sym, Get latest price info for a symbol.          Args:             symbol: Trading s (+11 more)

### Community 8 - "TestCostTracking"
Cohesion: 0.14
Nodes (8): CORS_ORIGINS env-var and constructor behaviour., Given CORS_ORIGINS=http://a.com,http://b.com, settings must         produce ["ht, Passing a list[str] directly must be accepted as-is., With no env var, the default must be used., Trailing whitespace after commas must be stripped., A single origin without commas must produce a single-element list., An empty env var must produce an empty list (no default fallback)., TestCorsOrigins

### Community 9 - "ForexFactoryCalendar"
Cohesion: 0.11
Nodes (15): BatchResponse, BaseModel, Server-specific Pydantic models., Summary of a single analysis run (schema-v2 summary contract).      Exactly: sym, Batch envelope returned by POST /api/run (§12.3, FR-033).      ``results`` is ke, Safe per-symbol terminal error envelope (§12.3).      Carries a stable diagnosti, RunSummary, SymbolError (+7 more)

### Community 10 - "orchestrator/test_synthesizer_cache.py"
Cohesion: 0.20
Nodes (19): build_confluence(), build_timeframe_context(), _direction_from_bias(), Any, _require_parent(), analyze_multi_timeframe(), analyze_snapshot(), _apply_structural_event_transition() (+11 more)

### Community 11 - "Agent Instructions"
Cohesion: 0.10
Nodes (31): BiasLevel, Structural bias levels., AnalysisEnvelope, DecisionBlock, DeterministicFacts, OHLCBar, OHLCData, BaseModel (+23 more)

### Community 12 - "config/__init__.py"
Cohesion: 0.04
Nodes (46): autoprefixer, axios, echarts, happy-dom, postcss, tailwindcss, @types/node, typescript (+38 more)

### Community 13 - "trading-ai-agent"
Cohesion: 0.12
Nodes (11): input_tokens_details = None must not crash., output_tokens_details = None must not crash., When primary field is 0 and fallback is non-zero, primary wins., All token fields normalise negative values to 0., Booleans in usage fields are normalised to 0., Provider returned total_tokens=0 → keep 0, do not derive., No total_tokens field → derive as input + output., total_tokens = None → derive as input + output. (+3 more)

### Community 14 - "src/calendar/__init__.py"
Cohesion: 0.04
Nodes (44): After D1 close (17:00), the current candle is today's., H4 period containing the given time, anchored at 00:00., At exact H4 boundary, the period starts at that boundary., H1 period is floored to the current hour., H1 period crossing midnight boundary works correctly., D1 should run analysis when no cache file exists., D1 after close with existing cache should skip analysis., D1 after close without cache should run analysis. (+36 more)

### Community 15 - "src/data/__init__.py"
Cohesion: 0.08
Nodes (15): Sliding-window rate limiter — in-memory, pure Python., In-memory sliding-window rate limiter.      Tracks request timestamps per client, Return ``True`` if the client may proceed, ``False`` if rate-limited., Seconds until the client's window frees a slot (for ``Retry-After``).          W, Remove all expired buckets to free memory., SlidingWindowRateLimiter, RunService — port of the TypeScript runner service.  Spawns the Python analyzer, Tests for authentication and rate-limiting middleware. (+7 more)

### Community 16 - "src/decision/__init__.py"
Cohesion: 0.22
Nodes (9): Analysis Layer (`analyzer/src/analysis/`), Calendar Layer (`analyzer/src/calendar/`), Components, Configuration (`analyzer/config/`), Data Layer (`analyzer/src/data/`), Decision Layer (`analyzer/src/decision/`), Orchestrator (`analyzer/src/orchestrator/`), Server (`server/`) (+1 more)

### Community 17 - "src/__init__.py"
Cohesion: 0.10
Nodes (15): extract_ohlc_from_all_timeframes(), extract_ohlc_from_csv(), OHLCBar, OHLC data extractor — parses CSV candle data into structured OHLCBar objects.  P, Parse CSV candle data into a list of OHLCBar objects.      Uses the shared :func, Extract OHLC bars for all timeframes from a mapping of CSV strings.      Args:, Tests for OHLC extractor., An empty CSV in any timeframe propagates ValueError. (+7 more)

### Community 18 - "src/orchestrator/__init__.py"
Cohesion: 0.36
Nodes (9): analyze_candles(), _classify_engulfing(), Any, build_levels(), _cluster_side(), Any, canonical_level_id(), round_or_none() (+1 more)

### Community 19 - "tests/calendar/__init__.py"
Cohesion: 0.14
Nodes (16): grade_setup(), Any, Grade a trading setup based on multi-timeframe structural analysis.      This fu, _d1_context(), _h1_context(), _h4_context(), Any, AAA can be achieved with ALIGNED_PULLBACK as well. (+8 more)

### Community 20 - "tests/data/__init__.py"
Cohesion: 0.04
Nodes (69): Structure analysis missing required 'timeframes' schema., StructureSchemaError, DeterministicSetupState, EnforcementViolation, ExecutionPolicyState, FinalDecisionState, BaseModel, An enforcement violation detected during setup validation.      Attributes: (+61 more)

### Community 21 - "tests/decision/__init__.py"
Cohesion: 0.12
Nodes (28): _deterministic_bias(), _format_field(), _format_field_int(), _get_decision_field(), _get_field(), _initialize_pipeline(), _model_or_dict(), _print_summary() (+20 more)

### Community 22 - "tests/__init__.py"
Cohesion: 0.14
Nodes (11): calculate_entry_plan(), Calculate entry plan from raw setup data.      Accepts the raw entry data from t, calculate_entry_plan integration test., When geometry is invalid, status is TEMPORARILY_UNAVAILABLE., NO_SETUP with missing prices must not be labelled INSUFFICIENT_DATA.          Th, A CLASSIFIED candidate with missing prices is genuinely INSUFFICIENT_DATA., Entry calculator accepts TradeDirection as string., Entry calculator accepts TradeDirection as enum. (+3 more)

### Community 23 - "tests/orchestrator/__init__.py"
Cohesion: 0.14
Nodes (13): _make_analysis_result(), Path, A degraded analysis (synthesis failure, valid facts) must not be         rewritt, When there are errors but no fatal_error, status should be 'partial'., OHLC bars appear in the output JSON under 'ohlc'., ResultWriterContractError when analysis_result is missing., Entry-plan fields are None when analysis_result has default SLTPOverlay., Entry-plan values come from analysis_result.sl_tp_overlay. (+5 more)

### Community 24 - "_make_mcp_tool_result"
Cohesion: 0.09
Nodes (22): DOM, DOM.Iterable, env.d.ts, ES2022, src/**/*.ts, src/**/*.vue, compilerOptions, baseUrl (+14 more)

### Community 25 - "TerminalApiError"
Cohesion: 0.15
Nodes (12): Walk the data directory tree, read/parse JSON result files,     filter/sort into, ResultScanner, Path, Legacy fatal results must not make the run list endpoint fail., Helper to write a result JSON file., Files not in YYYY/MM/DD/SYMBOL/ pattern are skipped., When JSON has a 'symbol' field, it overrides the path-derived symbol., Tests for ResultScanner.get_run(). (+4 more)

### Community 26 - "test_terminal_data_provider.py"
Cohesion: 0.12
Nodes (10): Immutable state for risk management policy evaluation.      Attributes:, Final risk percentage after grade multiplier is applied., Whether the estimated reward-to-risk meets the minimum threshold., RiskPolicyState, Deterministic risk policy creation for the multi-timeframe pipeline.  This modul, RiskPolicyState.risk_reward_ok computation., R/R of 0.0 is rejected by the model's gt=0 constraint., RiskPolicyState.final_risk_percentage computation. (+2 more)

### Community 27 - "TestGetCandlesBrokerNow"
Cohesion: 0.10
Nodes (11): CostLimitExceeded, Exception, CostTracker — tracks LLM API call costs.  Exposes a single :class:`CostTracker`, Raised when per-symbol LLM cost exceeds the configured limit., Record an LLM API call and return its usage with cost filled in.          Parame, CostLimitExceeded is a subclass of Exception., record_call raises CostLimitExceeded when total_cost > limit., set_limit() after calls already recorded does not retroactively raise. (+3 more)

### Community 28 - "TestGetPositions"
Cohesion: 0.10
Nodes (47): _action_value(), _blockers(), DeterministicValidation, DeterministicValidator, _finite_number(), _non_negative_integer(), _parse_timestamp(), Any (+39 more)

### Community 29 - "._run_async"
Cohesion: 0.13
Nodes (12): _field(), Any, Bounded per-batch run metrics counters (NFR §18).  Counters are process-local an, Read ``key`` from a pydantic model or dict, tolerating ``None``., Aggregate analysis outcome counters for one CLI batch (NFR §18)., Categorize one symbol run into a bounded outcome bucket.          Args:, Count a sent or suppressed Telegram notification., Emit one bounded summary line with all counters. (+4 more)

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
Cohesion: 0.10
Nodes (21): actionLabel(), entryPlanOverlay(), formatConfidencePct(), hasCompleteDeterministicSetup(), isActionableRun(), isLegacyRun(), isLegacySummary(), isOperationalRun() (+13 more)

### Community 36 - "TestRepeatedRuns"
Cohesion: 0.14
Nodes (13): Tests for engine field rename (no _utc suffix) and engine deepcopy behavior., analyze_snapshot must NOT deepcopy the input snapshot before passing to validate, _ALLOWED_BAR must accept open_time, not open_time_utc., Swing dataclass must have timestamp, not timestamp_utc., Engine source_audit must use latest_closed_candle_time, not _utc., _ALLOWED_TOP_LEVEL must accept retrieved_at, not retrieved_at_utc., Engine must export scoring.latest_close, matching technical_context.close., test_analyze_snapshot_does_not_deepcopy_input() (+5 more)

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
Cohesion: 0.12
Nodes (14): _default_mcp_probe(), HealthReport, HealthService, Any, Path, Health and readiness checks for the Trading Analysis server.  Readiness distingu, Evaluate all checks and return a snapshot., Return True only when *url*'s host:port accepts a TCP connection.      The probe (+6 more)

### Community 43 - "TradingGraph"
Cohesion: 0.13
Nodes (4): Path, TEST-013 / AC-013: the single-synthesizer graph must not retain any     reviewer, TestNoReviewerDeciderResidue, TestProjectFiles

### Community 44 - "test_analyze_structure_fresh_saves_mtf_cache"
Cohesion: 0.14
Nodes (10): integration_client(), integration_data(), Path, Integration tests with real file I/O., Create a temporary data directory with fixture JSON files., FR-034 — list/detail responses use v2 or safe legacy without review fields., Create app pointing at the mock data directory., Integration tests for GET /api/runs with real file I/O. (+2 more)

### Community 45 - "TestSettingsDescriptions"
Cohesion: 0.10
Nodes (20): chartOption, props, BatchStatus, DecisionBlock, DeterministicFacts, Direction, EntryPlan, EnvelopeStatus (+12 more)

### Community 46 - "BiasLevel"
Cohesion: 0.27
Nodes (6): Type of price action trigger for a setup., TriggerType, _is_bos(), CHoCH/BOS trigger classification for the H1 timeframe.  This module implements `, Return ``True`` when the trigger is a Break-of-Structure event., TestIsBos

### Community 47 - "test_analyze_structure_passes_broker_time_to_snapshot_builder"
Cohesion: 0.17
Nodes (12): Agent Instructions, Agent skills, Architectural notes, Architecture, Critical invariants, Domain docs, Graphify first, Issue tracker (+4 more)

### Community 48 - "test_analyze_structure_fetches_all_timeframes"
Cohesion: 0.31
Nodes (10): Any, TimeframeProfile, _assign_status(), _candidate_indexes(), detect_swings(), _group_local_plateaus(), _prominence(), Any (+2 more)

### Community 49 - "test_analyze_structure_full_cache_hit"
Cohesion: 0.29
Nodes (9): startRun(), buildRequestURL(), capString(), extractErrorDetail(), formatApiError(), looksLikeHTML(), MinimalRequestConfig, safeStringify() (+1 more)

### Community 50 - "main.py"
Cohesion: 0.10
Nodes (15): _make_run_summary(), _mock_process(), Unit tests for RunService., Create a RunService with test defaults., Create a mock asyncio subprocess., Tests for RunService._wait_for_results()., RunService with minimal retry delays for fast tests., Scanner returns empty on first N-1 calls, then succeeds. (+7 more)

### Community 54 - "main.py"
Cohesion: 0.06
Nodes (25): Spawn Python subprocess to run analysis, enforce timeout,     capture stderr, an, RunService, Verify --model flag is absent when model is None., A resolved provider base_url is passed as --base-url to the analyzer., Verify --base-url is absent when base_url is None., Non-zero exit yields a per-symbol error; stderr secrets never surface., Process should be killed on timeout and mapped to per-symbol errors., A timeout after some symbols completed keeps the completed results. (+17 more)

### Community 55 - "test_result_pipeline_writes_json"
Cohesion: 0.15
Nodes (11): Path, ``resolved_cache_dir`` must resolve relative paths from the project root.      B, Compute the project root from the test file location.          Mirror the same t, Given ``analysis_cache_dir="data"``, the resolved path must be         ``<projec, Given an absolute path, ``resolved_cache_dir`` must return it         unchanged., The default ``analysis_cache_dir`` is ``"data"``, which must         resolve to, Setting ``TRADING_ANALYSIS_CACHE_DIR`` to a relative value must         resolve, Setting ``TRADING_ANALYSIS_CACHE_DIR`` to an absolute value must         be retu (+3 more)

### Community 57 - "TestOhlcCachePath"
Cohesion: 0.31
Nodes (3): _determine_d1_directional(), Determine if D1 shows clear directional bias.      Args:         d1_bias: D1 bia, TestDetermineD1Directional

### Community 58 - "test_h4_candle_period_at_boundary"
Cohesion: 0.20
Nodes (17): _cache_path(), _digest_cache_path(), _get_cache_date(), _get_settings(), Any, datetime, Path, File-based cache for SynthesizerAgent output, keyed by (symbol, day, H1-closing- (+9 more)

### Community 59 - "AgentState"
Cohesion: 0.23
Nodes (4): _determine_entry_type(), Determine the entry type based on price relationship.      Args:         entry_p, _determine_entry_type classifies entry based on price relationship., TestDetermineEntryType

### Community 60 - "test_analyze_structure_uses_broker_time_not_utc"
Cohesion: 0.27
Nodes (4): Validate that geometry is correct for the trade direction.      For BULLISH: ent, validate_geometry(), validate_geometry checks entry/stop/target ordering by direction., TestValidateGeometry

### Community 76 - "DecisionOutput"
Cohesion: 0.15
Nodes (7): OpenAIProviderAdapter, OpenAI provider adapter — instructor-based structured output.  Wraps the ``instr, The provider this adapter handles., Resolved identity for the configured model., The raw model identifier., Optional reasoning effort level., OpenAI provider adapter using ``instructor`` for structured output.      Conform

### Community 80 - "test_cache_path_d1_uses_folder_date_not_broker_now"
Cohesion: 0.15
Nodes (10): _compact_timeframe_facts(), Exception, Map a stored action to the canonical v2 decision action (DEC-002).      ``wait_f, Raised when ResultWriter receives an invalid or incomplete result., Extract compact, bounded facts for a single timeframe engine output.      The ra, _resolve_action(), ResultWriterContractError, FR-031 / Section 13: temp-file + atomic replace + cleanup. (+2 more)

### Community 81 - ".write"
Cohesion: 0.12
Nodes (21): get_cache_date(), Return the cache date for the given timeframes.      Returns a datetime whose da, load_ohlc_cache(), OHLCBar, Save OHLC bars to cache, same directory structure as analysis cache.      Args:, Load cached OHLC bars from disk if available.      Args:         timeframe: "D1", save_ohlc_cache(), D1 file path uses folder_date from get_cache_date, not raw broker_now. (+13 more)

### Community 82 - "test_should_run_d1_after_close_with_cache"
Cohesion: 0.33
Nodes (6): Development environment (Docker), Quick commands (run inside container), Running from Docker (host → container), Setup, Starting the container, Stopping

### Community 84 - "setup_logging"
Cohesion: 0.13
Nodes (12): MonkeyPatch, TRADING_MODEL_PRICING JSON env var overrides the default (new format)., Tests for the primary LLM instructor_mode and timeout Settings fields.      Thes, openai_instructor_mode defaults to 'json_mode'., json_mode' is a valid value., tool_call' is a valid value., An unsupported instructor_mode value is rejected at parse time., An empty primary instructor_mode is a misconfiguration and is rejected. (+4 more)

### Community 85 - "test_should_run_h1_different_period"
Cohesion: 0.12
Nodes (26): _cache_path(), _candle_period(), _get_settings(), load_cached_analysis(), Any, datetime, Determine if analysis should run for this timeframe.      Args:         timefram, Save analysis result to disk.      Args:         timeframe: "D1", "H4", or "H1" (+18 more)

### Community 86 - "TestAgentApiKey"
Cohesion: 0.13
Nodes (9): Any, Record the result files that exist before the run starts.          Maps each sym, Return True when *run*'s file was produced by the current batch.          A file, Build the analyzer CLI argument list., Spawn the Python process and wait for completion.          On timeout the proces, Retry reading result files with backoff.          After a subprocess completes t, Return the subset of *symbols* with no run freshly produced by the         curre, Walk the data directory via ResultScanner and return the most recent         fre (+1 more)

### Community 87 - "test_result_pipeline_writes_json"
Cohesion: 0.31
Nodes (4): LegacyAdapter, Server-owned, read-only, idempotent adapter for legacy result files.      Produc, The legacy adapter is read-only, idempotent, and review-free (AC-015)., TestLegacyAdapter

### Community 88 - "send_trade_notification"
Cohesion: 0.05
Nodes (32): _as_dict(), _canonical_analysis_result(), extract_trade_levels(), Any, Telegram notification sender — best-effort, never blocks the pipeline., Send a compact trade notification to Telegram.      Best-effort: logs warning on, Normalize a pydantic model or mapping for notification checks., Return the nested v2 result, never treating legacy fields as canonical. (+24 more)

### Community 91 - "test_result_pipeline_writes_json"
Cohesion: 0.21
Nodes (8): Synchronous variant of :meth:`generate_structured`.          Returns ``(response, LLMUsage, parse_usage(), Extract an ``LLMUsage`` from a provider response.      Handles:     * ``None`` r, Immutable record of token usage for a single LLM API call.      Token fields are, TestLLMUsageDefaults, TestParseUsageDict, TestParseUsageNoneOrMissing

### Community 92 - "test_runner.py"
Cohesion: 0.12
Nodes (13): ResultScanner — reads schema-v2 envelopes and adapts legacy files.  The scanner, health_env(), _make_client(), Path, TestClient, Health and readiness endpoint tests (NFR §18 / ticket 08)., Configure env so create_app targets a tmp data root and known MCP URL., Build a TestClient with a controllable MCP probe. (+5 more)

### Community 94 - "test_load_returns_none_when_missing"
Cohesion: 0.29
Nodes (4): _check_path_a_confirmed_retest(), Path A: CHoCH is confirmed by a retest of the broken level.      A confirmed ret, Path A: CHoCH confirmed by a retest of the broken level., TestCheckPathAConfirmedRetest

### Community 95 - "test_save_h1_creates_hour_suffixed_file"
Cohesion: 0.22
Nodes (9): Environment Configuration, Installation, License, Native Setup, Overview, Prerequisites, Project Structure, Services (+1 more)

### Community 96 - "test_save_h4_creates_hour_suffixed_file"
Cohesion: 0.24
Nodes (7): TestClient, Tests that exceptions are logged before re-raising., list_runs must log the original exception before raising RuntimeError., get_run must log the original exception before raising RuntimeError., run_analysis must log the original exception before raising RuntimeError., run_analysis must not have a dedicated 502 path: a TimeoutError that         esc, TestErrorLogging

### Community 97 - "test_load_handles_corrupt_json"
Cohesion: 0.29
Nodes (7): Configuration, Cost Analysis, Cost Estimate (GPT-4o), Default Model Pricing, Environment Variables — Analyzer, Environment Variables — Server, Token Estimates (GPT-4o)

### Community 98 - "server/tests/conftest.py"
Cohesion: 0.11
Nodes (18): client_with_auth(), mock_data_dir(), mock_runner(), Any, Path, RunSummary, Shared fixtures for server tests., Create a temporary data directory with fixture JSON files. (+10 more)

### Community 99 - "test_cache_path_d1_no_hour_suffix"
Cohesion: 0.24
Nodes (4): Return a non-negative ``int`` or ``0`` for invalid/missing values.      Handles, safe_non_negative_int(), TestSafeNonNegativeInt, LogCaptureFixture

### Community 100 - "context.py"
Cohesion: 0.15
Nodes (10): Any, Path, RunSummary, List all runs, optionally filtered by symbol and date range.          Returns so, Get a single run's full result.          v2 envelopes are returned as-is; legacy, Normalize a legacy file, count it, and warn (NFR §18).          Legacy reads are, Full directory walk (fallback when no symbol is specified)., Walk only directories that match *symbol_upper*.          Directory layout:  dat (+2 more)

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
Nodes (23): create_llm_client(), LLMClientProtocol, LLMCommunicationClient, OpenAIProviderAdapter, Protocol, LLM client protocol, provider adapters, and factory for structured LLM calls.  T, Raised when an unsupported LLM provider is requested., OpenAI provider adapter implementing ``LLMClientProtocol``.      Wraps an ``inst (+15 more)

### Community 106 - "TestListRunsPruning"
Cohesion: 0.13
Nodes (15): AnalysisEnvelope, Any, datetime, OHLCBar, Path, Write a success/degraded/partial schema-v2 envelope to disk.          Fatal pipe, Collect stable, bounded error codes for the completion log.          Combines po, Validate and return the flat internal AnalysisResult for a run. (+7 more)

### Community 107 - "TestListRunsIntegration"
Cohesion: 0.29
Nodes (5): _check_path_b_continuation_bos(), Any, Path B: CHoCH is confirmed by a continuation BOS in the same direction.      A c, Path B: CHoCH confirmed by a continuation BOS in the same direction., TestCheckPathBContinuationBos

### Community 109 - "Development"
Cohesion: 0.33
Nodes (6): Commands, Contributing, Dependencies, Development, Knowledge Graph, Pre-commit Hooks

### Community 111 - "test_cache_path_mtf"
Cohesion: 0.11
Nodes (11): evaluate_execution_policy(), Evaluate execution policy and return an :class:`ExecutionPolicyState`.      Cons, Self, Create an ExecutionPolicyState from a setup and blockers.          Extracts the, _make_risk_policy(), _make_setup(), Calendar has highest priority among non-execution blockers., When multiple blocker types present, status uses the highest priority. (+3 more)

### Community 112 - "Usage"
Cohesion: 0.40
Nodes (5): Analyzer CLI, API Server, Programmatic Usage, UI Dashboard, Usage

### Community 113 - "Code Review Analysis"
Cohesion: 0.40
Nodes (5): Architecture Diagram, External Dependencies and I/O Boundaries, Project Facts and Conventions, Test Coverage — Analyzer, Testing

### Community 114 - "TestFatalError"
Cohesion: 0.14
Nodes (8): LRU caching with TTL., Second identical call returns cached results; deleting files has no effect., After invalidate_cache a subsequent read picks up disk changes., After invalidate_cache and file deletion, fresh read returns empty., Different filter tuples produce different cache entries., Force TTL expiry by monkey-patching time.monotonic., Empty list results are also cached., TestListRunsCache

### Community 115 - "Docker"
Cohesion: 0.25
Nodes (8): Development, Docker, First-time setup, Images, Migration from root-based setup, Prerequisites, Production, Running commands

### Community 116 - "TestGetRunIntegration"
Cohesion: 0.33
Nodes (5): emit, localDay, localMonth, localYear, props

### Community 117 - "Architecture"
Cohesion: 0.10
Nodes (9): StrEnum, Outcome of a model identity resolution attempt., ResolutionStatus, Tests for LLM model configuration and identity resolution (Section 16.7).  Tests, GenericAliasModelIdentityResolver — always supports, resolves as fallback., ResolutionStatus values., TestGenericAliasModelIdentityResolver, TestProviderKind (+1 more)

### Community 118 - "test_cache_path_mtf_uses_d1_date"
Cohesion: 0.36
Nodes (3): _determine_h1_choch_based(), Determine if H1 trigger is CHoCH-based.      Args:         h1_trigger_type: H1 t, TestDetermineH1ChochBased

### Community 119 - "TestParseUsageChatCompletions"
Cohesion: 0.33
Nodes (3): _determine_lifecycle_status(), Determine lifecycle status based on trigger confirmation.      Args:         h1_, TestDetermineLifecycleStatus

### Community 120 - "TestCORS"
Cohesion: 0.22
Nodes (5): Directory pruning: when symbol is provided only matching dirs are walked., EURUSD must NOT be discovered when scanning for XAUUSD., The pruned path does *not* call os.walk., Date ranges narrow the walked directories., TestListRunsPruning

### Community 122 - "test_d1_candle_period_after_close"
Cohesion: 0.20
Nodes (5): Tests for CHoCH/BOS trigger classification (Section 16.5).  Tests the triggers.p, None trigger event handling., When multiple confirmation events are provided, any one path suffices., TestClassifyTriggerMultiplePaths, TestClassifyTriggerNull

### Community 124 - "test_h4_candle_period_at_boundary"
Cohesion: 0.15
Nodes (12): GenericAliasModelIdentityResolver, ProviderKind, LLM model configuration and provider-aware identity resolution.  This module def, Fallback resolver that treats the entire model string as the family.      Used w, Resolve a model string to its provider-aware identity.      Iterates through reg, Supported LLM provider identifiers., resolve_model_identity(), resolve_model_identity() orchestrates resolution through registered resolvers. (+4 more)

### Community 125 - "testget_cache_date_d1_before_close"
Cohesion: 0.23
Nodes (7): CORS header verification tests., Issue an OPTIONS preflight request with standard CORS headers., OPTIONS preflight must return restricted allow-methods., OPTIONS preflight must return restricted allow-headers.          The middleware, OPTIONS preflight from a configured origin should echo it back., OPTIONS preflight must include allow-credentials: true., TestCORS

### Community 126 - "test_h1_candle_period_at_boundary"
Cohesion: 0.08
Nodes (16): LLMProviderAdapter, LLMProviderAdapterFactory, Any, Protocol, LLM provider adapter — base interface and factory.  Defines the abstract adapter, Register an adapter class for a provider.          Args:             provider: P, Create an adapter instance for the given config.          Args:             conf, Return the list of providers with registered adapters. (+8 more)

### Community 127 - "test_should_run_d1_after_close_without_cache"
Cohesion: 0.33
Nodes (4): _check_path_c_sweep_and_reclaim(), Path C: CHoCH is confirmed by a sweep-and-reclaim pattern.      A sweep-and-recl, Path C: CHoCH confirmed by a sweep-and-reclaim pattern., TestCheckPathCSweepAndReclaim

### Community 128 - "usage.py"
Cohesion: 0.18
Nodes (10): _calculate_entry_plan_inner(), _extract_entry_prices(), Any, Extract and normalize entry price data from setup context.      Args:         se, Inner implementation that may raise InvalidTradeDirectionError., InvalidTradeDirectionError, Trade direction string does not map to a valid TradeDirection., Tests for entry plan calculation and geometry validation (Section 16.4).  Tests (+2 more)

### Community 129 - "test_should_run_d1_after_close_with_cache"
Cohesion: 0.11
Nodes (13): AnthropicModelIdentityResolver, ModelIdentityResolver, OpenAIModelIdentityResolver, Protocol, Protocol for provider-specific model identity resolvers.      Implementations mu, Return ``True`` if this resolver can handle *model*., Resolver for OpenAI model identifiers.      Recognises patterns like ``gpt-4o-20, Resolver for Anthropic model identifiers.      Recognises patterns like ``claude (+5 more)

### Community 130 - "_is_choch"
Cohesion: 0.43
Nodes (3): _is_choch(), Return ``True`` when the trigger is a Change-of-Character event., TestIsChoch

### Community 131 - "TestReviewerIndependenceLevel"
Cohesion: 0.31
Nodes (10): _extract_int(), _extract_total_tokens(), _field_exists(), _get_field(), Any, LLM usage tracking — parse provider responses and extract token counts.  This mo, Return ``True`` if the nested attribute/dict path exists.      Works with object, Return the value at a nested attribute/dict path, or ``None``. (+2 more)

### Community 132 - "TestCostTrackerWiring"
Cohesion: 0.44
Nodes (8): _decision(), _enforce(), _policy(), Deterministic enforcement assertions; no approval or retry stage exists., _setup(), test_actionable_deterministic_policy_passes(), test_missing_candidate_is_blocked_by_enforcement(), test_policy_blocker_is_enforced_without_second_llm_decision()

### Community 133 - ".invalidate_cache"
Cohesion: 0.24
Nodes (9): mocks, legacyEnvelope, legacySummary, v2DegradedEnvelope, v2InvalidEnvelope, v2NoSetupEnvelope, v2SuccessEnvelope, v2SuccessSummary (+1 more)

### Community 134 - "reload_settings"
Cohesion: 0.22
Nodes (24): get_profile(), _canonicalize(), _event_type(), Any, _quality(), scan_events(), _scope(), _bar() (+16 more)

### Community 136 - ".test_empty_pricing_table"
Cohesion: 0.18
Nodes (8): Compute the project root from the test file location.          Mirror the same t, Default ``analysis_cache_dir="data"`` resolves to ``<project_root>/data``., A relative path resolves against the project root, not CWD., An absolute path is returned as-is., Setting ``TRADING_ANALYSIS_CACHE_DIR`` to an absolute value must         be retu, Analyzer and server must resolve the same default to the same path., Tests for the ``resolved_analysis_cache_dir`` property.      Both the analyzer a, TestResolvedAnalysisCacheDir

### Community 138 - ".test_cache_disabled_by_env"
Cohesion: 0.16
Nodes (8): LLMModelConfig, Immutable configuration for an LLM endpoint.      Attributes:         model: Mod, Edge cases for LLM configuration., When provider is None, automatic detection kicks in., Model string with whitespace is treated literally (no stripping)., LLMModelConfig dataclass construction., TestLLMConfigEdgeCases, TestLLMModelConfig

### Community 139 - "TestArgparseMultiSymbol"
Cohesion: 0.17
Nodes (7): Tests for the new synthesizer_cache_enabled Settings field.      RED phase: thes, synthesizer_cache_enabled defaults to True when no env var is set., TRADING_SYNTHESIZER_CACHE_ENABLED=true yields True., TRADING_SYNTHESIZER_CACHE_ENABLED=false yields False., TRADING_SYNTHESIZER_CACHE_ENABLED=0 yields False (bool coercion)., Invalid TRADING_SYNTHESIZER_CACHE_ENABLED value either raises or falls back to d, TestSynthesizerCacheEnabled

### Community 140 - "TestDetermineLifecycleStatus"
Cohesion: 0.09
Nodes (63): _build_blockers(), PolicySettings, Deterministic execution policy evaluation for the multi-timeframe pipeline.  Thi, Configuration for execution policy evaluation.      Attributes:         countert, Evaluate all blocker conditions and return the active blockers.      This is an, BlockerSeverity, DecisionAction, derive_allowed_actions() (+55 more)

### Community 141 - "test_h1_candle_period"
Cohesion: 0.10
Nodes (11): CostTracker, Accumulated cost across all recorded calls., Number of calls recorded., Reset accumulated cost and call count to zero., Tracks LLM API call costs using per-model token pricing.      Each instance is i, Set a per-symbol cost limit.          When *limit* is ``<= 0`` or ``None`` the l, Set the current symbol for error context.          The symbol is used by :meth:`, set_limit(0) disables enforcement. (+3 more)

### Community 142 - "TestAnthropicModelIdentityResolver"
Cohesion: 0.33
Nodes (5): Consequences, Context, Decision, Deterministic decision, validation, and single Synthesizer, Status

### Community 143 - "TestDetermineD1Directional"
Cohesion: 0.27
Nodes (17): _bar(), _level(), Any, _swing(), test_clustered_level_id_uses_serialized_rounded_price(), test_level_lifecycle_precedence_and_accepted_beyond_block(), test_levels_block_when_only_one_directional_candidate_is_eligible(), test_validator_accepts_no_setup_with_over_age_historical_level() (+9 more)

### Community 144 - "test_grading.py"
Cohesion: 0.29
Nodes (4): Tests for the new openai_reasoning_effort Settings field.      These tests will, openai_reasoning_effort defaults to empty string (not set)., TRADING_OPENAI_REASONING_EFFORT env var overrides the default., TestReasoningEffortSettings

### Community 145 - "src/models.py"
Cohesion: 0.08
Nodes (11): client(), client_with_provider(), mock_runner(), Route-level tests with mocked scanner/runner., Mock RunService returning an empty successful BatchResult., Create a test client with mocked scanner and runner., API-002: unknown /api/* paths return 404 JSON, not SPA text/html., Create a test client whose server config knows one provider id. (+3 more)

### Community 146 - "_mock_analysis_result"
Cohesion: 0.20
Nodes (6): Tests for the new terminal_server_url and terminal_api_key Settings fields., Settings().terminal_server_url returns the default MCP URL., Settings().terminal_api_key returns empty string by default., TRADING_TERMINAL_API_KEY env var overrides the default., TRADING_TERMINAL_SERVER_URL env var overrides the default., TestTerminalSettings

### Community 147 - "TestDetermineGeometryStatus"
Cohesion: 0.18
Nodes (7): Return the resolved identity information about the configured LLM., LLMModelIdentity, Human-readable model identity string for logging., Resolve *model* into an :class:`LLMModelIdentity`., Immutable, provider-aware identity for a resolved LLM model.      This is the ca, LLMModelIdentity dataclass and display_name., TestLLMModelIdentity

### Community 148 - "TestDetermineH1ChochBased"
Cohesion: 0.22
Nodes (6): _build_app(), Tests for credential redaction in server logs (FR-038 / §16).  API keys, proxy m, Create an app instance (installs the redaction filter)., Configured secrets and generic credential shapes are redacted., The generic URL pattern catches credentials not in the config., TestSecretRedaction

### Community 149 - "TestDetermineH1TriggerConfirmed"
Cohesion: 0.08
Nodes (53): ValidationStatus, Entry plan calculation for the multi-timeframe pipeline.  This module implements, _determine_h4_aligned(), Deterministic setup grading for the multi-timeframe pipeline.  This module imple, Determine if H4 is aligned with D1.      Args:         h4_alignment_status: H4 a, Trade direction based on bias., Quality grade assigned to a trading setup., Structured rejection codes for deterministic setup classification. (+45 more)

### Community 150 - "TestListRuns"
Cohesion: 0.47
Nodes (3): TEST-014 / AC-014: a v2 file written by the analyzer at the shared     project-r, ROOT-001 / AC-014: with a RELATIVE TRADING_ANALYSIS_CACHE_DIR the         analyz, TestSharedRootRoundTrip

### Community 151 - "derive_allowed_actions"
Cohesion: 0.36
Nodes (3): _determine_h1_trigger_confirmed(), Determine if H1 trigger is confirmed.      BOS triggers are considered confirmed, TestDetermineH1TriggerConfirmed

### Community 152 - "test_routes.py"
Cohesion: 0.33
Nodes (3): Configure structured logging for the trading agent., setup_logging(), TestSetupLogging

### Community 153 - "TestSynthesizeContextCanonicalPrice"
Cohesion: 0.15
Nodes (6): A schema-v2 file written by the analyzer is returned verbatim., Path-traversal attempts never reach the scanner (route boundary)., Integration tests for GET /api/runs/{symbol}/{year}/{month}/{day}/{file}., The legacy review-based fixture is returned normalized and         review-free v, Legacy files remain readable without inventing a MARKET order., TestGetRunIntegration

### Community 154 - "Issue tracker: GitHub"
Cohesion: 0.29
Nodes (6): Conventions, Issue tracker: GitHub, Pull requests as a triage surface, Wayfinding operations, When a skill says "fetch the relevant ticket", When a skill says "publish to the issue tracker"

### Community 155 - "Domain Docs"
Cohesion: 0.33
Nodes (5): Before exploring, read these, Domain Docs, File structure, Flag ADR conflicts, Use the glossary's vocabulary

### Community 156 - "Agent skills"
Cohesion: 0.17
Nodes (8): make_raw_response(), Build a mock provider response with controlled usage fields.      The returned o, Tests for usage.py — LLMUsage, safe_non_negative_int, and parse_usage.  No exter, Primary field names: input_tokens / output_tokens., cached_input_tokens > input_tokens → clamped to input, uncached = 0., Fallback field names: prompt_tokens / completion_tokens., TestParseUsageChatCompletions, TestParseUsageResponsesApi

### Community 157 - "testget_cache_date_h4_returns_closing_hour"
Cohesion: 0.19
Nodes (11): useRun(), useRuns(), api, createApiClient(), defaultBaseURL(), fetchRunResult(), fetchRuns(), resolveApiBaseURL() (+3 more)

### Community 158 - "test_routes.py"
Cohesion: 0.12
Nodes (11): _build_parser(), main(), _parse_and_configure_settings(), Build the CLI argument parser.      Returns:         Configured ArgumentParser i, Parse CLI args into a configured Settings instance.      Applies CLI overrides (, Main entry point.      Parses CLI arguments, initialises the analysis pipeline,, ROOT-001 / AC-014: with a RELATIVE TRADING_ANALYSIS_CACHE_DIR the     writer con, test_initialize_pipeline_passes_only_synthesizer_to_graph() (+3 more)

### Community 159 - "test_d1_candle_period_after_close"
Cohesion: 0.09
Nodes (19): LLMClientError, Any, Exception, T, Synchronous variant of :meth:`generate_structured`.          Returns the respons, Raised when an LLM API call fails after all retries., Send messages to the LLM and return a structured Pydantic model.          This m, Send messages to the LLM and return a structured Pydantic model.          Args: (+11 more)

### Community 161 - ".run_analysis"
Cohesion: 0.16
Nodes (10): BaseHTTPMiddleware, FastAPI, Request, RequestResponseEndpoint, Response, AuthMiddleware, Any, Authentication middleware — validates X-API-Key or trusted proxy marker.  Produc (+2 more)

### Community 162 - "test_load_returns_none_when_missing"
Cohesion: 0.20
Nodes (19): Extract compact analytical fields from a single timeframe engine output.      Th, _summarize_timeframe(), _assembled(), _enforcement(), _graph(), _policy_state(), _risk_state(), _setup_state() (+11 more)

### Community 163 - "test_save_analysis_creates_directories"
Cohesion: 0.21
Nodes (19): _build_graph(), _enforcement(), _invoke(), _policy_state(), Graph-level integration tests for the single-synthesizer routing.  TEST-010 / AC, Construct a TradingGraph with fully-mocked deterministic seams.      The data pr, Each payload violates the SynthesisResponse presentation contract., TEST-021: every presentation-contract violation degrades the run     through the (+11 more)

### Community 164 - "test_h4_candle_period"
Cohesion: 0.40
Nodes (4): Consequences, Context, Decision, Superseded: default the structured output mode to `json_mode`

### Community 165 - "SecretRedactionFilter"
Cohesion: 0.11
Nodes (15): LogRecord, install_secret_redaction(), FastAPI application entry point — port of the TypeScript Express server., Validate detail-route path components against traversal and bounded     formats, Resolve a provider_id to its server-side base URL (FR-039 / DEC-014).      The r, Attach a fresh redaction filter to the app and root loggers (FR-038).      Repla, Validate and normalize a batch symbol list (400 on invalid input).      Returns, Validate a YYYY-MM-DD query filter (400 on malformed input). (+7 more)

### Community 166 - "create_app"
Cohesion: 0.33
Nodes (6): create_app(), Create and configure the FastAPI application., client(), proxy_app(), Create a test client with mocked scanner and runner (no API key)., App configured with a trusted proxy CIDR and no API key.      Returns ``(app, mo

### Community 167 - "test_h4_candle_period_at_boundary"
Cohesion: 0.13
Nodes (10): Request body for POST /api/run.      Accepts 1–20 validated symbols plus optiona, Bound model id length/format (NFR-004 input hygiene)., Bound provider_id length/format (FR-039 input hygiene).          Provider ids ar, RunRequest, POST /api/run request contract (FR-039 / DEC-014)., A free-form ``base_url`` must be rejected (FR-039)., Unknown fields are forbidden — the contract is strict., NFR-004: model is bounded in length and character format. (+2 more)

### Community 168 - "server/tests/test_main.py"
Cohesion: 0.14
Nodes (11): 1. Shared data root, 2. Health and readiness, 3. Proxy trust and header stripping, 4. Legacy read behavior, 5. Rerunning failed symbols, 6. Completion diagnostics and bounded counters, 7. Rollout and rollback, 8. Release preflight checklist (evidence for the gate) (+3 more)

### Community 169 - "TestProxyMarkerAuthentication"
Cohesion: 0.27
Nodes (4): ``X-Authenticated-User`` is trusted only from ``TRADING_TRUSTED_PROXY_CIDRS``., Empty TRADING_TRUSTED_PROXY_CIDRS never trusts a client marker., A valid machine key authorizes even when a forged marker is present., TestProxyMarkerAuthentication

### Community 170 - "TestDetermineGeometryStatus"
Cohesion: 0.13
Nodes (8): AdvisoryLevels, MarketContextSummary, BaseModel, Summary of market context from synthesizer agent., Optional LLM-proposed levels, never used for execution or chart overlays., TestDecisionOutput, TestMarketContextSummary, save_synthesis should NOT catch errors that aren't OSError or         pydantic V

### Community 172 - "TestDetermineH4Aligned"
Cohesion: 0.10
Nodes (10): AnalysisResult, Top-level pipeline output serialized to JSON for the web viewer.      Fields are, Path, End-to-end persistence tests for the canonical deterministic output., test_result_pipeline_writes_canonical_json(), SYNTH-010: the CLI summary must show the deterministic direction and     the LLM, A valid no-trade run shows its deterministic neutral direction, never     a fabr, test_print_symbol_summary_shows_no_setup_bias_for_no_trade() (+2 more)

### Community 173 - "test_save_h4_creates_hour_suffixed_file"
Cohesion: 0.20
Nodes (6): _create_agents(), Create the single LLM presentation agent used in the pipeline.      Args:, Synthesizes market context from structure analysis and calendar., SynthesizerAgent, test_synthesizer_uses_injected_client_once(), test_synthesizer_prompt_treats_deterministic_facts_as_authoritative()

### Community 174 - "test_cache_path_zero_padded_hour"
Cohesion: 0.17
Nodes (9): ExecutionMode, StrEnum, _get_settings(), ohlc_cache_path(), datetime, Compute OHLC cache file path, parallel to analysis cache.      Cache path conven, Tests for OHLC bar cache., Full path follows analysis/YYYY/MM/DD/SYMBOL/ pattern. (+1 more)

### Community 175 - "test_get_settings_respects_monkeypatch"
Cohesion: 0.33
Nodes (3): _determine_trade_direction(), Determine trade direction from D1 bias and H4 preferred direction.      Args:, TestDetermineTradeDirection

### Community 176 - "orchestrator/test_synthesizer_cache.py"
Cohesion: 0.17
Nodes (9): _make_summary(), When os.makedirs raises, save_synthesis logs warning and returns., Cache scoped by (symbol, day)., Save EURUSD → should_run_synthesis('XAUUSD', same time) ⇒ True., File path includes H1 closing hour: ``…/synthesizer-h1-13.json``., After save, next should_run for same symbol+day returns False., Runs at different H1 hours → cache miss (different H1 closing hours)., 14:59 (closing hour 15) vs 15:01 (closing hour 16) → cache miss. (+1 more)

### Community 177 - ".test_record_call_does_not_raise_when_below_limit"
Cohesion: 0.07
Nodes (22): Tests for CostTracker — tracks LLM API call costs.  CostTracker lives in ``src/d, Unknown model logs warning, preserves token fields, cost fields zero., Missing cached_input_per_million → cached_input_cost = 0.0., Missing input_per_million → input_cost = 0.0., CostTracker: tracks LLM API call costs., Zero tokens result in zero cost but call IS counted., Many calls accumulate total_cost correctly., Missing output_per_million → output_cost = 0.0. (+14 more)

### Community 178 - ".test_multiple_calls_accumulate"
Cohesion: 0.25
Nodes (7): Authentication and security contract (ticket 07), Batch envelope, Health and readiness (ticket 08), Input boundaries (validated at the route boundary, before any analyzer/disk access), Routes, Server `/api` route inventory and input boundaries, Status codes

### Community 179 - "_CommaDelimitedEnvSource"
Cohesion: 0.25
Nodes (7): EnvSettingsSource, _CommaDelimitedEnvSource, Any, BaseSettings, Replace the default EnvSettingsSource with our comma-aware variant., Env source that parses comma-separated values for list fields.      pydantic-set, Split comma-separated env values for known list fields.

### Community 180 - "WebSettings"
Cohesion: 0.17
Nodes (7): Server configuration loaded from environment variables.      Uses Field(alias=.., Reject malformed CIDRs at settings load (CONFIG-001).          ``AuthMiddleware`, WebSettings, CONFIG-001: invalid CIDRs fail at settings load with a clear error.      Previou, ``TRADING_TRUSTED_PROXY_CIDRS`` configures the trusted proxy sources.      FR-03, TestTrustedProxyCidrs, TestTrustedProxyCidrValidation

### Community 181 - "secretScan.test.ts"
Cohesion: 0.27
Nodes (10): collectTargets(), DIST_DIR, FORBIDDEN_PATTERNS, isDirectory(), SKIP_FILES, SKIP_SUFFIXES, SRC_DIR, UI_ROOT (+2 more)

### Community 182 - "main"
Cohesion: 0.21
Nodes (12): Path, Preflight filesystem checks for the analysis CLI (NFR §18 / AC-014)., Preflight write/read roundtrip on the analysis data root (AC-014).      Creates, verify_data_root_writable(), Path, Tests for the analysis CLI data-root preflight (AC-014 / NFR §18)., A root whose parent is a file fails preflight without claiming a signal., chmod 0o500 makes writes fail for the non-root probe (best effort).      When th (+4 more)

### Community 183 - "Domain Glossary"
Cohesion: 0.25
Nodes (7): Analysis Pipeline, Analysis Runs, Domain Glossary, Liquidity and Levels, Risk and LLM Boundary, Setup and Decision, Structural Events

### Community 184 - "Architecture"
Cohesion: 0.40
Nodes (5): Analysis Pipeline (LangGraph State Machine), Architecture, Deployment Architecture, Design Principles, Service Architecture

### Community 185 - ".generate_structured_sync"
Cohesion: 0.22
Nodes (7): Writes schema-v2 analysis envelopes to JSON files in the data tree., ResultWriter, FR-031 / INV-011: INVALID persists as partial; fatal does not., A decision action outside the v2 enum must be rejected before any         file (, The completion log carries required diagnostic fields without secrets., TestCompletionLog, TestInvalidPersistence

### Community 186 - "TestAuthMiddleware"
Cohesion: 0.07
Nodes (12): API-002: an authenticated request to an unknown /api/* path gets         404 JSO, Auth runs before the 404 catch-all: a missing credential is 401., §15: a 401 on POST /api/run must never reach the runner., Static assets / SPA fallback are served through the proxy, not /api., API-001: the /api auth boundary is case-insensitive; no /API variant         byp, A valid credential passes the case-insensitive boundary; the path is         the, Tests for AuthMiddleware behaviour via client_with_auth.      Auth is enforced w, CORS-001: in enforced mode, OPTIONS /api/* preflight is protected.          ``Au (+4 more)

### Community 187 - ".test_cache_disabled_by_env"
Cohesion: 0.17
Nodes (7): openai_temperature defaults to 0.0., TRADING_OPENAI_TEMPERATURE env var overrides the default., openai_temperature = 0.0 is valid (lower bound)., openai_temperature = 2.0 is valid (upper bound)., openai_temperature = 1.0 is valid (mid-range)., Tests for the openai_temperature Settings field.      These tests verify that th, TestOpenAITemperatureSettings

### Community 188 - "EngineError"
Cohesion: 0.23
Nodes (15): EngineError, ExternalDerivedValuesError, InsufficientDataError, Any, Exception, Base class for deterministic engine errors., TimeframeMismatchError, UnsupportedTimeframeError (+7 more)

### Community 190 - "TestGenericAliasModelIdentityResolver"
Cohesion: 0.25
Nodes (4): Server-specific settings using Pydantic BaseSettings., Tests for WebSettings environment-variable loading.  The _CommaDelimitedEnvSourc, ``PROVIDER_CONFIG`` maps a server-side provider id to an endpoint URL.      Endp, TestProviderConfig

### Community 192 - "TestLogLlmCall"
Cohesion: 0.14
Nodes (10): _log_llm_call(), Any, LLM agents for the trading pipeline.  The synthesizer is the only LLM integratio, Record an LLM call and log its cost. Returns enriched usage with costs., Tests for agent cost-logging helper extraction., _log_llm_call extracts duplicated cost-logging from agents., When usage is provided, logs cost details., When usage is all-zero (no usage data), logs zero cost. (+2 more)

### Community 193 - "BiasLevel"
Cohesion: 0.21
Nodes (11): Presentation-only output from the single Synthesizer call., SynthesisResponse, TestSynthesisResponse, _graph(), The synthesizer is the only optional LLM call in the graph., _state(), test_cache_hit_skips_llm_call(), test_deterministic_decision_does_not_call_synthesizer() (+3 more)

### Community 194 - "test_result_pipeline_writes_canonical_json"
Cohesion: 0.42
Nodes (10): adx(), calculate_indicators(), ema(), macd(), Any, roc(), rsi(), sma() (+2 more)

### Community 195 - ".validate_execution_policy"
Cohesion: 0.36
Nodes (3): _determine_geometry_status(), Determine geometry status based on entry plan validity.      Args:         h1_se, TestDetermineGeometryStatus

### Community 197 - "_get_decision_field"
Cohesion: 0.22
Nodes (4): Tests for GET /api/runs/{symbol}/{year}/{month}/{day}/{file}., Malformed date/file components are rejected at the route boundary         before, Traversal attempts are absorbed by URL normalization or rejected;         in no, TestGetRun

### Community 198 - "test_should_run_d1_after_close_with_cache"
Cohesion: 0.25
Nodes (5): Lazy sentinel initialisation and env-driven disable., _settings is lazy-initialised; second call returns same instance., Setting _settings = None re-reads Settings from env., Env false → should_run_synthesis returns True even after save., TestSettingsSentinel

### Community 200 - ".test_set_limit_none_disables_enforcement"
Cohesion: 0.25
Nodes (5): Tests for ResultWriter (schema-v2 nested envelope persistence)., Convenience wrapper around ResultWriter.write., Deterministic facts derived from structure_analysis stay compact and     bounded, TestCompactFacts, _write()

### Community 201 - ".test_reset_zeroes_state"
Cohesion: 0.31
Nodes (5): FR-038: exception tracebacks (``logger.exception``) are redacted too.      ``rec, A configured API key inside the exception message is redacted., OpenAI-style keys in exception messages are caught by the pattern., Redaction keeps non-secret traceback content intact., TestExceptionRedaction

### Community 203 - ".generate_structured_sync"
Cohesion: 0.29
Nodes (5): Any, T, The underlying sync instructor-patched OpenAI client., Send messages to the LLM and return a structured Pydantic model.          Runs t, Synchronous variant of :meth:`generate_structured`.          Returns ``(response

### Community 204 - "test_scanner.py"
Cohesion: 0.29
Nodes (5): Unit tests for ResultScanner (v2 envelopes + legacy adapter)., Minimal schema-v2 envelope mirroring the analyzer writer output., Legacy reads increment a bounded counter and emit a warning (NFR §18)., TestLegacyReadDiagnostics, _v2_envelope()

### Community 205 - "RunCard.vue"
Cohesion: 0.25
Nodes (7): biasArrow, biasColor, biasKey, emit, isOperational, props, validationClass

### Community 206 - "analyzer/tests/conftest.py"
Cohesion: 0.29
Nodes (6): _dict_to_sns(), Recursively convert a dict to a SimpleNamespace., Reset the _settings sentinel in synthesizer_cache before each test.      Mirrors, reset_synthesizer_cache_settings(), sample_decision(), sample_market_context()

### Community 207 - "main"
Cohesion: 0.47
Nodes (5): check(), _load_server_src(), main(), Record a PASS/FAIL check., Map the top-level ``src`` package to the server package.      Both analyzer and

## Knowledge Gaps
- **227 isolated node(s):** `trading-ai-agent`, `create-user.sh script`, `start-dev.sh script`, `trading-server`, `*.vue` (+222 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main()` connect `main` to `create_app`, `Agent Instructions`, `TestDetermineH4Aligned`, `WebSettings`, `.generate_structured_sync`, `._run_async`, `TerminalApiError`?**
  _High betweenness centrality (0.223) - this node is a cross-community bridge._
- **Why does `Settings` connect `DataSource` to `.test_empty_pricing_table`, `TestCostTracking`, `TestArgparseMultiSymbol`, `TestDetermineLifecycleStatus`, `test_grading.py`, `_mock_analysis_result`, `tests/data/__init__.py`, `tests/decision/__init__.py`, `test_routes.py`, `test_save_h4_creates_hour_suffixed_file`, `test_cache_path_zero_padded_hour`, `WebSettings`, `test_result_pipeline_writes_json`, `.generate_structured_sync`, `test_h4_candle_period_at_boundary`, `.test_cache_disabled_by_env`, `TestGenericAliasModelIdentityResolver`, `test_cache_path_d1_uses_folder_date_not_broker_now`, `setup_logging`, `test_should_run_h1_different_period`?**
  _High betweenness centrality (0.198) - this node is a cross-community bridge._
- **Why does `ResultScanner` connect `TerminalApiError` to `Mt5DataProvider`, `server/tests/conftest.py`, `context.py`, `create_app`, `AgentState`, `test_scanner.py`, `main`, `main.py`, `TestFatalError`, `main.py`, `test_result_pipeline_writes_json`, `TestCORS`, `TestListRuns`, `test_runner.py`, `.invalidate_cache`?**
  _High betweenness centrality (0.142) - this node is a cross-community bridge._
- **Are the 65 inferred relationships involving `Settings` (e.g. with `ExecutionMode` and `_get_settings()`) actually correct?**
  _`Settings` has 65 INFERRED edges - model-reasoned connections that need verification._
- **Are the 62 inferred relationships involving `ResultScanner` (e.g. with `main()` and `create_app()`) actually correct?**
  _`ResultScanner` has 62 INFERRED edges - model-reasoned connections that need verification._
- **Are the 55 inferred relationships involving `TradeDirection` (e.g. with `DeterministicValidation` and `DeterministicValidator`) actually correct?**
  _`TradeDirection` has 55 INFERRED edges - model-reasoned connections that need verification._
- **Are the 51 inferred relationships involving `DecisionAction` (e.g. with `DeterministicValidation` and `DeterministicValidator`) actually correct?**
  _`DecisionAction` has 51 INFERRED edges - model-reasoned connections that need verification._
