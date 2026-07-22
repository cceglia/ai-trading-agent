# Graph Report - Agent  (2026-07-22)

## Corpus Check
- 39 files · ~13,065 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 472 nodes · 806 edges · 31 communities (29 shown, 2 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 116 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `155ecb57`
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
- ._retry_operation
- ForexFactoryCalendar
- TestProjectFiles
- Agent Instructions
- trading-ai-agent
- _make_mcp_tool_result
- test_mt5_data_provider.py
- Mt5DataProvider
- ._retry_operation
- TestPersistentEventLoop
- ._run_async
- TestConnectionLifecycle

## God Nodes (most connected - your core abstractions)
1. `Mt5DataProvider` - 34 edges
2. `MarketContextSummary` - 33 edges
3. `ReviewVerdict` - 32 edges
4. `Evaluator` - 31 edges
5. `DecisionOutput` - 31 edges
6. `SnapshotBuilder` - 30 edges
7. `AgentState` - 28 edges
8. `TradingGraph` - 28 edges
9. `SynthesizerAgent` - 21 edges
10. `DataSource` - 18 edges

## Surprising Connections (you probably didn't know these)
- `TestCallToolLazyConnect` --uses--> `Mt5DataProvider`  [INFERRED]
  tests/data/test_mt5_data_provider.py → src/data/mt5_data_provider.py
- `TestConnectionLifecycle` --uses--> `Mt5DataProvider`  [INFERRED]
  tests/data/test_mt5_data_provider.py → src/data/mt5_data_provider.py
- `TestGetData` --uses--> `Mt5DataProvider`  [INFERRED]
  tests/data/test_mt5_data_provider.py → src/data/mt5_data_provider.py
- `TestParseCandlesCsv` --uses--> `Mt5DataProvider`  [INFERRED]
  tests/data/test_mt5_data_provider.py → src/data/mt5_data_provider.py
- `TestPersistentEventLoop` --uses--> `Mt5DataProvider`  [INFERRED]
  tests/data/test_mt5_data_provider.py → src/data/mt5_data_provider.py

## Import Cycles
- None detected.

## Communities (31 total, 2 thin omitted)

### Community 0 - "MarketContextSummary"
Cohesion: 0.08
Nodes (25): BaseModel, Any, BiasLevel, DecisionAction, DecisionOutput, MarketContextSummary, Summary of market context from synthesizer agent., Decision output from decider agent. (+17 more)

### Community 1 - "Mt5DataProvider"
Cohesion: 0.36
Nodes (3): Configure structured logging for the trading agent., setup_logging(), TestSetupLogging

### Community 2 - "DataSource"
Cohesion: 0.10
Nodes (17): Protocol, CalendarProvider, DataSource, Any, Get latest price info for a symbol.          Args:             symbol: Trading s, Get open positions.          Args:             symbol: Optional symbol filter, Get pending orders.          Args:             symbol: Optional symbol filter, Economic calendar data provider. (+9 more)

### Community 3 - "AgentState"
Cohesion: 0.09
Nodes (25): CompiledStateGraph, AgentState, Any, Fetch market data from MT5., Analyze market structure with candle-aligned caching., Evaluate calendar events., Synthesize market context., Make trading decision. (+17 more)

### Community 4 - "SnapshotBuilder"
Cohesion: 0.10
Nodes (12): datetime, Any, Snapshot builder for converting MCP CSV data to normalized engine snapshots., Build normalized snapshot from parsed bars.          Args:             bars: Lis, Validate snapshot against engine schema.          Args:             snapshot: Th, Builds normalized snapshots from MCP CSV data.      Converts raw CSV candle data, Convert CSV to normalized snapshot.          Args:             csv_data: CSV str, Parse CSV string to list of bar dicts.          Args:             csv_data: Raw (+4 more)

### Community 5 - "Evaluator"
Cohesion: 0.07
Nodes (18): Evaluator, Any, Check if an event falls within the time window from now.          Returns False, Evaluate events for symbol with timeframe-dependent window.          Args:, Evaluates calendar events for trading symbols., High-impact event outside the window should NOT block., High-impact event within the window SHOULD block., Event with no time field should be excluded (fail-safe). (+10 more)

### Community 6 - "Trading AI Agent"
Cohesion: 0.07
Nodes (28): Analysis Layer (`src/analysis/`), Architecture, Calendar Layer (`src/calendar/`), CLI Commands, Code Quality, Components, Configuration, Configuration (`config/`) (+20 more)

### Community 7 - "TestSynthesizerPrompt"
Cohesion: 0.11
Nodes (4): LLM prompts with embedded rules.json content., TestDeciderPrompt, TestReviewerPrompt, TestSynthesizerPrompt

### Community 8 - "._retry_operation"
Cohesion: 0.07
Nodes (30): BaseSettings, Trading agent configuration., Settings, main(), Trading AI Agent - CLI Entry Point., OpenAI, DeciderAgent, Reviews trading decisions and provides feedback. (+22 more)

### Community 9 - "ForexFactoryCalendar"
Cohesion: 0.16
Nodes (10): ForexFactoryCalendar, Any, Convert raw time text to ISO timestamp (best-effort)., Map raw impact text to standard impact level., Economic calendar provider via ForexFactory scraping., Initialize calendar provider.          Args:             cache_hours: Hours to c, Fetch upcoming economic calendar events.          Returns:             List of e, Check if cache is still valid. (+2 more)

### Community 11 - "Agent Instructions"
Cohesion: 0.25
Nodes (7): Agent Instructions, Architecture, Critical Invariants, graphify, Quick Commands, Testing, Toolchain

### Community 24 - "_make_mcp_tool_result"
Cohesion: 0.13
Nodes (10): _make_mcp_tool_result(), Create a mock MCP CallToolResult with a text content block., _call_tool should auto-connect when _client is None., _call_tool should forward tool_name and arguments to ClientSession.call_tool., _call_tool with no arguments should pass an empty dict., Tests for get_candles, get_symbol_price, get_positions, get_pending_orders., Provide a provider that's already connected (mocked)., Invalid MCP response is retried and eventually wrapped as ConnectionError. (+2 more)

### Community 25 - "test_mt5_data_provider.py"
Cohesion: 0.11
Nodes (10): MetaTrader 5 data provider via MCP server., mock_client_session(), mock_sse_context(), provider(), Tests for Mt5DataProvider — MCP data provider with persistent event loop., Mock ``mcp.client.sse.sse_client`` async context manager.      Yields (read_stre, Mock ``mcp.ClientSession``., Create an Mt5DataProvider with a known server URL. (+2 more)

### Community 26 - "Mt5DataProvider"
Cohesion: 0.14
Nodes (9): Mt5DataProvider, Disconnect from MCP server (sync wrapper)., MetaTrader 5 data provider via MCP server.      Implements the DataSource protoc, Initialize MT5 data provider.          Args:             server_url: MCP server, Return string representation., Entry point for the background loop thread., Disconnect from MCP server (runs on the background loop)., TestRepr (+1 more)

### Community 27 - "._retry_operation"
Cohesion: 0.19
Nodes (7): Any, Execute operation with retry logic and exponential backoff.          Args:, Fetch OHLC candles as CSV string.          Args:             symbol: Trading sym, Get latest price info for a symbol.          Args:             symbol: Trading s, Get open positions.          Args:             symbol: Optional symbol filter. I, Get pending orders.          Args:             symbol: Optional symbol filter. I, Parse CSV candle data into list of dictionaries.          Args:             csv_

### Community 28 - "TestPersistentEventLoop"
Cohesion: 0.17
Nodes (7): Same event loop is used for every _call_tool invocation., Disconnecting cleanly must NOT raise RuntimeError.          This is the exact sy, The event loop thread must be a daemon so it won't block process exit., After disconnect() the background loop must be stopped and references cleared., After disconnect, a new call_tool should reconnect on a fresh loop., Verify the background event loop persists across tool calls.      The original b, TestPersistentEventLoop

### Community 29 - "._run_async"
Cohesion: 0.18
Nodes (6): AbstractEventLoop, Establish connection to MCP server (sync wrapper)., Call an MCP tool synchronously.          Args:             tool_name: Name of th, Return the dedicated background event loop, starting it if needed., Schedule a coroutine on the background loop and block until done., Establish connection to MCP server (runs on the background loop).

### Community 30 - "TestConnectionLifecycle"
Cohesion: 0.22
Nodes (5): connect() should enter the SSE context, create a ClientSession, and initialize., disconnect() should exit the ClientSession and SSE context., If the MCP server is unreachable, connect() raises ConnectionError., If mcp is not installed, connect() logs warning and sets client to None., TestConnectionLifecycle

## Knowledge Gaps
- **27 isolated node(s):** `trading-ai-agent`, `graphify`, `Quick Commands`, `Critical Invariants`, `Architecture` (+22 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Mt5DataProvider` connect `Mt5DataProvider` to `._retry_operation`, `_make_mcp_tool_result`, `test_mt5_data_provider.py`, `._retry_operation`, `TestPersistentEventLoop`, `._run_async`, `TestConnectionLifecycle`?**
  _High betweenness centrality (0.279) - this node is a cross-community bridge._
- **Why does `TradingGraph` connect `AgentState` to `._retry_operation`, `MarketContextSummary`, `SnapshotBuilder`?**
  _High betweenness centrality (0.195) - this node is a cross-community bridge._
- **Why does `main()` connect `._retry_operation` to `ForexFactoryCalendar`, `Mt5DataProvider`, `AgentState`, `Mt5DataProvider`?**
  _High betweenness centrality (0.152) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `Mt5DataProvider` (e.g. with `TestCallToolLazyConnect` and `TestConnectionLifecycle`) actually correct?**
  _`Mt5DataProvider` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `MarketContextSummary` (e.g. with `DeciderAgent` and `ReviewerAgent`) actually correct?**
  _`MarketContextSummary` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `ReviewVerdict` (e.g. with `DeciderAgent` and `ReviewerAgent`) actually correct?**
  _`ReviewVerdict` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `Evaluator` (e.g. with `TestEvaluatorBlocking` and `TestEvaluatorConfig`) actually correct?**
  _`Evaluator` has 7 INFERRED edges - model-reasoned connections that need verification._
