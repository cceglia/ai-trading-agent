# Graph Report - Agent  (2026-07-23)

## Corpus Check
- 40 files · ~14,175 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 476 nodes · 855 edges · 25 communities (23 shown, 2 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 131 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `47baf34a`
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
- ForexFactoryCalendar
- TestProjectFiles
- Agent Instructions
- trading-ai-agent
- _make_mcp_tool_result
- ._run_async

## God Nodes (most connected - your core abstractions)
1. `MarketContextSummary` - 33 edges
2. `Evaluator` - 31 edges
3. `TerminalDataProvider` - 31 edges
4. `DecisionOutput` - 31 edges
5. `ReviewVerdict` - 31 edges
6. `SnapshotBuilder` - 30 edges
7. `AgentState` - 28 edges
8. `TradingGraph` - 28 edges
9. `_make_mcp_result()` - 23 edges
10. `SynthesizerAgent` - 21 edges

## Surprising Connections (you probably didn't know these)
- `TestErrorHandling` --uses--> `TerminalApiError`  [INFERRED]
  tests/data/test_terminal_data_provider.py → src/data/terminal_data_provider.py
- `TestGetCandlesCsv` --uses--> `TerminalApiError`  [INFERRED]
  tests/data/test_terminal_data_provider.py → src/data/terminal_data_provider.py
- `TestGetPendingOrders` --uses--> `TerminalApiError`  [INFERRED]
  tests/data/test_terminal_data_provider.py → src/data/terminal_data_provider.py
- `TestGetPositions` --uses--> `TerminalApiError`  [INFERRED]
  tests/data/test_terminal_data_provider.py → src/data/terminal_data_provider.py
- `TestGetSymbolPrice` --uses--> `TerminalApiError`  [INFERRED]
  tests/data/test_terminal_data_provider.py → src/data/terminal_data_provider.py

## Import Cycles
- None detected.

## Communities (25 total, 2 thin omitted)

### Community 0 - "MarketContextSummary"
Cohesion: 0.05
Nodes (46): BaseModel, OpenAI, DeciderAgent, Any, Reviews trading decisions and provides feedback., Synthesizes market context from structure analysis and calendar., Makes trading decisions based on market context., ReviewerAgent (+38 more)

### Community 1 - "Mt5DataProvider"
Cohesion: 0.12
Nodes (15): BaseSettings, Trading agent configuration., Settings, main(), Trading AI Agent - CLI Entry Point., MonkeyPatch, Configure structured logging for the trading agent., setup_logging() (+7 more)

### Community 2 - "DataSource"
Cohesion: 0.10
Nodes (17): Protocol, CalendarProvider, DataSource, Any, Get latest price info for a symbol.          Args:             symbol: Trading s, Get open positions.          Args:             symbol: Optional symbol filter, Get pending orders.          Args:             symbol: Optional symbol filter, Economic calendar data provider. (+9 more)

### Community 3 - "AgentState"
Cohesion: 0.07
Nodes (33): CompiledStateGraph, AgentState, Any, Build a compact version of structure analysis suitable for LLM prompts.      The, State for the trading graph., LangGraph orchestrator for trading analysis., Initialize trading graph with dependencies.          Args:             data_prov, Build the LangGraph StateGraph. (+25 more)

### Community 4 - "SnapshotBuilder"
Cohesion: 0.11
Nodes (11): Any, Snapshot builder for converting MCP CSV data to normalized engine snapshots., Build normalized snapshot from parsed bars.          Args:             bars: Lis, Validate snapshot against engine schema.          Args:             snapshot: Th, Builds normalized snapshots from MCP CSV data.      Converts raw CSV candle data, Convert CSV to normalized snapshot.          Args:             csv_data: CSV str, Parse CSV string to list of bar dicts.          Args:             csv_data: Raw, SnapshotBuilder (+3 more)

### Community 5 - "Evaluator"
Cohesion: 0.07
Nodes (18): Evaluator, Any, Check if an event falls within the time window from now.          Returns False, Evaluate events for symbol with timeframe-dependent window.          Args:, Evaluates calendar events for trading symbols., High-impact event outside the window should NOT block., High-impact event within the window SHOULD block., Event with no time field should be excluded (fail-safe). (+10 more)

### Community 6 - "Trading AI Agent"
Cohesion: 0.07
Nodes (28): Analysis Layer (`src/analysis/`), Architecture, Calendar Layer (`src/calendar/`), CLI Commands, Code Quality, Components, Configuration, Configuration (`config/`) (+20 more)

### Community 7 - "TestSynthesizerPrompt"
Cohesion: 0.11
Nodes (4): LLM prompts with embedded rules.json content., TestDeciderPrompt, TestReviewerPrompt, TestSynthesizerPrompt

### Community 9 - "ForexFactoryCalendar"
Cohesion: 0.17
Nodes (10): ForexFactoryCalendar, Any, Convert raw time text to ISO timestamp (best-effort)., Map raw impact text to standard impact level., Economic calendar provider via ForexFactory scraping., Initialize calendar provider.          Args:             cache_hours: Hours to c, Fetch upcoming economic calendar events.          Returns:             List of e, Check if cache is still valid. (+2 more)

### Community 11 - "Agent Instructions"
Cohesion: 0.25
Nodes (7): Agent Instructions, Architecture, Critical Invariants, graphify, Quick Commands, Testing, Toolchain

### Community 24 - "_make_mcp_tool_result"
Cohesion: 0.07
Nodes (18): datetime, RuntimeError, _make_mcp_result(), provider(), Tests for TerminalDataProvider — MCP Streamable HTTP data provider., Verify get_candles returns correctly formatted CSV., Create a mock object mimicking mcp.types.CallToolResult.      Matches the real s, Verify error conditions are surfaced as the right exception types. (+10 more)

### Community 29 - "._run_async"
Cohesion: 0.07
Nodes (26): AbstractEventLoop, Any, Terminal MCP data provider via MCP Streamable HTTP protocol., Tear down MCP session., Call an MCP tool via the persistent session.          Returns:             CallT, Non-retryable server-side error from the terminal MCP server., Call an MCP tool with retry on transient failures.          Args:             to, Data provider using terminal MCP server via MCP Streamable HTTP protocol.      F (+18 more)

## Knowledge Gaps
- **27 isolated node(s):** `trading-ai-agent`, `graphify`, `Quick Commands`, `Critical Invariants`, `Architecture` (+22 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TerminalDataProvider` connect `._run_async` to `_make_mcp_tool_result`, `Mt5DataProvider`?**
  _High betweenness centrality (0.185) - this node is a cross-community bridge._
- **Why does `TradingGraph` connect `AgentState` to `MarketContextSummary`, `Mt5DataProvider`, `SnapshotBuilder`?**
  _High betweenness centrality (0.135) - this node is a cross-community bridge._
- **Why does `main()` connect `Mt5DataProvider` to `MarketContextSummary`, `ForexFactoryCalendar`, `AgentState`, `._run_async`?**
  _High betweenness centrality (0.114) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `MarketContextSummary` (e.g. with `DeciderAgent` and `ReviewerAgent`) actually correct?**
  _`MarketContextSummary` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `Evaluator` (e.g. with `TestEvaluatorBlocking` and `TestEvaluatorConfig`) actually correct?**
  _`Evaluator` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `TerminalDataProvider` (e.g. with `TestErrorHandling` and `TestGetCandlesCsv`) actually correct?**
  _`TerminalDataProvider` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `DecisionOutput` (e.g. with `DeciderAgent` and `ReviewerAgent`) actually correct?**
  _`DecisionOutput` has 13 INFERRED edges - model-reasoned connections that need verification._
