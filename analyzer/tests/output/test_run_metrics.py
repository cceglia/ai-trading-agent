"""Tests for bounded per-batch run metrics counters (NFR §18)."""

from __future__ import annotations

import logging

from src.output.run_metrics import RunMetrics


def _result(status: str, validation_status: str = "VALID", fatal: bool = False) -> dict:
    return {
        "analysis_result": {
            "status": status,
            "validation_status": validation_status,
        },
        "fatal_error": "boom" if fatal else None,
    }


class TestRunMetricsRecord:
    def test_success_bucket(self):
        metrics = RunMetrics()
        metrics.record("XAUUSD", "success", _result("success", "VALID"))
        assert metrics._outcomes["analysis_success"] == 1

    def test_degraded_bucket(self):
        metrics = RunMetrics()
        metrics.record("XAUUSD", "success", _result("degraded", "VALID"))
        assert metrics._outcomes["analysis_degraded"] == 1

    def test_invalid_bucket(self):
        metrics = RunMetrics()
        metrics.record("XAUUSD", "success", _result("partial", "INVALID"))
        assert metrics._outcomes["analysis_invalid"] == 1

    def test_unrecognized_status_falls_back_to_degraded(self):
        """METRICS-002: partial/validation statuses without a dedicated bucket
        map to ``analysis_degraded`` (documented fallback semantics)."""
        metrics = RunMetrics()
        metrics.record("XAUUSD", "success", _result("partial", "VALID"))
        assert metrics._outcomes["analysis_degraded"] == 1
        assert metrics._outcomes["analysis_success"] == 0

    def test_error_bucket_for_fatal_result(self):
        metrics = RunMetrics()
        metrics.record("XAUUSD", "success", _result("success", "VALID", fatal=True))
        assert metrics._outcomes["analysis_error"] == 1

    def test_error_bucket_for_cli_error(self):
        metrics = RunMetrics()
        metrics.record("XAUUSD", "error", {"fatal_error": "no data"})
        assert metrics._outcomes["analysis_error"] == 1

    def test_symbol_labels_are_bounded(self):
        metrics = RunMetrics(symbol_label_limit=3)
        for i in range(10):
            metrics.record(f"SYM{i}", "success", _result("success", "VALID"))
        assert len(metrics._symbols) == 3

    def test_record_notification_sent_and_suppressed(self):
        metrics = RunMetrics()
        metrics.record_notification(True)
        metrics.record_notification(False)
        metrics.record_notification(True)
        assert metrics.notifications_sent == 2
        assert metrics.notifications_suppressed == 1

    def test_summary_line_is_emitted(self, caplog):
        metrics = RunMetrics()
        metrics.llm_calls = 1
        metrics.record("XAUUSD", "success", _result("success", "VALID"))
        metrics.record("EURUSD", "error", {"fatal_error": "no data"})
        metrics.record_notification(False)
        with caplog.at_level(logging.INFO, logger="src.output.run_metrics"):
            metrics.log_summary()
        assert "Run metrics:" in caplog.text
        assert "llm_calls=1" in caplog.text
        assert "analysis_success=1" in caplog.text
        assert "analysis_error=1" in caplog.text
        assert "notifications_suppressed=1" in caplog.text
