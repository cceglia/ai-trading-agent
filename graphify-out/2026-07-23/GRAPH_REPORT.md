# Graph Report - Agent  (2026-07-23)

## Corpus Check
- 40 files · ~16,524 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 553 nodes · 990 edges · 37 communities (31 shown, 6 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 144 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b16d6b1e`
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

## God Nodes (most connected - your core abstractions)
1. `MarketContextSummary` - 42 edges
2. `TerminalDataProvider` - 36 edges
3. `SnapshotBuilder` - 35 edges
4. `DecisionOutput` - 35 edges
5. `AgentState` - 33 edges
6. `TradingGraph` - 33 edges
7. `_make_mcp_result()` - 32 edges
8. `Evaluator` - 31 edges
9. `ReviewVerdict` - 31 edges
10. `SynthesizerAgent` - 25 edges

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

## Communities (37 total, 6 thin omitted)

### Community 0 - "MarketContextSummary"
Cohesion: 0.12
Nodes (15): BaseModel, BiasLevel, DecisionAction, Structural bias levels., Review verdict from reviewer agent., ReviewVerdict, StrEnum, sample_decision() (+7 more)

### Community 1 - "Mt5DataProvider"
Cohesion: 0.12
Nodes (15): BaseSettings, Trading agent configuration., Settings, main(), Trading AI Agent - CLI Entry Point., MonkeyPatch, Configure structured logging for the trading agent., setup_logging() (+7 more)

### Community 2 - "DataSource"
Cohesion: 0.09
Nodes (19): Protocol, CalendarProvider, DataSource, Any, datetime, Fetch OHLC candles as CSV string.          Args:             symbol: Trading sym, Get latest price info for a symbol.          Args:             symbol: Trading s, Get open positions.          Args:             symbol: Optional symbol filter (+11 more)

### Community 3 - "AgentState"
Cohesion: 0.06
Nodes (43): CompiledStateGraph, AgentState, Any, Build a compact version of structure analysis suitable for LLM prompts.      The, State for the trading graph., LangGraph orchestrator for trading analysis., Initialize trading graph with dependencies.          Args:             data_prov, Build the LangGraph StateGraph. (+35 more)

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
Cohesion: 0.13
Nodes (8): User prompt must render current_price and current_price_time values., When no price is supplied, the current-price line must state None., SynthesizerAgent must use SYNTHESIZER_SYSTEM_PROMPT from prompts.py., SynthesizerAgent.synthesize must accept current_price/current_price_time kwargs., DeciderAgent user prompt must render the current_price anchor value., Regression guard: positional decide(context, [], []) must not raise., SynthesizerAgent.synthesize must accept current_price/current_price_time kwargs., TestAgentPrompts

### Community 9 - "ForexFactoryCalendar"
Cohesion: 0.16
Nodes (10): ForexFactoryCalendar, Any, Convert raw time text to ISO timestamp (best-effort)., Map raw impact text to standard impact level., Economic calendar provider via ForexFactory scraping., Initialize calendar provider.          Args:             cache_hours: Hours to c, Fetch upcoming economic calendar events.          Returns:             List of e, Check if cache is still valid. (+2 more)

### Community 11 - "Agent Instructions"
Cohesion: 0.25
Nodes (7): Agent Instructions, Architecture, Critical Invariants, graphify, Quick Commands, Testing, Toolchain

### Community 24 - "_make_mcp_tool_result"
Cohesion: 0.27
Nodes (4): _make_mcp_result(), Create a mock object mimicking mcp.types.CallToolResult.      Matches the real s, Verify get_broker_time returns naive datetime and sends correct request., TestGetBrokerTime

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
Cohesion: 0.12
Nodes (15): Reviews trading decisions and provides feedback., Synthesizes market context from structure analysis and calendar., ReviewerAgent, SynthesizerAgent, Tests for API key and base_url passthrough in agents., When a pre-built client is provided, base_url must be ignored., SynthesizerAgent must pass both api_key and base_url when provided., ReviewerAgent must pass api_key to OpenAI constructor. (+7 more)

### Community 33 - "MarketContextSummary"
Cohesion: 0.15
Nodes (7): OpenAI, DeciderAgent, Makes trading decisions based on market context., DeciderAgent must pass api_key to OpenAI constructor., DeciderAgent must pass base_url to OpenAI constructor., DeciderAgent.decide must accept a current_price keyword argument., DeciderAgent must use DECIDER_SYSTEM_PROMPT from prompts.py.

### Community 34 - "setup_logging"
Cohesion: 0.22
Nodes (4): Any, MarketContextSummary, Summary of market context from synthesizer agent., TestMarketContextSummary

### Community 35 - "DecisionOutput"
Cohesion: 0.24
Nodes (4): DecisionOutput, Decision output from decider agent., ReviewerAgent must use REVIEWER_SYSTEM_PROMPT from prompts.py., TestDecisionOutput

## Knowledge Gaps
- **27 isolated node(s):** `trading-ai-agent`, `graphify`, `Quick Commands`, `Critical Invariants`, `Architecture` (+22 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TerminalDataProvider` connect `._run_async` to `Mt5DataProvider`, `TestGetCandlesCsv`, `_make_mcp_tool_result`, `TerminalApiError`, `test_terminal_data_provider.py`, `TestGetCandlesBrokerNow`, `TestGetPositions`, `TestGetPendingOrders`, `TestGetSymbolPrice`?**
  _High betweenness centrality (0.176) - this node is a cross-community bridge._
- **Why does `TradingGraph` connect `AgentState` to `MarketContextSummary`, `Mt5DataProvider`, `setup_logging`, `DecisionOutput`, `SnapshotBuilder`?**
  _High betweenness centrality (0.176) - this node is a cross-community bridge._
- **Why does `main()` connect `Mt5DataProvider` to `SynthesizerAgent`, `MarketContextSummary`, `AgentState`, `ForexFactoryCalendar`, `._run_async`?**
  _High betweenness centrality (0.138) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `MarketContextSummary` (e.g. with `DeciderAgent` and `ReviewerAgent`) actually correct?**
  _`MarketContextSummary` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `TerminalDataProvider` (e.g. with `TestErrorHandling` and `TestGetBrokerTime`) actually correct?**
  _`TerminalDataProvider` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `SnapshotBuilder` (e.g. with `AgentState` and `TradingGraph`) actually correct?**
  _`SnapshotBuilder` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `DecisionOutput` (e.g. with `DeciderAgent` and `ReviewerAgent`) actually correct?**
  _`DecisionOutput` has 15 INFERRED edges - model-reasoned connections that need verification._
