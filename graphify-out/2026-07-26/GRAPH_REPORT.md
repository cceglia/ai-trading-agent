# Graph Report - Agent  (2026-07-26)

## Corpus Check
- 48 files · ~29,942 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 926 nodes · 1883 edges · 54 communities (47 shown, 7 thin omitted)
- Extraction: 84% EXTRACTED · 16% INFERRED · 0% AMBIGUOUS · INFERRED: 292 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `55b51911`
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
- trading-ai-agent
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
- setup_logging
- graph.py
- _canonical_structure_analysis
- test_analyze_structure_fresh_saves_mtf_cache
- TestSettingsDescriptions
- test_analyze_structure_cache_hit_mtf_missing
- test_analyze_structure_passes_broker_time_to_snapshot_builder
- test_analyze_structure_fetches_all_timeframes
- test_analyze_structure_full_cache_hit
- BiasLevel
- orchestrator/test_synthesizer_cache.py
- main.py
- DeciderAgent
- main
- _make_tracking_side_effect

## God Nodes (most connected - your core abstractions)
1. `MarketContextSummary` - 77 edges
2. `AgentState` - 70 edges
3. `CostTracker` - 65 edges
4. `TradingGraph` - 61 edges
5. `DecisionOutput` - 56 edges
6. `ReviewVerdict` - 54 edges
7. `SynthesizerAgent` - 52 edges
8. `Settings` - 45 edges
9. `TerminalDataProvider` - 36 edges
10. `SnapshotBuilder` - 35 edges

## Surprising Connections (you probably didn't know these)
- `AgentState` --uses--> `Settings`  [INFERRED]
  src/orchestrator/graph.py → config/settings.py
- `TradingGraph` --uses--> `Settings`  [INFERRED]
  src/orchestrator/graph.py → config/settings.py
- `TestErrorHandling` --uses--> `Settings`  [INFERRED]
  tests/data/test_terminal_data_provider.py → config/settings.py
- `TestGetBrokerTime` --uses--> `Settings`  [INFERRED]
  tests/data/test_terminal_data_provider.py → config/settings.py
- `TestGetCandlesBrokerNow` --uses--> `Settings`  [INFERRED]
  tests/data/test_terminal_data_provider.py → config/settings.py

## Import Cycles
- None detected.

## Communities (54 total, 7 thin omitted)

### Community 0 - "TestFatalError"
Cohesion: 0.33
Nodes (4): When ``state.fatal_error`` is set, ``_synthesize_context`` short-circuits., fatal_error set \u2192 returns {} without checking cache or calling LLM., fatal_error set \u2192 cache is NOT written even if synthesizer runs.          N, TestFatalError

### Community 1 - "Mt5DataProvider"
Cohesion: 0.06
Nodes (31): BaseSettings, Parse JSON string env var and validate all prices are non-negative., Trading agent configuration., Settings, MonkeyPatch, config/settings.py should not contain commented-out pricing entries., Tests for the new synthesizer_cache_enabled Settings field.      RED phase: thes, synthesizer_cache_enabled defaults to True when no env var is set. (+23 more)

### Community 2 - "DataSource"
Cohesion: 0.09
Nodes (19): Protocol, CalendarProvider, DataSource, Any, datetime, Fetch OHLC candles as CSV string.          Args:             symbol: Trading sym, Get latest price info for a symbol.          Args:             symbol: Trading s, Get open positions.          Args:             symbol: Optional symbol filter (+11 more)

### Community 3 - "AgentState"
Cohesion: 0.06
Nodes (45): LangGraph orchestrator for trading analysis., TradingGraph, H1 analysis must now be saved to cache like D1/H4., If get_broker_time() fails, _analyze_structure should set fatal_error., get_candles must be called with broker_time param., snapshot_builder.build must be called with broker_time., AgentState must NOT have 'account_info'; it must have 'symbol_price' instead., AgentState must NOT have 'market_data' — the dead field was removed.      This v (+37 more)

### Community 4 - "SnapshotBuilder"
Cohesion: 0.08
Nodes (24): Any, datetime, Snapshot builder for converting MCP CSV data to normalized engine snapshots., Build normalized snapshot from parsed bars.          Args:             bars: Lis, Builds normalized snapshots from MCP CSV data.      Converts raw CSV candle data, Validate snapshot against engine schema.          Args:             snapshot: Th, Convert CSV to normalized snapshot.          Args:             csv_data: CSV str, Parse CSV string to list of bar dicts.          Args:             csv_data: Raw (+16 more)

### Community 5 - "Evaluator"
Cohesion: 0.07
Nodes (19): Evaluator, Any, datetime, Check if an event falls within the time window from now.          Returns False, Evaluate events for symbol with timeframe-dependent window.          Args:, Evaluates calendar events for trading symbols., High-impact event outside the window should NOT block., High-impact event within the window SHOULD block. (+11 more)

### Community 6 - "Trading AI Agent"
Cohesion: 0.07
Nodes (28): Analysis Layer (`src/analysis/`), Architecture, Calendar Layer (`src/calendar/`), CLI Commands, Code Quality, Components, Configuration, Configuration (`config/`) (+20 more)

### Community 7 - "TestSynthesizerPrompt"
Cohesion: 0.09
Nodes (4): LLM prompts with embedded rules.json content., TestDeciderPrompt, TestReviewerPrompt, TestSynthesizerPrompt

### Community 8 - "TestCostTracking"
Cohesion: 0.50
Nodes (3): CostTracker integration — cache hit must not call LLM so     ``cost_tracker.call, Cache miss → cost_tracker.call_count == 1 (one LLM call recorded)., TestCostTracking

### Community 9 - "ForexFactoryCalendar"
Cohesion: 0.16
Nodes (10): ForexFactoryCalendar, Any, Convert raw time text to ISO timestamp (best-effort)., Map raw impact text to standard impact level., Economic calendar provider via ForexFactory scraping., Initialize calendar provider.          Args:             cache_hours: Hours to c, Fetch upcoming economic calendar events.          Returns:             List of e, Check if cache is still valid. (+2 more)

### Community 11 - "Agent Instructions"
Cohesion: 0.25
Nodes (7): Agent Instructions, Architecture, Critical Invariants, graphify, Quick Commands, Testing, Toolchain

### Community 24 - "_make_mcp_tool_result"
Cohesion: 0.10
Nodes (10): _make_mcp_result(), Verify get_candles returns correctly formatted CSV., Create a mock object mimicking mcp.types.CallToolResult.      Matches the real s, Verify get_symbol_price returns price dict and sends correct request., Verify get_positions returns list of positions and sends correct request., Verify get_broker_time returns naive datetime and sends correct request., TestGetBrokerTime, TestGetCandlesCsv (+2 more)

### Community 25 - "TerminalApiError"
Cohesion: 0.23
Nodes (5): RuntimeError, Non-retryable server-side error from the terminal MCP server., TerminalApiError, Verify retry behaviour via _call_with_retry., TestRetryLogic

### Community 26 - "test_terminal_data_provider.py"
Cohesion: 0.13
Nodes (8): provider(), Tests for TerminalDataProvider — MCP Streamable HTTP data provider., Settings field descriptions should refer to broker time, not UTC., Verify get_pending_orders returns list of orders and sends correct request., Verify terminal_data_provider.py has no imports inside function bodies.      All, test_no_inline_imports(), TestGetPendingOrders, TestSettingsDescriptions

### Community 27 - "TestGetCandlesBrokerNow"
Cohesion: 0.20
Nodes (6): get_candles must accept a broker_now parameter for broker-local time., get_candles must use broker_now for lookback when provided., Without broker_now, get_candles uses datetime.now(UTC)., Explicit broker_now=None must use datetime.now(UTC)., get_candles must raise ValueError when broker_now has tzinfo., TestGetCandlesBrokerNow

### Community 28 - "TestGetPositions"
Cohesion: 0.17
Nodes (7): End-to-end: reasoning_effort flows from constructor → create() kwargs., synthesize() must include reasoning_effort in create_with_completion kwargs when, Must NOT include reasoning_effort in create_with_completion kwargs when None., decide() must include reasoning_effort in create_with_completion() kwargs when s, review() must include reasoning_effort in create_with_completion() kwargs when s, Pre-built client: reasoning_effort still flows to create_with_completion()., TestReasoningEffortIntegration

### Community 29 - "._run_async"
Cohesion: 0.11
Nodes (18): Any, Call an MCP tool via the persistent session.          Returns:             CallT, Call an MCP tool with retry on transient failures.          Args:             to, Extract text from CallToolResult.content[0].text., Extract candle history from CallToolResult.          The text payload is a JSON, Convert terminal candle list to CSV string.          CSV columns: time,open,high, Data provider using terminal MCP server via MCP Streamable HTTP protocol.      F, Extract candle history from MCP result and normalize to CSV. (+10 more)

### Community 30 - "TestGetPendingOrders"
Cohesion: 0.17
Nodes (7): Tests for reasoning_effort logging in agent __init__ methods., SynthesizerAgent must log reasoning_effort at init., SynthesizerAgent must log reasoning_effort even when None., DeciderAgent must log reasoning_effort at init., ReviewerAgent must log reasoning_effort at init., Log message must include the agent class name., TestReasoningEffortLogging

### Community 31 - "TestGetSymbolPrice"
Cohesion: 0.29
Nodes (4): datetime, Terminal MCP data provider via MCP Streamable HTTP protocol., Fetch OHLC candles from terminal MCP server.          Args:             symbol:, Fetch current broker server time from terminal MCP server.          Returns:

### Community 33 - "MarketContextSummary"
Cohesion: 0.15
Nodes (7): When a pre-built client is provided, base_url must be ignored., SynthesizerAgent must pass both api_key and base_url when provided., SynthesizerAgent must pass base_url to OpenAI constructor., DeciderAgent must pass base_url to OpenAI constructor., ReviewerAgent must pass base_url to OpenAI constructor., When no base_url given, OpenAI() uses its own default., TestAgentBaseUrl

### Community 36 - "TestRepeatedRuns"
Cohesion: 0.50
Nodes (3): Multiple invocations within a day — only the first miss calls the LLM., 5 sequential runs on same symbol/day → exactly 1 LLM call.          First run: c, TestRepeatedRuns

### Community 37 - "_select_canonical_current_price"
Cohesion: 0.33
Nodes (6): RED-first tests for the canonical current-price selection helper (TASK-6).  Thes, Lazy-import the not-yet-existing helper so collection succeeds.      Raises ``Im, Build a single per-timeframe engine-output dict for the selector., _select_canonical_current_price(), TestSelectCanonicalCurrentPrice, _tf()

### Community 38 - "AgentState"
Cohesion: 0.11
Nodes (14): CompiledStateGraph, AgentState, Any, State for the trading graph., Initialize trading graph with dependencies.          Args:             data_prov, Build the LangGraph StateGraph., Fetch market data from MT5., Analyze market structure with candle-aligned caching.          The multi-timefra (+6 more)

### Community 39 - "setup_logging"
Cohesion: 0.07
Nodes (20): CostTracker, Reset accumulated cost and call count to zero., Tracks LLM API call costs using per-model token pricing.      Each instance is i, Record an LLM API call and return its cost.          Parameters         --------, Accumulated cost across all recorded calls., Number of calls recorded., Tests for CostTracker — tracks LLM API call costs.  CostTracker lives in ``src/d, Zero tokens result in zero cost and call is NOT recorded. (+12 more)

### Community 40 - "graph.py"
Cohesion: 0.18
Nodes (9): _log_llm_call(), Any, Record an LLM call and log its cost. Returns cost or None if no usage., Tests for agent cost-logging helper extraction., _log_llm_call extracts duplicated cost-logging from agents., When usage is provided, logs cost details., When usage is None, logs N/A., Records the call on the cost tracker when usage is provided. (+1 more)

### Community 41 - "_canonical_structure_analysis"
Cohesion: 0.25
Nodes (7): _canonical_structure_analysis(), Build a structure_analysis fixture whose H1 timeframe has the     most-recent cl, _synthesize_context must compute the canonical current price from         the pe, Even when the LLM-returned summary has current_price=None, the         orchestra, get_broker_time() should be called once in _analyze_structure and     reused in, test_get_broker_time_called_once_per_run(), TestSynthesizeContextCanonicalPrice

### Community 44 - "test_analyze_structure_fresh_saves_mtf_cache"
Cohesion: 0.06
Nodes (58): _cache_path(), _get_cache_date(), _get_settings(), load_cached_synthesis(), Any, datetime, Path, File-based cache for SynthesizerAgent output, keyed by (symbol, broker-day).  Mi (+50 more)

### Community 46 - "test_analyze_structure_cache_hit_mtf_missing"
Cohesion: 0.07
Nodes (21): Synthesizes market context from structure analysis and calendar., SynthesizerAgent, Tests for API key and base_url passthrough in agents., SynthesizerAgent must accept reasoning_effort param., When not specified, reasoning_effort defaults to None., reasoning_effort is a create()-level kwarg, not an OpenAI() constructor arg., When reasoning_effort is set, it must appear in client.create() kwargs., DeciderAgent must pass api_key to OpenAI constructor. (+13 more)

### Community 47 - "test_analyze_structure_passes_broker_time_to_snapshot_builder"
Cohesion: 0.10
Nodes (24): _canonical_structure_analysis(), _make_cached_summary(), datetime, Cache hit → cost_tracker.call_count == 0 (no LLM call recorded)., Build a ``MarketContextSummary`` that looks like it came from the cache., Minimal ``structure_analysis`` with H1 as most-recently-closed timeframe., When the cache has a valid ``MarketContextSummary`` for (symbol, day).      The, Cache hit \u2192 ``_synthesize_context`` returns the cached summary (not LLM). (+16 more)

### Community 48 - "test_analyze_structure_fetches_all_timeframes"
Cohesion: 0.12
Nodes (13): Per-call cost logging for synthesizer, decider, and reviewer agents.      These, Build a mock raw_response with a usable .usage attribute., Build a mock raw_response with usage set to None., SynthesizerAgent must log prompt_tokens, completion_tokens and total_tokens., SynthesizerAgent must log cost=$ with a numeric value., DeciderAgent must log token usage after decide()., ReviewerAgent must log token usage after review()., Agents must call create_with_completion, not create. (+5 more)

### Community 51 - "BiasLevel"
Cohesion: 0.05
Nodes (46): BaseModel, BiasLevel, DecisionAction, DecisionOutput, MarketContextSummary, Structural bias levels., Summary of market context from synthesizer agent., Decision output from decider agent. (+38 more)

### Community 53 - "orchestrator/test_synthesizer_cache.py"
Cohesion: 0.13
Nodes (11): Path, RED-first tests for orchestrator-level synthesizer cache integration.  Tests ver, Reset the ``_settings`` sentinel in ``synthesizer_cache`` before each test., Write arbitrary content to the synthesizer cache path.      This lets us simulat, When the cache is disabled, corrupt, or has bad pydantic data.      The orchestr, Corrupt cache file \u2192 fall through to LLM, don't crash., Cache file with bad pydantic data \u2192 fall through to LLM., reset_synthesizer_cache_settings() (+3 more)

### Community 54 - "main.py"
Cohesion: 0.36
Nodes (3): Configure structured logging for the trading agent., setup_logging(), TestSetupLogging

### Community 56 - "DeciderAgent"
Cohesion: 0.16
Nodes (11): main(), Trading AI Agent - CLI Entry Point., OpenAI, DeciderAgent, Makes trading decisions based on market context., Reviews trading decisions and provides feedback., ReviewerAgent, CostTracker — tracks LLM API call costs.  Exposes a single :class:`CostTracker` (+3 more)

### Community 58 - "main"
Cohesion: 0.18
Nodes (8): CaptureFixture, Tests for main.py entry point — Issue #13 error duplication., Duplicate error-printing blocks in main.py (Issue #13).      The first block (li, main.py should not log 'Total LLM cost' — graph.run() already does., Verify errors are printed exactly once, not twice.          mocks:         - Set, main.py must not log 'Total LLM cost' — that's graph.run()'s job., TestMainCostLogging, TestMainErrorDuplication

### Community 61 - "_make_tracking_side_effect"
Cohesion: 0.33
Nodes (4): _make_tracking_side_effect(), Create a side effect that records an LLM call on the shared CostTracker.      Th, Run TradingGraph with mocked agents that have a shared CostTracker,         asse, Verify that a CostTracker instance can be shared across all 3 agents         and

## Knowledge Gaps
- **27 isolated node(s):** `trading-ai-agent`, `graphify`, `Quick Commands`, `Critical Invariants`, `Architecture` (+22 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `Mt5DataProvider` to `AgentState`, `DecisionOutput`, `AgentState`, `test_analyze_structure_fresh_saves_mtf_cache`, `DeciderAgent`, `_make_mcp_tool_result`, `test_terminal_data_provider.py`, `TestGetCandlesBrokerNow`, `TerminalApiError`?**
  _High betweenness centrality (0.186) - this node is a cross-community bridge._
- **Why does `MarketContextSummary` connect `BiasLevel` to `TestFatalError`, `MarketContextSummary`, `AgentState`, `TestRepeatedRuns`, `AgentState`, `graph.py`, `_canonical_structure_analysis`, `TestCostTracking`, `test_analyze_structure_fresh_saves_mtf_cache`, `test_analyze_structure_cache_hit_mtf_missing`, `test_analyze_structure_passes_broker_time_to_snapshot_builder`, `test_analyze_structure_fetches_all_timeframes`, `orchestrator/test_synthesizer_cache.py`, `DeciderAgent`, `TestGetPositions`, `TestGetPendingOrders`?**
  _High betweenness centrality (0.123) - this node is a cross-community bridge._
- **Why does `TradingGraph` connect `AgentState` to `TestFatalError`, `Mt5DataProvider`, `SnapshotBuilder`, `TestRepeatedRuns`, `AgentState`, `TestCostTracking`, `_canonical_structure_analysis`, `test_analyze_structure_fresh_saves_mtf_cache`, `test_analyze_structure_passes_broker_time_to_snapshot_builder`, `BiasLevel`, `orchestrator/test_synthesizer_cache.py`, `DeciderAgent`, `_make_tracking_side_effect`?**
  _High betweenness centrality (0.113) - this node is a cross-community bridge._
- **Are the 41 inferred relationships involving `MarketContextSummary` (e.g. with `DeciderAgent` and `ReviewerAgent`) actually correct?**
  _`MarketContextSummary` has 41 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `AgentState` (e.g. with `Settings` and `SnapshotBuilder`) actually correct?**
  _`AgentState` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 26 inferred relationships involving `CostTracker` (e.g. with `DeciderAgent` and `ReviewerAgent`) actually correct?**
  _`CostTracker` has 26 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `TradingGraph` (e.g. with `Settings` and `SnapshotBuilder`) actually correct?**
  _`TradingGraph` has 18 INFERRED edges - model-reasoned connections that need verification._
