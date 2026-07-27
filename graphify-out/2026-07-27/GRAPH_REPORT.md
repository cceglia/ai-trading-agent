# Graph Report - Agent  (2026-07-27)

## Corpus Check
- 113 files · ~50,290 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1540 nodes · 2858 edges · 113 communities (85 shown, 28 thin omitted)
- Extraction: 72% EXTRACTED · 28% INFERRED · 0% AMBIGUOUS · INFERRED: 800 edges (avg confidence: 0.69)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b38e7d1d`
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
- test_h1_candle_period_midnight
- trading-server
- test_h1_candle_period
- test_cache_path_d1_uses_folder_date_not_broker_now
- testget_cache_date_d1_after_close
- test_should_run_d1_without_cache
- test_cache_path_d1_no_hour_suffix
- test_should_run_h1_without_cache
- test_cache_path_h4_includes_closing_hour
- server/tests/conftest.py
- TestPostRun
- test_cache_path_mtf
- test_cache_path_mtf_uses_d1_date
- test_cache_path_zero_padded_hour
- test_d1_candle_period_before_close
- create_app
- TestListRuns
- TestListRunsIntegration
- test_d1_candle_period_after_close
- test_d1_candle_period_before_close
- TestFatalError

## God Nodes (most connected - your core abstractions)
1. `MarketContextSummary` - 83 edges
2. `AgentState` - 68 edges
3. `DecisionOutput` - 66 edges
4. `ReviewVerdict` - 60 edges
5. `CostTracker` - 58 edges
6. `TradingGraph` - 58 edges
7. `SynthesizerAgent` - 49 edges
8. `Settings` - 39 edges
9. `Evaluator` - 30 edges
10. `DeciderAgent` - 30 edges

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

## Communities (113 total, 28 thin omitted)

### Community 0 - "TestFatalError"
Cohesion: 0.05
Nodes (93): analyze_candles(), _classify_engulfing(), Any, get_profile(), Any, TimeframeProfile, build_confluence(), build_timeframe_context() (+85 more)

### Community 1 - "Mt5DataProvider"
Cohesion: 0.07
Nodes (49): _cache_path(), _get_cache_date(), _get_settings(), load_cached_synthesis(), Any, datetime, Path, File-based cache for SynthesizerAgent output, keyed by (symbol, broker-day).  Mi (+41 more)

### Community 2 - "DataSource"
Cohesion: 0.06
Nodes (35): BaseSettings, Trading agent configuration., Parse JSON string env var and validate all prices are non-negative., Settings, test_settings_has_analysis_cache_dir(), test_settings_has_d1_close_time(), test_settings_has_h4_close_interval_hours(), test_settings_has_h4_close_time() (+27 more)

### Community 3 - "AgentState"
Cohesion: 0.06
Nodes (45): LangGraph orchestrator for trading analysis., TradingGraph, H1 analysis must now be saved to cache like D1/H4., If get_broker_time() fails, _analyze_structure should set fatal_error., get_candles must be called with broker_time param., snapshot_builder.build must be called with broker_time., AgentState must NOT have 'account_info'; it must have 'symbol_price' instead., AgentState must NOT have 'market_data' — the dead field was removed.      This v (+37 more)

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
Cohesion: 0.08
Nodes (30): _canonical_structure_analysis(), _make_cached_summary(), datetime, Path, Cache hit → cost_tracker.call_count == 0 (no LLM call recorded)., 5 sequential runs on same symbol/day → exactly 1 LLM call.          First run: c, Build a ``MarketContextSummary`` that looks like it came from the cache., Minimal ``structure_analysis`` with H1 as most-recently-closed timeframe. (+22 more)

### Community 9 - "ForexFactoryCalendar"
Cohesion: 0.06
Nodes (27): CostTracker, CostTracker — tracks LLM API call costs.  Exposes a single :class:`CostTracker`, Reset accumulated cost and call count to zero., Tracks LLM API call costs using per-model token pricing.      Each instance is i, Record an LLM API call and return its cost.          Parameters         --------, Accumulated cost across all recorded calls., Number of calls recorded., Tests for CostTracker — tracks LLM API call costs.  CostTracker lives in ``src/d (+19 more)

### Community 10 - "TestProjectFiles"
Cohesion: 0.22
Nodes (7): _get_settings(), ohlc_cache_path(), datetime, Compute OHLC cache file path, parallel to analysis cache.      Cache path conven, Tests for OHLC bar cache., Full path follows analysis/YYYY/MM/DD/SYMBOL/ pattern., TestOhlcCachePath

### Community 11 - "Agent Instructions"
Cohesion: 0.11
Nodes (10): Test that argparse accepts multiple symbols via _build_parser., _build_parser accepts multiple symbols as nargs+., _build_parser is backward-compatible with single symbol., --output-dir option is accepted., --output-dir defaults to None., --model option is accepted., --base-url option is accepted., --log-level option defaults to INFO. (+2 more)

### Community 12 - "config/__init__.py"
Cohesion: 0.05
Nodes (36): autoprefixer, axios, echarts, postcss, tailwindcss, typescript, dependencies, axios (+28 more)

### Community 13 - "trading-ai-agent"
Cohesion: 0.10
Nodes (18): MarketContextSummary, Summary of market context from synthesizer agent., _make_raw_response(), Tests for prompt usage in agents., SynthesizerAgent.synthesize must accept current_price/current_price_time kwargs., User prompt must render current_price and current_price_time values., Build a mock raw_response with a usable .usage attribute., When no price is supplied, the current-price line must state None. (+10 more)

### Community 14 - "src/calendar/__init__.py"
Cohesion: 0.09
Nodes (22): At exact H1 boundary, period starts at that time., H4 cache date includes the closing hour in cache_date.hour., H4 should skip analysis when cache file exists for that period., D1 before close should always run analysis (candle not closed)., D1 after close without cache should run analysis., Verify the path check uses the correct folder date, not a stale one., H1 should skip analysis when cache file exists for that period., H1 filename includes the closing hour (e.g. h1-14-analysis.json). (+14 more)

### Community 15 - "src/data/__init__.py"
Cohesion: 0.15
Nodes (9): CaptureFixture, Tests for multi-symbol support in main.py., Verify main() calls graph.run() for each symbol., When one symbol fails, main() continues with remaining symbols., When --output-dir is given, ResultWriter is used., When result has no broker_now, main() uses datetime.now() instead., Test that main() loops over all symbols correctly., TestMainMultiSymbolExecution (+1 more)

### Community 16 - "src/decision/__init__.py"
Cohesion: 0.04
Nodes (47): Analysis Layer (`analyzer/src/analysis/`), Analysis Pipeline (LangGraph State Machine), Analyzer CLI, API Server, Architecture, Calendar Layer (`analyzer/src/calendar/`), Commands, Components (+39 more)

### Community 17 - "src/__init__.py"
Cohesion: 0.10
Nodes (15): extract_ohlc_from_all_timeframes(), extract_ohlc_from_csv(), OHLCBar, OHLC data extractor — parses CSV candle data into structured OHLCBar objects.  P, Parse CSV candle data into a list of OHLCBar objects.      Uses the shared :func, Extract OHLC bars for all timeframes from a mapping of CSV strings.      Args:, Tests for OHLC extractor., An empty CSV in any timeframe propagates ValueError. (+7 more)

### Community 18 - "src/orchestrator/__init__.py"
Cohesion: 0.27
Nodes (12): _cache_path(), _candle_period(), get_cache_date(), _get_settings(), datetime, Determine if analysis should run for this timeframe.      Args:         timefram, Compute cache file path.      Args:         timeframe: "D1", "H4", or "H1", Compute the start and end of a candle period.      Args:         timeframe: "D1" (+4 more)

### Community 19 - "tests/calendar/__init__.py"
Cohesion: 0.10
Nodes (17): Any, Select the canonical current price across timeframes.      The canonical current, Build a compact version of structure analysis suitable for LLM prompts.      The, Initialize trading graph with dependencies.          Args:             data_prov, Build the LangGraph StateGraph., Fetch market data from MT5., Extract compact analytical fields from a single timeframe engine output.      Th, Evaluate calendar events. (+9 more)

### Community 20 - "tests/data/__init__.py"
Cohesion: 0.16
Nodes (13): _build_parser(), _format_field(), _format_field_int(), _get_decision_field(), _print_symbol_summary(), Any, Trading AI Agent - CLI Entry Point., Build the CLI argument parser.      Returns:         Configured ArgumentParser i (+5 more)

### Community 21 - "tests/decision/__init__.py"
Cohesion: 0.38
Nodes (4): Path, RunSummary, List all runs, optionally filtered by symbol and date range.          Returns so, Parse a result JSON file into a RunSummary.          Path convention: data/YYYY/

### Community 22 - "tests/__init__.py"
Cohesion: 0.15
Nodes (12): Synthesizes market context from structure analysis and calendar., SynthesizerAgent, Tests for API key and base_url passthrough in agents., When a pre-built client is provided, base_url must be ignored., SynthesizerAgent must pass both api_key and base_url when provided., Empty string → None conversion in main.py (same pattern as api_key/base_url)., Agent must accept None reasoning_effort without error., Agent must accept empty string reasoning_effort (though main.py converts it). (+4 more)

### Community 23 - "tests/orchestrator/__init__.py"
Cohesion: 0.12
Nodes (13): Per-call cost logging for synthesizer, decider, and reviewer agents.      These, Build a mock raw_response with a usable .usage attribute., Build a mock raw_response with usage set to None., SynthesizerAgent must log prompt_tokens, completion_tokens and total_tokens., SynthesizerAgent must log cost=$ with a numeric value., DeciderAgent must log token usage after decide()., ReviewerAgent must log token usage after review()., Agents must call create_with_completion, not create. (+5 more)

### Community 24 - "_make_mcp_tool_result"
Cohesion: 0.09
Nodes (22): DOM, DOM.Iterable, env.d.ts, ES2022, src/**/*.ts, src/**/*.vue, compilerOptions, baseUrl (+14 more)

### Community 25 - "TerminalApiError"
Cohesion: 0.17
Nodes (12): Walk the data directory tree, read/parse JSON result files,     filter/sort into, ResultScanner, Path, Unit tests for ResultScanner., Helper to write a result JSON file., Files not in YYYY/MM/DD/SYMBOL/ pattern are skipped., When JSON has a 'symbol' field, it overrides the path-derived symbol., Tests for ResultScanner.get_run(). (+4 more)

### Community 26 - "test_terminal_data_provider.py"
Cohesion: 0.23
Nodes (11): load_ohlc_cache(), OHLCBar, Save OHLC bars to cache, same directory structure as analysis cache.      Args:, Load cached OHLC bars from disk if available.      Args:         timeframe: "D1", save_ohlc_cache(), OHLCBar, Single OHLC bar for chart rendering., Path (+3 more)

### Community 27 - "TestGetCandlesBrokerNow"
Cohesion: 0.18
Nodes (10): Writes analysis results to JSON files in the data/ directory tree., ResultWriter, Path, Tests for ResultWriter., When there are errors but no fatal_error, status should be 'partial'., OHLC bars appear in the output JSON under 'ohlc'., SL/TP overlay is populated from decision when available., SL/TP overlay fields are None when there is no decision. (+2 more)

### Community 29 - "._run_async"
Cohesion: 0.18
Nodes (10): OHLCData, BaseModel, OHLC data keyed by timeframe., Entry, stop-loss and take-profit overlay for charts., SLTPOverlay, Tests for output result models., ints passed to float fields are promoted to float., TestOHLCBar (+2 more)

### Community 30 - "TestGetPendingOrders"
Cohesion: 0.10
Nodes (3): TestDeciderPrompt, TestReviewerPrompt, TestSynthesizerPrompt

### Community 31 - "TestGetSymbolPrice"
Cohesion: 0.17
Nodes (10): main(), Main entry point.      Accepts one or more trading symbols, runs the analysis pi, Test that --telegram flag triggers notifications for approved setups., With --telegram flag, notification is sent for approved buy/sell setups., Without --telegram flag, no notification code executes., With --telegram, notification is NOT sent when action is no_trade., With --telegram, notification is NOT sent when review is not approved., Warning is logged when --telegram is set but token/chat_id are empty. (+2 more)

### Community 32 - "setup_logging"
Cohesion: 0.14
Nodes (13): EnvSettingsSource, _CommaDelimitedEnvSource, Any, BaseSettings, Path, Server-specific settings using Pydantic BaseSettings., Env source that parses comma-separated values for list fields.      pydantic-set, Split comma-separated env values for known list fields. (+5 more)

### Community 33 - "MarketContextSummary"
Cohesion: 0.16
Nodes (10): ForexFactoryCalendar, Any, Convert raw time text to ISO timestamp (best-effort)., Map raw impact text to standard impact level., Economic calendar provider via ForexFactory scraping., Initialize calendar provider.          Args:             cache_hours: Hours to c, Fetch upcoming economic calendar events.          Returns:             List of e, Check if cache is still valid. (+2 more)

### Community 34 - "setup_logging"
Cohesion: 0.17
Nodes (9): _log_llm_call(), Any, Record an LLM call and log its cost. Returns cost or None if no usage., Tests for agent cost-logging helper extraction., _log_llm_call extracts duplicated cost-logging from agents., When usage is provided, logs cost details., When usage is None, logs N/A., Records the call on the cost tracker when usage is provided. (+1 more)

### Community 35 - "DecisionOutput"
Cohesion: 0.17
Nodes (5): useRun(), FullResult, { result, loading, error }, route, router

### Community 37 - "_select_canonical_current_price"
Cohesion: 0.26
Nodes (7): MarketStructureEngine, Any, Concrete adapter implementing StructureAnalyzer.      Wraps the module-level ana, Analyze market structure from snapshots.          Args:             snapshots: D, Build engine request from snapshots., Delegate analysis to the engine., Validate engine output.

### Community 38 - "AgentState"
Cohesion: 0.17
Nodes (7): reasoning_effort is a create()-level kwarg, not an OpenAI() constructor arg., When reasoning_effort is set, it must appear in client.create() kwargs., When reasoning_effort is None, the key must be absent from create() kwargs., When reasoning_effort is explicitly None, key absent from create() kwargs., DeciderAgent passes reasoning_effort to create()., ReviewerAgent passes reasoning_effort to create()., TestReasoningEffortPassthrough

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
Cohesion: 0.23
Nodes (5): AnalysisResult, Top-level pipeline output serialized to JSON for the web viewer., Critical invariant: entry_authorized must always be False., Full-featured AnalysisResult with all optional fields set., TestAnalysisResult

### Community 47 - "test_analyze_structure_passes_broker_time_to_snapshot_builder"
Cohesion: 0.25
Nodes (7): Agent Instructions, Architecture, Critical Invariants, graphify, Quick Commands, Testing, Toolchain

### Community 48 - "test_analyze_structure_fetches_all_timeframes"
Cohesion: 0.25
Nodes (7): Reset the _settings sentinel in candle_cache before each test.      Tests use mo, Reset the _settings sentinel in synthesizer_cache before each test.      Mirrors, reset_candle_cache_settings(), reset_synthesizer_cache_settings(), sample_decision(), sample_market_context(), sample_review()

### Community 49 - "test_analyze_structure_full_cache_hit"
Cohesion: 0.22
Nodes (6): biasArrow, biasColor, emit, props, useRuns(), RunSummary

### Community 50 - "main.py"
Cohesion: 0.14
Nodes (9): DeciderAgent, Makes trading decisions based on market context., SynthesizerAgent must accept reasoning_effort param., When not specified, reasoning_effort defaults to None., DeciderAgent must accept reasoning_effort param., ReviewerAgent must accept reasoning_effort param., DeciderAgent must pass api_key to OpenAI constructor., DeciderAgent must pass base_url to OpenAI constructor. (+1 more)

### Community 54 - "main.py"
Cohesion: 0.09
Nodes (19): Spawn Python subprocess to run analysis, enforce timeout,     capture stderr, an, Run analysis for the given symbols.          Spawns: python main.py --output-dir, Spawn the Python process and wait for completion.          On timeout the proces, Walk the data directory via ResultScanner and return the         most recent res, RunService, _mock_process(), Unit tests for RunService., Process should be killed on timeout. (+11 more)

### Community 56 - "TestSynthesizeContextCanonicalPrice"
Cohesion: 0.17
Nodes (7): End-to-end: reasoning_effort flows from constructor → create() kwargs., synthesize() must include reasoning_effort in create_with_completion kwargs when, Must NOT include reasoning_effort in create_with_completion kwargs when None., decide() must include reasoning_effort in create_with_completion() kwargs when s, review() must include reasoning_effort in create_with_completion() kwargs when s, Pre-built client: reasoning_effort still flows to create_with_completion()., TestReasoningEffortIntegration

### Community 57 - "TestOhlcCachePath"
Cohesion: 0.13
Nodes (10): mock_decider(), mock_reviewer(), mock_synthesizer(), RED-first tests for orchestrator-level synthesizer cache integration.  Tests ver, CostTracker integration — cache hit must not call LLM so     ``cost_tracker.call, Cache miss → cost_tracker.call_count == 1 (one LLM call recorded)., Reset the ``_settings`` sentinel in ``synthesizer_cache`` before each test., reset_synthesizer_cache_settings() (+2 more)

### Community 59 - "AgentState"
Cohesion: 0.17
Nodes (7): Tests for reasoning_effort logging in agent __init__ methods., SynthesizerAgent must log reasoning_effort at init., SynthesizerAgent must log reasoning_effort even when None., DeciderAgent must log reasoning_effort at init., ReviewerAgent must log reasoning_effort at init., Log message must include the agent class name., TestReasoningEffortLogging

### Community 76 - "DecisionOutput"
Cohesion: 0.24
Nodes (5): DecisionOutput, BaseModel, Decision output from decider agent., TestDecisionOutput, mock_decider()

### Community 80 - "test_cache_path_d1_uses_folder_date_not_broker_now"
Cohesion: 0.13
Nodes (15): FastAPI, create_app(), FastAPI application entry point — port of the TypeScript Express server., Create and configure the FastAPI application., ErrorBody, BaseModel, Server-specific Pydantic models., Request body for POST /api/run. (+7 more)

### Community 81 - ".write"
Cohesion: 0.24
Nodes (6): Any, datetime, OHLCBar, Path, Write result JSON to disk. Returns the file path written.          Args:, Compute data/YYYY/MM/DD/SYMBOL/result-HH-MM.json path.

### Community 84 - "setup_logging"
Cohesion: 0.33
Nodes (3): Configure structured logging for the trading agent., setup_logging(), TestSetupLogging

### Community 85 - "test_h1_candle_period"
Cohesion: 0.12
Nodes (15): BiasLevel, DecisionAction, Structural bias levels., Review verdict from reviewer agent., ReviewVerdict, TestReviewVerdict, mock_reviewer(), TestMaxReviewAttempts (+7 more)

### Community 86 - "TestAgentApiKey"
Cohesion: 0.14
Nodes (8): Reviews trading decisions and provides feedback., ReviewerAgent, ReviewerAgent must pass api_key to OpenAI constructor., When no api_key given, OpenAI() uses its own default., SynthesizerAgent must pass api_key to OpenAI constructor., ReviewerAgent must pass base_url to OpenAI constructor., TestAgentApiKey, OpenAI

### Community 87 - "test_result_pipeline_writes_json"
Cohesion: 0.28
Nodes (8): Path, End-to-end integration test for the result JSON pipeline., Pipeline with fatal error produces valid error result., Result with no OHLC data produces empty arrays., Full pipeline simulation writes valid JSON result., test_empty_ohlc_defaults(), test_result_pipeline_writes_json(), test_result_with_fatal_error()

### Community 88 - "send_trade_notification"
Cohesion: 0.19
Nodes (6): Any, Telegram notification sender — best-effort, never blocks the pipeline., Send a compact trade notification to Telegram.      Best-effort: logs warning on, send_trade_notification(), Tests for telegram_sender module., TestSendTradeNotification

### Community 98 - "server/tests/conftest.py"
Cohesion: 0.15
Nodes (13): mock_data_dir(), Path, RunSummary, Shared fixtures for server tests., Create a ResultScanner pointing at the mock data directory., Create a RunService with test defaults., Sample RunSummary matching the Python model shape., Sample FullResult matching AnalysisResult.model_dump(mode='json') shape. (+5 more)

### Community 99 - "TestPostRun"
Cohesion: 0.25
Nodes (3): Exception, Tests for GET /api/runs/{symbol}/{year}/{month}/{day}/{file}., TestGetRun

### Community 103 - "test_d1_candle_period_before_close"
Cohesion: 0.17
Nodes (3): Tests for POST /api/run., Symbols must be 1-20 alphanumeric characters., TestPostRun

### Community 105 - "create_app"
Cohesion: 0.33
Nodes (3): client(), Route-level tests with mocked scanner/runner., Create a test client with mocked scanner and runner.

### Community 107 - "TestListRunsIntegration"
Cohesion: 0.50
Nodes (3): EngineError, Any, Base class for deterministic engine errors.

### Community 114 - "TestFatalError"
Cohesion: 0.12
Nodes (16): AgentState, State for the trading graph., Conditional edge from review to decide or end., _canonical_structure_analysis(), Build a structure_analysis fixture whose H1 timeframe has the     most-recent cl, _synthesize_context must compute the canonical current price from         the pe, Even when the LLM-returned summary has current_price=None, the         orchestra, get_broker_time() should be called once in _analyze_structure and     reused in (+8 more)

## Knowledge Gaps
- **122 isolated node(s):** `trading-ai-agent`, `trading-server`, `*.vue`, `name`, `version` (+117 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main()` connect `TestGetSymbolPrice` to `MarketContextSummary`, `DataSource`, `AgentState`, `_select_canonical_current_price`, `ForexFactoryCalendar`, `AgentState`, `src/data/__init__.py`, `main.py`, `tests/data/__init__.py`, `setup_logging`, `TestAgentApiKey`, `tests/__init__.py`, `send_trade_notification`, `TestGetCandlesBrokerNow`?**
  _High betweenness centrality (0.141) - this node is a cross-community bridge._
- **Why does `AgentState` connect `TestFatalError` to `DataSource`, `AgentState`, `Evaluator`, `TestCostTracking`, `ForexFactoryCalendar`, `DecisionOutput`, `trading-ai-agent`, `tests/calendar/__init__.py`, `test_h1_candle_period`, `TestOhlcCachePath`, `test_terminal_data_provider.py`?**
  _High betweenness centrality (0.129) - this node is a cross-community bridge._
- **Why does `get_profile()` connect `TestFatalError` to `Evaluator`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Are the 72 inferred relationships involving `MarketContextSummary` (e.g. with `DeciderAgent` and `ReviewerAgent`) actually correct?**
  _`MarketContextSummary` has 72 INFERRED edges - model-reasoned connections that need verification._
- **Are the 56 inferred relationships involving `AgentState` (e.g. with `Settings` and `DecisionOutput`) actually correct?**
  _`AgentState` has 56 INFERRED edges - model-reasoned connections that need verification._
- **Are the 60 inferred relationships involving `DecisionOutput` (e.g. with `DeciderAgent` and `ReviewerAgent`) actually correct?**
  _`DecisionOutput` has 60 INFERRED edges - model-reasoned connections that need verification._
- **Are the 56 inferred relationships involving `ReviewVerdict` (e.g. with `DeciderAgent` and `ReviewerAgent`) actually correct?**
  _`ReviewVerdict` has 56 INFERRED edges - model-reasoned connections that need verification._
