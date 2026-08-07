"""Current execution-mode and model-identity enum contracts."""

from src.analysis.market_structure_engine.models import (
    ExecutionMode,
    ModelIdentityResolutionStatus,
)


def test_model_identity_status_values():
    assert {item.value for item in ModelIdentityResolutionStatus} == {
        "RESOLVED",
        "OVERRIDDEN",
        "UNRESOLVED",
    }


def test_execution_modes_are_explicit():
    assert ExecutionMode.LIVE.value == "LIVE"
    assert ExecutionMode.PAPER.value == "PAPER"
    assert ExecutionMode.DETERMINISTIC_BACKTEST.value == "DETERMINISTIC_BACKTEST"


def test_shared_decision_enums_remain_consistent():
    from src.analysis.market_structure_engine.models import DecisionAction as EngineAction
    from src.decision.models import DecisionAction

    assert EngineAction is DecisionAction
