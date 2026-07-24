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
        self, trading_graph, mock_synthesizer
    ):
        """_synthesize_context must compute the canonical current price from
        the per-timeframe structure analysis and forward it (plus its
        timestamp) to SynthesizerAgent.synthesize.

        RED: today _synthesize_context does not pass current_price /
        current_price_time, so the call kwargs assertion fails.
        """
        state = AgentState(
            symbol="EURUSD",
            market_data={},
            current_positions=[],
            current_pending_orders=[],
            account_info=None,
            structure_analysis=_canonical_structure_analysis(),
            calendar_events=[],
            market_context=None,
            decision=None,
            review=None,
            review_feedback=None,
            review_attempts=0,
            errors=[],
            fatal_error=None,
            final_output=None,
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
        self, trading_graph, mock_synthesizer
    ):
        """Even when the LLM-returned summary has current_price=None, the
        orchestrator must set it post-hoc from the canonical computation.

        RED: today _synthesize_context returns the LLM summary unchanged
        (current_price stays None), so the assertion fails.
        """
        # The shared mock_synthesizer fixture already returns a summary with
        # current_price=None (default). Make that explicit for clarity.
        returned = mock_synthesizer.synthesize.return_value
        assert returned.current_price is None

        state = AgentState(
            symbol="EURUSD",
            market_data={},
            current_positions=[],
            current_pending_orders=[],
            account_info=None,
            structure_analysis=_canonical_structure_analysis(),
            calendar_events=[],
            market_context=None,
            decision=None,
            review=None,
            review_feedback=None,
            review_attempts=0,
            errors=[],
            fatal_error=None,
            final_output=None,
        )

        result = trading_graph._synthesize_context(state)

        # Post-hoc stamping: the summary returned to the graph must carry
        # the canonical price even though the LLM omitted it.
        assert result["market_context"].current_price == 1.12
        assert result["market_context"].current_price_time == "2024-01-03T20:00:00"
