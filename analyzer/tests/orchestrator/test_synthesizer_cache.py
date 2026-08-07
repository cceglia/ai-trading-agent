"""The synthesizer is the only optional LLM call in the graph."""

from unittest.mock import MagicMock

from src.analysis.market_structure_engine.models import BiasLevel
from src.decision.models import MarketContextSummary
from src.orchestrator.graph import TradingGraph


def _graph(synthesizer):
    return TradingGraph(
        data_provider=MagicMock(),
        structure_analyzer=MagicMock(),
        calendar_provider=MagicMock(),
        synthesizer=synthesizer,
    )


def test_synthesis_makes_at_most_one_llm_call(monkeypatch):
    synthesizer = MagicMock()
    synthesizer.synthesize.return_value = MarketContextSummary(
        symbol="EURUSD", bias=BiasLevel.NEUTRAL, confidence=50, reasoning="context"
    )
    graph = _graph(synthesizer)
    monkeypatch.setattr("src.orchestrator.graph.should_run_synthesis", lambda *_: True)
    state = {
        "symbol": "EURUSD",
        "structure_analysis": {"timeframes": {}},
        "calendar_events": [],
        "broker_now": None,
        "deterministic_setup": MagicMock(),
        "risk_policy": MagicMock(),
        "execution_policy": MagicMock(),
        "fatal_error": None,
    }
    graph._synthesize_context(state)
    assert synthesizer.synthesize.call_count == 1
    assert not hasattr(graph, "secondary_agent")


def test_deterministic_decision_does_not_call_synthesizer():
    synthesizer = MagicMock()
    graph = _graph(synthesizer)
    policy = MagicMock(allowed_actions=(), execution_blockers=())
    result = graph._deterministic_decision(
        {"symbol": "EURUSD", "execution_policy": policy, "fatal_error": None}
    )
    assert result["decision"].action == "no_trade"
    synthesizer.synthesize.assert_not_called()
