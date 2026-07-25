# Graph Report - Agent  (2026-07-24)

## Corpus Check
- 41 files · ~19,589 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 624 nodes · 1129 edges · 47 communities (39 shown, 8 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 167 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d81e8152`
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
- SynthesizerAgent
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
- test_analyze_structure_cache_hit_confluence_correct
- test_analyze_structure_cache_hit_mtf_missing

## God Nodes (most connected - your core abstractions)
1. `MarketContextSummary` - 50 edges
2. `AgentState` - 42 edges
3. `TradingGraph` - 40 edges
4. `TerminalDataProvider` - 36 edges
5. `SynthesizerAgent` - 36 edges
6. `DecisionOutput` - 36 edges
7. `SnapshotBuilder` - 35 edges
8. `ReviewVerdict` - 32 edges
9. `_make_mcp_result()` - 32 edges
10. `Evaluator` - 31 edges

## Surprising Connections (you probably didn't know these)
- `TestErrorHandling` --uses--> `Settings`  [INFERRED]
  tests/data/test_terminal_data_provider.py → config/settings.py
- `TestGetBrokerTime` --uses--> `Settings`  [INFERRED]
  tests/data/test_terminal_data_provider.py → config/settings.py
- `TestGetCandlesBrokerNow` --uses--> `Settings`  [INFERRED]
  tests/data/test_terminal_data_provider.py → config/settings.py
- `TestGetCandlesCsv` --uses--> `Settings`  [INFERRED]
  tests/data/test_terminal_data_provider.py → config/settings.py
- `TestGetPendingOrders` --uses--> `Settings`  [INFERRED]
  tests/data/test_terminal_data_provider.py → config/settings.py

## Import Cycles
- None detected.

## Communities (47 total, 8 thin omitted)

### Community 0 - "MarketContextSummary"
Cohesion: 0.10
Nodes (20): BaseModel, BiasLevel, DecisionAction, DecisionOutput, Structural bias levels., Decision output from decider agent., Review verdict from reviewer agent., ReviewVerdict (+12 more)

### Community 1 - "Mt5DataProvider"
Cohesion: 0.14
Nodes (14): BaseSettings, Trading agent configuration., Settings, MonkeyPatch, openai_reasoning_effort defaults to empty string (not set)., TRADING_OPENAI_REASONING_EFFORT env var overrides the default., Tests for the new terminal_server_url and terminal_api_key Settings fields., Settings().terminal_server_url returns the default MCP URL. (+6 more)

### Community 2 - "DataSource"
Cohesion: 0.09
Nodes (19): Protocol, CalendarProvider, DataSource, Any, datetime, Fetch OHLC candles as CSV string.          Args:             symbol: Trading sym, Get latest price info for a symbol.          Args:             symbol: Trading s, Get open positions.          Args:             symbol: Optional symbol filter (+11 more)

### Community 3 - "AgentState"
Cohesion: 0.09
Nodes (26): LangGraph orchestrator for trading analysis., Conditional edge from review to decide or end., TradingGraph, get_candles must be called with broker_time param., snapshot_builder.build must be called with broker_time., _analyze_structure must fetch all three timeframes fresh (no partial cache)., When no cache files exist, all 3 TFs must be fetched fresh., _analyze_structure must use SnapshotBuilder to convert CSV to dicts. (+18 more)

### Community 4 - "SnapshotBuilder"
Cohesion: 0.07
Nodes (26): Any, datetime, Snapshot builder for converting MCP CSV data to normalized engine snapshots., Build normalized snapshot from parsed bars.          Args:             bars: Lis, Validate snapshot against engine schema.          Args:             snapshot: Th, Builds normalized snapshots from MCP CSV data.      Converts raw CSV candle data, Convert CSV to normalized snapshot.          Args:             csv_data: CSV str, Parse CSV string to list of bar dicts.          Args:             csv_data: Raw (+18 more)

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
Nodes (9): CompiledStateGraph, Any, Initialize trading graph with dependencies.          Args:             data_prov, Build the LangGraph StateGraph., Fetch market data from MT5., Analyze market structure with candle-aligned caching.          The multi-timefra, Evaluate calendar events., Make trading decision. (+1 more)

### Community 9 - "ForexFactoryCalendar"
Cohesion: 0.16
Nodes (10): ForexFactoryCalendar, Any, Convert raw time text to ISO timestamp (best-effort)., Map raw impact text to standard impact level., Economic calendar provider via ForexFactory scraping., Initialize calendar provider.          Args:             cache_hours: Hours to c, Fetch upcoming economic calendar events.          Returns:             List of e, Check if cache is still valid. (+2 more)

### Community 11 - "Agent Instructions"
Cohesion: 0.25
Nodes (7): Agent Instructions, Architecture, Critical Invariants, graphify, Quick Commands, Testing, Toolchain

### Community 24 - "_make_mcp_tool_result"
Cohesion: 0.17
Nodes (6): _make_mcp_result(), Verify get_candles returns correctly formatted CSV., Create a mock object mimicking mcp.types.CallToolResult.      Matches the real s, Verify get_broker_time returns naive datetime and sends correct request., TestGetBrokerTime, TestGetCandlesCsv

### Community 25 - "TerminalApiError"
Cohesion: 0.24
Nodes (3): RuntimeError, Verify retry behaviour via _call_with_retry., TestRetryLogic

### Community 26 - "test_terminal_data_provider.py"
Cohesion: 0.25
Nodes (4): provider(), Tests for TerminalDataProvider — MCP Streamable HTTP data provider., Verify error conditions are surfaced as the right exception types., TestErrorHandling

### Community 27 - "TestGetCandlesBrokerNow"
Cohesion: 0.20
Nodes (6): get_candles must accept a broker_now parameter for broker-local time., get_candles must use broker_now for lookback when provided., Without broker_now, get_candles uses datetime.now(UTC)., Explicit broker_now=None must use datetime.now(UTC)., get_candles must raise ValueError when broker_now has tzinfo., TestGetCandlesBrokerNow

### Community 29 - "._run_async"
Cohesion: 0.06
Nodes (31): AbstractEventLoop, Any, datetime, Terminal MCP data provider via MCP Streamable HTTP protocol., Tear down MCP session., Call an MCP tool via the persistent session.          Returns:             CallT, Call an MCP tool with retry on transient failures.          Args:             to, Non-retryable server-side error from the terminal MCP server. (+23 more)

### Community 32 - "SynthesizerAgent"
Cohesion: 0.17
Nodes (9): Synthesizes market context from structure analysis and calendar., SynthesizerAgent, When a pre-built client is provided, base_url must be ignored., SynthesizerAgent must pass both api_key and base_url when provided., SynthesizerAgent must pass base_url to OpenAI constructor., DeciderAgent must pass base_url to OpenAI constructor., ReviewerAgent must pass base_url to OpenAI constructor., When no base_url given, OpenAI() uses its own default. (+1 more)

### Community 33 - "MarketContextSummary"
Cohesion: 0.18
Nodes (6): Tests for API key and base_url passthrough in agents., DeciderAgent must pass api_key to OpenAI constructor., ReviewerAgent must pass api_key to OpenAI constructor., When no api_key given, OpenAI() uses its own default., SynthesizerAgent must pass api_key to OpenAI constructor., TestAgentApiKey

### Community 34 - "setup_logging"
Cohesion: 0.09
Nodes (15): MarketContextSummary, Summary of market context from synthesizer agent., User prompt must render current_price and current_price_time values., When no price is supplied, the current-price line must state None., SynthesizerAgent must use SYNTHESIZER_SYSTEM_PROMPT from prompts.py., SynthesizerAgent.synthesize must accept current_price/current_price_time kwargs., DeciderAgent.decide must accept a current_price keyword argument., DeciderAgent user prompt must render the current_price anchor value. (+7 more)

### Community 35 - "DecisionOutput"
Cohesion: 0.17
Nodes (7): End-to-end: reasoning_effort flows from constructor → create() kwargs., synthesize() must include reasoning_effort in create() kwargs when set., synthesize() must NOT include reasoning_effort in create() kwargs when None., decide() must include reasoning_effort in create() kwargs when set., review() must include reasoning_effort in create() kwargs when set., When pre-built client is provided, reasoning_effort still flows to create()., TestReasoningEffortIntegration

### Community 36 - "TestGetCandlesCsv"
Cohesion: 0.24
Nodes (7): main(), Trading AI Agent - CLI Entry Point., OpenAI, DeciderAgent, Reviews trading decisions and provides feedback., Makes trading decisions based on market context., ReviewerAgent

### Community 37 - "_select_canonical_current_price"
Cohesion: 0.33
Nodes (6): RED-first tests for the canonical current-price selection helper (TASK-6).  Thes, Lazy-import the not-yet-existing helper so collection succeeds.      Raises ``Im, Build a single per-timeframe engine-output dict for the selector., _select_canonical_current_price(), TestSelectCanonicalCurrentPrice, _tf()

### Community 38 - "AgentState"
Cohesion: 0.24
Nodes (8): AgentState, State for the trading graph., When per-TF files exist but MTF is missing, must fall back to fresh fetch., Fresh-fetch path must also save the MTF cache file., test_analyze_structure_cache_hit_mtf_missing(), test_analyze_structure_fresh_saves_mtf_cache(), TestTradingGraphNodes, TypedDict

### Community 39 - "setup_logging"
Cohesion: 0.36
Nodes (3): Configure structured logging for the trading agent., setup_logging(), TestSetupLogging

### Community 40 - "graph.py"
Cohesion: 0.22
Nodes (5): SynthesizerAgent must accept reasoning_effort param., When not specified, reasoning_effort defaults to None., DeciderAgent must accept reasoning_effort param., ReviewerAgent must accept reasoning_effort param., TestReasoningEffortConstructor

### Community 41 - "_canonical_structure_analysis"
Cohesion: 0.33
Nodes (5): _canonical_structure_analysis(), Build a structure_analysis fixture whose H1 timeframe has the     most-recent cl, _synthesize_context must compute the canonical current price from         the pe, Even when the LLM-returned summary has current_price=None, the         orchestra, TestSynthesizeContextCanonicalPrice

### Community 44 - "test_analyze_structure_fresh_saves_mtf_cache"
Cohesion: 0.28
Nodes (7): Select the canonical current price across timeframes.      The canonical current, Build a compact version of structure analysis suitable for LLM prompts.      The, Extract compact analytical fields from a single timeframe engine output.      Th, Synthesize market context., _select_canonical_current_price(), _summarize_structure_analysis(), _summarize_timeframe()

### Community 46 - "test_analyze_structure_cache_hit_mtf_missing"
Cohesion: 0.17
Nodes (7): reasoning_effort is a create()-level kwarg, not an OpenAI() constructor arg., When reasoning_effort is set, it must appear in client.create() kwargs., When reasoning_effort is None, the key must be absent from create() kwargs., When reasoning_effort is explicitly None, key absent from create() kwargs., DeciderAgent passes reasoning_effort to create()., ReviewerAgent passes reasoning_effort to create()., TestReasoningEffortPassthrough

## Knowledge Gaps
- **27 isolated node(s):** `trading-ai-agent`, `graphify`, `Quick Commands`, `Critical Invariants`, `Architecture` (+22 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TradingGraph` connect `AgentState` to `MarketContextSummary`, `setup_logging`, `TestGetCandlesCsv`, `SnapshotBuilder`, `AgentState`, `SynthesizerAgent`, `_canonical_structure_analysis`, `test_analyze_structure_handles_broker_time_failure`, `test_analyze_structure_fetches_all_when_no_cache`, `test_analyze_structure_fresh_saves_mtf_cache`?**
  _High betweenness centrality (0.185) - this node is a cross-community bridge._
- **Why does `TerminalDataProvider` connect `._run_async` to `TestGetCandlesCsv`, `_make_mcp_tool_result`, `TerminalApiError`, `test_terminal_data_provider.py`, `TestGetCandlesBrokerNow`, `TestGetPositions`, `TestGetPendingOrders`, `TestGetSymbolPrice`?**
  _High betweenness centrality (0.167) - this node is a cross-community bridge._
- **Why does `main()` connect `TestGetCandlesCsv` to `SynthesizerAgent`, `Mt5DataProvider`, `AgentState`, `setup_logging`, `ForexFactoryCalendar`, `._run_async`?**
  _High betweenness centrality (0.141) - this node is a cross-community bridge._
- **Are the 22 inferred relationships involving `MarketContextSummary` (e.g. with `DeciderAgent` and `ReviewerAgent`) actually correct?**
  _`MarketContextSummary` has 22 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `AgentState` (e.g. with `SnapshotBuilder` and `DecisionOutput`) actually correct?**
  _`AgentState` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `TradingGraph` (e.g. with `SnapshotBuilder` and `DecisionOutput`) actually correct?**
  _`TradingGraph` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `TerminalDataProvider` (e.g. with `TestErrorHandling` and `TestGetBrokerTime`) actually correct?**
  _`TerminalDataProvider` has 9 INFERRED edges - model-reasoned connections that need verification._
