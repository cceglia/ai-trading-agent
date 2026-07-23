from unittest.mock import MagicMock

import pytest

from src.decision.models import (
    BiasLevel,
    DecisionAction,
    DecisionOutput,
    MarketContextSummary,
    ReviewVerdict,
)
from src.orchestrator.graph import MAX_REVIEW_ATTEMPTS, AgentState, TradingGraph


@pytest.fixture
def mock_data_provider():
    provider = MagicMock()
    provider.get_positions.return_value = []
    provider.get_pending_orders.return_value = []
    provider.get_symbol_price.return_value = {"bid": 1.0875, "ask": 1.0877}
    provider.get_candles.return_value = (
        "time,open,high,low,close\n2024-01-01,1.0850,1.0900,1.0800,1.0875\n"
    )
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


class TestTradingGraphNodes:
    def test_fetch_data_calls_provider(self, trading_graph, mock_data_provider):
        state = AgentState(
            symbol="EURUSD",
            market_data={},
            current_positions=[],
            current_pending_orders=[],
            account_info=None,
            structure_analysis=None,
            calendar_events=None,
            market_context=None,
            decision=None,
            review=None,
            review_feedback=None,
            review_attempts=0,
            errors=[],
            fatal_error=None,
            final_output=None,
        )
        result = trading_graph._fetch_data(state)
        mock_data_provider.get_positions.assert_called_with("EURUSD")
        mock_data_provider.get_pending_orders.assert_called_with("EURUSD")
        mock_data_provider.get_symbol_price.assert_called_with("EURUSD")
        assert "current_positions" in result

    def test_fetch_data_handles_error(self, trading_graph, mock_data_provider):
        mock_data_provider.get_positions.side_effect = Exception("Connection lost")
        state = AgentState(
            symbol="EURUSD",
            market_data={},
            current_positions=[],
            current_pending_orders=[],
            account_info=None,
            structure_analysis=None,
            calendar_events=None,
            market_context=None,
            decision=None,
            review=None,
            review_feedback=None,
            review_attempts=0,
            errors=[],
            fatal_error=None,
            final_output=None,
        )
        result = trading_graph._fetch_data(state)
        assert result["fatal_error"] == "Data fetch failed: Connection lost"

    def test_evaluate_calendar_fetches_events(self, trading_graph, mock_calendar_provider):
        state = AgentState(
            symbol="EURUSD",
            market_data={},
            current_positions=[],
            current_pending_orders=[],
            account_info=None,
            structure_analysis=None,
            calendar_events=None,
            market_context=None,
            decision=None,
            review=None,
            review_feedback=None,
            review_attempts=0,
            errors=[],
            fatal_error=None,
            final_output=None,
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
            "review_attempts": MAX_REVIEW_ATTEMPTS,
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
            "review_attempts": MAX_REVIEW_ATTEMPTS,
            "fatal_error": None,
        }
        assert trading_graph._review_to_decide(state) == "end"


class TestMaxReviewAttempts:
    def test_constant_value(self):
        assert MAX_REVIEW_ATTEMPTS == 2


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
        symbol="XAUUSD",
        market_data={},
        current_positions=[],
        current_pending_orders=[],
        account_info=None,
        structure_analysis=None,
        calendar_events=None,
        market_context=None,
        decision=None,
        review=None,
        review_feedback=None,
        review_attempts=0,
        errors=[],
        fatal_error=None,
        final_output=None,
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


def test_analyze_structure_h1_always_fetched_fresh(tmp_path, monkeypatch):
    """H1 must always be fetched (no caching for H1)."""
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
        symbol="XAUUSD",
        market_data={},
        current_positions=[],
        current_pending_orders=[],
        account_info=None,
        structure_analysis=None,
        calendar_events=None,
        market_context=None,
        decision=None,
        review=None,
        review_feedback=None,
        review_attempts=0,
        errors=[],
        fatal_error=None,
        final_output=None,
    )
    result = graph._analyze_structure(state)

    # H1 is always fetched fresh
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
        symbol="EURUSD",
        market_data={},
        current_positions=[],
        current_pending_orders=[],
        account_info=None,
        structure_analysis=None,
        calendar_events=None,
        market_context=None,
        decision=None,
        review=None,
        review_feedback=None,
        review_attempts=0,
        errors=[],
        fatal_error=None,
        final_output=None,
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
        symbol="EURUSD",
        market_data={},
        current_positions=[],
        current_pending_orders=[],
        account_info=None,
        structure_analysis=None,
        calendar_events=None,
        market_context=None,
        decision=None,
        review=None,
        review_feedback=None,
        review_attempts=0,
        errors=[],
        fatal_error=None,
        final_output=None,
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
        symbol="XAUUSD",
        market_data={},
        current_positions=[],
        current_pending_orders=[],
        account_info=None,
        structure_analysis=None,
        calendar_events=None,
        market_context=None,
        decision=None,
        review=None,
        review_feedback=None,
        review_attempts=0,
        errors=[],
        fatal_error=None,
        final_output=None,
    )

    graph._analyze_structure(state)

    # Must call get_broker_time() instead of datetime.now(UTC)
    assert mock_data_provider.get_broker_time.call_count >= 1


def test_analyze_structure_saves_h1_cache(tmp_path, monkeypatch):
    """H1 analysis must now be saved to cache like D1/H4."""
    from datetime import datetime
    from unittest.mock import MagicMock

    from src.orchestrator.graph import AgentState, TradingGraph

    cache_dir = tmp_path / "analysis"
    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(cache_dir))

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
        symbol="XAUUSD",
        market_data={},
        current_positions=[],
        current_pending_orders=[],
        account_info=None,
        structure_analysis=None,
        calendar_events=None,
        market_context=None,
        decision=None,
        review=None,
        review_feedback=None,
        review_attempts=0,
        errors=[],
        fatal_error=None,
        final_output=None,
    )

    graph._analyze_structure(state)

    # H1 cache file must exist
    h1_cache = cache_dir / "2026" / "07" / "21" / "XAUUSD" / "h1-15-analysis.json"
    assert h1_cache.exists(), f"H1 cache file not found at {h1_cache}"
    # D1 cache file must exist (regression)
    # D1 period starts on the previous day when broker time (14:30) is before
    # the D1 close (17:00), so cache date is 2026-07-20.
    d1_cache = cache_dir / "2026" / "07" / "20" / "XAUUSD" / "d1-analysis.json"
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
        symbol="XAUUSD",
        market_data={},
        current_positions=[],
        current_pending_orders=[],
        account_info=None,
        structure_analysis=None,
        calendar_events=None,
        market_context=None,
        decision=None,
        review=None,
        review_feedback=None,
        review_attempts=0,
        errors=[],
        fatal_error=None,
        final_output=None,
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
        symbol="XAUUSD",
        market_data={},
        current_positions=[],
        current_pending_orders=[],
        account_info=None,
        structure_analysis=None,
        calendar_events=None,
        market_context=None,
        decision=None,
        review=None,
        review_feedback=None,
        review_attempts=0,
        errors=[],
        fatal_error=None,
        final_output=None,
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
        symbol="XAUUSD",
        market_data={},
        current_positions=[],
        current_pending_orders=[],
        account_info=None,
        structure_analysis=None,
        calendar_events=None,
        market_context=None,
        decision=None,
        review=None,
        review_feedback=None,
        review_attempts=0,
        errors=[],
        fatal_error=None,
        final_output=None,
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
