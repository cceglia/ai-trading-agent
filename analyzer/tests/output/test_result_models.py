"""Tests for output result models."""

from datetime import datetime

from src.decision.models import (
    BiasLevel,
    DecisionAction,
    DecisionOutput,
    MarketContextSummary,
    ReviewVerdict,
)
from src.output.result_models import AnalysisResult, OHLCBar, OHLCData, SLTPOverlay


class TestOHLCBar:
    def test_create(self):
        bar = OHLCBar(time="2026-07-25T17:00", open=2350.0, high=2370.0, low=2345.0, close=2365.5)
        assert bar.time == "2026-07-25T17:00"
        assert bar.open == 2350.0
        assert bar.high == 2370.0
        assert bar.low == 2345.0
        assert bar.close == 2365.5

    def test_float_coercion(self):
        """ints passed to float fields are promoted to float."""
        bar = OHLCBar(time="t", open=1, high=2, low=3, close=4)
        assert isinstance(bar.open, float)
        assert bar.open == 1.0


class TestOHLCData:
    def test_default_empty_lists(self):
        data = OHLCData()
        assert data.D1 == []
        assert data.H4 == []
        assert data.H1 == []

    def test_with_bars(self):
        bar = OHLCBar(time="2026-07-25T17:00", open=2350.0, high=2370.0, low=2345.0, close=2365.5)
        data = OHLCData(D1=[bar])
        assert len(data.D1) == 1
        assert data.H4 == []
        assert data.H1 == []


class TestSLTPOverlay:
    def test_default_nulls(self):
        overlay = SLTPOverlay()
        assert overlay.entry_price is None
        assert overlay.stop_loss is None
        assert overlay.take_profit is None

    def test_with_values(self):
        overlay = SLTPOverlay(entry_price=2350.0, stop_loss=2340.0, take_profit=2380.0)
        assert overlay.entry_price == 2350.0
        assert overlay.stop_loss == 2340.0
        assert overlay.take_profit == 2380.0


class TestAnalysisResult:
    def test_version_default(self):
        result = AnalysisResult(
            symbol="XAUUSD",
            run_id="test",
            started_at=datetime.now(),
            completed_at=datetime.now(),
            status="success",
        )
        assert result.version == "1.0"

    def test_with_market_context(self):
        ctx = MarketContextSummary(
            symbol="XAUUSD", bias=BiasLevel.BULLISH, confidence=75.0, reasoning="test"
        )
        result = AnalysisResult(
            symbol="XAUUSD",
            run_id="test",
            started_at=datetime.now(),
            completed_at=datetime.now(),
            status="success",
            market_context=ctx,
        )
        assert result.market_context is not None
        assert result.market_context.bias == "bullish"

    def test_with_decision(self):
        dec = DecisionOutput(symbol="XAUUSD", action=DecisionAction.BUY_SETUP, reasoning="test")
        result = AnalysisResult(
            symbol="XAUUSD",
            run_id="test",
            started_at=datetime.now(),
            completed_at=datetime.now(),
            status="success",
            decision=dec,
        )
        assert result.decision is not None
        assert result.decision.action == "buy_setup"

    def test_with_review(self):
        rev = ReviewVerdict(approved=True, reasoning="test")
        result = AnalysisResult(
            symbol="XAUUSD",
            run_id="test",
            started_at=datetime.now(),
            completed_at=datetime.now(),
            status="success",
            review=rev,
        )
        assert result.review is not None
        assert result.review.approved is True

    def test_serialization_roundtrip(self):
        ctx = MarketContextSummary(
            symbol="XAUUSD", bias=BiasLevel.BULLISH, confidence=75.0, reasoning="test"
        )
        result = AnalysisResult(
            symbol="XAUUSD",
            run_id="test",
            started_at=datetime.now(),
            completed_at=datetime.now(),
            status="success",
            market_context=ctx,
        )
        serialized = result.model_dump(mode="json")
        deserialized = AnalysisResult.model_validate(serialized)
        assert deserialized.symbol == "XAUUSD"
        assert deserialized.version == "1.0"
        assert deserialized.market_context is not None

    def test_entry_authorized_always_false(self):
        """Critical invariant: entry_authorized must always be False."""
        # Test direct DecisionOutput enforcement
        decision = DecisionOutput(
            symbol="XAUUSD",
            action="buy_setup",
            reasoning="test",
            entry_authorized=True,  # Try to set True
        )
        assert decision.entry_authorized is False

        # Test via AnalysisResult
        result = AnalysisResult(
            symbol="XAUUSD",
            run_id="test",
            started_at=datetime.now(),
            completed_at=datetime.now(),
            status="success",
            decision=DecisionOutput(
                symbol="XAUUSD",
                action="buy_setup",
                reasoning="test",
                entry_authorized=True,
            ),
        )
        assert result.decision is not None
        assert result.decision.entry_authorized is False

    def test_status_enum_values(self):
        result = AnalysisResult(
            symbol="XAUUSD",
            run_id="test",
            started_at=datetime.now(),
            completed_at=datetime.now(),
            status="success",
        )
        assert result.status == "success"

    def test_fatal_error_and_errors(self):
        result = AnalysisResult(
            symbol="XAUUSD",
            run_id="test",
            started_at=datetime.now(),
            completed_at=datetime.now(),
            status="error",
            errors=["Something went wrong"],
            fatal_error="Critical failure",
        )
        assert len(result.errors) == 1
        assert result.fatal_error == "Critical failure"

    def test_ohlc_and_sl_tp_defaults(self):
        result = AnalysisResult(
            symbol="XAUUSD",
            run_id="test",
            started_at=datetime.now(),
            completed_at=datetime.now(),
            status="success",
        )
        assert result.ohlc.D1 == []
        assert result.ohlc.H4 == []
        assert result.ohlc.H1 == []
        assert result.sl_tp_overlay.entry_price is None

    def test_all_fields_populated(self):
        """Full-featured AnalysisResult with all optional fields set."""
        now = datetime.now()
        ctx = MarketContextSummary(
            symbol="XAUUSD", bias=BiasLevel.BULLISH, confidence=80.0, reasoning="Strong trend"
        )
        dec = DecisionOutput(
            symbol="XAUUSD",
            action=DecisionAction.BUY_SETUP,
            entry_price=2350.0,
            stop_loss=2320.0,
            take_profit=2410.0,
            reasoning="Good R/R",
            risk_reward_ratio=2.0,
        )
        rev = ReviewVerdict(
            approved=True,
            reasoning="Looks good",
            concerns=["Spread a bit wide"],
        )
        ohlc = OHLCData(
            D1=[
                OHLCBar(time="2026-07-25T17:00", open=2350.0, high=2370.0, low=2345.0, close=2365.5)
            ],
        )
        sltp = SLTPOverlay(entry_price=2350.0, stop_loss=2320.0, take_profit=2410.0)

        result = AnalysisResult(
            version="2.0",
            symbol="XAUUSD",
            run_id="full-test",
            started_at=now,
            completed_at=now,
            status="success",
            errors=[],
            fatal_error=None,
            market_context=ctx,
            decision=dec,
            review=rev,
            ohlc=ohlc,
            sl_tp_overlay=sltp,
        )

        assert result.version == "2.0"
        assert result.market_context.bias == "bullish"
        assert result.decision.action == "buy_setup"
        assert result.review.approved is True
        assert len(result.ohlc.D1) == 1
        assert result.sl_tp_overlay.entry_price == 2350.0
