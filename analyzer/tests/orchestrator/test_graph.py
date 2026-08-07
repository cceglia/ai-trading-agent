from unittest.mock import MagicMock

from src.analysis.market_structure_engine.models import (
    DecisionAction,
    ExecutionBlockerType,
)
from src.decision.models import BiasLevel, MarketContextSummary
from src.orchestrator.graph import TradingGraph


def _graph(synthesizer=None):
    return TradingGraph(
        data_provider=MagicMock(),
        structure_analyzer=MagicMock(),
        calendar_provider=MagicMock(),
        synthesizer=synthesizer or MagicMock(),
    )


def test_graph_has_no_secondary_llm_nodes():
    graph = _graph()
    nodes = set(graph.graph.get_graph().nodes)
    assert "decide" not in nodes
    assert "review" not in nodes
    assert "deterministic_decision" in nodes
    assert "pre_llm_validation" in nodes


def test_deterministic_decision_uses_policy_action_without_llm():
    graph = _graph()
    policy = MagicMock()
    policy.allowed_actions = (DecisionAction.SELL_SETUP,)
    policy.execution_blockers = ()
    state = {
        "symbol": "EURUSD",
        "execution_policy": policy,
        "calendar_events": [],
        "fatal_error": None,
    }

    result = graph._deterministic_decision(state)

    assert result["decision"].action == DecisionAction.SELL_SETUP
    assert result["deterministic_validation"] is None
    graph.synthesizer.synthesize.assert_not_called()


def test_deterministic_decision_defaults_to_no_trade_when_policy_blocks():
    graph = _graph()
    policy = MagicMock()
    policy.allowed_actions = ()
    policy.execution_blockers = (MagicMock(blocker_type=ExecutionBlockerType.CANDIDATE),)

    result = graph._deterministic_decision(
        {
            "symbol": "EURUSD",
            "execution_policy": policy,
            "calendar_events": [],
            "fatal_error": None,
        }
    )

    assert result["decision"].action == DecisionAction.NO_TRADE


def test_synthesis_receives_deterministic_facts(monkeypatch):
    synthesizer = MagicMock()
    synthesizer.synthesize.return_value = MarketContextSummary(
        symbol="EURUSD", bias=BiasLevel.NEUTRAL, confidence=50, reasoning="facts"
    )
    graph = _graph(synthesizer)
    monkeypatch.setattr("src.orchestrator.graph.should_run_synthesis", lambda *_: True)
    setup = MagicMock()
    risk = MagicMock()
    policy = MagicMock()
    graph._synthesize_context(
        {
            "symbol": "EURUSD",
            "structure_analysis": {"timeframes": {}},
            "calendar_events": [],
            "broker_now": None,
            "deterministic_setup": setup,
            "risk_policy": risk,
            "execution_policy": policy,
            "fatal_error": None,
        }
    )

    call = synthesizer.synthesize.call_args.kwargs
    assert call["deterministic_setup"] is setup
    assert call["risk_policy"] is risk
    assert call["execution_policy"] is policy
