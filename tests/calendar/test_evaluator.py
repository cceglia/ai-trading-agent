from src.calendar.evaluator import Evaluator


class TestEvaluatorConfig:
    def test_timeframe_windows(self):
        assert Evaluator.TIMEFRAME_WINDOWS["D1"] == 48
        assert Evaluator.TIMEFRAME_WINDOWS["H4"] == 24
        assert Evaluator.TIMEFRAME_WINDOWS["H1"] == 12

    def test_symbol_mappings_include_forex(self):
        assert "EURUSD" in Evaluator.SYMBOL_MAPPINGS
        assert "GBPUSD" in Evaluator.SYMBOL_MAPPINGS
        assert "USDJPY" in Evaluator.SYMBOL_MAPPINGS

    def test_symbol_mappings_include_commodities(self):
        assert "XAUUSD" in Evaluator.SYMBOL_MAPPINGS
        assert "XTIUSD" in Evaluator.SYMBOL_MAPPINGS

    def test_symbol_mappings_include_indices(self):
        assert "US30" in Evaluator.SYMBOL_MAPPINGS
        assert "US500" in Evaluator.SYMBOL_MAPPINGS
        assert "NASDAQ100" in Evaluator.SYMBOL_MAPPINGS

    def test_eurusd_maps_to_eur_and_usd(self):
        assert Evaluator.SYMBOL_MAPPINGS["EURUSD"] == ["EUR", "USD"]


class TestEvaluatorSafeConditions:
    def test_safe_with_no_events(self):
        evaluator = Evaluator()
        result = evaluator.evaluate_for_symbol([], "EURUSD", "H4")
        assert result["safe"] is True
        assert result["blocking"] == []
        assert result["warning"] == []

    def test_safe_with_unrelated_currency(self):
        evaluator = Evaluator()
        events = [{"currency": "JPY", "impact": "high", "title": "BOJ Rate"}]
        result = evaluator.evaluate_for_symbol(events, "EURUSD", "H4")
        assert result["safe"] is True
        assert result["blocking"] == []

    def test_safe_with_low_impact_event(self):
        evaluator = Evaluator()
        events = [{"currency": "USD", "impact": "low", "title": "Fed Speech"}]
        result = evaluator.evaluate_for_symbol(events, "EURUSD", "H4")
        assert result["safe"] is True


class TestEvaluatorBlocking:
    def test_blocking_with_high_impact(self):
        from datetime import UTC, datetime, timedelta

        evaluator = Evaluator()
        now = datetime.now(UTC)
        events = [
            {
                "currency": "USD",
                "impact": "high",
                "title": "NFP",
                "time": (now - timedelta(hours=2)).isoformat(),
            }
        ]
        result = evaluator.evaluate_for_symbol(events, "EURUSD", "H4")
        assert result["safe"] is False
        assert len(result["blocking"]) == 1
        assert result["blocking"][0]["title"] == "NFP"

    def test_multiple_blocking_events(self):
        from datetime import UTC, datetime, timedelta

        evaluator = Evaluator()
        now = datetime.now(UTC)
        events = [
            {
                "currency": "USD",
                "impact": "high",
                "title": "NFP",
                "time": (now - timedelta(hours=2)).isoformat(),
            },
            {
                "currency": "EUR",
                "impact": "high",
                "title": "ECB Rate",
                "time": (now - timedelta(hours=1)).isoformat(),
            },
        ]
        result = evaluator.evaluate_for_symbol(events, "EURUSD", "H4")
        assert result["safe"] is False
        assert len(result["blocking"]) == 2


class TestEvaluatorWarnings:
    def test_medium_impact_is_warning(self):
        from datetime import UTC, datetime, timedelta

        evaluator = Evaluator()
        now = datetime.now(UTC)
        events = [
            {
                "currency": "USD",
                "impact": "medium",
                "title": "CPI",
                "time": (now - timedelta(hours=2)).isoformat(),
            }
        ]
        result = evaluator.evaluate_for_symbol(events, "EURUSD", "H4")
        assert result["safe"] is True
        assert len(result["warning"]) == 1
        assert result["warning"][0]["title"] == "CPI"

    def test_mixed_impacts(self):
        from datetime import UTC, datetime, timedelta

        evaluator = Evaluator()
        now = datetime.now(UTC)
        events = [
            {
                "currency": "USD",
                "impact": "high",
                "title": "NFP",
                "time": (now - timedelta(hours=2)).isoformat(),
            },
            {
                "currency": "USD",
                "impact": "medium",
                "title": "CPI",
                "time": (now - timedelta(hours=1)).isoformat(),
            },
            {
                "currency": "USD",
                "impact": "low",
                "title": "Fed Speech",
                "time": (now - timedelta(hours=3)).isoformat(),
            },
        ]
        result = evaluator.evaluate_for_symbol(events, "EURUSD", "H4")
        assert result["safe"] is False
        assert len(result["blocking"]) == 1
        assert len(result["warning"]) == 1


class TestEvaluatorTimeframeDependence:
    def test_h1_window_is_12_hours(self):
        evaluator = Evaluator()
        result = evaluator.evaluate_for_symbol([], "EURUSD", "H1")
        assert result["window_hours"] == 12

    def test_h4_window_is_24_hours(self):
        evaluator = Evaluator()
        result = evaluator.evaluate_for_symbol([], "EURUSD", "H4")
        assert result["window_hours"] == 24

    def test_d1_window_is_48_hours(self):
        evaluator = Evaluator()
        result = evaluator.evaluate_for_symbol([], "EURUSD", "D1")
        assert result["window_hours"] == 48

    def test_unknown_timeframe_defaults_to_24(self):
        evaluator = Evaluator()
        result = evaluator.evaluate_for_symbol([], "EURUSD", "M15")
        assert result["window_hours"] == 24


class TestEvaluatorCurrencies:
    def test_currencies_returned_for_known_symbol(self):
        evaluator = Evaluator()
        result = evaluator.evaluate_for_symbol([], "EURUSD", "H4")
        assert result["currencies"] == ["EUR", "USD"]

    def test_currencies_empty_for_unknown_symbol(self):
        evaluator = Evaluator()
        result = evaluator.evaluate_for_symbol([], "UNKNOWN", "H4")
        assert result["currencies"] == []


class TestEvaluatorTimeFiltering:
    def test_high_impact_outside_window_not_blocking(self):
        """High-impact event outside the window should NOT block."""
        from datetime import UTC, datetime, timedelta

        evaluator = Evaluator()
        now = datetime.now(UTC)
        old_event = {
            "currency": "USD",
            "impact": "high",
            "title": "Old NFP",
            "time": (now - timedelta(hours=100)).isoformat(),
        }
        result = evaluator.evaluate_for_symbol([old_event], "EURUSD", "H4")
        assert result["safe"] is True
        assert result["blocking"] == []

    def test_high_impact_within_window_blocks(self):
        """High-impact event within the window SHOULD block."""
        from datetime import UTC, datetime, timedelta

        evaluator = Evaluator()
        now = datetime.now(UTC)
        recent_event = {
            "currency": "USD",
            "impact": "high",
            "title": "NFP",
            "time": (now - timedelta(hours=2)).isoformat(),
        }
        result = evaluator.evaluate_for_symbol([recent_event], "EURUSD", "H4")
        assert result["safe"] is False
        assert len(result["blocking"]) == 1

    def test_event_with_missing_time_excluded(self):
        """Event with no time field should be excluded (fail-safe)."""
        evaluator = Evaluator()
        events = [
            {
                "currency": "USD",
                "impact": "high",
                "title": "NFP",
                # No "time" field
            }
        ]
        result = evaluator.evaluate_for_symbol(events, "EURUSD", "H4")
        assert result["safe"] is True
        assert result["blocking"] == []

    def test_event_with_unparseable_time_excluded(self):
        """Event with unparseable time should be excluded."""
        evaluator = Evaluator()
        events = [{"currency": "USD", "impact": "high", "title": "NFP", "time": "not-a-date"}]
        result = evaluator.evaluate_for_symbol(events, "EURUSD", "H4")
        assert result["safe"] is True
        assert result["blocking"] == []

    def test_medium_impact_outside_window_not_warning(self):
        """Medium-impact event outside window should not be a warning."""
        from datetime import UTC, datetime, timedelta

        evaluator = Evaluator()
        now = datetime.now(UTC)
        old_event = {
            "currency": "USD",
            "impact": "medium",
            "title": "CPI",
            "time": (now - timedelta(hours=100)).isoformat(),
        }
        result = evaluator.evaluate_for_symbol([old_event], "EURUSD", "H4")
        assert result["safe"] is True
        assert result["warning"] == []

    def test_window_hours_d1_is_48(self):
        """D1 window should filter events within 48 hours."""
        from datetime import UTC, datetime, timedelta

        evaluator = Evaluator()
        now = datetime.now(UTC)
        event_50h_ago = {
            "currency": "USD",
            "impact": "high",
            "title": "NFP",
            "time": (now - timedelta(hours=50)).isoformat(),
        }
        result = evaluator.evaluate_for_symbol([event_50h_ago], "EURUSD", "D1")
        assert result["safe"] is True  # Outside 48h window
