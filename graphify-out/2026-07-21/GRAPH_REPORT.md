# Graph Report - Agent  (2026-07-21)

## Corpus Check
- 38 files · ~10,919 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 380 nodes · 652 edges · 26 communities (24 shown, 2 thin omitted)
- Extraction: 84% EXTRACTED · 16% INFERRED · 0% AMBIGUOUS · INFERRED: 106 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

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
- setup_logging
- main.py

## God Nodes (most connected - your core abstractions)
1. `MarketContextSummary` - 33 edges
2. `ReviewVerdict` - 32 edges
3. `Evaluator` - 31 edges
4. `DecisionOutput` - 31 edges
5. `SnapshotBuilder` - 30 edges
6. `AgentState` - 28 edges
7. `TradingGraph` - 28 edges
8. `DataSource` - 18 edges
9. `SynthesizerAgent` - 16 edges
10. `BiasLevel` - 16 edges

## Surprising Connections (you probably didn't know these)
- `TestMaxReviewAttempts` --uses--> `BiasLevel`  [INFERRED]
  tests/orchestrator/test_graph.py → src/decision/models.py
- `TestTradingGraphInit` --uses--> `BiasLevel`  [INFERRED]
  tests/orchestrator/test_graph.py → src/decision/models.py
- `TestTradingGraphNodes` --uses--> `BiasLevel`  [INFERRED]
  tests/orchestrator/test_graph.py → src/decision/models.py
- `mock_synthesizer()` --calls--> `MarketContextSummary`  [EXTRACTED]
  tests/orchestrator/test_graph.py → src/decision/models.py
- `TestMaxReviewAttempts` --uses--> `MarketContextSummary`  [INFERRED]
  tests/orchestrator/test_graph.py → src/decision/models.py

## Import Cycles
- None detected.

## Communities (26 total, 2 thin omitted)

### Community 0 - "MarketContextSummary"
Cohesion: 0.06
Nodes (38): BaseModel, Enum, OpenAI, DeciderAgent, Reviews trading decisions and provides feedback., Synthesizes market context from structure analysis and calendar., Makes trading decisions based on market context., ReviewerAgent (+30 more)

### Community 1 - "Mt5DataProvider"
Cohesion: 0.14
Nodes (8): Mt5DataProvider, MetaTrader 5 data provider via MCP server., MetaTrader 5 data provider via MCP server.      Implements the DataSource protoc, Parse CSV candle data into list of dictionaries.          Args:             csv_, Initialize MT5 data provider.          Args:             server_url: MCP server, Return string representation., Establish connection to MCP server., Disconnect from MCP server.

### Community 2 - "DataSource"
Cohesion: 0.09
Nodes (16): Protocol, CalendarProvider, DataSource, Get latest price info for a symbol.          Args:             symbol: Trading s, Get open positions.          Args:             symbol: Optional symbol filter, Get pending orders.          Args:             symbol: Optional symbol filter, Economic calendar data provider., Read-only market data provider. (+8 more)

### Community 3 - "AgentState"
Cohesion: 0.06
Nodes (30): datetime, AgentState, Analyze market structure with candle-aligned caching., State for the trading graph., Evaluate calendar events., Synthesize market context., Make trading decision., Conditional edge from review to decide or end. (+22 more)

### Community 4 - "SnapshotBuilder"
Cohesion: 0.11
Nodes (11): Any, Snapshot builder for converting MCP CSV data to normalized engine snapshots., Build normalized snapshot from parsed bars.          Args:             bars: Lis, Validate snapshot against engine schema.          Args:             snapshot: Th, Builds normalized snapshots from MCP CSV data.      Converts raw CSV candle data, Convert CSV to normalized snapshot.          Args:             csv_data: CSV str, Parse CSV string to list of bar dicts.          Args:             csv_data: Raw, SnapshotBuilder (+3 more)

### Community 5 - "Evaluator"
Cohesion: 0.07
Nodes (17): Evaluator, Check if an event falls within the time window from now.          Returns False, Evaluate events for symbol with timeframe-dependent window.          Args:, Evaluates calendar events for trading symbols., High-impact event outside the window should NOT block., High-impact event within the window SHOULD block., Event with no time field should be excluded (fail-safe)., Event with unparseable time should be excluded. (+9 more)

### Community 6 - "Trading AI Agent"
Cohesion: 0.07
Nodes (28): Analysis Layer (`src/analysis/`), Architecture, Calendar Layer (`src/calendar/`), CLI Commands, Code Quality, Components, Configuration, Configuration (`config/`) (+20 more)

### Community 7 - "TestSynthesizerPrompt"
Cohesion: 0.11
Nodes (4): LLM prompts with embedded rules.json content., TestDeciderPrompt, TestReviewerPrompt, TestSynthesizerPrompt

### Community 8 - "SynthesizerAgent"
Cohesion: 0.15
Nodes (7): Any, Call an MCP tool synchronously.          Args:             tool_name: Name of th, Fetch OHLC candles as CSV string.          Args:             symbol: Trading sym, Get latest price info for a symbol.          Args:             symbol: Trading s, Get open positions.          Args:             symbol: Optional symbol filter. I, Get pending orders.          Args:             symbol: Optional symbol filter. I, Execute operation with retry logic and exponential backoff.          Args:

### Community 9 - "ForexFactoryCalendar"
Cohesion: 0.15
Nodes (9): ForexFactoryCalendar, Convert raw time text to ISO timestamp (best-effort)., Map raw impact text to standard impact level., Economic calendar provider via ForexFactory scraping., Initialize calendar provider.          Args:             cache_hours: Hours to c, Fetch upcoming economic calendar events.          Returns:             List of e, Check if cache is still valid., Scrape ForexFactory calendar page. (+1 more)

### Community 11 - "Agent Instructions"
Cohesion: 0.25
Nodes (7): Agent Instructions, Architecture, Critical Invariants, graphify, Quick Commands, Testing, Toolchain

### Community 24 - "setup_logging"
Cohesion: 0.36
Nodes (3): Configure structured logging for the trading agent., setup_logging(), TestSetupLogging

### Community 25 - "main.py"
Cohesion: 0.38
Nodes (5): BaseSettings, Trading agent configuration., Settings, main(), Trading AI Agent - CLI Entry Point.

## Knowledge Gaps
- **27 isolated node(s):** `trading-ai-agent`, `graphify`, `Quick Commands`, `Critical Invariants`, `Architecture` (+22 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TradingGraph` connect `AgentState` to `MarketContextSummary`, `main.py`, `SnapshotBuilder`?**
  _High betweenness centrality (0.156) - this node is a cross-community bridge._
- **Why does `SnapshotBuilder` connect `SnapshotBuilder` to `AgentState`?**
  _High betweenness centrality (0.111) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `MarketContextSummary` (e.g. with `DeciderAgent` and `ReviewerAgent`) actually correct?**
  _`MarketContextSummary` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `ReviewVerdict` (e.g. with `DeciderAgent` and `ReviewerAgent`) actually correct?**
  _`ReviewVerdict` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `Evaluator` (e.g. with `TestEvaluatorBlocking` and `TestEvaluatorConfig`) actually correct?**
  _`Evaluator` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `DecisionOutput` (e.g. with `DeciderAgent` and `ReviewerAgent`) actually correct?**
  _`DecisionOutput` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `SnapshotBuilder` (e.g. with `AgentState` and `TradingGraph`) actually correct?**
  _`SnapshotBuilder` has 5 INFERRED edges - model-reasoned connections that need verification._
