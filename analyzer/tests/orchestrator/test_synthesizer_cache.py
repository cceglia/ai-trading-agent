"""The synthesizer is the only optional LLM call in the graph."""

from datetime import datetime
from unittest.mock import MagicMock

from src.decision.models import SynthesisResponse
from src.orchestrator.graph import TradingGraph


def _graph(synthesizer):
    return TradingGraph(
        data_provider=MagicMock(),
        structure_analyzer=MagicMock(),
        calendar_provider=MagicMock(),
        synthesizer=synthesizer,
    )


def _state(**overrides):
    state = {
        "symbol": "EURUSD",
        "structure_analysis": {"timeframes": {}},
        "calendar_events": [],
        "broker_now": datetime(2026, 8, 7, 12),
        "deterministic_setup": MagicMock(),
        "risk_policy": MagicMock(),
        "execution_policy": MagicMock(),
        "deterministic_validation": MagicMock(valid=True),
        "fatal_error": None,
    }
    state.update(overrides)
    return state


def test_synthesis_makes_at_most_one_llm_call_and_succeeds(monkeypatch, tmp_path):
    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
    synthesizer = MagicMock()
    synthesizer.synthesize.return_value = SynthesisResponse(
        explanation="deterministic context",
        risks=["Calendar risk"],
        confluences=["Confirmed structure"],
    )
    graph = _graph(synthesizer)
    monkeypatch.setattr("src.orchestrator.graph.should_run_synthesis", lambda *_: True)
    result = graph._synthesize_context(_state())
    assert synthesizer.synthesize.call_count == 1
    assert result["synthesis_status"] == "SUCCESS"
    assert isinstance(result["synthesis"], SynthesisResponse)
    assert result["synthesis"].explanation == "deterministic context"
    assert list((tmp_path / "analysis").rglob("*.json")) != []
    assert not hasattr(graph, "secondary_agent")


def test_schema_invalid_synthesis_is_distinct_from_provider_failure(monkeypatch, tmp_path):
    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
    synthesizer = MagicMock()
    synthesizer.synthesize.return_value = {
        "explanation": "ok",
        "risks": [],
        "confluences": [],
        "action": "buy_setup",
    }
    graph = _graph(synthesizer)
    monkeypatch.setattr("src.orchestrator.graph.should_run_synthesis", lambda *_: True)
    result = graph._synthesize_context(_state())
    assert result["synthesis_status"] == "FAILED"
    assert result["synthesis"] is None
    assert result["synthesis_error"] == "SYNTHESIS_SCHEMA_INVALID"
    synthesizer.synthesize.assert_called_once()
    assert list((tmp_path / "analysis").rglob("*.json")) == []


def test_cache_hit_skips_llm_call(monkeypatch, tmp_path):
    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
    synthesizer = MagicMock()
    synthesizer.synthesize.return_value = SynthesisResponse(
        explanation="context", risks=[], confluences=[]
    )
    graph = _graph(synthesizer)
    state = _state(
        structure_analysis={
            "timeframes": {"D1": {"market_structure": {"primary_structure": "BULLISH"}}}
        }
    )
    first = graph._synthesize_context(state)
    assert first["synthesis_status"] == "SUCCESS"
    assert synthesizer.synthesize.call_count == 1
    second = graph._synthesize_context(state)
    assert second["synthesis_status"] == "SUCCESS"
    assert second["synthesis"].explanation == "context"
    assert synthesizer.synthesize.call_count == 1


def test_deterministic_decision_does_not_call_synthesizer():
    synthesizer = MagicMock()
    graph = _graph(synthesizer)
    policy = MagicMock(allowed_actions=(), execution_blockers=())
    result = graph._deterministic_decision(
        {"symbol": "EURUSD", "execution_policy": policy, "fatal_error": None}
    )
    assert result["decision"].action == "no_trade"
    synthesizer.synthesize.assert_not_called()


def test_synthesizer_failure_is_degraded_without_invalidating_deterministic_facts(
    monkeypatch, tmp_path
):
    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
    synthesizer = MagicMock()
    synthesizer.synthesize.side_effect = TimeoutError("provider timeout")
    graph = _graph(synthesizer)
    validation = MagicMock(valid=True)
    result = graph._synthesize_context(_state(deterministic_validation=validation))
    assert result["synthesis_status"] == "FAILED"
    assert result["synthesis"] is None
    assert result["synthesis_error"] == "SYNTHESIS_UNAVAILABLE"
    assert validation.valid is True
    synthesizer.synthesize.assert_called_once()
    assert list((tmp_path / "analysis").rglob("*.json")) == []
