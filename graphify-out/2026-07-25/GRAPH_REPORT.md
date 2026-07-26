# Graph Report - Agent  (2026-07-25)

## Corpus Check
- 44 files · ~22,195 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 714 nodes · 1267 edges · 51 communities (40 shown, 11 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 179 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `55b51911`
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
- test_analyze_structure_handles_broker_time_failure

## God Nodes (most connected - your core abstractions)
1. `MarketContextSummary` - 52 edges
2. `TradingGraph` - 46 edges
3. `SynthesizerAgent` - 43 edges
4. `AgentState` - 43 edges
5. `TerminalDataProvider` - 36 edges
6. `DecisionOutput` - 36 edges
7. `Settings` - 35 edges
8. `SnapshotBuilder` - 35 edges
9. `ReviewVerdict` - 34 edges
10. `_make_mcp_result()` - 32 edges

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

## Communities (51 total, 11 thin omitted)

### Community 0 - "MarketContextSummary"
Cohesion: 0.10
Nodes (20): BaseModel, BiasLevel, DecisionAction, DecisionOutput, Structural bias levels., Decision output from decider agent., Review verdict from reviewer agent., ReviewVerdict (+12 more)

### Community 1 - "Mt5DataProvider"
Cohesion: 0.09
Nodes (22): BaseSettings, Parse JSON string env var and validate all prices are non-negative., Trading agent configuration., Settings, MonkeyPatch, openai_reasoning_effort defaults to empty string (not set)., TRADING_OPENAI_REASONING_EFFORT env var overrides the default., Tests for the new terminal_server_url and terminal_api_key Settings fields. (+14 more)

### Community 2 - "DataSource"
Cohesion: 0.09
Nodes (19): Protocol, CalendarProvider, DataSource, Any, datetime, Fetch OHLC candles as CSV string.          Args:             symbol: Trading sym, Get latest price info for a symbol.          Args:             symbol: Trading s, Get open positions.          Args:             symbol: Optional symbol filter (+11 more)

### Community 3 - "AgentState"
Cohesion: 0.10
Nodes (17): mock_decider(), mock_reviewer(), mock_synthesizer(), snapshot_builder.build must be called with broker_time., AgentState must NOT have 'account_info'; it must have 'symbol_price' instead., AgentState must NOT have 'market_data' — the dead field was removed.      This v, With max_review_attempts=2, decider.decide must be called exactly 3 times     (1, _analyze_structure must fetch all three timeframes fresh (no partial cache). (+9 more)

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
Cohesion: 0.08
Nodes (20): CaptureFixture, main(), Trading AI Agent - CLI Entry Point., ForexFactoryCalendar, Any, Convert raw time text to ISO timestamp (best-effort)., Map raw impact text to standard impact level., Economic calendar provider via ForexFactory scraping. (+12 more)

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
Nodes (7): End-to-end: reasoning_effort flows from constructor → create() kwargs., synthesize() must include reasoning_effort in create() kwargs when set., synthesize() must NOT include reasoning_effort in create() kwargs when None., decide() must include reasoning_effort in create() kwargs when set., review() must include reasoning_effort in create() kwargs when set., When pre-built client is provided, reasoning_effort still flows to create()., TestReasoningEffortIntegration

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
Cohesion: 0.07
Nodes (25): OpenAI, Reviews trading decisions and provides feedback., Synthesizes market context from structure analysis and calendar., ReviewerAgent, SynthesizerAgent, Tests for API key and base_url passthrough in agents., When a pre-built client is provided, base_url must be ignored., SynthesizerAgent must pass both api_key and base_url when provided. (+17 more)

### Community 36 - "TestGetCandlesCsv"
Cohesion: 0.18
Nodes (5): DeciderAgent, Any, Makes trading decisions based on market context., DeciderAgent must accept reasoning_effort param., DeciderAgent must pass api_key to OpenAI constructor.

### Community 37 - "_select_canonical_current_price"
Cohesion: 0.33
Nodes (6): RED-first tests for the canonical current-price selection helper (TASK-6).  Thes, Lazy-import the not-yet-existing helper so collection succeeds.      Raises ``Im, Build a single per-timeframe engine-output dict for the selector., _select_canonical_current_price(), TestSelectCanonicalCurrentPrice, _tf()

### Community 38 - "AgentState"
Cohesion: 0.16
Nodes (12): AgentState, State for the trading graph., H1 analysis must now be saved to cache like D1/H4., _analyze_structure must request preferred_bars for each timeframe., _analyze_structure must call get_broker_time() instead of datetime.now(UTC)., Corrupt per-TF cache file must not crash — fall back to fresh fetch., test_analyze_structure_corrupt_cache_fallback(), test_analyze_structure_saves_h1_cache() (+4 more)

### Community 39 - "setup_logging"
Cohesion: 0.07
Nodes (20): CostTracker, CostTracker — tracks LLM API call costs.  Exposes a single :class:`CostTracker`, Reset accumulated cost and call count to zero., Tracks LLM API call costs using per-model token pricing.      Each instance is i, Record an LLM API call and return its cost.          Parameters         --------, Accumulated cost across all recorded calls., Number of calls recorded., Tests for CostTracker — tracks LLM API call costs.  CostTracker lives in ``src/d (+12 more)

### Community 40 - "graph.py"
Cohesion: 0.09
Nodes (15): MarketContextSummary, Summary of market context from synthesizer agent., sample_market_context(), User prompt must render current_price and current_price_time values., When no price is supplied, the current-price line must state None., SynthesizerAgent must use SYNTHESIZER_SYSTEM_PROMPT from prompts.py., SynthesizerAgent.synthesize must accept current_price/current_price_time kwargs., DeciderAgent.decide must accept a current_price keyword argument. (+7 more)

### Community 41 - "_canonical_structure_analysis"
Cohesion: 0.33
Nodes (4): _canonical_structure_analysis(), Build a structure_analysis fixture whose H1 timeframe has the     most-recent cl, _synthesize_context must compute the canonical current price from         the pe, Even when the LLM-returned summary has current_price=None, the         orchestra

### Community 42 - "test_analyze_structure_handles_broker_time_failure"
Cohesion: 0.12
Nodes (16): LangGraph orchestrator for trading analysis., Conditional edge from review to decide or end., TradingGraph, get_candles must be called with broker_time param., With max_review_attempts=2, feedback must be forwarded to decider.decide     on, The first call to decider.decide must have feedback=None.      This may already, When all 3 TFs + MTF are cached, must NOT call get_candles., Cache-hit confluence must be the real engine confluence, not D1 analysis_context (+8 more)

### Community 44 - "test_analyze_structure_fresh_saves_mtf_cache"
Cohesion: 0.40
Nodes (3): CompiledStateGraph, Initialize trading graph with dependencies.          Args:             data_prov, Build the LangGraph StateGraph.

### Community 46 - "test_analyze_structure_cache_hit_mtf_missing"
Cohesion: 0.17
Nodes (7): reasoning_effort is a create()-level kwarg, not an OpenAI() constructor arg., When reasoning_effort is set, it must appear in client.create() kwargs., When reasoning_effort is None, the key must be absent from create() kwargs., When reasoning_effort is explicitly None, key absent from create() kwargs., DeciderAgent passes reasoning_effort to create()., ReviewerAgent passes reasoning_effort to create()., TestReasoningEffortPassthrough

## Knowledge Gaps
- **27 isolated node(s):** `trading-ai-agent`, `graphify`, `Quick Commands`, `Critical Invariants`, `Architecture` (+22 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `Mt5DataProvider` to `DecisionOutput`, `AgentState`, `SynthesizerAgent`, `ForexFactoryCalendar`, `test_analyze_structure_handles_broker_time_failure`, `test_analyze_structure_fresh_saves_mtf_cache`, `_make_mcp_tool_result`, `TerminalApiError`, `test_terminal_data_provider.py`, `TestGetCandlesBrokerNow`?**
  _High betweenness centrality (0.158) - this node is a cross-community bridge._
- **Why does `TradingGraph` connect `test_analyze_structure_handles_broker_time_failure` to `MarketContextSummary`, `Mt5DataProvider`, `AgentState`, `SnapshotBuilder`, `AgentState`, `SynthesizerAgent`, `ForexFactoryCalendar`, `graph.py`, `test_analyze_structure_fetches_all_when_no_cache`, `test_analyze_structure_fresh_saves_mtf_cache`, `test_analyze_structure_passes_broker_time_to_snapshot_builder`, `test_analyze_structure_fetches_all_timeframes`, `test_analyze_structure_handles_broker_time_failure`?**
  _High betweenness centrality (0.124) - this node is a cross-community bridge._
- **Why does `TerminalDataProvider` connect `._run_async` to `setup_logging`, `setup_logging`, `DecisionOutput`, `ForexFactoryCalendar`, `TestSettingsDescriptions`, `test_analyze_structure_full_cache_hit`, `_make_mcp_tool_result`, `TerminalApiError`, `test_terminal_data_provider.py`, `TestGetCandlesBrokerNow`, `TestGetSymbolPrice`?**
  _High betweenness centrality (0.110) - this node is a cross-community bridge._
- **Are the 24 inferred relationships involving `MarketContextSummary` (e.g. with `DeciderAgent` and `ReviewerAgent`) actually correct?**
  _`MarketContextSummary` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `TradingGraph` (e.g. with `Settings` and `SnapshotBuilder`) actually correct?**
  _`TradingGraph` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `SynthesizerAgent` (e.g. with `DecisionOutput` and `MarketContextSummary`) actually correct?**
  _`SynthesizerAgent` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `AgentState` (e.g. with `Settings` and `SnapshotBuilder`) actually correct?**
  _`AgentState` has 10 INFERRED edges - model-reasoned connections that need verification._
