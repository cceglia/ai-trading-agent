# Graph Report - Agent  (2026-07-23)

## Corpus Check
- 41 files · ~17,500 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 573 nodes · 1032 edges · 38 communities (33 shown, 5 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 151 edges (avg confidence: 0.54)
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
- _select_canonical_current_price

## God Nodes (most connected - your core abstractions)
1. `MarketContextSummary` - 43 edges
2. `TerminalDataProvider` - 36 edges
3. `DecisionOutput` - 36 edges
4. `AgentState` - 36 edges
5. `SnapshotBuilder` - 35 edges
6. `TradingGraph` - 34 edges
7. `ReviewVerdict` - 32 edges
8. `_make_mcp_result()` - 32 edges
9. `Evaluator` - 31 edges
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

## Communities (38 total, 5 thin omitted)

### Community 0 - "MarketContextSummary"
Cohesion: 0.22
Nodes (5): Review verdict from reviewer agent., ReviewVerdict, TestReviewVerdict, mock_reviewer(), TestReviewRouting

### Community 1 - "Mt5DataProvider"
Cohesion: 0.19
Nodes (10): BaseSettings, Trading agent configuration., Settings, MonkeyPatch, Settings().terminal_server_url returns the default MCP URL., Settings().terminal_api_key returns empty string by default., TRADING_TERMINAL_API_KEY env var overrides the default., TRADING_TERMINAL_SERVER_URL env var overrides the default. (+2 more)

### Community 2 - "DataSource"
Cohesion: 0.09
Nodes (19): Protocol, CalendarProvider, DataSource, Any, datetime, Fetch OHLC candles as CSV string.          Args:             symbol: Trading sym, Get latest price info for a symbol.          Args:             symbol: Trading s, Get open positions.          Args:             symbol: Optional symbol filter (+11 more)

### Community 3 - "AgentState"
Cohesion: 0.05
Nodes (53): CompiledStateGraph, BiasLevel, DecisionAction, Structural bias levels., AgentState, Any, Select the canonical current price across timeframes.      The canonical current, Build a compact version of structure analysis suitable for LLM prompts.      The (+45 more)

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
Cohesion: 0.10
Nodes (15): main(), Trading AI Agent - CLI Entry Point., ForexFactoryCalendar, Any, Convert raw time text to ISO timestamp (best-effort)., Map raw impact text to standard impact level., Economic calendar provider via ForexFactory scraping., Initialize calendar provider.          Args:             cache_hours: Hours to c (+7 more)

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
Cohesion: 0.16
Nodes (11): Synthesizes market context from structure analysis and calendar., SynthesizerAgent, Tests for API key and base_url passthrough in agents., When a pre-built client is provided, base_url must be ignored., SynthesizerAgent must pass both api_key and base_url when provided., When no api_key given, OpenAI() uses its own default., SynthesizerAgent must pass base_url to OpenAI constructor., SynthesizerAgent must pass api_key to OpenAI constructor. (+3 more)

### Community 33 - "MarketContextSummary"
Cohesion: 0.15
Nodes (7): OpenAI, DeciderAgent, Makes trading decisions based on market context., DeciderAgent must pass api_key to OpenAI constructor., DeciderAgent must pass base_url to OpenAI constructor., DeciderAgent.decide must accept a current_price keyword argument., DeciderAgent must use DECIDER_SYSTEM_PROMPT from prompts.py.

### Community 34 - "setup_logging"
Cohesion: 0.18
Nodes (7): MarketContextSummary, Summary of market context from synthesizer agent., sample_decision(), sample_market_context(), sample_review(), TestMarketContextSummary, mock_synthesizer()

### Community 35 - "DecisionOutput"
Cohesion: 0.17
Nodes (6): BaseModel, Any, DecisionOutput, Decision output from decider agent., TestDecisionOutput, mock_decider()

### Community 36 - "TestGetCandlesCsv"
Cohesion: 0.18
Nodes (6): Reviews trading decisions and provides feedback., ReviewerAgent, ReviewerAgent must pass api_key to OpenAI constructor., ReviewerAgent must pass base_url to OpenAI constructor., Tests for prompt usage in agents., ReviewerAgent must use REVIEWER_SYSTEM_PROMPT from prompts.py.

### Community 37 - "_select_canonical_current_price"
Cohesion: 0.33
Nodes (6): RED-first tests for the canonical current-price selection helper (TASK-6).  Thes, Lazy-import the not-yet-existing helper so collection succeeds.      Raises ``Im, Build a single per-timeframe engine-output dict for the selector., _select_canonical_current_price(), TestSelectCanonicalCurrentPrice, _tf()

## Knowledge Gaps
- **27 isolated node(s):** `trading-ai-agent`, `graphify`, `Quick Commands`, `Critical Invariants`, `Architecture` (+22 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TradingGraph` connect `AgentState` to `MarketContextSummary`, `setup_logging`, `DecisionOutput`, `SnapshotBuilder`, `ForexFactoryCalendar`?**
  _High betweenness centrality (0.186) - this node is a cross-community bridge._
- **Why does `TerminalDataProvider` connect `._run_async` to `ForexFactoryCalendar`, `_make_mcp_tool_result`, `TerminalApiError`, `test_terminal_data_provider.py`, `TestGetCandlesBrokerNow`, `TestGetPositions`, `TestGetPendingOrders`, `TestGetSymbolPrice`?**
  _High betweenness centrality (0.174) - this node is a cross-community bridge._
- **Why does `main()` connect `ForexFactoryCalendar` to `SynthesizerAgent`, `Mt5DataProvider`, `MarketContextSummary`, `AgentState`, `TestGetCandlesCsv`, `._run_async`?**
  _High betweenness centrality (0.138) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `MarketContextSummary` (e.g. with `DeciderAgent` and `ReviewerAgent`) actually correct?**
  _`MarketContextSummary` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `TerminalDataProvider` (e.g. with `TestErrorHandling` and `TestGetBrokerTime`) actually correct?**
  _`TerminalDataProvider` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `DecisionOutput` (e.g. with `DeciderAgent` and `ReviewerAgent`) actually correct?**
  _`DecisionOutput` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `AgentState` (e.g. with `SnapshotBuilder` and `DecisionOutput`) actually correct?**
  _`AgentState` has 9 INFERRED edges - model-reasoned connections that need verification._
