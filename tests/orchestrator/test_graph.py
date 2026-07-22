import pytest
from unittest.mock import MagicMock

from src.decision.models import (
    BiasLevel,
    DecisionAction,
    DecisionOutput,
    MarketContextSummary,
    ReviewVerdict,
)
from src.orchestrator.graph import AgentState, TradingGraph, MAX_REVIEW_ATTEMPTS


@pytest.fixture
def mock_data_provider():
    provider = MagicMock()
    provider.get_positions.return_value = []
    provider.get_pending_orders.return_value = []
    provider.get_symbol_price.return_value = {"bid": 1.0875, "ask": 1.0877}
    provider.get_candles.return_value = "time,open,high,low,close\n2024-01-01,1.0850,1.0900,1.0800,1.0875\n"
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
            final_output=None,
        )
        result = trading_graph._fetch_data(state)
        assert len(result["errors"]) == 1
        assert "Data fetch failed" in result["errors"][0]

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
        }
        assert trading_graph._review_to_decide(state) == "end"

    def test_review_to_retry_when_not_approved(self, trading_graph):
        state = {
            "review": ReviewVerdict(approved=False, reasoning="Bad"),
            "review_attempts": 1,
        }
        assert trading_graph._review_to_decide(state) == "retry"

    def test_review_to_end_when_max_attempts(self, trading_graph):
        state = {
            "review": ReviewVerdict(approved=False, reasoning="Bad"),
            "review_attempts": MAX_REVIEW_ATTEMPTS,
        }
        assert trading_graph._review_to_decide(state) == "end"

    def test_review_retries_when_no_review_and_attempts_remaining(self, trading_graph):
        state = {
            "review": None,
            "review_attempts": 0,
        }
        assert trading_graph._review_to_decide(state) == "retry"

    def test_review_ends_when_no_review_and_max_attempts(self, trading_graph):
        state = {
            "review": None,
            "review_attempts": MAX_REVIEW_ATTEMPTS,
        }
        assert trading_graph._review_to_decide(state) == "end"


class TestMaxReviewAttempts:
    def test_constant_value(self):
        assert MAX_REVIEW_ATTEMPTS == 2


def test_analyze_structure_uses_cache(tmp_path, monkeypatch):
    """D1/H4 should use cache when available, H1 always fresh."""
    from datetime import datetime, timezone
    import json
    from unittest.mock import MagicMock, patch
    from src.orchestrator.graph import TradingGraph, AgentState

    # Setup cache
    cache_dir = tmp_path / "analysis"
    cache_dir.mkdir()

    # Use monkeypatch.setenv for Pydantic BaseSettings
    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(cache_dir))

    # Mock dependencies
    mock_data_provider = MagicMock()
    mock_structure_analyzer = MagicMock()
    mock_calendar_provider = MagicMock()
    mock_synthesizer = MagicMock()
    mock_decider = MagicMock()
    mock_reviewer = MagicMock()

    graph = TradingGraph(
        data_provider=mock_data_provider,
        structure_analyzer=mock_structure_analyzer,
        calendar_provider=mock_calendar_provider,
        synthesizer=mock_synthesizer,
        decider=mock_decider,
        reviewer=mock_reviewer,
    )

    cached_d1 = {"cached_d1": True}
    cached_h4 = {"cached_h4": True}

    with patch("src.orchestrator.graph.should_run_analysis") as mock_should_run, \
         patch("src.orchestrator.graph.load_cached_analysis") as mock_load_cache:
        # D1/H4 say cache is valid (False = don't run), H1 always fresh (True = run)
        mock_should_run.side_effect = lambda tf, sym, now: tf == "H1"
        # Return cached data for D1/H4
        mock_load_cache.side_effect = lambda tf, sym, now: cached_d1 if tf == "D1" else cached_h4

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
            final_output=None,
        )
        result = graph._analyze_structure(state)

        from unittest.mock import call as mock_call
        # Should NOT fetch D1/H4 candles (cached)
        assert mock_call("XAUUSD", "D1", 100) not in mock_data_provider.get_candles.call_args_list
        assert mock_call("XAUUSD", "H4", 100) not in mock_data_provider.get_candles.call_args_list
        # Should fetch H1 (always fresh)
        mock_data_provider.get_candles.assert_called_with("XAUUSD", "H1", 100)
        # Verify cached results flow through to output
        assert result["structure_analysis"]["D1"] == cached_d1
        assert result["structure_analysis"]["H4"] == cached_h4


def test_h1_always_fresh_even_when_d1_h4_cached(tmp_path, monkeypatch):
    """H1 must always fetch fresh data even when D1/H4 are cached."""
    from datetime import datetime, timezone
    from unittest.mock import MagicMock, patch
    from src.orchestrator.graph import TradingGraph, AgentState

    cache_dir = tmp_path / "analysis"
    cache_dir.mkdir()

    # Use monkeypatch.setenv for Pydantic BaseSettings
    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(cache_dir))

    # Mock dependencies
    mock_data_provider = MagicMock()
    mock_structure_analyzer = MagicMock()
    mock_calendar_provider = MagicMock()
    mock_synthesizer = MagicMock()
    mock_decider = MagicMock()
    mock_reviewer = MagicMock()

    # Mock H1 fresh data - use valid CSV and proper key format
    csv_data = "time,open,high,low,close\n2024-01-01T00:00:00,1.0850,1.0900,1.0800,1.0875\n"
    mock_data_provider.get_candles.return_value = csv_data
    mock_structure_analyzer.analyze.return_value = {"H1": {"fresh_h1": True}}

    graph = TradingGraph(
        data_provider=mock_data_provider,
        structure_analyzer=mock_structure_analyzer,
        calendar_provider=mock_calendar_provider,
        synthesizer=mock_synthesizer,
        decider=mock_decider,
        reviewer=mock_reviewer,
    )

    cached_d1 = {"cached_d1": True}
    cached_h4 = {"cached_h4": True}

    with patch("src.orchestrator.graph.should_run_analysis") as mock_should_run, \
         patch("src.orchestrator.graph.load_cached_analysis") as mock_load_cache:
        # D1/H4 say cache is valid (False = don't run), H1 always fresh (True = run)
        mock_should_run.side_effect = lambda tf, sym, now: tf == "H1"
        # Return cached data for D1/H4
        mock_load_cache.side_effect = lambda tf, sym, now: cached_d1 if tf == "D1" else cached_h4

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
            final_output=None,
        )
        result = graph._analyze_structure(state)

        # H1 must always be fetched fresh
        mock_data_provider.get_candles.assert_called_with("XAUUSD", "H1", 100)
        # D1/H4 should use cached data
        assert result["structure_analysis"]["D1"] == cached_d1
        assert result["structure_analysis"]["H4"] == cached_h4
        # H1 should have fresh analysis result
        assert result["structure_analysis"]["H1"] == {"fresh_h1": True}


def test_analyze_structure_converts_csv_to_snapshots(tmp_path, monkeypatch):
    """_analyze_structure must use SnapshotBuilder to convert CSV to dicts."""
    from datetime import datetime, timezone
    from unittest.mock import MagicMock, patch
    from src.orchestrator.graph import TradingGraph, AgentState

    csv_data = (
        "time,open,high,low,close,tick_volume,spread,real_volume\n"
        "2024-01-01T00:00:00,1.0850,1.0900,1.0800,1.0875,1000,1,500\n"
        "2024-01-02T00:00:00,1.0875,1.0950,1.0850,1.0920,1200,1,600\n"
    )

    mock_data_provider = MagicMock()
    mock_data_provider.get_candles.return_value = csv_data

    mock_structure_analyzer = MagicMock()
    mock_structure_analyzer.analyze.return_value = {"D1": {"analyzed": True}}

    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))

    with patch("src.analysis.candle_cache.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2026, 7, 21, 14, 0, tzinfo=timezone.utc)
        mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        graph = TradingGraph(
            data_provider=mock_data_provider,
            structure_analyzer=mock_structure_analyzer,
            calendar_provider=MagicMock(),
            synthesizer=MagicMock(),
            decider=MagicMock(),
            reviewer=MagicMock(),
        )

        state = AgentState(
            symbol="EURUSD", market_data={}, current_positions=[],
            current_pending_orders=[], account_info=None,
            structure_analysis=None, calendar_events=None,
            market_context=None, decision=None, review=None,
            review_feedback=None, review_attempts=0, errors=[],
            final_output=None,
        )

        result = graph._analyze_structure(state)

        # Verify structure_analyzer.analyze received dicts, not strings
        analyze_call = mock_structure_analyzer.analyze.call_args
        snapshots_arg = analyze_call[0][0]

        # H1 should be a dict (not a CSV string)
        assert isinstance(snapshots_arg.get("H1"), dict), \
            f"Expected dict, got {type(snapshots_arg.get('H1'))}"

        # Verify the dict has the correct schema
        h1_snapshot = snapshots_arg["H1"]
        assert "bars" in h1_snapshot
        assert "market" in h1_snapshot
        assert h1_snapshot["market"]["symbol"] == "EURUSD"


def test_analyze_structure_uses_should_run_analysis(tmp_path, monkeypatch):
    """should_run_analysis must gate whether cache is used."""
    from datetime import datetime, timezone
    from unittest.mock import MagicMock, patch
    from src.orchestrator.graph import TradingGraph, AgentState

    csv_data = "time,open,high,low,close\n2024-01-01T00:00:00,1.0850,1.0900,1.0800,1.0875\n"

    mock_data_provider = MagicMock()
    mock_data_provider.get_candles.return_value = csv_data

    mock_structure_analyzer = MagicMock()
    mock_structure_analyzer.analyze.return_value = {"H1": {"fresh": True}}

    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))

    with patch("src.analysis.candle_cache.datetime") as mock_dt, \
         patch("src.orchestrator.graph.should_run_analysis") as mock_should_run:
        mock_dt.now.return_value = datetime(2026, 7, 21, 18, 0, tzinfo=timezone.utc)
        mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        # D1: should_run_analysis says True (stale) → must fetch fresh
        # H4: should_run_analysis says False (valid cache) → must use cache
        mock_should_run.side_effect = lambda tf, sym, now: tf == "D1"

        # Create cache for H4
        cache_dir = tmp_path / "analysis" / "2026" / "07" / "21" / "EURUSD"
        cache_dir.mkdir(parents=True)
        (cache_dir / "h4-analysis.json").write_text('{"cached_h4": true}')

        graph = TradingGraph(
            data_provider=mock_data_provider,
            structure_analyzer=mock_structure_analyzer,
            calendar_provider=MagicMock(),
            synthesizer=MagicMock(),
            decider=MagicMock(),
            reviewer=MagicMock(),
        )

        state = AgentState(
            symbol="EURUSD", market_data={}, current_positions=[],
            current_pending_orders=[], account_info=None,
            structure_analysis=None, calendar_events=None,
            market_context=None, decision=None, review=None,
            review_feedback=None, review_attempts=0, errors=[],
            final_output=None,
        )

        result = graph._analyze_structure(state)

        # should_run_analysis must have been called for D1 and H4
        assert mock_should_run.call_count >= 2

        # D1 should have fresh data (should_run returned True)
        assert "D1" in result["structure_analysis"]

        # H4 should use cache (should_run returned False)
        assert result["structure_analysis"]["H4"] == {"cached_h4": True}
