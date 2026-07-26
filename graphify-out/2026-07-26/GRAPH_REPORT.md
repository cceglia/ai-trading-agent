# Graph Report - Agent  (2026-07-26)

## Corpus Check
- 110 files · ~48,486 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1413 nodes · 2682 edges · 89 communities (66 shown, 23 thin omitted)
- Extraction: 72% EXTRACTED · 28% INFERRED · 0% AMBIGUOUS · INFERRED: 760 edges (avg confidence: 0.68)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6ebceb67`
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
- test_analyze_structure_fetches_all_when_no_cache
- test_h4_candle_period_at_boundary
- AgentState
- test_analyze_structure_uses_broker_time_not_utc
- _make_tracking_side_effect
- PriceCard.vue
- test_cache_path_d1_uses_folder_date_not_broker_now
- test_should_run_h4_without_cache
- test_should_run_d1_after_close_with_cache
- test_cache_path_d1_no_hour_suffix
- test_should_run_h1_without_cache
- test_cache_path_h4_includes_closing_hour
- test_cache_path_mtf
- test_cache_path_zero_padded_hour
- test_d1_candle_period_before_close

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
- `createRunsRouter()` --indirect_call--> `day()`  [INFERRED]
  server/src/routes/runs.ts → ui/src/views/Detail.vue
- `createRunsRouter()` --indirect_call--> `file()`  [INFERRED]
  server/src/routes/runs.ts → ui/src/views/Detail.vue
- `createRunsRouter()` --indirect_call--> `month()`  [INFERRED]
  server/src/routes/runs.ts → ui/src/views/Detail.vue
- `createRunsRouter()` --indirect_call--> `symbol()`  [INFERRED]
  server/src/routes/runs.ts → ui/src/views/Detail.vue
- `createRunsRouter()` --indirect_call--> `year()`  [INFERRED]
  server/src/routes/runs.ts → ui/src/views/Detail.vue

## Import Cycles
- None detected.

## Communities (89 total, 23 thin omitted)

### Community 0 - "TestFatalError"
Cohesion: 0.05
Nodes (93): analyze_candles(), _classify_engulfing(), Any, get_profile(), Any, TimeframeProfile, build_confluence(), build_timeframe_context() (+85 more)

### Community 1 - "Mt5DataProvider"
Cohesion: 0.07
Nodes (49): _cache_path(), _get_cache_date(), _get_settings(), load_cached_synthesis(), Any, datetime, Path, File-based cache for SynthesizerAgent output, keyed by (symbol, broker-day).  Mi (+41 more)

### Community 2 - "DataSource"
Cohesion: 0.06
Nodes (35): Trading agent configuration., Parse JSON string env var and validate all prices are non-negative., Settings, test_settings_has_analysis_cache_dir(), test_settings_has_d1_close_time(), test_settings_has_h4_close_interval_hours(), test_settings_has_h4_close_time(), MonkeyPatch (+27 more)

### Community 3 - "AgentState"
Cohesion: 0.06
Nodes (43): LangGraph orchestrator for trading analysis., Conditional edge from review to decide or end., TradingGraph, mock_decider(), mock_reviewer(), mock_synthesizer(), H1 analysis must now be saved to cache like D1/H4., If get_broker_time() fails, _analyze_structure should set fatal_error. (+35 more)

### Community 4 - "SnapshotBuilder"
Cohesion: 0.07
Nodes (19): Evaluator, Any, datetime, Check if an event falls within the time window from now.          Returns False, Evaluate events for symbol with timeframe-dependent window.          Args:, Evaluates calendar events for trading symbols., High-impact event outside the window should NOT block., High-impact event within the window SHOULD block. (+11 more)

### Community 5 - "Evaluator"
Cohesion: 0.09
Nodes (25): app, port, runner, scanner, createRunRouter(), createRunsRouter(), RunService, ResultScanner (+17 more)

### Community 6 - "Trading AI Agent"
Cohesion: 0.05
Nodes (31): chartOption, props, biasArrow, biasColor, emit, props, emit, emit (+23 more)

### Community 7 - "TestSynthesizerPrompt"
Cohesion: 0.08
Nodes (19): CalendarProvider, DataSource, Any, datetime, Analyze market structure from snapshots.          Args:             snapshots: D, Fetch OHLC candles as CSV string.          Args:             symbol: Trading sym, Get latest price info for a symbol.          Args:             symbol: Trading s, Get open positions.          Args:             symbol: Optional symbol filter (+11 more)

### Community 8 - "TestCostTracking"
Cohesion: 0.09
Nodes (26): _canonical_structure_analysis(), _make_cached_summary(), datetime, Cache hit → cost_tracker.call_count == 0 (no LLM call recorded)., Cache miss → cost_tracker.call_count == 1 (one LLM call recorded)., 5 sequential runs on same symbol/day → exactly 1 LLM call.          First run: c, Build a ``MarketContextSummary`` that looks like it came from the cache., Minimal ``structure_analysis`` with H1 as most-recently-closed timeframe. (+18 more)

### Community 9 - "ForexFactoryCalendar"
Cohesion: 0.06
Nodes (21): CostTracker, CostTracker — tracks LLM API call costs.  Exposes a single :class:`CostTracker`, Reset accumulated cost and call count to zero., Tracks LLM API call costs using per-model token pricing.      Each instance is i, Record an LLM API call and return its cost.          Parameters         --------, Accumulated cost across all recorded calls., Number of calls recorded., Tests for CostTracker — tracks LLM API call costs.  CostTracker lives in ``src/d (+13 more)

### Community 10 - "TestProjectFiles"
Cohesion: 0.08
Nodes (22): Synthesizes market context from structure analysis and calendar., SynthesizerAgent, Tests for API key and base_url passthrough in agents., When a pre-built client is provided, base_url must be ignored., SynthesizerAgent must pass both api_key and base_url when provided., reasoning_effort is a create()-level kwarg, not an OpenAI() constructor arg., When reasoning_effort is set, it must appear in client.create() kwargs., When reasoning_effort is None, the key must be absent from create() kwargs. (+14 more)

### Community 11 - "Agent Instructions"
Cohesion: 0.06
Nodes (23): EngineError, Any, Base class for deterministic engine errors., CaptureFixture, Tests for multi-symbol support in main.py., Verify main() calls graph.run() for each symbol., _build_parser accepts multiple symbols as nargs+., When one symbol fails, main() continues with remaining symbols. (+15 more)

### Community 12 - "config/__init__.py"
Cohesion: 0.05
Nodes (36): autoprefixer, axios, echarts, postcss, tailwindcss, dependencies, axios, echarts (+28 more)

### Community 13 - "trading-ai-agent"
Cohesion: 0.10
Nodes (17): MarketContextSummary, Summary of market context from synthesizer agent., _make_raw_response(), Tests for prompt usage in agents., SynthesizerAgent.synthesize must accept current_price/current_price_time kwargs., User prompt must render current_price and current_price_time values., Build a mock raw_response with a usable .usage attribute., When no price is supplied, the current-price line must state None. (+9 more)

### Community 14 - "src/calendar/__init__.py"
Cohesion: 0.09
Nodes (22): At exact H1 boundary, period starts at that time., H4 cache date includes the closing hour in cache_date.hour., H4 should skip analysis when cache file exists for that period., D1 before close should always run analysis (candle not closed)., D1 after close without cache should run analysis., Verify the path check uses the correct folder date, not a stale one., H1 should skip analysis when cache file exists for that period., H1 filename includes the closing hour (e.g. h1-14-analysis.json). (+14 more)

### Community 15 - "src/data/__init__.py"
Cohesion: 0.06
Nodes (34): cors, dotenv, express, dependencies, cors, dotenv, express, devDependencies (+26 more)

### Community 16 - "src/decision/__init__.py"
Cohesion: 0.06
Nodes (34): Analysis Layer (`src/analysis/`), Architecture, Calendar Layer (`src/calendar/`), CLI, Code Quality, Components, Configuration, Configuration (`config/`) (+26 more)

### Community 17 - "src/__init__.py"
Cohesion: 0.10
Nodes (15): extract_ohlc_from_all_timeframes(), extract_ohlc_from_csv(), OHLCBar, OHLC data extractor — parses CSV candle data into structured OHLCBar objects.  P, Parse CSV candle data into a list of OHLCBar objects.      Uses the shared :func, Extract OHLC bars for all timeframes from a mapping of CSV strings.      Args:, Tests for OHLC extractor., An empty CSV in any timeframe propagates ValueError. (+7 more)

### Community 18 - "src/orchestrator/__init__.py"
Cohesion: 0.09
Nodes (26): load_cached_analysis(), Any, Save analysis result to disk.      Args:         timeframe: "D1", "H4", or "H1", Load cached analysis from disk if available.      Args:         timeframe: "D1",, save_analysis(), Analyze market structure with candle-aligned caching.          The multi-timefra, D1 save then load returns identical dict (round-trip fidelity)., H4 save then load returns identical dict. (+18 more)

### Community 19 - "tests/calendar/__init__.py"
Cohesion: 0.10
Nodes (17): Any, Select the canonical current price across timeframes.      The canonical current, Build a compact version of structure analysis suitable for LLM prompts.      The, Initialize trading graph with dependencies.          Args:             data_prov, Build the LangGraph StateGraph., Fetch market data from MT5., Extract compact analytical fields from a single timeframe engine output.      Th, Evaluate calendar events. (+9 more)

### Community 20 - "tests/data/__init__.py"
Cohesion: 0.11
Nodes (16): _build_parser(), _format_field(), _format_field_int(), _get_decision_field(), _print_symbol_summary(), Any, Trading AI Agent - CLI Entry Point., Build the CLI argument parser.      Returns:         Configured ArgumentParser i (+8 more)

### Community 21 - "tests/decision/__init__.py"
Cohesion: 0.17
Nodes (7): End-to-end: reasoning_effort flows from constructor → create() kwargs., synthesize() must include reasoning_effort in create_with_completion kwargs when, Must NOT include reasoning_effort in create_with_completion kwargs when None., decide() must include reasoning_effort in create_with_completion() kwargs when s, review() must include reasoning_effort in create_with_completion() kwargs when s, Pre-built client: reasoning_effort still flows to create_with_completion()., TestReasoningEffortIntegration

### Community 22 - "tests/__init__.py"
Cohesion: 0.06
Nodes (23): main(), Main entry point.      Accepts one or more trading symbols, runs the analysis pi, DeciderAgent, Makes trading decisions based on market context., Reviews trading decisions and provides feedback., ReviewerAgent, SynthesizerAgent must accept reasoning_effort param., When not specified, reasoning_effort defaults to None. (+15 more)

### Community 23 - "tests/orchestrator/__init__.py"
Cohesion: 0.12
Nodes (13): Per-call cost logging for synthesizer, decider, and reviewer agents.      These, Build a mock raw_response with a usable .usage attribute., Build a mock raw_response with usage set to None., SynthesizerAgent must log prompt_tokens, completion_tokens and total_tokens., SynthesizerAgent must log cost=$ with a numeric value., DeciderAgent must log token usage after decide()., ReviewerAgent must log token usage after review()., Agents must call create_with_completion, not create. (+5 more)

### Community 24 - "_make_mcp_tool_result"
Cohesion: 0.09
Nodes (22): DOM, DOM.Iterable, env.d.ts, ES2022, src/**/*.ts, src/**/*.vue, compilerOptions, baseUrl (+14 more)

### Community 26 - "test_terminal_data_provider.py"
Cohesion: 0.19
Nodes (13): _get_settings(), load_ohlc_cache(), ohlc_cache_path(), datetime, OHLCBar, Compute OHLC cache file path, parallel to analysis cache.      Cache path conven, Save OHLC bars to cache, same directory structure as analysis cache.      Args:, Load cached OHLC bars from disk if available.      Args:         timeframe: "D1" (+5 more)

### Community 27 - "TestGetCandlesBrokerNow"
Cohesion: 0.18
Nodes (10): Writes analysis results to JSON files in the data/ directory tree., ResultWriter, Path, Tests for ResultWriter., When there are errors but no fatal_error, status should be 'partial'., OHLC bars appear in the output JSON under 'ohlc'., SL/TP overlay is populated from decision when available., SL/TP overlay fields are None when there is no decision. (+2 more)

### Community 28 - "TestGetPositions"
Cohesion: 0.10
Nodes (20): dist, node_modules, src/**/*, **/__tests__/**, compilerOptions, declaration, declarationMap, esModuleInterop (+12 more)

### Community 30 - "TestGetPendingOrders"
Cohesion: 0.10
Nodes (3): TestDeciderPrompt, TestReviewerPrompt, TestSynthesizerPrompt

### Community 31 - "TestGetSymbolPrice"
Cohesion: 0.13
Nodes (8): DecisionOutput, BaseModel, Decision output from decider agent., Review verdict from reviewer agent., ReviewVerdict, TestDecisionOutput, TestReviewVerdict, TestReviewRouting

### Community 32 - "setup_logging"
Cohesion: 0.13
Nodes (14): AgentState, State for the trading graph., _analyze_structure must fetch all three timeframes fresh (no partial cache)., _analyze_structure must call get_broker_time() instead of datetime.now(UTC)., Corrupt per-TF cache file must not crash — fall back to fresh fetch., test_analyze_structure_corrupt_cache_fallback(), test_analyze_structure_fetches_all_timeframes(), test_analyze_structure_uses_broker_time_not_utc() (+6 more)

### Community 33 - "MarketContextSummary"
Cohesion: 0.16
Nodes (10): ForexFactoryCalendar, Any, Convert raw time text to ISO timestamp (best-effort)., Map raw impact text to standard impact level., Economic calendar provider via ForexFactory scraping., Initialize calendar provider.          Args:             cache_hours: Hours to c, Fetch upcoming economic calendar events.          Returns:             List of e, Check if cache is still valid. (+2 more)

### Community 34 - "setup_logging"
Cohesion: 0.17
Nodes (9): _log_llm_call(), Any, Record an LLM call and log its cost. Returns cost or None if no usage., Tests for agent cost-logging helper extraction., _log_llm_call extracts duplicated cost-logging from agents., When usage is provided, logs cost details., When usage is None, logs N/A., Records the call on the cost tracker when usage is provided. (+1 more)

### Community 35 - "DecisionOutput"
Cohesion: 0.19
Nodes (12): OHLCBar, OHLCData, BaseModel, Single OHLC bar for chart rendering., OHLC data keyed by timeframe., Entry, stop-loss and take-profit overlay for charts., SLTPOverlay, Tests for output result models. (+4 more)

### Community 36 - "TestRepeatedRuns"
Cohesion: 0.11
Nodes (14): mock_decider(), mock_reviewer(), mock_synthesizer(), Path, RED-first tests for orchestrator-level synthesizer cache integration.  Tests ver, Reset the ``_settings`` sentinel in ``synthesizer_cache`` before each test., Write arbitrary content to the synthesizer cache path.      This lets us simulat, When the cache is disabled, corrupt, or has bad pydantic data.      The orchestr (+6 more)

### Community 37 - "_select_canonical_current_price"
Cohesion: 0.26
Nodes (7): MarketStructureEngine, Any, Concrete adapter implementing StructureAnalyzer.      Wraps the module-level ana, Analyze market structure from snapshots.          Args:             snapshots: D, Build engine request from snapshots., Delegate analysis to the engine., Validate engine output.

### Community 38 - "AgentState"
Cohesion: 0.23
Nodes (5): AnalysisResult, Top-level pipeline output serialized to JSON for the web viewer., Critical invariant: entry_authorized must always be False., Full-featured AnalysisResult with all optional fields set., TestAnalysisResult

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
Cohesion: 0.27
Nodes (12): _cache_path(), _candle_period(), get_cache_date(), _get_settings(), datetime, Determine if analysis should run for this timeframe.      Args:         timefram, Compute cache file path.      Args:         timeframe: "D1", "H4", or "H1", Compute the start and end of a candle period.      Args:         timeframe: "D1" (+4 more)

### Community 46 - "BiasLevel"
Cohesion: 0.21
Nodes (10): BiasLevel, DecisionAction, Structural bias levels., TestMaxReviewAttempts, TestTradingGraphInit, CostTracker integration — cache hit must not call LLM so     ``cost_tracker.call, Multiple invocations within a day — only the first miss calls the LLM., TestCostTracking (+2 more)

### Community 47 - "test_analyze_structure_passes_broker_time_to_snapshot_builder"
Cohesion: 0.25
Nodes (7): Agent Instructions, Architecture, Critical Invariants, graphify, Quick Commands, Testing, Toolchain

### Community 48 - "test_analyze_structure_fetches_all_timeframes"
Cohesion: 0.25
Nodes (7): Reset the _settings sentinel in candle_cache before each test.      Tests use mo, Reset the _settings sentinel in synthesizer_cache before each test.      Mirrors, reset_candle_cache_settings(), reset_synthesizer_cache_settings(), sample_decision(), sample_market_context(), sample_review()

### Community 49 - "test_analyze_structure_full_cache_hit"
Cohesion: 0.29
Nodes (6): _make_tracking_side_effect(), Create a side effect that records an LLM call on the shared CostTracker.      Th, Tests for CostTracker wiring in TradingGraph.run().      These tests verify that, Run TradingGraph with mocked agents that have a shared CostTracker,         asse, Verify that a CostTracker instance can be shared across all 3 agents         and, TestCostTrackerWiring

### Community 50 - "main.py"
Cohesion: 0.25
Nodes (3): Tests for OHLC bar cache., Full path follows analysis/YYYY/MM/DD/SYMBOL/ pattern., TestOhlcCachePath

### Community 53 - ".write"
Cohesion: 0.24
Nodes (6): Any, datetime, OHLCBar, Path, Write result JSON to disk. Returns the file path written.          Args:, Compute data/YYYY/MM/DD/SYMBOL/result-HH-MM.json path.

### Community 55 - "test_result_pipeline_writes_json"
Cohesion: 0.28
Nodes (8): Path, End-to-end integration test for the result JSON pipeline., Pipeline with fatal error produces valid error result., Result with no OHLC data produces empty arrays., Full pipeline simulation writes valid JSON result., test_empty_ohlc_defaults(), test_result_pipeline_writes_json(), test_result_with_fatal_error()

### Community 56 - "TestSynthesizeContextCanonicalPrice"
Cohesion: 0.25
Nodes (7): _canonical_structure_analysis(), Build a structure_analysis fixture whose H1 timeframe has the     most-recent cl, _synthesize_context must compute the canonical current price from         the pe, Even when the LLM-returned summary has current_price=None, the         orchestra, get_broker_time() should be called once in _analyze_structure and     reused in, test_get_broker_time_called_once_per_run(), TestSynthesizeContextCanonicalPrice

## Knowledge Gaps
- **157 isolated node(s):** `trading-ai-agent`, `name`, `version`, `private`, `type` (+152 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_profile()` connect `TestFatalError` to `src/orchestrator/__init__.py`?**
  _High betweenness centrality (0.107) - this node is a cross-community bridge._
- **Why does `main()` connect `tests/__init__.py` to `MarketContextSummary`, `DataSource`, `AgentState`, `_select_canonical_current_price`, `ForexFactoryCalendar`, `TestProjectFiles`, `Agent Instructions`, `AgentState`, `tests/data/__init__.py`, `TestGetCandlesBrokerNow`?**
  _High betweenness centrality (0.105) - this node is a cross-community bridge._
- **Why does `TradingGraph` connect `AgentState` to `setup_logging`, `DataSource`, `DecisionOutput`, `TestRepeatedRuns`, `TestCostTracking`, `trading-ai-agent`, `BiasLevel`, `test_analyze_structure_full_cache_hit`, `src/orchestrator/__init__.py`, `tests/calendar/__init__.py`, `tests/__init__.py`, `TestSynthesizeContextCanonicalPrice`, `TestGetSymbolPrice`?**
  _High betweenness centrality (0.100) - this node is a cross-community bridge._
- **Are the 72 inferred relationships involving `MarketContextSummary` (e.g. with `DeciderAgent` and `ReviewerAgent`) actually correct?**
  _`MarketContextSummary` has 72 INFERRED edges - model-reasoned connections that need verification._
- **Are the 56 inferred relationships involving `AgentState` (e.g. with `Settings` and `DecisionOutput`) actually correct?**
  _`AgentState` has 56 INFERRED edges - model-reasoned connections that need verification._
- **Are the 60 inferred relationships involving `DecisionOutput` (e.g. with `DeciderAgent` and `ReviewerAgent`) actually correct?**
  _`DecisionOutput` has 60 INFERRED edges - model-reasoned connections that need verification._
- **Are the 56 inferred relationships involving `ReviewVerdict` (e.g. with `DeciderAgent` and `ReviewerAgent`) actually correct?**
  _`ReviewVerdict` has 56 INFERRED edges - model-reasoned connections that need verification._
