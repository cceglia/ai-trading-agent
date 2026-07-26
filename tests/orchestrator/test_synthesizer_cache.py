"""RED-first tests for orchestrator-level synthesizer cache integration.

Tests verify that ``_synthesize_context`` in ``src/orchestrator/graph.py``
consults the synthesizer cache (``should_run_synthesis`` /
``load_cached_synthesis`` / ``save_synthesis``). The method does NOT yet
consult the cache, so all cache-hit and cache-fill assertions fail RED.

Categories (12 tests):
  Cache hit paths   (4) — cached summary returned, synth skipped, decide/review run
  Cache miss paths  (3) — synth called, LLM result returned, cache filled
  Corrupt/disabled  (3) — fall through to LLM when cache is broken or off
  Fatal error paths (2) — short-circuit before cache check, no cache write
"""

from __future__ import annotations

import json
import pathlib
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from src.decision.cost_tracker import CostTracker
from src.decision.models import (
    BiasLevel,
    DecisionAction,
    DecisionOutput,
    MarketContextSummary,
    ReviewVerdict,
)
from src.orchestrator.graph import AgentState, TradingGraph


# ---------------------------------------------------------------------------
# Shared fixtures (mirror those in test_graph.py since they are not in conftest)
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Autouse fixture — reset synthesizer_cache sentinel before each test
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def reset_synthesizer_cache_settings():
    """Reset the ``_settings`` sentinel in ``synthesizer_cache`` before each test.

    Tests that monkeypatch env vars (``TRADING_SYNTHESIZER_CACHE_ENABLED``,
    ``TRADING_ANALYSIS_CACHE_DIR``) need the sentinel cleared so that
    ``_get_settings()`` picks up the changes.
    """
    import src.decision.synthesizer_cache

    src.decision.synthesizer_cache._settings = None
    yield
    src.decision.synthesizer_cache._settings = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _make_cached_summary(**overrides: object) -> MarketContextSummary:
    """Build a ``MarketContextSummary`` that looks like it came from the cache."""
    defaults: dict[str, object] = {
        "symbol": "EURUSD",
        "bias": "bullish",
        "confidence": 80.0,
        "reasoning": "Cached analysis \u2014 no LLM call",
        "key_levels": ["1.0850", "1.0900"],
        "structural_events": ["BOS at 1.0850"],
        "calendar_context": "No high-impact events",
        "current_price": 1.0875,
        "current_price_time": "2024-01-03T20:00:00",
    }
    defaults.update(overrides)
    return MarketContextSummary(**defaults)  # type: ignore[arg-type]


def _canonical_structure_analysis() -> dict:
    """Minimal ``structure_analysis`` with H1 as most-recently-closed timeframe."""
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


def _write_cache_file(
    tmp_path: pathlib.Path,
    symbol: str,
    dt: datetime,
    content: str,
) -> pathlib.Path:
    """Write arbitrary content to the synthesizer cache path.

    This lets us simulate corrupt files, invalid JSON, and bad pydantic
    data without going through ``save_synthesis``.
    """
    cache_dir = (
        tmp_path / "analysis" / f"{dt.year:04d}" / f"{dt.month:02d}" / f"{dt.day:02d}" / symbol
    )
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / "synthesizer.json"
    cache_file.write_text(content)
    return cache_file


# ===================================================================
# Cache hit paths (4 tests)
# ===================================================================
class TestCacheHit:
    """When the cache has a valid ``MarketContextSummary`` for (symbol, day).

    The orchestrator must return the cached summary and skip the LLM call.
    Downstream nodes (decide, review) must still execute.
    """

    def test_cache_hit_returns_cached_summary(
        self,
        trading_graph,
        mock_synthesizer,
        tmp_path,
        monkeypatch,
    ):
        """Cache hit \u2192 ``_synthesize_context`` returns the cached summary (not LLM).

        RED: today ``_synthesize_context`` always calls ``synthesizer.synthesize``
        and returns its output, ignoring the cache entirely.
        """
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
        broker_now = datetime(2026, 7, 25, 14, 0)

        # Pre-populate cache with a known summary
        from src.decision.synthesizer_cache import save_synthesis

        cached = _make_cached_summary()
        save_synthesis("EURUSD", broker_now, cached)

        # Make the mock synthesizer return a DIFFERENT summary so we can
        # tell which one the method picks.
        mock_synthesizer.synthesize.return_value = _make_cached_summary(
            reasoning="LLM-generated (should NOT be returned when cache hits)",
        )

        # Ensure broker_time is available for the future cache integration
        trading_graph.data_provider.get_broker_time.return_value = broker_now

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

        # The cached summary has reasoning "Cached analysis — no LLM call"
        assert result["market_context"].reasoning == cached.reasoning, (
            f"Expected cached reasoning {cached.reasoning!r}, "
            f"got {result['market_context'].reasoning!r}"
        )

    def test_cache_hit_synthesizer_not_called(
        self,
        trading_graph,
        mock_synthesizer,
        tmp_path,
        monkeypatch,
    ):
        """Cache hit \u2192 ``synthesizer.synthesize`` must NOT be called.

        RED: today ``_synthesize_context`` ignores the cache and always calls
        ``synthesize``, so ``assert_not_called()`` fails.
        """
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
        broker_now = datetime(2026, 7, 25, 14, 0)

        from src.decision.synthesizer_cache import save_synthesis

        save_synthesis("EURUSD", broker_now, _make_cached_summary())
        trading_graph.data_provider.get_broker_time.return_value = broker_now

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

        trading_graph._synthesize_context(state)

        # This assertion FAILS (RED) because _synthesize_context calls
        # synthesize even when the cache has valid data.
        mock_synthesizer.synthesize.assert_not_called()

    def test_cache_hit_decide_still_called(
        self,
        mock_data_provider,
        mock_structure_analyzer,
        mock_calendar_provider,
        mock_synthesizer,
        mock_decider,
        mock_reviewer,
        tmp_path,
        monkeypatch,
    ):
        """Cache hit \u2192 the decide node must still run.

        The cache should only skip the synthesizer LLM call, not block
        downstream nodes.  This test runs the full graph with a pre-populated
        cache and asserts ``decider.decide`` was called.
        """
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
        broker_now = datetime(2026, 7, 25, 14, 0)
        mock_data_provider.get_broker_time.return_value = broker_now
        mock_data_provider.get_candles.return_value = (
            "time,open,high,low,close\n2024-01-01T00:00:00,1.0850,1.0900,1.0800,1.0875\n"
        )
        mock_structure_analyzer.analyze.return_value = {
            "timeframes": {
                "D1": {
                    "market_structure": {"primary_structure": "BULLISH"},
                    "timeframe": "D1",
                },
                "H4": {
                    "market_structure": {"primary_structure": "BULLISH"},
                    "timeframe": "H4",
                },
                "H1": {
                    "market_structure": {"primary_structure": "BULLISH"},
                    "timeframe": "H1",
                },
            },
            "confluence": {"status": "NO_VALID_CANDIDATE"},
        }

        # Pre-populate synthesizer cache
        from src.decision.synthesizer_cache import save_synthesis

        save_synthesis("EURUSD", broker_now, _make_cached_summary())

        graph = TradingGraph(
            data_provider=mock_data_provider,
            structure_analyzer=mock_structure_analyzer,
            calendar_provider=mock_calendar_provider,
            synthesizer=mock_synthesizer,
            decider=mock_decider,
            reviewer=mock_reviewer,
        )

        graph.run("EURUSD")

        # Decide must still be called \u2014 cache is a synthesizer-only optimisation
        assert mock_decider.decide.call_count >= 1, (
            "decider.decide was not called \u2014 the cache may have blocked "
            "the downstream pipeline"
        )

    def test_cache_hit_review_still_called(
        self,
        mock_data_provider,
        mock_structure_analyzer,
        mock_calendar_provider,
        mock_synthesizer,
        mock_decider,
        mock_reviewer,
        tmp_path,
        monkeypatch,
    ):
        """Cache hit \u2192 the review node must still run."""
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
        broker_now = datetime(2026, 7, 25, 14, 0)
        mock_data_provider.get_broker_time.return_value = broker_now
        mock_data_provider.get_candles.return_value = (
            "time,open,high,low,close\n2024-01-01T00:00:00,1.0850,1.0900,1.0800,1.0875\n"
        )
        mock_structure_analyzer.analyze.return_value = {
            "timeframes": {
                "D1": {
                    "market_structure": {"primary_structure": "BULLISH"},
                    "timeframe": "D1",
                },
                "H4": {
                    "market_structure": {"primary_structure": "BULLISH"},
                    "timeframe": "H4",
                },
                "H1": {
                    "market_structure": {"primary_structure": "BULLISH"},
                    "timeframe": "H1",
                },
            },
            "confluence": {"status": "NO_VALID_CANDIDATE"},
        }

        from src.decision.synthesizer_cache import save_synthesis

        save_synthesis("EURUSD", broker_now, _make_cached_summary())

        graph = TradingGraph(
            data_provider=mock_data_provider,
            structure_analyzer=mock_structure_analyzer,
            calendar_provider=mock_calendar_provider,
            synthesizer=mock_synthesizer,
            decider=mock_decider,
            reviewer=mock_reviewer,
        )

        graph.run("EURUSD")

        assert mock_reviewer.review.call_count >= 1, (
            "reviewer.review was not called \u2014 the cache may have blocked "
            "the downstream pipeline"
        )


# ===================================================================
# Cache miss path (3 tests)
# ===================================================================
class TestCacheMiss:
    """When no cache file exists for (symbol, day).

    The orchestrator must call ``synthesizer.synthesize``, return the LLM
    result, and fill the cache for subsequent lookups.
    """

    def test_cache_miss_calls_synthesizer(
        self,
        trading_graph,
        mock_synthesizer,
        tmp_path,
        monkeypatch,
    ):
        """Cache miss \u2192 ``synthesizer.synthesize`` is called."""
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
        trading_graph.data_provider.get_broker_time.return_value = datetime(2026, 7, 25, 14, 0)

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

        trading_graph._synthesize_context(state)

        mock_synthesizer.synthesize.assert_called_once()

    def test_cache_miss_returns_llm_summary(
        self,
        trading_graph,
        mock_synthesizer,
        tmp_path,
        monkeypatch,
    ):
        """Cache miss \u2192 result is the LLM-produced summary, not cached data."""
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))

        llm_reasoning = "Fresh LLM analysis"
        mock_synthesizer.synthesize.return_value = _make_cached_summary(
            reasoning=llm_reasoning,
        )
        trading_graph.data_provider.get_broker_time.return_value = datetime(2026, 7, 25, 14, 0)

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

        assert result["market_context"].reasoning == llm_reasoning, (
            f"Expected LLM reasoning {llm_reasoning!r}, got {result['market_context'].reasoning!r}"
        )

    def test_cache_miss_saves_to_cache(
        self,
        trading_graph,
        mock_synthesizer,
        tmp_path,
        monkeypatch,
    ):
        """Cache miss \u2192 the result is persisted via ``save_synthesis``.

        RED: today ``_synthesize_context`` does not call ``save_synthesis``,
        so the cache file does not exist after the method returns.
        """
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
        broker_now = datetime(2026, 7, 25, 14, 0)
        trading_graph.data_provider.get_broker_time.return_value = broker_now

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

        trading_graph._synthesize_context(state)

        # After a cache miss, the cache file should exist.
        cache_file = tmp_path / "analysis" / "2026" / "07" / "25" / "EURUSD" / "synthesizer.json"
        assert cache_file.exists(), (
            f"Expected cache file at {cache_file} after synthesizer ran, "
            f"but it does not exist.  _synthesize_context did not call "
            f"save_synthesis."
        )


# ===================================================================
# Corrupt / disabled paths (3 tests)
# ===================================================================
class TestCorruptAndDisabledCache:
    """When the cache is disabled, corrupt, or has bad pydantic data.

    The orchestrator must fall through to the LLM synthesizer in all cases.
    """

    def test_disabled_cache_calls_llm(
        self,
        trading_graph,
        mock_synthesizer,
        tmp_path,
        monkeypatch,
    ):
        """Cache disabled by env \u2192 LLM is called regardless of cache state.

        Even with a valid cache file present, ``should_run_synthesis`` returns
        ``True`` when disabled, so the orchestrator must call ``synthesize``.
        """
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
        broker_now = datetime(2026, 7, 25, 14, 0)

        # Write a valid cache file (should be ignored when disabled)
        from src.decision.synthesizer_cache import save_synthesis

        save_synthesis("EURUSD", broker_now, _make_cached_summary())

        # Disable the cache
        monkeypatch.setenv("TRADING_SYNTHESIZER_CACHE_ENABLED", "false")

        # Reset sentinel so the env var is picked up
        import src.decision.synthesizer_cache as sc

        sc._settings = None

        trading_graph.data_provider.get_broker_time.return_value = broker_now
        # Make synth return a distinctive value
        llm_reasoning = "Called because cache is disabled"
        mock_synthesizer.synthesize.return_value = _make_cached_summary(
            reasoning=llm_reasoning,
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

        result = trading_graph._synthesize_context(state)

        # Must have called the LLM (not returned cached data)
        mock_synthesizer.synthesize.assert_called_once()
        assert result["market_context"].reasoning == llm_reasoning, (
            f"Expected LLM reasoning {llm_reasoning!r}, "
            f"got {result['market_context'].reasoning!r} "
            f"\u2014 may have returned cached data despite disabled flag"
        )

    def test_corrupt_cache_fallback_to_llm(
        self,
        trading_graph,
        mock_synthesizer,
        tmp_path,
        monkeypatch,
    ):
        """Corrupt cache file \u2192 fall through to LLM, don't crash."""
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
        broker_now = datetime(2026, 7, 25, 14, 0)

        # Write an invalid (corrupt) cache file
        _write_cache_file(tmp_path, "EURUSD", broker_now, "not valid json")
        trading_graph.data_provider.get_broker_time.return_value = broker_now

        llm_reasoning = "Corrupt cache fallback"
        mock_synthesizer.synthesize.return_value = _make_cached_summary(
            reasoning=llm_reasoning,
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

        result = trading_graph._synthesize_context(state)

        # Must not crash, must produce a market_context from the LLM
        assert "market_context" in result, (
            "Expected market_context in result even with corrupt cache"
        )
        assert "fatal_error" not in result, "Corrupt cache must not cause a fatal error"
        mock_synthesizer.synthesize.assert_called_once()
        assert result["market_context"].reasoning == llm_reasoning, (
            f"Expected LLM reasoning {llm_reasoning!r} (corrupt cache fallback), "
            f"got {result['market_context'].reasoning!r}"
        )

    def test_bad_pydantic_cache_fallback_to_llm(
        self,
        trading_graph,
        mock_synthesizer,
        tmp_path,
        monkeypatch,
    ):
        """Cache file with bad pydantic data \u2192 fall through to LLM."""
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
        broker_now = datetime(2026, 7, 25, 14, 0)

        # Write JSON that is valid JSON but fails MarketContextSummary validation
        _write_cache_file(
            tmp_path,
            "EURUSD",
            broker_now,
            json.dumps({"symbol": "EURUSD"}),  # missing bias, confidence, etc.
        )

        trading_graph.data_provider.get_broker_time.return_value = broker_now

        llm_reasoning = "Bad pydantic cache fallback"
        mock_synthesizer.synthesize.return_value = _make_cached_summary(
            reasoning=llm_reasoning,
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

        result = trading_graph._synthesize_context(state)

        # Must not crash, must use LLM fallback
        assert "market_context" in result, "Expected market_context despite bad pydantic cache data"
        assert "fatal_error" not in result, "Bad pydantic cache data must not cause a fatal error"
        mock_synthesizer.synthesize.assert_called_once()
        assert result["market_context"].reasoning == llm_reasoning, (
            f"Expected LLM reasoning {llm_reasoning!r} "
            f"(bad pydantic fallback), "
            f"got {result['market_context'].reasoning!r}"
        )


# ===================================================================
# Fatal error path (2 tests)
# ===================================================================
class TestFatalError:
    """When ``state.fatal_error`` is set, ``_synthesize_context`` short-circuits."""

    def test_fatal_error_short_circuits(
        self,
        trading_graph,
        mock_synthesizer,
    ):
        """fatal_error set \u2192 returns {} without checking cache or calling LLM."""
        state = AgentState(
            calendar_events=[],
            current_pending_orders=[],
            current_positions=[],
            decision=None,
            errors=[],
            fatal_error="Prior error in pipeline",
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

        assert result == {}, f"Expected empty dict on fatal_error, got {result}"
        # Synthesizer must NOT be called when fatal_error is set
        mock_synthesizer.synthesize.assert_not_called()

    def test_fatal_error_no_cache_write(
        self,
        trading_graph,
        mock_synthesizer,
        tmp_path,
        monkeypatch,
    ):
        """fatal_error set \u2192 cache is NOT written even if synthesizer runs.

        Note: ``_synthesize_context`` checks ``fatal_error`` before calling
        ``synthesize``, so the synthesizer should not run either.  This test
        guards against a regression where synthesizer runs before the
        ``fatal_error`` check, and also asserts no cache file is created.
        """
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))

        state = AgentState(
            calendar_events=[],
            current_pending_orders=[],
            current_positions=[],
            decision=None,
            errors=[],
            fatal_error="Pipeline failure",
            final_output=None,
            market_context=None,
            review=None,
            review_attempts=0,
            review_feedback=None,
            structure_analysis=_canonical_structure_analysis(),
            symbol="EURUSD",
            symbol_price=None,
        )

        trading_graph._synthesize_context(state)

        # Cache should NOT have been written
        cache_file = tmp_path / "analysis" / "2026" / "07" / "25" / "EURUSD" / "synthesizer.json"
        assert not cache_file.exists(), (
            f"Cache file should NOT exist when fatal_error is set, but found at {cache_file}"
        )
        # Synthesizer must not have been called either
        mock_synthesizer.synthesize.assert_not_called()


# ===================================================================
# Cache key isolation (4 tests)
# ===================================================================
class TestCacheKeyIsolation:
    """Cache key is based on (symbol, broker-day) — not on calendar events,
    model version, or other dimensions.

    These tests verify that the orchestrator's cache consultation logic
    matches the unit-level semantics of ``should_run_synthesis``.
    """

    def test_synthesize_context_cross_symbol_at_orchestrator(
        self,
        trading_graph,
        mock_synthesizer,
        tmp_path,
        monkeypatch,
    ):
        """EURUSD cached → run for XAUUSD ⇒ LLM synthesizer called (different symbol)."""
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
        broker_now = datetime(2026, 7, 25, 14, 0)
        trading_graph.data_provider.get_broker_time.return_value = broker_now

        # Pre-populate cache for EURUSD
        from src.decision.synthesizer_cache import save_synthesis

        save_synthesis("EURUSD", broker_now, _make_cached_summary())

        # Run for a different symbol
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
            symbol="XAUUSD",
            symbol_price=None,
        )

        trading_graph._synthesize_context(state)

        # Cache miss for XAUUSD — synthesizer must be called
        mock_synthesizer.synthesize.assert_called_once()

    def test_synthesize_context_day_rollover_at_orchestrator(
        self,
        trading_graph,
        mock_synthesizer,
        tmp_path,
        monkeypatch,
    ):
        """Cache saved at 23:59 → run at 00:01 next day ⇒ LLM called."""
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
        evening = datetime(2026, 7, 25, 23, 59, 0)
        next_morning = datetime(2026, 7, 26, 0, 1, 0)

        # Pre-populate cache for the evening time
        from src.decision.synthesizer_cache import save_synthesis

        save_synthesis("EURUSD", evening, _make_cached_summary())

        # Run with next-day broker time
        trading_graph.data_provider.get_broker_time.return_value = next_morning

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

        trading_graph._synthesize_context(state)

        # Cache miss for the new day — synthesizer must be called
        mock_synthesizer.synthesize.assert_called_once()

    def test_calendar_drift_within_day_uses_cache(
        self,
        trading_graph,
        mock_synthesizer,
        tmp_path,
        monkeypatch,
    ):
        """Different calendar events on same day → cache hit (key is symbol+day only)."""
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
        broker_now = datetime(2026, 7, 25, 14, 0)
        trading_graph.data_provider.get_broker_time.return_value = broker_now

        # Pre-populate cache
        from src.decision.synthesizer_cache import save_synthesis

        save_synthesis("EURUSD", broker_now, _make_cached_summary())

        # Run with DIFFERENT calendar events (cache key ignores calendar)
        state = AgentState(
            calendar_events=[{"event": "NFP", "impact": "high"}],
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

        # Cache hit — synthesizer NOT called, cached reasoning returned
        mock_synthesizer.synthesize.assert_not_called()
        assert result["market_context"].reasoning == _make_cached_summary().reasoning, (
            "Expected cached reasoning, not LLM output"
        )

    def test_model_version_drift_uses_cache(
        self,
        trading_graph,
        mock_synthesizer,
        tmp_path,
        monkeypatch,
    ):
        """Model changed across runs → cache hit (model version not in cache key).

        The cache is keyed only on (symbol, broker-day). A model change
        between runs does NOT invalidate the cache. This is a deliberate
        design choice because the cache stores the synthesizer *output*,
        not the LLM request; the orchestrator must produce the same
        MarketContextSummary regardless of which model generated it.
        """
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
        broker_now = datetime(2026, 7, 25, 14, 0)
        trading_graph.data_provider.get_broker_time.return_value = broker_now

        # Pre-populate cache with known content
        from src.decision.synthesizer_cache import save_synthesis

        cached = _make_cached_summary(reasoning="Cached — regardless of model")
        save_synthesis("EURUSD", broker_now, cached)

        # The mock_synthesizer has a default model; changing it has no
        # effect on cache key — cache key uses (symbol, day) only.
        mock_synthesizer.model = "gpt-4o-mini"

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

        # Cache hit despite model change
        mock_synthesizer.synthesize.assert_not_called()
        assert result["market_context"].reasoning == cached.reasoning, (
            "Expected cached reasoning despite model change"
        )


# ===================================================================
# Cost tracking (2 tests)
# ===================================================================
class TestCostTracking:
    """CostTracker integration — cache hit must not call LLM so
    ``cost_tracker.call_count`` stays unchanged; cache miss must result
    in exactly one LLM call recorded.

    The mock synthesizer is given a *real* ``CostTracker`` instance and
    its ``synthesize`` is wired to call ``record_call`` so that the
    cost-tracking behaviour is observable through the graph.
    """

    def test_cache_hit_does_not_increment_cost_tracker(
        self,
        trading_graph,
        mock_synthesizer,
        tmp_path,
        monkeypatch,
    ):
        """Cache hit → cost_tracker.call_count == 0 (no LLM call recorded)."""
        # Attach a real CostTracker
        tracker = CostTracker()
        mock_synthesizer.cost_tracker = tracker

        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
        broker_now = datetime(2026, 7, 25, 14, 0)
        trading_graph.data_provider.get_broker_time.return_value = broker_now

        # Pre-populate cache
        from src.decision.synthesizer_cache import save_synthesis

        save_synthesis("EURUSD", broker_now, _make_cached_summary())

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

        trading_graph._synthesize_context(state)

        # Cache hit — synthesizer.synthesize was NOT called, so no cost recorded
        assert tracker.call_count == 0, (
            f"Expected cost_tracker.call_count == 0 on cache hit, got {tracker.call_count}"
        )

    def test_cache_miss_increments_cost_tracker(
        self,
        trading_graph,
        mock_synthesizer,
        tmp_path,
        monkeypatch,
    ):
        """Cache miss → cost_tracker.call_count == 1 (one LLM call recorded)."""
        # Attach a real CostTracker and wire the mock to record calls
        tracker = CostTracker()
        mock_synthesizer.cost_tracker = tracker

        original_return = mock_synthesizer.synthesize.return_value

        def _synthesize_and_record(*args: object, **kwargs: object) -> MarketContextSummary:
            tracker.record_call("gpt-4o", 100, 50)
            return original_return  # type: ignore[no-any-return]

        mock_synthesizer.synthesize.side_effect = _synthesize_and_record

        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
        broker_now = datetime(2026, 7, 25, 14, 0)
        trading_graph.data_provider.get_broker_time.return_value = broker_now

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

        trading_graph._synthesize_context(state)

        # Cache miss — synthesizer.synthesize called, so cost_tracker recorded the call
        assert tracker.call_count == 1, (
            f"Expected cost_tracker.call_count == 1 on cache miss, got {tracker.call_count}"
        )


# ===================================================================
# Repeated runs (1 test)
# ===================================================================
class TestRepeatedRuns:
    """Multiple invocations within a day — only the first miss calls the LLM."""

    def test_repeated_runs_within_day_one_llm_call(
        self,
        trading_graph,
        mock_synthesizer,
        tmp_path,
        monkeypatch,
    ):
        """5 sequential runs on same symbol/day → exactly 1 LLM call.

        First run: cache miss → LLM called, cache populated.
        Runs 2–5: cache hit → LLM skipped.
        """
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "analysis"))
        broker_now = datetime(2026, 7, 25, 14, 0)
        trading_graph.data_provider.get_broker_time.return_value = broker_now

        for i in range(5):
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
            trading_graph._synthesize_context(state)

        # Exactly one LLM call across all 5 runs
        assert mock_synthesizer.synthesize.call_count == 1, (
            f"Expected exactly 1 LLM call for 5 runs, got {mock_synthesizer.synthesize.call_count}"
        )
