# Graph Report - Agent  (2026-07-25)

## Corpus Check
- 42 files · ~20,804 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 651 nodes · 1176 edges · 50 communities (42 shown, 8 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 173 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `efcdb3bf`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- MarketContextSummary
- Mt5DataProvider
- DataSource
- AgentState
- SnapshotBuilder
- Evaluator
- Trading AI Agent
- TestSynthesizerPrompt
- SynthesizerAgent
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
- TestGetCandlesCsv
- _select_canonical_current_price
- AgentState
- setup_logging
- graph.py
- _canonical_structure_analysis
- test_analyze_structure_handles_broker_time_failure
- test_analyze_structure_fetches_all_when_no_cache
- test_analyze_structure_fresh_saves_mtf_cache
- TestSettingsDescriptions
- test_analyze_structure_cache_hit_mtf_missing
- test_analyze_structure_passes_broker_time_to_snapshot_builder
- test_analyze_structure_fetches_all_timeframes
- test_analyze_structure_full_cache_hit

## God Nodes (most connected - your core abstractions)
1. `MarketContextSummary` - 51 edges
2. `TradingGraph` - 46 edges
3. `AgentState` - 43 edges
4. `SynthesizerAgent` - 39 edges
5. `TerminalDataProvider` - 36 edges
6. `DecisionOutput` - 36 edges
7. `SnapshotBuilder` - 35 edges
8. `ReviewVerdict` - 34 edges
9. `_make_mcp_result()` - 32 edges
10. `Evaluator` - 31 edges

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

## Communities (50 total, 8 thin omitted)

### Community 0 - "MarketContextSummary"
Cohesion: 0.05
Nodes (37): BaseModel, Any, BiasLevel, DecisionAction, DecisionOutput, MarketContextSummary, Structural bias levels., Summary of market context from synthesizer agent. (+29 more)

### Community 1 - "Mt5DataProvider"
Cohesion: 0.15
Nodes (14): BaseSettings, Trading agent configuration., Settings, MonkeyPatch, openai_reasoning_effort defaults to empty string (not set)., TRADING_OPENAI_REASONING_EFFORT env var overrides the default., Tests for the new terminal_server_url and terminal_api_key Settings fields., Settings().terminal_server_url returns the default MCP URL. (+6 more)

### Community 2 - "DataSource"
Cohesion: 0.09
Nodes (19): Protocol, CalendarProvider, DataSource, Any, datetime, Fetch OHLC candles as CSV string.          Args:             symbol: Trading sym, Get latest price info for a symbol.          Args:             symbol: Trading s, Get open positions.          Args:             symbol: Optional symbol filter (+11 more)

### Community 3 - "AgentState"
Cohesion: 0.09
Nodes (17): snapshot_builder.build must be called with broker_time., AgentState must NOT have 'account_info'; it must have 'symbol_price' instead., AgentState must NOT have 'market_data' — the dead field was removed.      This v, With max_review_attempts=2, feedback must be forwarded to decider.decide     on, The first call to decider.decide must have feedback=None.      This may already, _analyze_structure must request preferred_bars for each timeframe., When per-TF files exist but MTF is missing, must fall back to fresh fetch., test_agentstate_rejects_account_info() (+9 more)

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

### Community 8 - "SynthesizerAgent"
Cohesion: 0.12
Nodes (13): Any, Select the canonical current price across timeframes.      The canonical current, Build a compact version of structure analysis suitable for LLM prompts.      The, Fetch market data from MT5., Analyze market structure with candle-aligned caching.          The multi-timefra, Extract compact analytical fields from a single timeframe engine output.      Th, Evaluate calendar events., Synthesize market context. (+5 more)

### Community 9 - "ForexFactoryCalendar"
Cohesion: 0.16
Nodes (10): ForexFactoryCalendar, Any, Convert raw time text to ISO timestamp (best-effort)., Map raw impact text to standard impact level., Economic calendar provider via ForexFactory scraping., Initialize calendar provider.          Args:             cache_hours: Hours to c, Fetch upcoming economic calendar events.          Returns:             List of e, Check if cache is still valid. (+2 more)

### Community 11 - "Agent Instructions"
Cohesion: 0.25
Nodes (7): Agent Instructions, Architecture, Critical Invariants, graphify, Quick Commands, Testing, Toolchain

### Community 24 - "_make_mcp_tool_result"
Cohesion: 0.14
Nodes (8): _make_mcp_result(), Verify get_candles returns correctly formatted CSV., Create a mock object mimicking mcp.types.CallToolResult.      Matches the real s, Verify get_positions returns list of positions and sends correct request., Verify get_pending_orders returns list of orders and sends correct request., TestGetCandlesCsv, TestGetPendingOrders, TestGetPositions

### Community 25 - "TerminalApiError"
Cohesion: 0.23
Nodes (5): RuntimeError, Non-retryable server-side error from the terminal MCP server., TerminalApiError, Verify retry behaviour via _call_with_retry., TestRetryLogic

### Community 26 - "test_terminal_data_provider.py"
Cohesion: 0.17
Nodes (7): Terminal MCP data provider via MCP Streamable HTTP protocol., provider(), Tests for TerminalDataProvider — MCP Streamable HTTP data provider., Verify get_symbol_price returns price dict and sends correct request., Verify terminal_data_provider.py has no imports inside function bodies.      All, test_no_inline_imports(), TestGetSymbolPrice

### Community 27 - "TestGetCandlesBrokerNow"
Cohesion: 0.20
Nodes (6): get_candles must accept a broker_now parameter for broker-local time., get_candles must use broker_now for lookback when provided., Without broker_now, get_candles uses datetime.now(UTC)., Explicit broker_now=None must use datetime.now(UTC)., get_candles must raise ValueError when broker_now has tzinfo., TestGetCandlesBrokerNow

### Community 28 - "TestGetPositions"
Cohesion: 0.17
Nodes (7): End-to-end: reasoning_effort flows from constructor → create() kwargs., synthesize() must include reasoning_effort in create() kwargs when set., synthesize() must NOT include reasoning_effort in create() kwargs when None., decide() must include reasoning_effort in create() kwargs when set., review() must include reasoning_effort in create() kwargs when set., When pre-built client is provided, reasoning_effort still flows to create()., TestReasoningEffortIntegration

### Community 29 - "._run_async"
Cohesion: 0.07
Nodes (26): AbstractEventLoop, Any, datetime, Tear down MCP session., Call an MCP tool via the persistent session.          Returns:             CallT, Call an MCP tool with retry on transient failures.          Args:             to, Extract text from CallToolResult.content[0].text., Extract candle history from CallToolResult.          The text payload is a JSON (+18 more)

### Community 30 - "TestGetPendingOrders"
Cohesion: 0.22
Nodes (7): CaptureFixture, main(), Trading AI Agent - CLI Entry Point., Tests for main.py entry point — Issue #13 error duplication., Duplicate error-printing blocks in main.py (Issue #13).      The first block (li, Verify errors are printed exactly once, not twice.          mocks:         - Set, TestMainErrorDuplication

### Community 31 - "TestGetSymbolPrice"
Cohesion: 0.29
Nodes (4): OpenAI, DeciderAgent, Makes trading decisions based on market context., DeciderAgent must pass base_url to OpenAI constructor.

### Community 32 - "setup_logging"
Cohesion: 0.36
Nodes (3): Configure structured logging for the trading agent., setup_logging(), TestSetupLogging

### Community 33 - "MarketContextSummary"
Cohesion: 0.25
Nodes (7): Synthesizes market context from structure analysis and calendar., SynthesizerAgent, When a pre-built client is provided, base_url must be ignored., SynthesizerAgent must pass both api_key and base_url when provided., SynthesizerAgent must pass base_url to OpenAI constructor., When no base_url given, OpenAI() uses its own default., TestAgentBaseUrl

### Community 36 - "TestGetCandlesCsv"
Cohesion: 0.22
Nodes (5): SynthesizerAgent must accept reasoning_effort param., When not specified, reasoning_effort defaults to None., DeciderAgent must accept reasoning_effort param., ReviewerAgent must accept reasoning_effort param., TestReasoningEffortConstructor

### Community 37 - "_select_canonical_current_price"
Cohesion: 0.33
Nodes (6): RED-first tests for the canonical current-price selection helper (TASK-6).  Thes, Lazy-import the not-yet-existing helper so collection succeeds.      Raises ``Im, Build a single per-timeframe engine-output dict for the selector., _select_canonical_current_price(), TestSelectCanonicalCurrentPrice, _tf()

### Community 38 - "AgentState"
Cohesion: 0.16
Nodes (12): AgentState, State for the trading graph., H1 analysis must now be saved to cache like D1/H4., When all 3 TFs + MTF are cached, must NOT call get_candles., Cache-hit confluence must be the real engine confluence, not D1 analysis_context, Fresh-fetch path must also save the MTF cache file., test_analyze_structure_cache_hit_confluence_correct(), test_analyze_structure_fresh_saves_mtf_cache() (+4 more)

### Community 39 - "setup_logging"
Cohesion: 0.22
Nodes (5): DeciderAgent must pass api_key to OpenAI constructor., ReviewerAgent must pass api_key to OpenAI constructor., When no api_key given, OpenAI() uses its own default., SynthesizerAgent must pass api_key to OpenAI constructor., TestAgentApiKey

### Community 40 - "graph.py"
Cohesion: 0.25
Nodes (5): Tests for API key and base_url passthrough in agents., Empty string → None conversion in main.py (same pattern as api_key/base_url)., Agent must accept None reasoning_effort without error., Agent must accept empty string reasoning_effort (though main.py converts it)., TestReasoningEffortNilConversion

### Community 41 - "_canonical_structure_analysis"
Cohesion: 0.33
Nodes (5): _canonical_structure_analysis(), Build a structure_analysis fixture whose H1 timeframe has the     most-recent cl, _synthesize_context must compute the canonical current price from         the pe, Even when the LLM-returned summary has current_price=None, the         orchestra, TestSynthesizeContextCanonicalPrice

### Community 42 - "test_analyze_structure_handles_broker_time_failure"
Cohesion: 0.12
Nodes (16): LangGraph orchestrator for trading analysis., Conditional edge from review to decide or end., TradingGraph, If get_broker_time() fails, _analyze_structure should set fatal_error., get_candles must be called with broker_time param., With max_review_attempts=2, decider.decide must be called exactly 3 times     (1, When no cache files exist, all 3 TFs must be fetched fresh., _analyze_structure must call get_broker_time() instead of datetime.now(UTC). (+8 more)

### Community 43 - "test_analyze_structure_fetches_all_when_no_cache"
Cohesion: 0.29
Nodes (4): Reviews trading decisions and provides feedback., ReviewerAgent, ReviewerAgent passes reasoning_effort to create()., ReviewerAgent must pass base_url to OpenAI constructor.

### Community 44 - "test_analyze_structure_fresh_saves_mtf_cache"
Cohesion: 0.40
Nodes (3): CompiledStateGraph, Initialize trading graph with dependencies.          Args:             data_prov, Build the LangGraph StateGraph.

### Community 46 - "test_analyze_structure_cache_hit_mtf_missing"
Cohesion: 0.20
Nodes (6): reasoning_effort is a create()-level kwarg, not an OpenAI() constructor arg., When reasoning_effort is set, it must appear in client.create() kwargs., When reasoning_effort is None, the key must be absent from create() kwargs., When reasoning_effort is explicitly None, key absent from create() kwargs., DeciderAgent passes reasoning_effort to create()., TestReasoningEffortPassthrough

## Knowledge Gaps
- **27 isolated node(s):** `trading-ai-agent`, `graphify`, `Quick Commands`, `Critical Invariants`, `Architecture` (+22 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `Mt5DataProvider` to `setup_logging`, `DecisionOutput`, `AgentState`, `SynthesizerAgent`, `test_analyze_structure_handles_broker_time_failure`, `test_analyze_structure_fresh_saves_mtf_cache`, `TestSettingsDescriptions`, `_make_mcp_tool_result`, `TerminalApiError`, `test_terminal_data_provider.py`, `TestGetCandlesBrokerNow`, `TestGetPendingOrders`?**
  _High betweenness centrality (0.153) - this node is a cross-community bridge._
- **Why does `TradingGraph` connect `test_analyze_structure_handles_broker_time_failure` to `MarketContextSummary`, `Mt5DataProvider`, `AgentState`, `SnapshotBuilder`, `AgentState`, `SynthesizerAgent`, `_canonical_structure_analysis`, `test_analyze_structure_fresh_saves_mtf_cache`, `test_analyze_structure_passes_broker_time_to_snapshot_builder`, `test_analyze_structure_fetches_all_timeframes`, `test_analyze_structure_full_cache_hit`, `TestGetPendingOrders`?**
  _High betweenness centrality (0.142) - this node is a cross-community bridge._
- **Why does `TerminalDataProvider` connect `._run_async` to `setup_logging`, `DecisionOutput`, `TestSettingsDescriptions`, `_make_mcp_tool_result`, `TerminalApiError`, `test_terminal_data_provider.py`, `TestGetCandlesBrokerNow`, `TestGetPendingOrders`?**
  _High betweenness centrality (0.125) - this node is a cross-community bridge._
- **Are the 23 inferred relationships involving `MarketContextSummary` (e.g. with `DeciderAgent` and `ReviewerAgent`) actually correct?**
  _`MarketContextSummary` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `TradingGraph` (e.g. with `Settings` and `SnapshotBuilder`) actually correct?**
  _`TradingGraph` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `AgentState` (e.g. with `Settings` and `SnapshotBuilder`) actually correct?**
  _`AgentState` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `SynthesizerAgent` (e.g. with `DecisionOutput` and `MarketContextSummary`) actually correct?**
  _`SynthesizerAgent` has 10 INFERRED edges - model-reasoned connections that need verification._
