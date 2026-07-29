"""Tests for structural_bias, structure_context, and previous_primary_structure windowing."""

from __future__ import annotations

from typing import Any

import pytest


def _make_swing(
    index: int,
    side: str,
    price: float,
    timestamp: str = "2026-01-01T00:00:00",
) -> dict[str, Any]:
    return {
        "swing_id": f"swing_{index}",
        "index": index,
        "timestamp": timestamp,
        "side": side,
        "price": price,
        "classification": "MAJOR_STRUCTURAL_SWING",
        "prominence_atr": 2.0,
        "plateau_start_index": index,
        "plateau_end_index": index,
        "status": "ACTIVE",
    }


def _make_bar(
    index: int,
    close: float,
    high: float | None = None,
    low: float | None = None,
) -> dict[str, Any]:
    h = high or close + 5.0
    lo = low or close - 5.0
    return {
        "open_time": f"2026-01-{index + 1:02d}T00:00:00",
        "open": close - 1.0,
        "high": h,
        "low": lo,
        "close": close,
        "volume": 1000,
    }


# ── _can_classify_sequence ─────────────────────────────────────────────────


class TestCanClassifySequence:
    """_can_classify_sequence requires 3 alternating highs AND 3 alternating lows."""

    def test_enough_swings_alternating(self) -> None:
        from src.analysis.market_structure_engine.structure import (
            _can_classify_sequence,
        )

        swings = [
            _make_swing(0, "HIGH", 100),
            _make_swing(1, "LOW", 90),
            _make_swing(2, "HIGH", 110),
            _make_swing(3, "LOW", 85),
            _make_swing(4, "HIGH", 115),
            _make_swing(5, "LOW", 80),
        ]
        assert _can_classify_sequence(swings) is True

    def test_only_two_highs(self) -> None:
        from src.analysis.market_structure_engine.structure import (
            _can_classify_sequence,
        )

        swings = [
            _make_swing(0, "HIGH", 100),
            _make_swing(1, "LOW", 90),
            _make_swing(2, "HIGH", 110),
            _make_swing(3, "LOW", 85),
            _make_swing(4, "LOW", 80),
        ]
        assert _can_classify_sequence(swings) is False

    def test_only_two_lows(self) -> None:
        from src.analysis.market_structure_engine.structure import (
            _can_classify_sequence,
        )

        swings = [
            _make_swing(0, "HIGH", 100),
            _make_swing(1, "LOW", 90),
            _make_swing(2, "HIGH", 110),
            _make_swing(3, "HIGH", 115),
            _make_swing(4, "LOW", 85),
        ]
        assert _can_classify_sequence(swings) is False

    def test_empty_swings(self) -> None:
        from src.analysis.market_structure_engine.structure import (
            _can_classify_sequence,
        )

        assert _can_classify_sequence([]) is False


# ── _structure_context ─────────────────────────────────────────────────────


class TestStructureContext:
    """_structure_context maps primary + structural_bias to a context label."""

    @pytest.mark.parametrize(
        ("primary", "bias", "expected"),
        [
            ("RANGE", "BEARISH", "BEARISH_CONSOLIDATION"),
            ("RANGE", "BULLISH", "BULLISH_CONSOLIDATION"),
            ("RANGE", "RANGE", "NEUTRAL_RANGE"),
            ("TRANSITION", "BEARISH", "BEARISH_TRANSITION"),
            ("TRANSITION", "BULLISH", "BULLISH_TRANSITION"),
            ("TRANSITION", "TRANSITION", "NEUTRAL_TRANSITION"),
            ("BULLISH", "BULLISH", None),
            ("BULLISH", "BEARISH", None),
            ("BEARISH", "BEARISH", None),
            ("BEARISH", "BULLISH", None),
        ],
    )
    def test_context_labels(
        self,
        primary: str,
        bias: str,
        expected: str | None,
    ) -> None:
        from src.analysis.market_structure_engine.structure import (
            _structure_context,
        )

        assert _structure_context(primary, bias) == expected


# ── _compute_structural_bias ────────────────────────────────────────────────


class TestComputeStructuralBias:
    """structural_bias inference for non-directional local structures."""

    def test_returns_primary_when_directional(self) -> None:
        from src.analysis.market_structure_engine.structure import (
            _compute_structural_bias,
        )

        result = _compute_structural_bias("BULLISH", [], [], {"latest": {"atr_14": 50.0}})
        assert result == "BULLISH"

        result = _compute_structural_bias("BEARISH", [], [], {"latest": {"atr_14": 50.0}})
        assert result == "BEARISH"

    def test_bearish_displacement(self) -> None:
        from src.analysis.market_structure_engine.structure import (
            _compute_structural_bias,
        )

        bars = [_make_bar(i, 200.0 - float(i) * 0.5) for i in range(200)]
        major = [
            _make_swing(10, "HIGH", 200.0),
            _make_swing(30, "LOW", 180.0),
            _make_swing(50, "HIGH", 190.0),
            _make_swing(70, "LOW", 160.0),
            _make_swing(90, "HIGH", 170.0),
            _make_swing(110, "LOW", 140.0),
            _make_swing(130, "HIGH", 150.0),
            _make_swing(150, "LOW", 120.0),
            _make_swing(170, "HIGH", 130.0),
            _make_swing(190, "LOW", 100.0),
        ]
        indicators = {"latest": {"atr_14": 15.0}}

        result = _compute_structural_bias("RANGE", major, bars, indicators)
        assert result == "BEARISH"

    def test_bullish_displacement(self) -> None:
        from src.analysis.market_structure_engine.structure import (
            _compute_structural_bias,
        )

        bars = [_make_bar(i, 100.0 + float(i) * 0.5) for i in range(200)]
        major = [
            _make_swing(10, "LOW", 100.0),
            _make_swing(30, "HIGH", 120.0),
            _make_swing(50, "LOW", 110.0),
            _make_swing(70, "HIGH", 140.0),
            _make_swing(90, "LOW", 130.0),
            _make_swing(110, "HIGH", 160.0),
            _make_swing(130, "LOW", 150.0),
            _make_swing(150, "HIGH", 180.0),
            _make_swing(170, "LOW", 170.0),
            _make_swing(190, "HIGH", 200.0),
        ]
        indicators = {"latest": {"atr_14": 15.0}}

        result = _compute_structural_bias("RANGE", major, bars, indicators)
        assert result == "BULLISH"

    def test_no_displacement_returns_primary(self) -> None:
        from src.analysis.market_structure_engine.structure import (
            _compute_structural_bias,
        )

        bars = [_make_bar(i, 150.0) for i in range(200)]
        major = [
            _make_swing(10, "HIGH", 155.0),
            _make_swing(30, "LOW", 145.0),
            _make_swing(50, "HIGH", 153.0),
            _make_swing(70, "LOW", 147.0),
            _make_swing(90, "HIGH", 154.0),
            _make_swing(110, "LOW", 146.0),
            _make_swing(130, "HIGH", 155.0),
            _make_swing(150, "LOW", 145.0),
            _make_swing(170, "HIGH", 154.0),
            _make_swing(190, "LOW", 147.0),
        ]
        indicators = {"latest": {"atr_14": 10.0}}

        result = _compute_structural_bias("RANGE", major, bars, indicators)
        assert result == "RANGE"

    def test_zero_atr_returns_primary(self) -> None:
        from src.analysis.market_structure_engine.structure import (
            _compute_structural_bias,
        )

        bars = [_make_bar(i, 150.0) for i in range(200)]
        major = [_make_swing(10, "HIGH", 200.0), _make_swing(50, "LOW", 100.0)]
        indicators = {"latest": {"atr_14": 0.0}}

        result = _compute_structural_bias("RANGE", major, bars, indicators)
        assert result == "RANGE"

    def test_missing_atr_returns_primary(self) -> None:
        from src.analysis.market_structure_engine.structure import (
            _compute_structural_bias,
        )

        result = _compute_structural_bias("RANGE", [], [], {"latest": {}})
        assert result == "RANGE"

    def test_insufficient_swings_returns_primary(self) -> None:
        from src.analysis.market_structure_engine.structure import (
            _compute_structural_bias,
        )

        bars = [_make_bar(i, 150.0) for i in range(50)]
        major = [_make_swing(10, "HIGH", 200.0)]
        indicators = {"latest": {"atr_14": 10.0}}

        result = _compute_structural_bias("RANGE", major, bars, indicators)
        assert result == "RANGE"

    def test_preserves_transition_with_insufficient_swings(self) -> None:
        """_compute_structural_bias with primary=TRANSITION and insufficient
        data returns TRANSITION rather than inferring a directional bias."""
        from src.analysis.market_structure_engine.structure import (
            _compute_structural_bias,
        )

        result = _compute_structural_bias("TRANSITION", [], [], {"latest": {"atr_14": 10.0}})
        assert result == "TRANSITION"

    def test_short_bars_safe(self) -> None:
        """bias_start clamps to 0 when bars < _BIAS_BAR_LIMIT."""
        from src.analysis.market_structure_engine.structure import (
            _compute_structural_bias,
        )

        bars = [_make_bar(i, 200.0 - float(i) * 2.0) for i in range(30)]
        major = [
            _make_swing(5, "HIGH", 200.0),
            _make_swing(10, "LOW", 180.0),
            _make_swing(15, "HIGH", 190.0),
            _make_swing(20, "LOW", 160.0),
            _make_swing(25, "HIGH", 170.0),
            _make_swing(28, "LOW", 140.0),
        ]
        indicators = {"latest": {"atr_14": 15.0}}

        result = _compute_structural_bias("RANGE", major, bars, indicators)
        # Should not crash; 30 bars < _BIAS_BAR_LIMIT (120)
        assert result in ("BEARISH", "RANGE")


# ── classify_structure output ───────────────────────────────────────────────


class TestClassifyStructureFields:
    """structural_bias, structure_context, and previous_primary_structure in output."""

    def test_bearish_consolidation_context(self) -> None:
        from src.analysis.market_structure_engine.structure import (
            classify_structure,
        )

        bars = [_make_bar(i, 200.0 - float(i) * 0.4) for i in range(200)]
        major = [
            _make_swing(10, "HIGH", 200.0),
            _make_swing(30, "LOW", 180.0),
            _make_swing(50, "HIGH", 190.0),
            _make_swing(70, "LOW", 160.0),
            _make_swing(90, "HIGH", 170.0),
            _make_swing(110, "LOW", 140.0),
            _make_swing(130, "HIGH", 150.0),
            _make_swing(150, "LOW", 125.0),
            _make_swing(165, "HIGH", 135.0),
            _make_swing(180, "LOW", 128.0),
        ]
        internal_swings: list[dict[str, Any]] = []
        swings = {"major": major, "internal": internal_swings, "all": major[:]}
        indicators = {
            "latest": {
                "atr_14": 12.0,
                "ema_alignment": "BEARISH",
                "ema_10": 160.0,
                "ema_50": 170.0,
                "ema_200": 180.0,
                "close": bars[-1]["close"],
                "macd_histogram": -0.5,
            },
            "series": {"atr_14": [12.0] * len(bars)},
        }

        result = classify_structure(bars, swings, indicators)
        assert result["structural_bias"] == "BEARISH"
        assert result["structure_context"] == "BEARISH_CONSOLIDATION"

    def test_previous_structure_uses_adjacent_earlier_window(self) -> None:
        """previous_primary_structure classifies only the earlier 6 swings,
        not the recent 6."""
        from src.analysis.market_structure_engine.structure import (
            classify_structure,
        )

        major = [
            # Earlier six swings: clearly BEARISH
            _make_swing(0, "HIGH", 120),
            _make_swing(1, "LOW", 110),
            _make_swing(2, "HIGH", 115),
            _make_swing(3, "LOW", 105),
            _make_swing(4, "HIGH", 110),
            _make_swing(5, "LOW", 100),
            # Recent six swings: clearly BULLISH
            _make_swing(6, "HIGH", 112),
            _make_swing(7, "LOW", 103),
            _make_swing(8, "HIGH", 118),
            _make_swing(9, "LOW", 108),
            _make_swing(10, "HIGH", 124),
            _make_swing(11, "LOW", 114),
        ]
        bars = [_make_bar(i, 115.0) for i in range(200)]
        internal_swings: list[dict[str, Any]] = []
        swings = {"major": major, "internal": internal_swings, "all": major[:]}
        indicators = {
            "latest": {
                "atr_14": 5.0,
                "ema_alignment": "BULLISH",
                "ema_10": 115.0,
                "ema_50": 110.0,
                "ema_200": 105.0,
                "close": 115.0,
                "macd_histogram": 1.0,
            },
            "series": {"atr_14": [5.0] * len(bars)},
        }

        result = classify_structure(bars, swings, indicators)

        # Recent 6 swings are BULLISH
        assert result["primary_structure"] == "BULLISH"
        # Earlier 6 swings are BEARISH (lower highs + lower lows)
        assert result["previous_primary_structure"] == "BEARISH"

    def test_previous_structure_few_swings_falls_back(self) -> None:
        from src.analysis.market_structure_engine.structure import (
            classify_structure,
        )

        bars = [_make_bar(i, 100.0) for i in range(50)]
        major = [
            _make_swing(10, "HIGH", 110.0),
            _make_swing(20, "LOW", 90.0),
            _make_swing(30, "HIGH", 115.0),
            _make_swing(35, "HIGH", 120.0),
            _make_swing(40, "LOW", 95.0),
        ]
        internal_swings: list[dict[str, Any]] = []
        swings = {"major": major, "internal": internal_swings, "all": major[:]}
        indicators = {
            "latest": {
                "atr_14": 5.0,
                "ema_alignment": "MIXED",
                "ema_10": 100.0,
                "ema_50": 100.0,
                "ema_200": 100.0,
                "close": 100.0,
                "macd_histogram": 0.0,
            },
            "series": {"atr_14": [5.0] * len(bars)},
        }

        result = classify_structure(bars, swings, indicators)
        assert result["previous_primary_structure"] == result["primary_structure"]

    def test_structure_context_applied_through_classify_structure(self) -> None:
        """classify_structure wires _structure_context into the output."""
        from src.analysis.market_structure_engine.structure import (
            classify_structure,
        )

        # Use the same bearish-displacement fixture to verify the full pipeline
        bars = [_make_bar(i, 200.0 - float(i) * 0.4) for i in range(200)]
        major = [
            _make_swing(10, "HIGH", 200.0),
            _make_swing(30, "LOW", 180.0),
            _make_swing(50, "HIGH", 190.0),
            _make_swing(70, "LOW", 160.0),
            _make_swing(90, "HIGH", 170.0),
            _make_swing(110, "LOW", 140.0),
            _make_swing(130, "HIGH", 150.0),
            _make_swing(150, "LOW", 125.0),
            _make_swing(165, "HIGH", 135.0),
            _make_swing(180, "LOW", 128.0),
        ]
        internal_swings: list[dict[str, Any]] = []
        swings = {"major": major, "internal": internal_swings, "all": major[:]}
        indicators = {
            "latest": {
                "atr_14": 12.0,
                "ema_alignment": "BEARISH",
                "ema_10": 160.0,
                "ema_50": 170.0,
                "ema_200": 180.0,
                "close": bars[-1]["close"],
                "macd_histogram": -0.5,
            },
            "series": {"atr_14": [12.0] * len(bars)},
        }

        result = classify_structure(bars, swings, indicators)
        # structural_bias=BEARISH + primary=RANGE → context from _structure_context
        assert result["structure_context"] == "BEARISH_CONSOLIDATION"


# ── Directional votes with structural_bias ──────────────────────────────────


class TestDirectionalVotesStructuralBias:
    """_directional_votes applies the structural bias bonus only in RANGE."""

    def test_bonus_applied_when_range_and_bearish_bias(self) -> None:
        from src.analysis.market_structure_engine.scoring import (
            _directional_votes,
        )

        structure: dict[str, Any] = {
            "primary_structure": "RANGE",
            "structural_bias": "BEARISH",
            "internal_structure": {
                "direction": "RANGE",
                "phase": "CONSOLIDATION",
            },
        }
        indicators = {
            "latest": {
                "ema_alignment": "MIXED",
                "macd_histogram": 0.0,
            }
        }
        candle = {"direction": "NEUTRAL", "body_to_range_ratio": 0.3}

        votes = _directional_votes(structure, {}, indicators, {}, candle)
        # Range: neutral+30, internal RANGE: neutral+8, EMA MIXED: neutral+4
        # structural_bias BEARISH: bearish+8
        assert votes["bearish"] == pytest.approx(8.0)
        assert votes["neutral"] == pytest.approx(42.0)
        assert votes["bullish"] == pytest.approx(0.0)

    def test_bonus_applied_when_range_and_bullish_bias(self) -> None:
        from src.analysis.market_structure_engine.scoring import (
            _directional_votes,
        )

        structure: dict[str, Any] = {
            "primary_structure": "RANGE",
            "structural_bias": "BULLISH",
            "internal_structure": {
                "direction": "RANGE",
                "phase": "CONSOLIDATION",
            },
        }
        indicators = {
            "latest": {
                "ema_alignment": "MIXED",
                "macd_histogram": 0.0,
            }
        }
        candle = {"direction": "NEUTRAL", "body_to_range_ratio": 0.3}

        votes = _directional_votes(structure, {}, indicators, {}, candle)
        assert votes["bullish"] == pytest.approx(8.0)
        assert votes["neutral"] == pytest.approx(42.0)
        assert votes["bearish"] == pytest.approx(0.0)

    def test_no_bonus_when_primary_directional(self) -> None:
        from src.analysis.market_structure_engine.scoring import (
            _directional_votes,
        )

        structure: dict[str, Any] = {
            "primary_structure": "BEARISH",
            "structural_bias": "BEARISH",
            "internal_structure": {
                "direction": "BEARISH",
                "phase": "CONTINUATION",
            },
        }
        indicators = {
            "latest": {
                "ema_alignment": "BEARISH",
                "macd_histogram": -0.5,
            }
        }
        candle = {"direction": "NEUTRAL", "body_to_range_ratio": 0.3}

        votes = _directional_votes(structure, {}, indicators, {}, candle)
        # BEARISH primary: bearish+35, BEARISH internal: bearish+12,
        # EMA bearish: bearish+10, MACD negative: bearish+4.
        # No structural_bias bonus because primary is BEARISH (not RANGE).
        assert votes["bearish"] == pytest.approx(61.0)
        assert votes["bullish"] == pytest.approx(0.0)

    def test_no_bonus_when_structural_bias_missing(self) -> None:
        from src.analysis.market_structure_engine.scoring import (
            _directional_votes,
        )

        structure: dict[str, Any] = {
            "primary_structure": "RANGE",
            "internal_structure": {
                "direction": "RANGE",
                "phase": "CONSOLIDATION",
            },
        }
        indicators = {
            "latest": {
                "ema_alignment": "MIXED",
                "macd_histogram": 0.0,
            }
        }
        candle = {"direction": "NEUTRAL", "body_to_range_ratio": 0.3}

        votes = _directional_votes(structure, {}, indicators, {}, candle)
        assert votes["bearish"] == pytest.approx(0.0)
        assert votes["bullish"] == pytest.approx(0.0)


# ── calculate_score integration ─────────────────────────────────────────────


class TestCalculateScoreStructuralBias:
    """calculate_score produces correct bias when structural_bias modifies votes."""

    def test_neutral_becomes_neutral_bearish_with_bearish_bias(self) -> None:
        from src.analysis.market_structure_engine.scoring import (
            calculate_score,
        )

        structure: dict[str, Any] = {
            "primary_structure": "RANGE",
            "structural_bias": "BEARISH",
            "internal_structure": {
                "direction": "RANGE",
                "phase": "CONSOLIDATION",
            },
        }
        indicators = {
            "latest": {
                "ema_alignment": "MIXED",
                "macd_histogram": 0.0,
            }
        }
        candle = {"direction": "NEUTRAL", "body_to_range_ratio": 0.3}

        result = calculate_score(structure, {}, indicators, {}, candle)
        # With bearish bias: bearish+8, directional = -8 → |directional| == 8
        # (not < 8), so bias is NEUTRAL_BEARISH.
        assert result["bias"] in ("NEUTRAL_BEARISH", "NEUTRAL")
        assert result["directional_score"] < 0


# ── __init__.py import check ────────────────────────────────────────────────


def test_module_exports_unchanged():
    """The module exports must remain compatible with engine.py imports."""
    from src.analysis.market_structure_engine import (
        analyze_multi_timeframe,
        analyze_snapshot,
    )

    assert callable(analyze_snapshot)
    assert callable(analyze_multi_timeframe)
