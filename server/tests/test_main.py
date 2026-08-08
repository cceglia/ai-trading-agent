"""Tests for authentication and rate-limiting middleware."""

from __future__ import annotations

import logging
from unittest.mock import patch

from fastapi.testclient import TestClient

from src.middleware.ratelimit import SlidingWindowRateLimiter
from src.runner import BatchResult


class TestAuthMiddleware:
    """Tests for AuthMiddleware behaviour via client_with_auth."""

    def test_post_without_key_returns_401(self, client_with_auth):
        test_client, _, _ = client_with_auth

        resp = test_client.post("/api/run", json={"symbols": ["XAUUSD"]})

        assert resp.status_code == 401
        assert resp.json() == {"error": "Missing or invalid API key"}

    def test_post_with_wrong_key_returns_401(self, client_with_auth):
        test_client, _, _ = client_with_auth

        resp = test_client.post(
            "/api/run",
            json={"symbols": ["XAUUSD"]},
            headers={"X-API-Key": "wrong-key"},
        )

        assert resp.status_code == 401
        assert resp.json() == {"error": "Missing or invalid API key"}

    def test_post_with_valid_key_returns_200(self, client_with_auth):
        test_client, _, mock_runner = client_with_auth
        mock_runner.run_analysis.return_value = BatchResult(
            results={"XAUUSD": {"symbol": "XAUUSD"}}, errors={}
        )

        resp = test_client.post(
            "/api/run",
            json={"symbols": ["XAUUSD"]},
            headers={"X-API-Key": "test-secret-key"},
        )

        assert resp.status_code == 200

    def test_get_endpoints_unprotected(self, client_with_auth):
        """GET endpoints must not require auth even when API key is set."""
        test_client, mock_scanner, _ = client_with_auth
        mock_scanner.list_runs.return_value = []

        resp = test_client.get("/api/runs")

        assert resp.status_code == 200

    def test_no_key_dev_mode_bypasses_auth(self, client):
        """When TRADING_API_KEY is empty (default), auth is skipped."""
        test_client, _, mock_runner = client
        mock_runner.run_analysis.return_value = BatchResult(
            results={"XAUUSD": {"symbol": "XAUUSD"}}, errors={}
        )

        resp = test_client.post("/api/run", json={"symbols": ["XAUUSD"]})

        assert resp.status_code == 200


class TestSlidingWindowRateLimiter:
    """Unit tests for the in-memory rate limiter."""

    def test_allows_first_request(self):
        limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=60)
        assert limiter.is_allowed("client-1") is True

    def test_allows_up_to_limit(self):
        limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=60)
        assert limiter.is_allowed("client-1") is True
        assert limiter.is_allowed("client-1") is True
        assert limiter.is_allowed("client-1") is True

    def test_blocks_after_limit(self):
        limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=60)
        for _ in range(3):
            limiter.is_allowed("client-1")
        assert limiter.is_allowed("client-1") is False

    def test_separate_buckets_per_client(self):
        limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=60)
        assert limiter.is_allowed("client-1") is True
        assert limiter.is_allowed("client-1") is True
        assert limiter.is_allowed("client-1") is False  # blocked
        assert limiter.is_allowed("client-2") is True  # different bucket
        assert limiter.is_allowed("client-2") is True
        assert limiter.is_allowed("client-2") is False  # blocked

    def test_cleanup_removes_expired_buckets(self):
        limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=0.001)
        assert limiter.is_allowed("client-1") is True
        # Bucket exists
        assert "client-1" in limiter._buckets

        import time

        time.sleep(0.002)
        limiter.cleanup()

        assert "client-1" not in limiter._buckets


class TestRateLimitIntegration:
    """Integration tests: rate limiter wired into POST /api/run."""

    def test_rate_limit_exceeded_returns_429(self, client):
        """After max_requests POSTs, the next one returns 429."""
        test_client, _, mock_runner = client
        mock_runner.run_analysis.return_value = BatchResult(
            results={"XAUUSD": {"symbol": "XAUUSD"}}, errors={}
        )

        # Default is 20 req / 60s — hit the limit
        for _ in range(20):
            resp = test_client.post("/api/run", json={"symbols": ["XAUUSD"]})
            assert resp.status_code == 200

        # 21st request should be rate-limited
        resp = test_client.post("/api/run", json={"symbols": ["XAUUSD"]})
        assert resp.status_code == 429
        assert resp.json() == {"error": "Rate limit exceeded"}

    def test_get_endpoints_not_rate_limited(self, client):
        """GET requests must not be affected by POST rate limit."""
        test_client, mock_scanner, _ = client
        mock_scanner.list_runs.return_value = []

        # Blast GET requests (they should not count toward the POST limit)
        for _ in range(25):
            resp = test_client.get("/api/runs")
            assert resp.status_code == 200

    def test_rate_limiter_window_reset(self):
        """After exhausting the limit, clearing the bucket allows requests again."""
        custom_limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=60)

        import src.main as main_module

        original = main_module.SlidingWindowRateLimiter
        try:
            main_module.SlidingWindowRateLimiter = lambda *a, **kw: custom_limiter  # type: ignore[method-assign]

            l_mock_scanner = __import__("unittest").mock.MagicMock()
            l_mock_runner = __import__("unittest").mock.AsyncMock()
            l_mock_runner.run_analysis.return_value = BatchResult(
                results={"XAUUSD": {"symbol": "XAUUSD"}}, errors={}
            )
            with (
                patch("src.main.ResultScanner", return_value=l_mock_scanner),
                patch("src.main.RunService", return_value=l_mock_runner),
            ):
                app = main_module.create_app()
            tc = TestClient(app)

            # Exhaust the limit
            resp = tc.post("/api/run", json={"symbols": ["XAUUSD"]})
            assert resp.status_code == 200
            resp = tc.post("/api/run", json={"symbols": ["XAUUSD"]})
            assert resp.status_code == 200
            resp = tc.post("/api/run", json={"symbols": ["XAUUSD"]})
            assert resp.status_code == 429

            # Clear bucket (simulating window expiry)
            custom_limiter._buckets.clear()

            # Should pass again
            resp = tc.post("/api/run", json={"symbols": ["XAUUSD"]})
            assert resp.status_code == 200
        finally:
            main_module.SlidingWindowRateLimiter = original


class TestErrorLogging:
    """Tests that exceptions are logged before re-raising."""

    def test_list_runs_logs_original_error(self, caplog):
        """list_runs must log the original exception before raising RuntimeError."""
        mock_scanner = __import__("unittest").mock.MagicMock()
        mock_scanner.list_runs.side_effect = Exception("disk error")
        mock_runner = __import__("unittest").mock.MagicMock()

        with (
            patch("src.main.ResultScanner", return_value=mock_scanner),
            patch("src.main.RunService", return_value=mock_runner),
        ):
            from src.main import create_app as _create_app

            app = _create_app()
        tc = TestClient(app)

        with caplog.at_level(logging.ERROR, logger="src.main"):
            resp = tc.get("/api/runs")

        assert resp.status_code == 500
        assert resp.json() == {"error": "Failed to list runs"}
        assert any("Failed to list runs" in rec.message for rec in caplog.records)
        # The original exception traceback should be captured
        assert any(
            "disk error" in rec.message
            or "disk error" in rec.exc_text
            or rec.exc_info is not None
            for rec in caplog.records
        )

    def test_get_run_logs_original_error(self, caplog):
        """get_run must log the original exception before raising RuntimeError."""
        mock_scanner = __import__("unittest").mock.MagicMock()
        mock_scanner.get_run.side_effect = Exception("disk error")
        mock_runner = __import__("unittest").mock.MagicMock()

        with (
            patch("src.main.ResultScanner", return_value=mock_scanner),
            patch("src.main.RunService", return_value=mock_runner),
        ):
            from src.main import create_app as _create_app

            app = _create_app()
        tc = TestClient(app)

        with caplog.at_level(logging.ERROR, logger="src.main"):
            resp = tc.get("/api/runs/XAUUSD/2026/07/26/result-08")

        assert resp.status_code == 500
        assert resp.json() == {"error": "Failed to get run"}
        assert any("Failed to get run" in rec.message for rec in caplog.records)

    def test_post_run_logs_original_error(self, caplog):
        """run_analysis must log the original exception before raising RuntimeError."""
        mock_scanner = __import__("unittest").mock.MagicMock()
        mock_runner = __import__("unittest").mock.MagicMock()
        mock_runner.run_analysis = __import__("unittest").mock.AsyncMock(
            side_effect=Exception("analysis crashed")
        )

        with (
            patch("src.main.ResultScanner", return_value=mock_scanner),
            patch("src.main.RunService", return_value=mock_runner),
        ):
            from src.main import create_app as _create_app

            app = _create_app()
        tc = TestClient(app)

        with caplog.at_level(logging.ERROR, logger="src.main"):
            resp = tc.post("/api/run", json={"symbols": ["XAUUSD"]})

        assert resp.status_code == 500
        assert any(
            "Analysis failed for symbols: ['XAUUSD']" in rec.message
            for rec in caplog.records
        )

    def test_post_run_logs_timeout_as_generic_failure(self, caplog):
        """run_analysis must not have a dedicated 502 path: a TimeoutError that
        escapes RunService (unreachable in production) is a generic failure."""
        mock_scanner = __import__("unittest").mock.MagicMock()
        mock_runner = __import__("unittest").mock.MagicMock()
        mock_runner.run_analysis = __import__("unittest").mock.AsyncMock(
            side_effect=TimeoutError("timed out after 600s")
        )

        with (
            patch("src.main.ResultScanner", return_value=mock_scanner),
            patch("src.main.RunService", return_value=mock_runner),
        ):
            from src.main import create_app as _create_app

            app = _create_app()
        tc = TestClient(app)

        with caplog.at_level(logging.ERROR, logger="src.main"):
            resp = tc.post("/api/run", json={"symbols": ["XAUUSD"]})

        assert resp.status_code == 500
        assert resp.json() == {"error": "Analysis failed"}
        assert any(
            "Analysis failed for symbols: ['XAUUSD']" in rec.message
            for rec in caplog.records
        )
