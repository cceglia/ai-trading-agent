import logging
from collections.abc import Callable
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from src.decision.cost_tracker import CostLimitExceeded, CostTracker
from src.decision.models import (
    BiasLevel,
    DecisionAction,
    DecisionOutput,
    MarketContextSummary,
    ReviewVerdict,
)
from src.orchestrator.graph import AgentState, TradingGraph


@pytest.fixture
def mock_data_provider():
    provider = MagicMock()
    provider.get_positions.return_value = []
    provider.get_pending_orders.return_value = []
    provider.get_symbol_price.return_value = {"bid": 1.0875, "ask": 1.0877}
    provider.get_candles.return_value = (
        "time,open,high,low,close\n2024-01-01,1.0850,1.0900,1.0800,1.0875\n"
    )
    provider.get_broker_time.return_value = datetime(2026, 7, 25, 14, 0)
    return provider


@pytest.fixture
def mock_structure_analyzer():
    analyzer = MagicMock()
    analyzer.analyze.return_value = {"bias": "bullish", "confidence": 75}
    return analyzer


@pytest.fixture
def mock_calendar_provider():
    provider = MagicMock()
    provider.fetch_events.return_value = []
    return provider


@pytest.fixture
def mock_synthesizer():
    synthesizer = MagicMock()
    synthesizer.synthesize.return_value = MarketContextSummary(
        symbol="EURUSD",
        bias=BiasLevel.BULLISH,
        confidence=75.0,
        reasoning="Bullish structure",
    )
    return synthesizer


@pytest.fixture
def mock_decider():
    decider = MagicMock()
    decider.decide.return_value = DecisionOutput(
        symbol="EURUSD",
        action=DecisionAction.BUY_SETUP,
        entry_price=1.0875,
        stop_loss=1.0825,
        take_profit=1.0975,
        reasoning="Good setup",
        risk_reward_ratio=2.0,
    )
    return decider


@pytest.fixture
def mock_reviewer():
    reviewer = MagicMock()
    reviewer.review.return_value = ReviewVerdict(
        approved=True,
        reasoning="All criteria met",
    )
    return reviewer


@pytest.fixture
def trading_graph(
    mock_data_provider,
    mock_structure_analyzer,
    mock_calendar_provider,
    mock_synthesizer,
    mock_decider,
    mock_reviewer,
):
    return TradingGraph(
        data_provider=mock_data_provider,
        structure_analyzer=mock_structure_analyzer,
        calendar_provider=mock_calendar_provider,
        synthesizer=mock_synthesizer,
        decider=mock_decider,
        reviewer=mock_reviewer,
    )


class TestTradingGraphInit:
    def test_creates_graph(self, trading_graph):
        assert trading_graph.graph is not None

    def test_stores_dependencies(self, trading_graph):
        assert trading_graph.data_provider is not None
        assert trading_graph.structure_analyzer is not None
        assert trading_graph.calendar_provider is not None
        assert trading_graph.synthesizer is not None
        assert trading_graph.decider is not None
        assert trading_graph.reviewer is not None


def test_trading_graph_accepts_max_review_attempts(
    mock_data_provider,
    mock_structure_analyzer,
    mock_calendar_provider,
    mock_synthesizer,
    mock_decider,
    mock_reviewer,
):
    graph = TradingGraph(
        data_provider=mock_data_provider,
        structure_analyzer=mock_structure_analyzer,
        calendar_provider=mock_calendar_provider,
        synthesizer=mock_synthesizer,
        decider=mock_decider,
        reviewer=mock_reviewer,
        max_review_attempts=3,
    )
    assert graph.max_review_attempts == 3


def test_trading_graph_defaults_max_review_attempts_from_settings(
    mock_data_provider,
    mock_structure_analyzer,
    mock_calendar_provider,
    mock_synthesizer,
    mock_decider,
    mock_reviewer,
):
    graph = TradingGraph(
        data_provider=mock_data_provider,
        structure_analyzer=mock_structure_analyzer,
        calendar_provider=mock_calendar_provider,
        synthesizer=mock_synthesizer,
        decider=mock_decider,
        reviewer=mock_reviewer,
    )
    assert graph.max_review_attempts == 2


class TestTradingGraphNodes:
    def test_fetch_data_calls_provider(self, trading_graph, mock_data_provider):
        state = AgentState(
            calendar_events=None,
            current_pending_orders=[],
            current_positions=[],
            decision=None,
            errors=[],
            fatal_error=None,
            final_output=None,
            market_context=None,
            review=None,
            review_attempts=0,
            review_feedback=None,
            structure_analysis=None,
            symbol="EURUSD",
            symbol_price=None,
        )
        result = trading_graph._fetch_data(state)
        mock_data_provider.get_positions.assert_called_with("EURUSD")
        mock_data_provider.get_pending_orders.assert_called_with("EURUSD")
        mock_data_provider.get_symbol_price.assert_called_with("EURUSD")
        assert "current_positions" in result

    def test_fetch_data_handles_error(self, trading_graph, mock_data_provider):
        mock_data_provider.get_positions.side_effect = Exception("Connection lost")
        state = AgentState(
            calendar_events=None,
            current_pending_orders=[],
            current_positions=[],
            decision=None,
            errors=[],
            fatal_error=None,
            final_output=None,
            market_context=None,
            review=None,
            review_attempts=0,
            review_feedback=None,
            structure_analysis=None,
            symbol="EURUSD",
            symbol_price=None,
        )
        result = trading_graph._fetch_data(state)
        assert result["fatal_error"] == "Data fetch failed: Connection lost"

    def test_evaluate_calendar_fetches_events(self, trading_graph, mock_calendar_provider):
        state = AgentState(
            calendar_events=None,
            current_pending_orders=[],
            current_positions=[],
            decision=None,
            errors=[],
            fatal_error=None,
            final_output=None,
            market_context=None,
            review=None,
            review_attempts=0,
            review_feedback=None,
            structure_analysis=None,
            symbol="EURUSD",
            symbol_price=None,
        )
        result = trading_graph._evaluate_calendar(state)
        mock_calendar_provider.fetch_events.assert_called_once()
        assert "calendar_events" in result


class TestReviewRouting:
    def test_review_to_end_when_approved(self, trading_graph):
        state = {
            "review": ReviewVerdict(approved=True, reasoning="OK"),
            "review_attempts": 1,
            "fatal_error": None,
        }
        assert trading_graph._review_to_decide(state) == "end"

    def test_review_to_retry_when_not_approved(self, trading_graph):
        state = {
            "review": ReviewVerdict(approved=False, reasoning="Bad"),
            "review_attempts": 1,
            "fatal_error": None,
        }
        assert trading_graph._review_to_decide(state) == "retry"

    def test_review_to_end_when_max_attempts(self, trading_graph):
        state = {
            "review": ReviewVerdict(approved=False, reasoning="Bad"),
            "review_attempts": trading_graph.max_review_attempts + 1,
            "fatal_error": None,
        }
        assert trading_graph._review_to_decide(state) == "end"

    def test_review_retries_when_no_review_and_attempts_remaining(self, trading_graph):
        state = {
            "review": None,
            "review_attempts": 0,
            "fatal_error": None,
        }
        assert trading_graph._review_to_decide(state) == "retry"

    def test_review_ends_when_no_review_and_max_attempts(self, trading_graph):
        state = {
            "review": None,
            "review_attempts": trading_graph.max_review_attempts + 1,
            "fatal_error": None,
        }
        assert trading_graph._review_to_decide(state) == "end"


class TestMaxReviewAttempts:
    def test_constant_value(self, trading_graph):
        assert trading_graph.max_review_attempts == 2


def test_analyze_structure_fetches_all_timeframes(tmp_path, monkeypatch):
    """_analyze_structure must fetch all three timeframes fresh (no partial cache)."""
    from datetime import datetime
    from unittest.mock import MagicMock

    from src.orchestrator.graph import AgentState, TradingGraph

    # Setup cache dir so cache mechanics are available
    cache_dir = tmp_path / "analysis"
    cache_dir.mkdir()
    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(cache_dir))

    mock_data_provider = MagicMock()
    mock_data_provider.get_candles.return_value = (
        "time,open,high,low,close\n2024-01-01T00:00:00,1.0850,1.0900,1.0800,1.0875\n"
    )
    broker_time = datetime(2026, 7, 21, 14, 0)
    mock_data_provider.get_broker_time.return_value = broker_time
    # Simulate engine returning multi-timeframe output shape
    mock_structure_analyzer = MagicMock()
    mock_structure_analyzer.analyze.return_value = {
        "timeframes": {
            "D1": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "D1"},
            "H4": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "H4"},
            "H1": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "H1"},
        },
        "confluence": {"status": "NO_VALID_CANDIDATE"},
    }

    graph = TradingGraph(
        data_provider=mock_data_provider,
        structure_analyzer=mock_structure_analyzer,
        calendar_provider=MagicMock(),
        synthesizer=MagicMock(),
        decider=MagicMock(),
        reviewer=MagicMock(),
    )

    state = AgentState(
        calendar_events=None,
        current_pending_orders=[],
        current_positions=[],
        decision=None,
        errors=[],
        fatal_error=None,
        final_output=None,
        market_context=None,
        review=None,
        review_attempts=0,
        review_feedback=None,
        structure_analysis=None,
        symbol="XAUUSD",
        symbol_price=None,
    )
    result = graph._analyze_structure(state)

    # All 3 timeframes must be fetched
    assert mock_data_provider.get_candles.call_count == 3
    from unittest.mock import call as mock_call

    assert (
        mock_call("XAUUSD", "D1", 500, broker_now=broker_time)
        in mock_data_provider.get_candles.call_args_list
    )
    assert (
        mock_call("XAUUSD", "H4", 750, broker_now=broker_time)
        in mock_data_provider.get_candles.call_args_list
    )
    assert (
        mock_call("XAUUSD", "H1", 1000, broker_now=broker_time)
        in mock_data_provider.get_candles.call_args_list
    )

    # Engine receives all 3 snapshots
    engine_snapshots = mock_structure_analyzer.analyze.call_args[0][0]
    for tf in ("D1", "H4", "H1"):
        assert tf in engine_snapshots

    # Per-timeframe keys present in result
    for tf in ("D1", "H4", "H1"):
        assert tf in result["structure_analysis"]


def test_analyze_structure_fetches_all_when_no_cache(tmp_path, monkeypatch):
    """When no cache files exist, all 3 TFs must be fetched fresh."""
    from datetime import datetime
    from unittest.mock import MagicMock

    from src.orchestrator.graph import AgentState, TradingGraph

    cache_dir = tmp_path / "analysis"
    cache_dir.mkdir()
    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(cache_dir))

    broker_time = datetime(2026, 7, 21, 14, 0)
    mock_data_provider = MagicMock()
    mock_data_provider.get_candles.return_value = (
        "time,open,high,low,close\n2024-01-01T00:00:00,1.0850,1.0900,1.0800,1.0875\n"
    )
    mock_data_provider.get_broker_time.return_value = broker_time
    mock_structure_analyzer = MagicMock()
    mock_structure_analyzer.analyze.return_value = {
        "timeframes": {
            "D1": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "D1"},
            "H4": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "H4"},
            "H1": {
                "market_structure": {"primary_structure": "BULLISH"},
                "timeframe": "H1",
                "fresh": True,
            },
        },
        "confluence": {"status": "NO_VALID_CANDIDATE"},
    }

    graph = TradingGraph(
        data_provider=mock_data_provider,
        structure_analyzer=mock_structure_analyzer,
        calendar_provider=MagicMock(),
        synthesizer=MagicMock(),
        decider=MagicMock(),
        reviewer=MagicMock(),
    )

    state = AgentState(
        calendar_events=None,
        current_pending_orders=[],
        current_positions=[],
        decision=None,
        errors=[],
        fatal_error=None,
        final_output=None,
        market_context=None,
        review=None,
        review_attempts=0,
        review_feedback=None,
        structure_analysis=None,
        symbol="XAUUSD",
        symbol_price=None,
    )
    result = graph._analyze_structure(state)

    # No cache exists → all 3 TFs fetched fresh
    assert mock_data_provider.get_candles.call_count == 3
    mock_data_provider.get_candles.assert_any_call("XAUUSD", "H1", 1000, broker_now=broker_time)
    assert result["structure_analysis"].get("H1", {}).get("fresh") is True


def test_analyze_structure_converts_csv_to_snapshots(tmp_path, monkeypatch):
    """_analyze_structure must use SnapshotBuilder to convert CSV to dicts."""
    from datetime import datetime
    from unittest.mock import MagicMock

    from src.orchestrator.graph import AgentState, TradingGraph

    csv_data = (
        "time,open,high,low,close,tick_volume,spread,real_volume\n"
        "2024-01-01T00:00:00,1.0850,1.0900,1.0800,1.0875,1000,1,500\n"
        "2024-01-02T00:00:00,1.0875,1.0950,1.0850,1.0920,1200,1,600\n"
    )

    mock_data_provider = MagicMock()
    mock_data_provider.get_candles.return_value = csv_data
    mock_data_provider.get_broker_time.return_value = datetime(2026, 7, 21, 14, 0)

    mock_structure_analyzer = MagicMock()
    mock_structure_analyzer.analyze.return_value = {"D1": {"analyzed": True}}

    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))

    graph = TradingGraph(
        data_provider=mock_data_provider,
        structure_analyzer=mock_structure_analyzer,
        calendar_provider=MagicMock(),
        synthesizer=MagicMock(),
        decider=MagicMock(),
        reviewer=MagicMock(),
    )

    state = AgentState(
        calendar_events=None,
        current_pending_orders=[],
        current_positions=[],
        decision=None,
        errors=[],
        fatal_error=None,
        final_output=None,
        market_context=None,
        review=None,
        review_attempts=0,
        review_feedback=None,
        structure_analysis=None,
        symbol="EURUSD",
        symbol_price=None,
    )

    graph._analyze_structure(state)

    # Verify structure_analyzer.analyze received dicts, not strings
    analyze_call = mock_structure_analyzer.analyze.call_args
    snapshots_arg = analyze_call[0][0]

    # H1 should be a dict (not a CSV string)
    assert isinstance(snapshots_arg.get("H1"), dict), (
        f"Expected dict, got {type(snapshots_arg.get('H1'))}"
    )

    # Verify the dict has the correct schema
    h1_snapshot = snapshots_arg["H1"]
    assert "bars" in h1_snapshot
    assert "market" in h1_snapshot
    assert h1_snapshot["market"]["symbol"] == "EURUSD"


def test_analyze_structure_uses_preferred_bars(tmp_path, monkeypatch):
    """_analyze_structure must request preferred_bars for each timeframe."""
    from datetime import datetime
    from unittest.mock import MagicMock

    from src.orchestrator.graph import AgentState, TradingGraph

    csv_data = "time,open,high,low,close\n2024-01-01T00:00:00,1.0850,1.0900,1.0800,1.0875\n"

    broker_time = datetime(2026, 7, 21, 14, 0)
    mock_data_provider = MagicMock()
    mock_data_provider.get_candles.return_value = csv_data
    mock_data_provider.get_broker_time.return_value = broker_time

    mock_structure_analyzer = MagicMock()
    mock_structure_analyzer.analyze.return_value = {
        "timeframes": {
            "D1": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "D1"},
            "H4": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "H4"},
            "H1": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "H1"},
        },
        "confluence": {"status": "NO_VALID_CANDIDATE"},
    }

    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))

    graph = TradingGraph(
        data_provider=mock_data_provider,
        structure_analyzer=mock_structure_analyzer,
        calendar_provider=MagicMock(),
        synthesizer=MagicMock(),
        decider=MagicMock(),
        reviewer=MagicMock(),
    )

    state = AgentState(
        calendar_events=None,
        current_pending_orders=[],
        current_positions=[],
        decision=None,
        errors=[],
        fatal_error=None,
        final_output=None,
        market_context=None,
        review=None,
        review_attempts=0,
        review_feedback=None,
        structure_analysis=None,
        symbol="EURUSD",
        symbol_price=None,
    )

    result = graph._analyze_structure(state)

    # All 3 timeframes must be fetched with preferred bar counts
    assert mock_data_provider.get_candles.call_count == 3
    mock_data_provider.get_candles.assert_any_call("EURUSD", "D1", 500, broker_now=broker_time)
    mock_data_provider.get_candles.assert_any_call("EURUSD", "H4", 750, broker_now=broker_time)
    mock_data_provider.get_candles.assert_any_call("EURUSD", "H1", 1000, broker_now=broker_time)

    # All timeframes present in result
    for tf in ("D1", "H4", "H1"):
        assert tf in result["structure_analysis"]


def test_analyze_structure_uses_broker_time_not_utc(tmp_path, monkeypatch):
    """_analyze_structure must call get_broker_time() instead of datetime.now(UTC)."""
    from datetime import datetime
    from unittest.mock import MagicMock

    from src.orchestrator.graph import AgentState, TradingGraph

    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))

    mock_data_provider = MagicMock()
    mock_data_provider.get_candles.return_value = (
        "time,open,high,low,close\n2024-01-01T00:00:00,1.0850,1.0900,1.0800,1.0875\n"
    )
    broker_time = datetime(2026, 7, 21, 14, 0)
    mock_data_provider.get_broker_time.return_value = broker_time

    mock_structure_analyzer = MagicMock()
    mock_structure_analyzer.analyze.return_value = {
        "timeframes": {
            "D1": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "D1"},
            "H4": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "H4"},
            "H1": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "H1"},
        },
        "confluence": {"status": "NO_VALID_CANDIDATE"},
    }

    graph = TradingGraph(
        data_provider=mock_data_provider,
        structure_analyzer=mock_structure_analyzer,
        calendar_provider=MagicMock(),
        synthesizer=MagicMock(),
        decider=MagicMock(),
        reviewer=MagicMock(),
    )

    state = AgentState(
        calendar_events=None,
        current_pending_orders=[],
        current_positions=[],
        decision=None,
        errors=[],
        fatal_error=None,
        final_output=None,
        market_context=None,
        review=None,
        review_attempts=0,
        review_feedback=None,
        structure_analysis=None,
        symbol="XAUUSD",
        symbol_price=None,
    )

    graph._analyze_structure(state)

    # Must call get_broker_time() instead of datetime.now(UTC)
    assert mock_data_provider.get_broker_time.call_count >= 1


# =============================================================================
# RED Tests for cache-hit (all 3 TFs + MTF cached → 0 MCP calls)
# =============================================================================


def test_analyze_structure_full_cache_hit(tmp_path, monkeypatch):
    """When all 3 TFs + MTF are cached, must NOT call get_candles."""
    import json
    from datetime import datetime
    from unittest.mock import MagicMock

    from src.orchestrator.graph import AgentState, TradingGraph

    cache_dir = tmp_path / "analysis"
    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(cache_dir))

    # Broker time = after D1 close → cache files are valid
    broker_time = datetime(2026, 7, 21, 18, 0)

    # Create per-TF cache files
    tf_dir = cache_dir / "2026" / "07" / "21" / "XAUUSD"
    tf_dir.mkdir(parents=True)
    for tf, fname in [
        ("D1", "d1-analysis.json"),
        ("H4", "h4-20-analysis.json"),
        ("H1", "h1-19-analysis.json"),
    ]:
        (tf_dir / fname).write_text(
            json.dumps(
                {
                    "market_structure": {"primary_structure": "BULLISH"},
                    "timeframe": tf,
                }
            )
        )

    # Create MTF cache with real confluence
    mtf_result = {
        "timeframes": {},
        "confluence": {"status": "NO_VALID_CANDIDATE", "reason": "No candidate found"},
    }
    (tf_dir / "mtf-analysis.json").write_text(json.dumps(mtf_result))

    mock_data_provider = MagicMock()
    mock_data_provider.get_broker_time.return_value = broker_time

    graph = TradingGraph(
        data_provider=mock_data_provider,
        structure_analyzer=MagicMock(),
        calendar_provider=MagicMock(),
        synthesizer=MagicMock(),
        decider=MagicMock(),
        reviewer=MagicMock(),
    )

    state = AgentState(
        calendar_events=None,
        current_pending_orders=[],
        current_positions=[],
        decision=None,
        errors=[],
        fatal_error=None,
        final_output=None,
        market_context=None,
        review=None,
        review_attempts=0,
        review_feedback=None,
        structure_analysis=None,
        symbol="XAUUSD",
        symbol_price=None,
    )

    result = graph._analyze_structure(state)

    # No MCP calls
    assert mock_data_provider.get_candles.call_count == 0
    # Engine not called
    graph.structure_analyzer.analyze.assert_not_called()
    # Confluence from MTF cache
    assert result["structure_analysis"]["confluence"]["status"] == "NO_VALID_CANDIDATE"
    # Per-TF data from cache
    assert result["structure_analysis"]["D1"]["market_structure"]["primary_structure"] == "BULLISH"


def test_analyze_structure_cache_hit_confluence_correct(tmp_path, monkeypatch):
    """Cache-hit confluence must be the real engine confluence, not D1 analysis_context."""
    import json
    from datetime import datetime
    from unittest.mock import MagicMock

    from src.orchestrator.graph import AgentState, TradingGraph

    cache_dir = tmp_path / "analysis"
    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(cache_dir))

    broker_time = datetime(2026, 7, 21, 18, 0)
    tf_dir = cache_dir / "2026" / "07" / "21" / "XAUUSD"
    tf_dir.mkdir(parents=True)
    for tf, fname in [
        ("D1", "d1-analysis.json"),
        ("H4", "h4-20-analysis.json"),
        ("H1", "h1-19-analysis.json"),
    ]:
        (tf_dir / fname).write_text(
            json.dumps(
                {
                    "market_structure": {"primary_structure": "BULLISH"},
                    "timeframe": tf,
                    "analysis_context": {"technical_bias": "BULLISH", "structure_bias": "BULLISH"},
                }
            )
        )

    mtf_result = {
        "timeframes": {},
        "confluence": {
            "status": "NO_VALID_CANDIDATE",
            "reason": "Trend and structure agree, no entry",
            "entry_authorized": False,
        },
    }
    (tf_dir / "mtf-analysis.json").write_text(json.dumps(mtf_result))

    mock_data_provider = MagicMock()
    mock_data_provider.get_broker_time.return_value = broker_time

    graph = TradingGraph(
        data_provider=mock_data_provider,
        structure_analyzer=MagicMock(),
        calendar_provider=MagicMock(),
        synthesizer=MagicMock(),
        decider=MagicMock(),
        reviewer=MagicMock(),
    )

    state = AgentState(
        calendar_events=None,
        current_pending_orders=[],
        current_positions=[],
        decision=None,
        errors=[],
        fatal_error=None,
        final_output=None,
        market_context=None,
        review=None,
        review_attempts=0,
        review_feedback=None,
        structure_analysis=None,
        symbol="XAUUSD",
        symbol_price=None,
    )

    result = graph._analyze_structure(state)

    # Confluence must match MTF cache, NOT D1.analysis_context
    assert result["structure_analysis"]["confluence"]["status"] == "NO_VALID_CANDIDATE"
    assert "entry_authorized" in result["structure_analysis"]["confluence"]
    assert result["structure_analysis"]["confluence"]["entry_authorized"] is False
    # D1 analysis_context must NOT be confused with confluence
    assert result["structure_analysis"]["confluence"].get("technical_bias") is None


def test_analyze_structure_cache_hit_mtf_missing(tmp_path, monkeypatch):
    """When per-TF files exist but MTF is missing, must fall back to fresh fetch."""
    import json
    from datetime import datetime
    from unittest.mock import MagicMock

    from src.orchestrator.graph import AgentState, TradingGraph

    cache_dir = tmp_path / "analysis"
    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(cache_dir))

    broker_time = datetime(2026, 7, 21, 18, 0)

    # Create per-TF files but NO mtf-analysis.json
    tf_dir = cache_dir / "2026" / "07" / "21" / "XAUUSD"
    tf_dir.mkdir(parents=True)
    for tf, fname in [
        ("D1", "d1-analysis.json"),
        ("H4", "h4-20-analysis.json"),
        ("H1", "h1-19-analysis.json"),
    ]:
        (tf_dir / fname).write_text(
            json.dumps({"market_structure": {"primary_structure": "BULLISH"}})
        )

    mock_data_provider = MagicMock()
    mock_data_provider.get_candles.return_value = (
        "time,open,high,low,close\n2024-01-01T00:00:00,1.0850,1.0900,1.0800,1.0875\n"
    )
    mock_data_provider.get_broker_time.return_value = broker_time

    mock_structure_analyzer = MagicMock()
    mock_structure_analyzer.analyze.return_value = {
        "timeframes": {
            "D1": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "D1"},
            "H4": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "H4"},
            "H1": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "H1"},
        },
        "confluence": {"status": "NO_VALID_CANDIDATE"},
    }

    graph = TradingGraph(
        data_provider=mock_data_provider,
        structure_analyzer=mock_structure_analyzer,
        calendar_provider=MagicMock(),
        synthesizer=MagicMock(),
        decider=MagicMock(),
        reviewer=MagicMock(),
    )

    state = AgentState(
        calendar_events=None,
        current_pending_orders=[],
        current_positions=[],
        decision=None,
        errors=[],
        fatal_error=None,
        final_output=None,
        market_context=None,
        review=None,
        review_attempts=0,
        review_feedback=None,
        structure_analysis=None,
        symbol="XAUUSD",
        symbol_price=None,
    )

    graph._analyze_structure(state)

    # Must fall back to fresh fetch
    assert mock_data_provider.get_candles.call_count == 3
    # MTF cache file should now be created from fresh fetch
    assert (tf_dir / "mtf-analysis.json").exists()


def test_analyze_structure_partial_cache_miss(tmp_path, monkeypatch):
    """When only 2 of 3 TFs are cached, must fetch all fresh."""
    import json
    from datetime import datetime
    from unittest.mock import MagicMock

    from src.orchestrator.graph import AgentState, TradingGraph

    cache_dir = tmp_path / "analysis"
    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(cache_dir))

    broker_time = datetime(2026, 7, 21, 18, 0)

    # Create only D1 and H4 cache files — no H1
    tf_dir = cache_dir / "2026" / "07" / "21" / "XAUUSD"
    tf_dir.mkdir(parents=True)
    for fname in ["d1-analysis.json", "h4-20-analysis.json"]:
        (tf_dir / fname).write_text(
            json.dumps({"market_structure": {"primary_structure": "BULLISH"}})
        )

    mock_data_provider = MagicMock()
    mock_data_provider.get_candles.return_value = (
        "time,open,high,low,close\n2024-01-01T00:00:00,1.0850,1.0900,1.0800,1.0875\n"
    )
    mock_data_provider.get_broker_time.return_value = broker_time

    mock_structure_analyzer = MagicMock()
    mock_structure_analyzer.analyze.return_value = {
        "timeframes": {
            "D1": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "D1"},
            "H4": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "H4"},
            "H1": {
                "market_structure": {"primary_structure": "BULLISH"},
                "timeframe": "H1",
                "fresh": True,
            },
        },
        "confluence": {"status": "NO_VALID_CANDIDATE"},
    }

    graph = TradingGraph(
        data_provider=mock_data_provider,
        structure_analyzer=mock_structure_analyzer,
        calendar_provider=MagicMock(),
        synthesizer=MagicMock(),
        decider=MagicMock(),
        reviewer=MagicMock(),
    )

    state = AgentState(
        calendar_events=None,
        current_pending_orders=[],
        current_positions=[],
        decision=None,
        errors=[],
        fatal_error=None,
        final_output=None,
        market_context=None,
        review=None,
        review_attempts=0,
        review_feedback=None,
        structure_analysis=None,
        symbol="XAUUSD",
        symbol_price=None,
    )

    result = graph._analyze_structure(state)

    # All 3 fresh
    assert mock_data_provider.get_candles.call_count == 3
    # Engine called
    mock_structure_analyzer.analyze.assert_called_once()
    # H1 has fresh data
    assert result["structure_analysis"]["H1"].get("fresh") is True


def test_analyze_structure_corrupt_cache_fallback(tmp_path, monkeypatch):
    """Corrupt per-TF cache file must not crash — fall back to fresh fetch."""
    import json
    from datetime import datetime
    from unittest.mock import MagicMock

    from src.orchestrator.graph import AgentState, TradingGraph

    cache_dir = tmp_path / "analysis"
    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(cache_dir))

    broker_time = datetime(2026, 7, 21, 18, 0)

    tf_dir = cache_dir / "2026" / "07" / "21" / "XAUUSD"
    tf_dir.mkdir(parents=True)
    # D1 cache file is corrupt
    (tf_dir / "d1-analysis.json").write_text("not valid json")
    (tf_dir / "h4-20-analysis.json").write_text(json.dumps({"ok": True}))
    (tf_dir / "h1-19-analysis.json").write_text(json.dumps({"ok": True}))

    mock_data_provider = MagicMock()
    mock_data_provider.get_candles.return_value = (
        "time,open,high,low,close\n2024-01-01T00:00:00,1.0850,1.0900,1.0800,1.0875\n"
    )
    mock_data_provider.get_broker_time.return_value = broker_time

    mock_structure_analyzer = MagicMock()
    mock_structure_analyzer.analyze.return_value = {
        "timeframes": {
            "D1": {"market_structure": {"primary_structure": "BULLISH"}},
            "H4": {"market_structure": {"primary_structure": "BULLISH"}},
            "H1": {"market_structure": {"primary_structure": "BULLISH"}},
        },
        "confluence": {"status": "NO_VALID_CANDIDATE"},
    }

    graph = TradingGraph(
        data_provider=mock_data_provider,
        structure_analyzer=mock_structure_analyzer,
        calendar_provider=MagicMock(),
        synthesizer=MagicMock(),
        decider=MagicMock(),
        reviewer=MagicMock(),
    )

    state = AgentState(
        calendar_events=None,
        current_pending_orders=[],
        current_positions=[],
        decision=None,
        errors=[],
        fatal_error=None,
        final_output=None,
        market_context=None,
        review=None,
        review_attempts=0,
        review_feedback=None,
        structure_analysis=None,
        symbol="XAUUSD",
        symbol_price=None,
    )

    result = graph._analyze_structure(state)

    # Falls back to fresh fetch without raising
    assert mock_data_provider.get_candles.call_count == 3
    assert "fatal_error" not in result


def test_analyze_structure_fresh_saves_mtf_cache(tmp_path, monkeypatch):
    """Fresh-fetch path must also save the MTF cache file."""
    from datetime import datetime
    from unittest.mock import MagicMock

    from src.orchestrator.graph import AgentState, TradingGraph

    cache_dir = tmp_path / "analysis"
    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(cache_dir))
    monkeypatch.setenv("TRADING_D1_CLOSE_TIME", "00:00")
    from src.analysis.candle_cache import reload_settings

    reload_settings()

    broker_time = datetime(2026, 7, 21, 14, 0)

    mock_data_provider = MagicMock()
    mock_data_provider.get_candles.return_value = (
        "time,open,high,low,close\n2024-01-01T00:00:00,1.0850,1.0900,1.0800,1.0875\n"
    )
    mock_data_provider.get_broker_time.return_value = broker_time

    mock_structure_analyzer = MagicMock()
    mock_structure_analyzer.analyze.return_value = {
        "timeframes": {
            "D1": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "D1"},
            "H4": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "H4"},
            "H1": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "H1"},
        },
        "confluence": {"status": "NO_VALID_CANDIDATE"},
    }

    graph = TradingGraph(
        data_provider=mock_data_provider,
        structure_analyzer=mock_structure_analyzer,
        calendar_provider=MagicMock(),
        synthesizer=MagicMock(),
        decider=MagicMock(),
        reviewer=MagicMock(),
    )

    state = AgentState(
        calendar_events=None,
        current_pending_orders=[],
        current_positions=[],
        decision=None,
        errors=[],
        fatal_error=None,
        final_output=None,
        market_context=None,
        review=None,
        review_attempts=0,
        review_feedback=None,
        structure_analysis=None,
        symbol="XAUUSD",
        symbol_price=None,
    )

    graph._analyze_structure(state)

    # MTF cache file must exist
    # D1 period: 14:00 >= 00:00 → period starts today (2026-07-21)
    mtf_cache = cache_dir / "2026" / "07" / "21" / "XAUUSD" / "mtf-analysis.json"
    assert mtf_cache.exists(), f"MTF cache not found at {mtf_cache}"


def test_analyze_structure_saves_h1_cache(tmp_path, monkeypatch):
    """H1 analysis must now be saved to cache like D1/H4."""
    from datetime import datetime
    from unittest.mock import MagicMock

    from src.orchestrator.graph import AgentState, TradingGraph

    cache_dir = tmp_path / "analysis"
    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(cache_dir))
    monkeypatch.setenv("TRADING_D1_CLOSE_TIME", "00:00")
    from src.analysis.candle_cache import reload_settings

    reload_settings()

    mock_data_provider = MagicMock()
    mock_data_provider.get_candles.return_value = (
        "time,open,high,low,close\n2024-01-01T00:00:00,1.0850,1.0900,1.0800,1.0875\n"
    )
    broker_time = datetime(2026, 7, 21, 14, 30)
    mock_data_provider.get_broker_time.return_value = broker_time

    mock_structure_analyzer = MagicMock()
    mock_structure_analyzer.analyze.return_value = {
        "timeframes": {
            "D1": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "D1"},
            "H4": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "H4"},
            "H1": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "H1"},
        },
        "confluence": {"status": "NO_VALID_CANDIDATE"},
    }

    graph = TradingGraph(
        data_provider=mock_data_provider,
        structure_analyzer=mock_structure_analyzer,
        calendar_provider=MagicMock(),
        synthesizer=MagicMock(),
        decider=MagicMock(),
        reviewer=MagicMock(),
    )

    state = AgentState(
        calendar_events=None,
        current_pending_orders=[],
        current_positions=[],
        decision=None,
        errors=[],
        fatal_error=None,
        final_output=None,
        market_context=None,
        review=None,
        review_attempts=0,
        review_feedback=None,
        structure_analysis=None,
        symbol="XAUUSD",
        symbol_price=None,
    )

    graph._analyze_structure(state)

    # H1 cache file must exist
    h1_cache = cache_dir / "2026" / "07" / "21" / "XAUUSD" / "h1-15-analysis.json"
    assert h1_cache.exists(), f"H1 cache file not found at {h1_cache}"
    # D1 cache file must exist (regression)
    # With d1_close_time=00:00, period at 14:30 starts today (2026-07-21).
    d1_cache = cache_dir / "2026" / "07" / "21" / "XAUUSD" / "d1-analysis.json"
    assert d1_cache.exists()


def test_analyze_structure_handles_broker_time_failure(tmp_path, monkeypatch):
    """If get_broker_time() fails, _analyze_structure should set fatal_error."""
    from unittest.mock import MagicMock

    from src.orchestrator.graph import AgentState, TradingGraph

    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))

    mock_data_provider = MagicMock()
    mock_data_provider.get_broker_time.side_effect = ConnectionError("Server unreachable")

    graph = TradingGraph(
        data_provider=mock_data_provider,
        structure_analyzer=MagicMock(),
        calendar_provider=MagicMock(),
        synthesizer=MagicMock(),
        decider=MagicMock(),
        reviewer=MagicMock(),
    )

    state = AgentState(
        calendar_events=None,
        current_pending_orders=[],
        current_positions=[],
        decision=None,
        errors=[],
        fatal_error=None,
        final_output=None,
        market_context=None,
        review=None,
        review_attempts=0,
        review_feedback=None,
        structure_analysis=None,
        symbol="XAUUSD",
        symbol_price=None,
    )

    result = graph._analyze_structure(state)
    assert "fatal_error" in result


def test_analyze_structure_passes_broker_time_to_get_candles(tmp_path, monkeypatch):
    """get_candles must be called with broker_time param."""
    from datetime import datetime
    from unittest.mock import MagicMock

    from src.orchestrator.graph import AgentState, TradingGraph

    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))

    mock_data_provider = MagicMock()
    mock_data_provider.get_candles.return_value = (
        "time,open,high,low,close\n2024-01-01T00:00:00,1.0850,1.0900,1.0800,1.0875\n"
    )
    broker_time = datetime(2026, 7, 21, 14, 0)
    mock_data_provider.get_broker_time.return_value = broker_time

    mock_structure_analyzer = MagicMock()
    mock_structure_analyzer.analyze.return_value = {
        "timeframes": {
            "D1": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "D1"}
        },
        "confluence": {"status": "NO_VALID_CANDIDATE"},
    }

    graph = TradingGraph(
        data_provider=mock_data_provider,
        structure_analyzer=mock_structure_analyzer,
        calendar_provider=MagicMock(),
        synthesizer=MagicMock(),
        decider=MagicMock(),
        reviewer=MagicMock(),
    )

    state = AgentState(
        calendar_events=None,
        current_pending_orders=[],
        current_positions=[],
        decision=None,
        errors=[],
        fatal_error=None,
        final_output=None,
        market_context=None,
        review=None,
        review_attempts=0,
        review_feedback=None,
        structure_analysis=None,
        symbol="XAUUSD",
        symbol_price=None,
    )

    graph._analyze_structure(state)

    # Verify get_candles was called with broker_now=broker_time for EVERY call
    assert mock_data_provider.get_candles.call_count == 3
    for call_args in mock_data_provider.get_candles.call_args_list:
        kwargs = call_args.kwargs
        assert "broker_now" in kwargs, f"broker_now missing in call {call_args}"
        assert kwargs["broker_now"] == broker_time


def test_analyze_structure_passes_broker_time_to_snapshot_builder(tmp_path, monkeypatch):
    """snapshot_builder.build must be called with broker_time."""
    from datetime import datetime
    from unittest.mock import MagicMock

    from src.orchestrator.graph import AgentState, TradingGraph

    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))

    broker_time = datetime(2026, 7, 21, 14, 0)

    mock_data_provider = MagicMock()
    mock_data_provider.get_candles.return_value = (
        "time,open,high,low,close\n2024-01-01T00:00:00,1.0850,1.0900,1.0800,1.0875\n"
    )
    mock_data_provider.get_broker_time.return_value = broker_time

    mock_structure_analyzer = MagicMock()
    mock_structure_analyzer.analyze.return_value = {
        "timeframes": {
            "D1": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "D1"}
        },
        "confluence": {"status": "NO_VALID_CANDIDATE"},
    }

    graph = TradingGraph(
        data_provider=mock_data_provider,
        structure_analyzer=mock_structure_analyzer,
        calendar_provider=MagicMock(),
        synthesizer=MagicMock(),
        decider=MagicMock(),
        reviewer=MagicMock(),
    )

    # Replace snapshot_builder with a spy
    mock_builder = MagicMock()
    mock_builder.build.return_value = {"bars": [], "market": {"symbol": "XAUUSD"}}
    graph._snapshot_builder = mock_builder

    state = AgentState(
        calendar_events=None,
        current_pending_orders=[],
        current_positions=[],
        decision=None,
        errors=[],
        fatal_error=None,
        final_output=None,
        market_context=None,
        review=None,
        review_attempts=0,
        review_feedback=None,
        structure_analysis=None,
        symbol="XAUUSD",
        symbol_price=None,
    )

    graph._analyze_structure(state)

    # Verify build was called with broker_now=broker_time for EVERY call
    assert mock_builder.build.call_count == 3
    for call_args in mock_builder.build.call_args_list:
        kwargs = call_args.kwargs
        assert "broker_now" in kwargs, (
            f"broker_now missing in snapshot_builder.build call {call_args}"
        )
        assert kwargs["broker_now"] == broker_time


# ---------------------------------------------------------------------------
# TASK-6: canonical current-price selection wiring in _synthesize_context
# ---------------------------------------------------------------------------


def _canonical_structure_analysis() -> dict:
    """Build a structure_analysis fixture whose H1 timeframe has the
    most-recent closed-candle timestamp and a close price of 1.12.

    The shape mirrors what _analyze_structure stores in state: per-timeframe
    engine output dicts (D1/H4/H1) each carrying ``source_audit`` and
    ``technical_context``. ``market_structure`` is present so
    ``_summarize_structure_analysis`` keeps them in the compact view.
    """
    return {
        "D1": {
            "market_structure": {"primary_structure": "BULLISH"},
            "source_audit": {"latest_closed_candle_time": "2024-01-03T00:00:00"},
            "technical_context": {"close": 1.10},
        },
        "H4": {
            "market_structure": {"primary_structure": "BULLISH"},
            "source_audit": {"latest_closed_candle_time": "2024-01-03T12:00:00"},
            "technical_context": {"close": 1.11},
        },
        "H1": {
            "market_structure": {"primary_structure": "BULLISH"},
            "source_audit": {"latest_closed_candle_time": "2024-01-03T20:00:00"},
            "technical_context": {"close": 1.12},
        },
    }


class TestSynthesizeContextCanonicalPrice:
    def test_synthesize_context_computes_and_forwards_current_price(
        self, trading_graph, mock_synthesizer, tmp_path, monkeypatch
    ):
        """_synthesize_context must compute the canonical current price from
        the per-timeframe structure analysis and forward it (plus its
        timestamp) to SynthesizerAgent.synthesize.

        Uses an isolated temp cache dir to avoid interference from real
        cached entries or other tests.
        """
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
        state = AgentState(
            calendar_events=[],
            current_pending_orders=[],
            current_positions=[],
            decision=None,
            errors=[],
            fatal_error=None,
            final_output=None,
            market_context=None,
            review=None,
            review_attempts=0,
            review_feedback=None,
            structure_analysis=_canonical_structure_analysis(),
            symbol="EURUSD",
            symbol_price=None,
        )

        result = trading_graph._synthesize_context(state)

        mock_synthesizer.synthesize.assert_called_once()
        _, kwargs = mock_synthesizer.synthesize.call_args
        assert kwargs.get("current_price") == 1.12, (
            f"expected canonical current_price=1.12 forwarded, got {kwargs.get('current_price')!r}"
        )
        assert kwargs.get("current_price_time") == "2024-01-03T20:00:00", (
            "expected canonical current_price_time='2024-01-03T20:00:00' forwarded, "
            f"got {kwargs.get('current_price_time')!r}"
        )
        # The orchestrator must also stamp the computed price onto the
        # returned MarketContextSummary.
        assert result["market_context"].current_price == 1.12

    def test_synthesize_context_sets_price_on_summary_when_llm_omits(
        self, trading_graph, mock_synthesizer, tmp_path, monkeypatch
    ):
        """Even when the LLM-returned summary has current_price=None, the
        orchestrator must set it post-hoc from the canonical computation.
        """
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
        # The shared mock_synthesizer fixture already returns a summary with
        # current_price=None (default). Make that explicit for clarity.
        returned = mock_synthesizer.synthesize.return_value
        assert returned.current_price is None

        state = AgentState(
            calendar_events=[],
            current_pending_orders=[],
            current_positions=[],
            decision=None,
            errors=[],
            fatal_error=None,
            final_output=None,
            market_context=None,
            review=None,
            review_attempts=0,
            review_feedback=None,
            structure_analysis=_canonical_structure_analysis(),
            symbol="EURUSD",
            symbol_price=None,
        )

        result = trading_graph._synthesize_context(state)

        # Post-hoc stamping: the summary returned to the graph must carry
        # the canonical price even though the LLM omitted it.
        assert result["market_context"].current_price == 1.12
        assert result["market_context"].current_price_time == "2024-01-03T20:00:00"


# =============================================================================
# TASK-1: AgentState rename account_info→symbol_price + remove market_data
# =============================================================================


def test_agentstate_rejects_account_info():
    """AgentState must NOT have 'account_info'; it must have 'symbol_price' instead.

    This validates the rename was applied to the type definition.
    See task: Rename account_info → symbol_price in AgentState TypedDict.
    """
    assert "account_info" not in AgentState.__annotations__, (
        "AgentState still has 'account_info' — it must be renamed to 'symbol_price'"
    )
    assert "symbol_price" in AgentState.__annotations__, (
        "AgentState missing 'symbol_price' — it must be renamed from 'account_info'"
    )


def test_agentstate_rejects_market_data():
    """AgentState must NOT have 'market_data' — the dead field was removed.

    This validates the removal was applied to the type definition.
    See task: Remove dead market_data field from AgentState.
    """
    assert "market_data" not in AgentState.__annotations__, (
        "AgentState still has 'market_data' — it must be removed"
    )


# =============================================================================
# TASK-3: Review Attempts Off-By-One — Retry cycle tests
# =============================================================================


def test_full_retry_cycle_gives_max_plus_one_decisions(
    mock_data_provider,
    mock_structure_analyzer,
    mock_calendar_provider,
    mock_synthesizer,
    mock_decider,
    mock_reviewer,
    tmp_path,
    monkeypatch,
):
    """With max_review_attempts=2, decider.decide must be called exactly 3 times
    (1 original + 2 retries) when the reviewer always rejects.

    RED: today _review_to_decide uses ``<`` so max_review_attempts=2 yields only
    2 decisions (1 original + 1 retry).
    """
    from datetime import datetime

    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))

    broker_time = datetime(2026, 7, 21, 14, 0)
    mock_data_provider.get_broker_time.return_value = broker_time

    # Reviewer always rejects → triggers retry loop
    mock_reviewer.review.return_value = ReviewVerdict(
        approved=False,
        reasoning="Risk too high",
        concerns=["Position size exceeds limits"],
        suggested_improvements="Reduce position size by 50%",
    )

    # Structure analyzer returns valid multi-timeframe result
    mock_structure_analyzer.analyze.return_value = {
        "timeframes": {
            "D1": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "D1"},
            "H4": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "H4"},
            "H1": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "H1"},
        },
        "confluence": {"status": "NO_VALID_CANDIDATE"},
    }

    graph = TradingGraph(
        data_provider=mock_data_provider,
        structure_analyzer=mock_structure_analyzer,
        calendar_provider=mock_calendar_provider,
        synthesizer=mock_synthesizer,
        decider=mock_decider,
        reviewer=mock_reviewer,
        max_review_attempts=2,
    )

    graph.run("EURUSD")

    assert mock_decider.decide.call_count == 3, (
        f"Expected 3 decide calls with max_review_attempts=2 (1 original + 2 retries), "
        f"got {mock_decider.decide.call_count}"
    )


def test_feedback_sent_on_all_retries(
    mock_data_provider,
    mock_structure_analyzer,
    mock_calendar_provider,
    mock_synthesizer,
    mock_decider,
    mock_reviewer,
    tmp_path,
    monkeypatch,
):
    """With max_review_attempts=2, feedback must be forwarded to decider.decide
    on every retry call (calls 2 and 3), not just the first retry.

    RED: today _review_to_decide short-circuits after 2 total decisions,
    so this test never reaches call index 2.
    """
    from datetime import datetime

    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))

    broker_time = datetime(2026, 7, 21, 14, 0)
    mock_data_provider.get_broker_time.return_value = broker_time

    mock_reviewer.review.return_value = ReviewVerdict(
        approved=False,
        reasoning="Risk too high",
        concerns=["Position size exceeds limits"],
        suggested_improvements="Reduce position size by 50%",
    )

    mock_structure_analyzer.analyze.return_value = {
        "timeframes": {
            "D1": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "D1"},
            "H4": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "H4"},
            "H1": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "H1"},
        },
        "confluence": {"status": "NO_VALID_CANDIDATE"},
    }

    graph = TradingGraph(
        data_provider=mock_data_provider,
        structure_analyzer=mock_structure_analyzer,
        calendar_provider=mock_calendar_provider,
        synthesizer=mock_synthesizer,
        decider=mock_decider,
        reviewer=mock_reviewer,
        max_review_attempts=2,
    )

    graph.run("EURUSD")

    assert mock_decider.decide.call_count == 3, (
        f"Need 3 decide calls to check feedback on retries, got {mock_decider.decide.call_count}"
    )

    call_2_kwargs = mock_decider.decide.call_args_list[1].kwargs
    assert call_2_kwargs.get("feedback") is not None, (
        f"Expected feedback on retry 1 (call 2), got {call_2_kwargs.get('feedback')!r}"
    )

    call_3_kwargs = mock_decider.decide.call_args_list[2].kwargs
    assert call_3_kwargs.get("feedback") is not None, (
        f"Expected feedback on retry 2 (call 3), got {call_3_kwargs.get('feedback')!r}"
    )


def test_first_decide_has_no_feedback(
    mock_data_provider,
    mock_structure_analyzer,
    mock_calendar_provider,
    mock_synthesizer,
    mock_decider,
    mock_reviewer,
    tmp_path,
    monkeypatch,
):
    """The first call to decider.decide must have feedback=None.

    This may already be GREEN because _decide checks ``attempts > 1``
    before forwarding feedback.
    """
    from datetime import datetime

    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))

    broker_time = datetime(2026, 7, 21, 14, 0)
    mock_data_provider.get_broker_time.return_value = broker_time

    mock_structure_analyzer.analyze.return_value = {
        "timeframes": {
            "D1": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "D1"},
            "H4": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "H4"},
            "H1": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "H1"},
        },
        "confluence": {"status": "NO_VALID_CANDIDATE"},
    }

    graph = TradingGraph(
        data_provider=mock_data_provider,
        structure_analyzer=mock_structure_analyzer,
        calendar_provider=mock_calendar_provider,
        synthesizer=mock_synthesizer,
        decider=mock_decider,
        reviewer=mock_reviewer,
    )

    graph.run("EURUSD")

    assert mock_decider.decide.call_count >= 1
    call_1_kwargs = mock_decider.decide.call_args_list[0].kwargs
    assert call_1_kwargs.get("feedback") is None, (
        f"Expected feedback=None on first decide, got {call_1_kwargs.get('feedback')!r}"
    )


# =============================================================================
# TASK-5: CostTracker wiring tests
# =============================================================================


def _make_tracking_side_effect(ct_instance: CostTracker) -> Callable[..., object]:
    """Create a side effect that records an LLM call on the shared CostTracker.

    This simulates what real agents do — calling ``cost_tracker.record_call``
    with synthetic token counts when their main method is invoked.
    """

    def side_effect(*args: object, **kwargs: object) -> MagicMock:
        from src.decision.usage import LLMUsage

        ct_instance.record_call(
            "gpt-4o",
            LLMUsage(
                input_tokens=100, uncached_input_tokens=100, output_tokens=50, total_tokens=150
            ),
        )
        return MagicMock()

    return side_effect


class TestCostTrackerWiring:
    """Tests for CostTracker wiring in TradingGraph.run().

    These tests verify that:
    1. A shared CostTracker instance is wired to all 3 agents.
    2. The graph run logs the total LLM cost accrued via the tracker.

    Both tests use mocked agents that record calls on a shared CostTracker.
    The mock agents' methods are replaced to call cost_tracker.record_call
    with synthetic token counts, simulating what real agents do.
    """

    def test_graph_run_logs_total_cost(
        self,
        mock_data_provider,
        mock_structure_analyzer,
        mock_calendar_provider,
        monkeypatch,
        tmp_path,
        caplog,
    ):
        """Run TradingGraph with mocked agents that have a shared CostTracker,
        assert log contains 'Total LLM cost for EURUSD'.
        """
        from datetime import datetime

        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))

        broker_time = datetime(2026, 7, 21, 14, 0)
        mock_data_provider.get_broker_time.return_value = broker_time
        mock_data_provider.get_candles.return_value = (
            "time,open,high,low,close\n2024-01-01T00:00:00,1.0850,1.0900,1.0800,1.0875\n"
        )

        mock_structure_analyzer.analyze.return_value = {
            "timeframes": {
                "D1": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "D1"},
                "H4": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "H4"},
                "H1": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "H1"},
            },
            "confluence": {"status": "NO_VALID_CANDIDATE"},
        }

        # Build agents that share a single CostTracker
        ct = CostTracker()
        track = _make_tracking_side_effect(ct)

        mock_synthesizer = MagicMock()
        mock_synthesizer.synthesize.side_effect = track
        mock_synthesizer.cost_tracker = ct

        mock_decider = MagicMock()
        mock_decider.decide.side_effect = track
        mock_decider.cost_tracker = ct

        mock_reviewer = MagicMock()
        mock_reviewer.review.side_effect = track
        mock_reviewer.cost_tracker = ct

        graph = TradingGraph(
            data_provider=mock_data_provider,
            structure_analyzer=mock_structure_analyzer,
            calendar_provider=mock_calendar_provider,
            synthesizer=mock_synthesizer,
            decider=mock_decider,
            reviewer=mock_reviewer,
        )

        with caplog.at_level(logging.INFO):
            graph.run("EURUSD")

        # Look for the total-cost log line in the captured log records
        total_cost_logged = any(
            "Total LLM cost for EURUSD" in record.getMessage() for record in caplog.records
        )
        assert total_cost_logged, (
            "Expected log message 'Total LLM cost for EURUSD' not found. "
            "The log should be emitted in TradingGraph.run() after graph.invoke()."
        )

    def test_main_wires_cost_tracker(
        self,
        mock_data_provider,
        mock_structure_analyzer,
        mock_calendar_provider,
        monkeypatch,
        tmp_path,
    ):
        """Verify that a CostTracker instance can be shared across all 3 agents
        and records calls consistently.
        """
        from datetime import datetime

        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))

        broker_time = datetime(2026, 7, 21, 14, 0)
        mock_data_provider.get_broker_time.return_value = broker_time
        mock_data_provider.get_candles.return_value = (
            "time,open,high,low,close\n2024-01-01T00:00:00,1.0850,1.0900,1.0800,1.0875\n"
        )

        mock_structure_analyzer.analyze.return_value = {
            "timeframes": {
                "D1": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "D1"},
                "H4": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "H4"},
                "H1": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "H1"},
            },
            "confluence": {"status": "NO_VALID_CANDIDATE"},
        }

        # Create a shared CostTracker with pricing and wire it to all 3 mock agents
        ct = CostTracker(
            pricing={
                "gpt-4o": {
                    "input_per_million": 2.50,
                    "cached_input_per_million": 1.25,
                    "output_per_million": 10.00,
                },
            }
        )
        track = _make_tracking_side_effect(ct)

        mock_synthesizer = MagicMock()
        mock_synthesizer.synthesize.side_effect = track
        mock_synthesizer.cost_tracker = ct

        mock_decider = MagicMock()
        mock_decider.decide.side_effect = track
        mock_decider.cost_tracker = ct

        mock_reviewer = MagicMock()
        mock_reviewer.review.side_effect = track
        mock_reviewer.cost_tracker = ct

        # Run the graph
        graph = TradingGraph(
            data_provider=mock_data_provider,
            structure_analyzer=mock_structure_analyzer,
            calendar_provider=mock_calendar_provider,
            synthesizer=mock_synthesizer,
            decider=mock_decider,
            reviewer=mock_reviewer,
        )

        graph.run("EURUSD")

        # Verify agents had the shared CostTracker reference
        assert mock_synthesizer.cost_tracker is ct, "Synthesizer lost shared CostTracker reference"
        assert mock_decider.cost_tracker is ct, "Decider lost shared CostTracker reference"
        assert mock_reviewer.cost_tracker is ct, "Reviewer lost shared CostTracker reference"

        # The CostTracker should have recorded calls from all 3 agents.
        # With the reviewer approving, the retry loop runs once (no retries),
        # so each of the 3 agents is called exactly once.
        assert ct.call_count >= 3, (
            f"Expected at least 3 recorded calls on the shared CostTracker "
            f"(one per agent), got {ct.call_count}"
        )
        assert ct.total_cost > 0.0, "Expected positive total_cost on the shared CostTracker"
        # Verify all three agents share the exact same tracker object
        assert (
            mock_synthesizer.cost_tracker is mock_decider.cost_tracker is mock_reviewer.cost_tracker
        ), "All three agents must share the exact same CostTracker instance"


# =============================================================================
# TASK-10: _summarize_timeframe should log warning on non-dict nested fields
# =============================================================================


def test_summarize_timeframe_logs_warning_on_non_dict(caplog):
    """_summarize_timeframe should log a warning when nested fields
    (events, levels, liquidity) are not dicts."""
    import logging

    from src.orchestrator.graph import _summarize_timeframe

    caplog.set_level(logging.WARNING)

    tf_data = {
        "events": "not a dict",  # Should be dict
        "levels": 42,  # Should be dict
        "liquidity": ["list", "not", "dict"],  # Should be dict
        "market_structure": {"primary": "BULLISH"},  # Valid
    }

    result = _summarize_timeframe(tf_data)

    # Non-dict fields should be skipped
    assert "events" not in result
    assert "levels" not in result
    assert "liquidity" not in result
    # Valid fields should be included
    assert result["market_structure"] == {"primary": "BULLISH"}
    # Warning should be logged
    assert "non-dict" in caplog.text.lower() or "unexpected" in caplog.text.lower()


# =============================================================================
# TASK-5: Eliminate redundant get_broker_time() call in _synthesize_context
# =============================================================================


def test_get_broker_time_called_once_per_run(
    mock_data_provider,
    mock_structure_analyzer,
    mock_calendar_provider,
    mock_synthesizer,
    mock_decider,
    mock_reviewer,
    tmp_path,
    monkeypatch,
):
    """get_broker_time() should be called once in _analyze_structure and
    reused in _synthesize_context, not called again."""
    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))

    broker_time = datetime(2026, 7, 21, 14, 0)
    mock_data_provider.get_broker_time.return_value = broker_time
    mock_data_provider.get_candles.return_value = (
        "time,open,high,low,close\n2024-01-01T00:00:00,1.0850,1.0900,1.0800,1.0875\n"
    )
    mock_structure_analyzer.analyze.return_value = {
        "timeframes": {
            "D1": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "D1"},
            "H4": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "H4"},
            "H1": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "H1"},
        },
        "confluence": {"status": "NO_VALID_CANDIDATE"},
    }

    graph = TradingGraph(
        data_provider=mock_data_provider,
        structure_analyzer=mock_structure_analyzer,
        calendar_provider=mock_calendar_provider,
        synthesizer=mock_synthesizer,
        decider=mock_decider,
        reviewer=mock_reviewer,
    )

    state = AgentState(
        calendar_events=[],
        current_pending_orders=[],
        current_positions=[],
        decision=None,
        errors=[],
        fatal_error=None,
        final_output=None,
        market_context=None,
        review=None,
        review_attempts=0,
        review_feedback=None,
        structure_analysis=_canonical_structure_analysis(),
        symbol="EURUSD",
        symbol_price=None,
    )

    # Run _analyze_structure first (calls get_broker_time internally)
    result = graph._analyze_structure(state)
    state.update(result)  # Simulate LangGraph state merging

    # Reset mock call count to track _synthesize_context calls independently
    mock_data_provider.get_broker_time.reset_mock()

    # Run _synthesize_context — should reuse broker_now from state
    graph._synthesize_context(state)

    # get_broker_time should NOT be called again in _synthesize_context
    assert mock_data_provider.get_broker_time.call_count == 0, (
        "get_broker_time() should not be called in _synthesize_context "
        "when broker_now is already in state"
    )


# =============================================================================
# TASK-2: Graph node re-raise guards for CostLimitExceeded
# =============================================================================


class TestCostLimitReRaise:
    """Tests for ``except CostLimitExceeded: raise`` in every graph node.

    Without the re-raise guards, ``CostLimitExceeded`` is caught by the
    generic ``except Exception`` handlers and returned as
    ``{"fatal_error": msg}`` instead of propagating. These tests verify
    that each node lets ``CostLimitExceeded`` propagate *out* of
    ``graph.run()``, while a normal ``Exception`` still produces a
    ``fatal_error`` result dict (unchanged behaviour).

    Because TASK-1 is already implemented (``CostLimitExceeded`` exists),
    but TASK-2 production code has *not* been written yet, every
    ``pytest.raises(CostLimitExceeded)`` test here is expected to FAIL
    RED — the exception will be swallowed by ``except Exception`` and
    the test will get a result dict instead.
    """

    # ------------------------------------------------------------------
    # Helper: a valid multi-timeframe result for mock_structure_analyzer
    # so that _analyze_structure can complete and later nodes can be
    # exercised.
    # ------------------------------------------------------------------
    _VALID_MTF_RESULT: dict = {
        "timeframes": {
            "D1": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "D1"},
            "H4": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "H4"},
            "H1": {"market_structure": {"primary_structure": "BULLISH"}, "timeframe": "H1"},
        },
        "confluence": {"status": "NO_VALID_CANDIDATE"},
    }

    _CSV_DATA: str = "time,open,high,low,close\n2024-01-01,1.0850,1.0900,1.0800,1.0875\n"

    # ------------------------------------------------------------------
    # Tests 1-3: LLM-agent nodes (synthesize, decide, review)
    # ------------------------------------------------------------------

    def test_synthesize_context_re_raises_cost_limit_exceeded(
        self,
        mock_data_provider,
        mock_structure_analyzer,
        mock_calendar_provider,
        mock_decider,
        mock_reviewer,
        monkeypatch,
        tmp_path,
    ):
        """When ``SynthesizerAgent.synthesize`` raises ``CostLimitExceeded``,
        it must propagate through ``_synthesize_context`` out of
        ``graph.run()`` — not be caught and returned as fatal_error."""
        from datetime import datetime

        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))

        broker_time = datetime(2026, 7, 25, 14, 0)
        mock_data_provider.get_broker_time.return_value = broker_time
        mock_data_provider.get_candles.return_value = self._CSV_DATA
        mock_structure_analyzer.analyze.return_value = self._VALID_MTF_RESULT

        mock_synthesizer = MagicMock()
        mock_synthesizer.synthesize.side_effect = CostLimitExceeded(limit=0.05, total_cost=0.06)

        graph = TradingGraph(
            data_provider=mock_data_provider,
            structure_analyzer=mock_structure_analyzer,
            calendar_provider=mock_calendar_provider,
            synthesizer=mock_synthesizer,
            decider=mock_decider,
            reviewer=mock_reviewer,
        )

        with pytest.raises(CostLimitExceeded):
            graph.run("EURUSD")

    def test_decide_re_raises_cost_limit_exceeded(
        self,
        mock_data_provider,
        mock_structure_analyzer,
        mock_calendar_provider,
        mock_reviewer,
        monkeypatch,
        tmp_path,
    ):
        """When ``DeciderAgent.decide`` raises ``CostLimitExceeded``,
        it must propagate through ``_decide`` out of ``graph.run()``."""
        from datetime import datetime

        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))

        broker_time = datetime(2026, 7, 25, 14, 0)
        mock_data_provider.get_broker_time.return_value = broker_time
        mock_data_provider.get_candles.return_value = self._CSV_DATA
        mock_structure_analyzer.analyze.return_value = self._VALID_MTF_RESULT

        # Synthesizer must succeed so _decide is reached
        mock_synthesizer = MagicMock()
        mock_synthesizer.synthesize.return_value = MarketContextSummary(
            symbol="EURUSD",
            bias=BiasLevel.BULLISH,
            confidence=75.0,
            reasoning="Bullish structure",
        )

        mock_decider = MagicMock()
        mock_decider.decide.side_effect = CostLimitExceeded(limit=0.05, total_cost=0.06)

        graph = TradingGraph(
            data_provider=mock_data_provider,
            structure_analyzer=mock_structure_analyzer,
            calendar_provider=mock_calendar_provider,
            synthesizer=mock_synthesizer,
            decider=mock_decider,
            reviewer=mock_reviewer,
        )

        with pytest.raises(CostLimitExceeded):
            graph.run("EURUSD")

    def test_review_re_raises_cost_limit_exceeded(
        self,
        mock_data_provider,
        mock_structure_analyzer,
        mock_calendar_provider,
        monkeypatch,
        tmp_path,
    ):
        """When ``ReviewerAgent.review`` raises ``CostLimitExceeded``,
        it must propagate through ``_review`` out of ``graph.run()``."""
        from datetime import datetime

        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))

        broker_time = datetime(2026, 7, 25, 14, 0)
        mock_data_provider.get_broker_time.return_value = broker_time
        mock_data_provider.get_candles.return_value = self._CSV_DATA
        mock_structure_analyzer.analyze.return_value = self._VALID_MTF_RESULT

        mock_synthesizer = MagicMock()
        mock_synthesizer.synthesize.return_value = MarketContextSummary(
            symbol="EURUSD",
            bias=BiasLevel.BULLISH,
            confidence=75.0,
            reasoning="Bullish structure",
        )

        mock_decider = MagicMock()
        mock_decider.decide.return_value = DecisionOutput(
            symbol="EURUSD",
            action=DecisionAction.BUY_SETUP,
            entry_price=1.0875,
            stop_loss=1.0825,
            take_profit=1.0975,
            reasoning="Good setup",
            risk_reward_ratio=2.0,
        )

        mock_reviewer = MagicMock()
        mock_reviewer.review.side_effect = CostLimitExceeded(limit=0.05, total_cost=0.06)

        graph = TradingGraph(
            data_provider=mock_data_provider,
            structure_analyzer=mock_structure_analyzer,
            calendar_provider=mock_calendar_provider,
            synthesizer=mock_synthesizer,
            decider=mock_decider,
            reviewer=mock_reviewer,
        )

        with pytest.raises(CostLimitExceeded):
            graph.run("EURUSD")

    # ------------------------------------------------------------------
    # Tests 4-6: Data-provider nodes (fetch_data, analyze_structure,
    #            evaluate_calendar)
    # ------------------------------------------------------------------

    def test_fetch_data_re_raises_cost_limit_exceeded(
        self,
        mock_data_provider,
        mock_structure_analyzer,
        mock_calendar_provider,
        mock_synthesizer,
        mock_decider,
        mock_reviewer,
        trading_graph,
    ):
        """When ``DataSource.get_positions`` raises ``CostLimitExceeded``,
        it must propagate through ``_fetch_data`` out of ``graph.run()``.

        We override ``get_positions`` on the fixture's mock to raise;
        the ``trading_graph`` fixture uses the same mock, so it picks up
        the change automatically.
        """
        mock_data_provider.get_positions.side_effect = CostLimitExceeded(
            limit=0.05, total_cost=0.06
        )

        with pytest.raises(CostLimitExceeded):
            trading_graph.run("EURUSD")

    def test_analyze_structure_re_raises_cost_limit_exceeded(
        self,
        mock_data_provider,
        mock_structure_analyzer,
        mock_calendar_provider,
        mock_synthesizer,
        mock_decider,
        mock_reviewer,
        monkeypatch,
        tmp_path,
    ):
        """When ``DataSource.get_candles`` raises ``CostLimitExceeded``
        inside ``_analyze_structure``'s main try/except, it must
        propagate — not be caught and returned as fatal_error.

        ``get_broker_time()`` is set to succeed so we get past the
        outer try/except in ``_analyze_structure`` and exercise the
        main try/except where ``get_candles`` is called.
        """
        from datetime import datetime

        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))

        broker_time = datetime(2026, 7, 25, 14, 0)
        mock_data_provider.get_broker_time.return_value = broker_time
        # Override get_candles to raise instead of returning CSV
        mock_data_provider.get_candles.side_effect = CostLimitExceeded(limit=0.05, total_cost=0.06)

        graph = TradingGraph(
            data_provider=mock_data_provider,
            structure_analyzer=mock_structure_analyzer,
            calendar_provider=mock_calendar_provider,
            synthesizer=mock_synthesizer,
            decider=mock_decider,
            reviewer=mock_reviewer,
        )

        with pytest.raises(CostLimitExceeded):
            graph.run("EURUSD")

    def test_evaluate_calendar_re_raises_cost_limit_exceeded(
        self,
        mock_data_provider,
        mock_structure_analyzer,
        mock_calendar_provider,
        mock_synthesizer,
        mock_decider,
        mock_reviewer,
        monkeypatch,
        tmp_path,
    ):
        """When ``CalendarProvider.fetch_events`` raises
        ``CostLimitExceeded``, it must propagate through
        ``_evaluate_calendar`` out of ``graph.run()``."""
        from datetime import datetime

        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))

        broker_time = datetime(2026, 7, 25, 14, 0)
        mock_data_provider.get_broker_time.return_value = broker_time
        mock_data_provider.get_candles.return_value = self._CSV_DATA
        mock_structure_analyzer.analyze.return_value = self._VALID_MTF_RESULT

        mock_calendar_provider.fetch_events.side_effect = CostLimitExceeded(
            limit=0.05, total_cost=0.06
        )

        graph = TradingGraph(
            data_provider=mock_data_provider,
            structure_analyzer=mock_structure_analyzer,
            calendar_provider=mock_calendar_provider,
            synthesizer=mock_synthesizer,
            decider=mock_decider,
            reviewer=mock_reviewer,
        )

        with pytest.raises(CostLimitExceeded):
            graph.run("EURUSD")

    # ------------------------------------------------------------------
    # Test 7: Normal Exception handling is unchanged
    # ------------------------------------------------------------------

    def test_normal_exception_still_handled(
        self,
        mock_data_provider,
        mock_structure_analyzer,
        mock_calendar_provider,
        mock_synthesizer,
        mock_decider,
        mock_reviewer,
        trading_graph,
    ):
        """A normal ``Exception`` (not ``CostLimitExceeded``) must still
        be caught and returned as ``{"fatal_error": ...}`` by every node.
        We trigger it in ``_fetch_data`` and verify the run returns a
        dict with a fatal_error message — it does NOT re-raise.
        """
        mock_data_provider.get_positions.side_effect = Exception("Something bad")

        result = trading_graph.run("EURUSD")

        assert isinstance(result, dict), (
            f"Expected dict result from graph.run(), got {type(result).__name__}"
        )
        assert "fatal_error" in result, (
            f"Expected fatal_error in result dict, got keys: {list(result.keys())}"
        )
        assert "Something bad" in result["fatal_error"]
