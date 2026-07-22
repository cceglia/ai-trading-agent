# Graph Report - Agent  (2026-07-22)

## Corpus Check
- 38 files · ~11,498 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 397 nodes · 697 edges · 24 communities (22 shown, 2 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 108 edges (avg confidence: 0.54)
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

## God Nodes (most connected - your core abstractions)
1. `MarketContextSummary` - 33 edges
2. `ReviewVerdict` - 32 edges
3. `Evaluator` - 31 edges
4. `DecisionOutput` - 31 edges
5. `SnapshotBuilder` - 30 edges
6. `AgentState` - 28 edges
7. `TradingGraph` - 28 edges
8. `SynthesizerAgent` - 21 edges
9. `DataSource` - 18 edges
10. `DeciderAgent` - 17 edges

## Surprising Connections (you probably didn't know these)
- `TestAgentApiKey` --uses--> `SynthesizerAgent`  [INFERRED]
  tests/decision/test_agents_api_key.py → src/decision/agents.py
- `TestAgentBaseUrl` --uses--> `SynthesizerAgent`  [INFERRED]
  tests/decision/test_agents_api_key.py → src/decision/agents.py
- `TestAgentPrompts` --uses--> `DeciderAgent`  [INFERRED]
  tests/decision/test_agents_prompts.py → src/decision/agents.py
- `TestAgentPrompts` --uses--> `ReviewerAgent`  [INFERRED]
  tests/decision/test_agents_prompts.py → src/decision/agents.py
- `TestTradingGraphNodes` --uses--> `BiasLevel`  [INFERRED]
  tests/orchestrator/test_graph.py → src/decision/models.py

## Import Cycles
- None detected.

## Communities (24 total, 2 thin omitted)

### Community 0 - "MarketContextSummary"
Cohesion: 0.08
Nodes (28): BaseModel, Any, Synthesizes market context from structure analysis and calendar., SynthesizerAgent, BiasLevel, DecisionAction, DecisionOutput, MarketContextSummary (+20 more)

### Community 1 - "Mt5DataProvider"
Cohesion: 0.07
Nodes (23): BaseSettings, Trading agent configuration., Settings, main(), Trading AI Agent - CLI Entry Point., Mt5DataProvider, Any, MetaTrader 5 data provider via MCP server. (+15 more)

### Community 2 - "DataSource"
Cohesion: 0.10
Nodes (17): Protocol, CalendarProvider, DataSource, Any, Get latest price info for a symbol.          Args:             symbol: Trading s, Get open positions.          Args:             symbol: Optional symbol filter, Get pending orders.          Args:             symbol: Optional symbol filter, Economic calendar data provider. (+9 more)

### Community 3 - "AgentState"
Cohesion: 0.07
Nodes (31): CompiledStateGraph, datetime, Snapshot builder for converting MCP CSV data to normalized engine snapshots., AgentState, Any, Fetch market data from MT5., Analyze market structure with candle-aligned caching., Evaluate calendar events. (+23 more)

### Community 4 - "SnapshotBuilder"
Cohesion: 0.12
Nodes (10): Any, Build normalized snapshot from parsed bars.          Args:             bars: Lis, Validate snapshot against engine schema.          Args:             snapshot: Th, Builds normalized snapshots from MCP CSV data.      Converts raw CSV candle data, Convert CSV to normalized snapshot.          Args:             csv_data: CSV str, Parse CSV string to list of bar dicts.          Args:             csv_data: Raw, SnapshotBuilder, TestSnapshotBuilderParsing (+2 more)

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
Cohesion: 0.08
Nodes (18): OpenAI, DeciderAgent, Reviews trading decisions and provides feedback., Makes trading decisions based on market context., ReviewerAgent, Tests for API key and base_url passthrough in agents., When a pre-built client is provided, base_url must be ignored., SynthesizerAgent must pass both api_key and base_url when provided. (+10 more)

### Community 9 - "ForexFactoryCalendar"
Cohesion: 0.17
Nodes (10): ForexFactoryCalendar, Any, Convert raw time text to ISO timestamp (best-effort)., Map raw impact text to standard impact level., Economic calendar provider via ForexFactory scraping., Initialize calendar provider.          Args:             cache_hours: Hours to c, Fetch upcoming economic calendar events.          Returns:             List of e, Check if cache is still valid. (+2 more)

### Community 11 - "Agent Instructions"
Cohesion: 0.25
Nodes (7): Agent Instructions, Architecture, Critical Invariants, graphify, Quick Commands, Testing, Toolchain

## Knowledge Gaps
- **27 isolated node(s):** `trading-ai-agent`, `graphify`, `Quick Commands`, `Critical Invariants`, `Architecture` (+22 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TradingGraph` connect `AgentState` to `MarketContextSummary`, `Mt5DataProvider`, `SnapshotBuilder`?**
  _High betweenness centrality (0.150) - this node is a cross-community bridge._
- **Why does `SnapshotBuilder` connect `SnapshotBuilder` to `AgentState`?**
  _High betweenness centrality (0.107) - this node is a cross-community bridge._
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
