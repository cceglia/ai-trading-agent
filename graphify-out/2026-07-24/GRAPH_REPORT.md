# Graph Report - Agent  (2026-07-24)

## Corpus Check
- 41 files · ~19,245 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 612 nodes · 1108 edges · 47 communities (38 shown, 9 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 163 edges (avg confidence: 0.54)
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
1. `MarketContextSummary` - 49 edges
2. `AgentState` - 42 edges
3. `TradingGraph` - 40 edges
4. `TerminalDataProvider` - 36 edges
5. `DecisionOutput` - 36 edges
6. `SnapshotBuilder` - 35 edges
7. `SynthesizerAgent` - 32 edges
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

## Communities (47 total, 9 thin omitted)

### Community 0 - "MarketContextSummary"
Cohesion: 0.11
Nodes (18): BaseModel, BiasLevel, DecisionAction, DecisionOutput, Structural bias levels., Decision output from decider agent., Review verdict from reviewer agent., ReviewVerdict (+10 more)

### Community 1 - "Mt5DataProvider"
Cohesion: 0.14
Nodes (14): BaseSettings, Trading agent configuration., Settings, MonkeyPatch, openai_reasoning_effort defaults to empty string (not set)., TRADING_OPENAI_REASONING_EFFORT env var overrides the default., Tests for the new terminal_server_url and terminal_api_key Settings fields., Settings().terminal_server_url returns the default MCP URL. (+6 more)

### Community 2 - "DataSource"
Cohesion: 0.09
Nodes (19): Protocol, CalendarProvider, DataSource, Any, datetime, Fetch OHLC candles as CSV string.          Args:             symbol: Trading sym, Get latest price info for a symbol.          Args:             symbol: Trading s, Get open positions.          Args:             symbol: Optional symbol filter (+11 more)

### Community 3 - "AgentState"
Cohesion: 0.11
Nodes (14): mock_decider(), mock_reviewer(), mock_synthesizer(), get_candles must be called with broker_time param., _analyze_structure must fetch all three timeframes fresh (no partial cache)., _analyze_structure must request preferred_bars for each timeframe., When only 2 of 3 TFs are cached, must fetch all fresh., Corrupt per-TF cache file must not crash — fall back to fresh fetch. (+6 more)

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
Nodes (11): Any, Build a compact version of structure analysis suitable for LLM prompts.      The, Fetch market data from MT5., Analyze market structure with candle-aligned caching.          The multi-timefra, Extract compact analytical fields from a single timeframe engine output.      Th, Evaluate calendar events., Synthesize market context., Make trading decision. (+3 more)

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
Cohesion: 0.08
Nodes (12): OpenAI, Synthesizes market context from structure analysis and calendar., SynthesizerAgent, SynthesizerAgent must pass both api_key and base_url when provided., When not specified, reasoning_effort defaults to None., SynthesizerAgent must pass base_url to OpenAI constructor., SynthesizerAgent must pass api_key to OpenAI constructor., When no base_url given, OpenAI() uses its own default. (+4 more)

### Community 33 - "MarketContextSummary"
Cohesion: 0.12
Nodes (13): DeciderAgent, Makes trading decisions based on market context., Tests for API key and base_url passthrough in agents., When a pre-built client is provided, base_url must be ignored., SynthesizerAgent must accept reasoning_effort param., DeciderAgent must accept reasoning_effort param., DeciderAgent must pass api_key to OpenAI constructor., ReviewerAgent must pass api_key to OpenAI constructor. (+5 more)

### Community 34 - "setup_logging"
Cohesion: 0.18
Nodes (5): Any, MarketContextSummary, Summary of market context from synthesizer agent., Regression guard: positional decide(context, [], []) must not raise., TestMarketContextSummary

### Community 35 - "DecisionOutput"
Cohesion: 0.40
Nodes (3): CompiledStateGraph, Initialize trading graph with dependencies.          Args:             data_prov, Build the LangGraph StateGraph.

### Community 36 - "TestGetCandlesCsv"
Cohesion: 0.17
Nodes (12): main(), Trading AI Agent - CLI Entry Point., LangGraph orchestrator for trading analysis., TradingGraph, snapshot_builder.build must be called with broker_time., When no cache files exist, all 3 TFs must be fetched fresh., _analyze_structure must use SnapshotBuilder to convert CSV to dicts., Fresh-fetch path must also save the MTF cache file. (+4 more)

### Community 37 - "_select_canonical_current_price"
Cohesion: 0.27
Nodes (8): Select the canonical current price across timeframes.      The canonical current, _select_canonical_current_price(), RED-first tests for the canonical current-price selection helper (TASK-6).  Thes, Lazy-import the not-yet-existing helper so collection succeeds.      Raises ``Im, Build a single per-timeframe engine-output dict for the selector., _select_canonical_current_price(), TestSelectCanonicalCurrentPrice, _tf()

### Community 38 - "AgentState"
Cohesion: 0.19
Nodes (9): AgentState, State for the trading graph., Conditional edge from review to decide or end., When all 3 TFs + MTF are cached, must NOT call get_candles., When per-TF files exist but MTF is missing, must fall back to fresh fetch., test_analyze_structure_cache_hit_mtf_missing(), test_analyze_structure_full_cache_hit(), TestTradingGraphNodes (+1 more)

### Community 39 - "setup_logging"
Cohesion: 0.36
Nodes (3): Configure structured logging for the trading agent., setup_logging(), TestSetupLogging

### Community 40 - "graph.py"
Cohesion: 0.12
Nodes (11): Reviews trading decisions and provides feedback., ReviewerAgent, ReviewerAgent must accept reasoning_effort param., ReviewerAgent must pass base_url to OpenAI constructor., Tests for prompt usage in agents., SynthesizerAgent must use SYNTHESIZER_SYSTEM_PROMPT from prompts.py., DeciderAgent.decide must accept a current_price keyword argument., DeciderAgent user prompt must render the current_price anchor value. (+3 more)

### Community 41 - "_canonical_structure_analysis"
Cohesion: 0.33
Nodes (4): _canonical_structure_analysis(), Build a structure_analysis fixture whose H1 timeframe has the     most-recent cl, _synthesize_context must compute the canonical current price from         the pe, Even when the LLM-returned summary has current_price=None, the         orchestra

### Community 46 - "test_analyze_structure_cache_hit_mtf_missing"
Cohesion: 0.17
Nodes (7): reasoning_effort is a create()-level kwarg, not an OpenAI() constructor arg., When reasoning_effort is set, it must appear in client.create() kwargs., When reasoning_effort is None, the key must be absent from create() kwargs., When reasoning_effort is explicitly None, key absent from create() kwargs., DeciderAgent passes reasoning_effort to create()., ReviewerAgent passes reasoning_effort to create()., TestReasoningEffortPassthrough

## Knowledge Gaps
- **27 isolated node(s):** `trading-ai-agent`, `graphify`, `Quick Commands`, `Critical Invariants`, `Architecture` (+22 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TradingGraph` connect `TestGetCandlesCsv` to `MarketContextSummary`, `setup_logging`, `DecisionOutput`, `SnapshotBuilder`, `AgentState`, `AgentState`, `SynthesizerAgent`, `test_analyze_structure_handles_broker_time_failure`, `test_analyze_structure_fetches_all_when_no_cache`, `test_analyze_structure_fresh_saves_mtf_cache`, `test_analyze_structure_cache_hit_confluence_correct`?**
  _High betweenness centrality (0.189) - this node is a cross-community bridge._
- **Why does `TerminalDataProvider` connect `._run_async` to `TestGetCandlesCsv`, `_make_mcp_tool_result`, `TerminalApiError`, `test_terminal_data_provider.py`, `TestGetCandlesBrokerNow`, `TestGetPositions`, `TestGetPendingOrders`, `TestGetSymbolPrice`?**
  _High betweenness centrality (0.169) - this node is a cross-community bridge._
- **Why does `main()` connect `TestGetCandlesCsv` to `SynthesizerAgent`, `Mt5DataProvider`, `MarketContextSummary`, `setup_logging`, `graph.py`, `ForexFactoryCalendar`, `._run_async`?**
  _High betweenness centrality (0.141) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `MarketContextSummary` (e.g. with `DeciderAgent` and `ReviewerAgent`) actually correct?**
  _`MarketContextSummary` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `AgentState` (e.g. with `SnapshotBuilder` and `DecisionOutput`) actually correct?**
  _`AgentState` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `TradingGraph` (e.g. with `SnapshotBuilder` and `DecisionOutput`) actually correct?**
  _`TradingGraph` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `TerminalDataProvider` (e.g. with `TestErrorHandling` and `TestGetBrokerTime`) actually correct?**
  _`TerminalDataProvider` has 9 INFERRED edges - model-reasoned connections that need verification._
