"""Tests for authentication and rate-limiting middleware."""

from __future__ import annotations

import logging
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.middleware.ratelimit import SlidingWindowRateLimiter
from src.runner import BatchResult


class TestAuthMiddleware:
    """Tests for AuthMiddleware behaviour via client_with_auth.

    Auth is enforced whenever an API key or trusted proxy CIDR is configured.
    Every ``/api`` route must reject missing/invalid credentials with 401
    (FR-035 / AC-017); non-API paths (static assets / SPA) stay reachable
    through the trusted proxy.
    """

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

    def test_get_endpoints_require_auth(self, client_with_auth):
        """AC-017: GET /api routes reject missing credentials when enforced."""
        test_client, mock_scanner, _ = client_with_auth
        mock_scanner.list_runs.return_value = []

        resp = test_client.get("/api/runs")

        assert resp.status_code == 401
        assert resp.json() == {"error": "Missing or invalid API key"}
        mock_scanner.list_runs.assert_not_called()

    def test_get_with_valid_key_returns_200(self, client_with_auth):
        test_client, mock_scanner, _ = client_with_auth
        mock_scanner.list_runs.return_value = []

        resp = test_client.get("/api/runs", headers={"X-API-Key": "test-secret-key"})

        assert resp.status_code == 200

    def test_get_detail_without_key_returns_401(self, client_with_auth):
        test_client, mock_scanner, _ = client_with_auth
        mock_scanner.get_run.return_value = {"symbol": "XAUUSD"}

        resp = test_client.get("/api/runs/XAUUSD/2026/07/26/result-08")

        assert resp.status_code == 401
        mock_scanner.get_run.assert_not_called()

    def test_get_detail_with_valid_key_returns_200(self, client_with_auth):
        test_client, mock_scanner, _ = client_with_auth
        mock_scanner.get_run.return_value = {"symbol": "XAUUSD"}

        resp = test_client.get(
            "/api/runs/XAUUSD/2026/07/26/result-08",
            headers={"X-API-Key": "test-secret-key"},
        )

        assert resp.status_code == 200

    def test_unknown_api_path_returns_404_json_when_authenticated(
        self, client_with_auth
    ):
        """API-002: an authenticated request to an unknown /api/* path gets
        404 JSON, never the SPA fallback (200 text/html)."""
        test_client, _, _ = client_with_auth

        resp = test_client.get(
            "/api/does-not-exist", headers={"X-API-Key": "test-secret-key"}
        )

        assert resp.status_code == 404
        assert resp.headers["content-type"].startswith("application/json")
        assert resp.json() == {"error": "Not found"}

    def test_unknown_api_path_still_requires_auth(self, client_with_auth):
        """Auth runs before the 404 catch-all: a missing credential is 401."""
        test_client, _, _ = client_with_auth

        resp = test_client.get("/api/does-not-exist")

        assert resp.status_code == 401
        assert resp.json() == {"error": "Missing or invalid API key"}

    def test_auth_failure_does_not_launch_analyzer(self, client_with_auth):
        """§15: a 401 on POST /api/run must never reach the runner."""
        test_client, _, mock_runner = client_with_auth

        resp = test_client.post("/api/run", json={"symbols": ["XAUUSD"]})

        assert resp.status_code == 401
        mock_runner.run_analysis.assert_not_called()

    def test_non_api_paths_not_auth_blocked(self, client_with_auth):
        """Static assets / SPA fallback are served through the proxy, not /api."""
        test_client, _, _ = client_with_auth

        resp = test_client.get("/some/spa/path")

        assert resp.status_code != 401

    @pytest.mark.parametrize(
        ("method", "path"),
        [
            ("get", "/API/runs"),
            ("get", "/Api/runs"),
            ("post", "/API/run"),
            ("get", "/API/runs/XAUUSD/2026/07/26/result-08"),
        ],
    )
    def test_case_variant_api_paths_require_auth(self, client_with_auth, method, path):
        """API-001: the /api auth boundary is case-insensitive; no /API variant
        bypasses authentication and reaches a route or the SPA fallback."""
        test_client, _, _ = client_with_auth
        kwargs = {"json": {"symbols": ["XAUUSD"]}} if method == "post" else {}
        resp = getattr(test_client, method)(path, **kwargs)

        assert resp.status_code == 401
        assert resp.json() == {"error": "Missing or invalid API key"}

    def test_case_variant_api_path_with_valid_key_not_blocked(self, client_with_auth):
        """A valid credential passes the case-insensitive boundary; the path is
        then routed normally (no case-variant route exists, so a 404)."""
        test_client, _, _ = client_with_auth

        resp = test_client.get("/API/runs", headers={"X-API-Key": "test-secret-key"})

        assert resp.status_code != 401

    def test_options_preflight_requires_auth(self, client_with_auth):
        """CORS-001: in enforced mode, OPTIONS /api/* preflight is protected.

        ``AuthMiddleware`` sits outside ``CORSMiddleware`` and rejects the
        preflight with 401 (no ``Access-Control-Allow-*`` headers) when no
        credential is presented. The trusted proxy must authenticate the
        preflight (or handle CORS itself) for browser clients; the server
        never answers preflights without a credential.
        """
        test_client, _, _ = client_with_auth

        resp = test_client.options(
            "/api/run",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type,x-api-key",
            },
        )

        assert resp.status_code == 401
        assert resp.json() == {"error": "Missing or invalid API key"}
        assert resp.headers.get("access-control-allow-origin") is None
        assert resp.headers.get("access-control-allow-methods") is None

    def test_options_preflight_with_valid_key_succeeds(self, client_with_auth):
        """An authenticated preflight reaches CORSMiddleware and gets CORS
        headers, confirming the CORS origins/credentials contract (FR-035)."""
        test_client, _, _ = client_with_auth

        resp = test_client.options(
            "/api/run",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type,x-api-key",
                "X-API-Key": "test-secret-key",
            },
        )

        assert resp.status_code == 200
        assert resp.headers.get("access-control-allow-origin") == (
            "http://localhost:5173"
        )
        assert "POST" in resp.headers.get("access-control-allow-methods", "")

    def test_no_key_dev_mode_bypasses_auth(self, client):
        """When TRADING_API_KEY and TRADING_TRUSTED_PROXY_CIDRS are empty
        (default), auth is explicitly permissive (dev mode)."""
        test_client, _, mock_runner = client
        mock_runner.run_analysis.return_value = BatchResult(
            results={"XAUUSD": {"symbol": "XAUUSD"}}, errors={}
        )

        resp = test_client.post("/api/run", json={"symbols": ["XAUUSD"]})

        assert resp.status_code == 200


class TestProxyMarkerAuthentication:
    """``X-Authenticated-User`` is trusted only from ``TRADING_TRUSTED_PROXY_CIDRS``.

    FR-036: FastAPI must reject a client-supplied marker from an untrusted
    source (including the direct client case where the proxy did not rewrite
    the header). Empty CIDR configuration never authorizes the marker.
    """

    @staticmethod
    def _client(app, host: str = "10.1.2.3") -> TestClient:
        return TestClient(app, client=(host, 54321))

    def test_trusted_marker_authorizes_get(self, proxy_app):
        app, mock_scanner, _ = proxy_app
        mock_scanner.list_runs.return_value = []

        resp = self._client(app).get(
            "/api/runs", headers={"X-Authenticated-User": "alice"}
        )

        assert resp.status_code == 200

    def test_trusted_marker_authorizes_post(self, proxy_app):
        app, _, mock_runner = proxy_app
        mock_runner.run_analysis.return_value = BatchResult(
            results={"XAUUSD": {"symbol": "XAUUSD"}}, errors={}
        )

        resp = self._client(app).post(
            "/api/run",
            json={"symbols": ["XAUUSD"]},
            headers={"X-Authenticated-User": "alice"},
        )

        assert resp.status_code == 200

    def test_marker_from_untrusted_source_rejected(self, proxy_app):
        app, mock_scanner, _ = proxy_app
        mock_scanner.list_runs.return_value = []

        resp = self._client(app, host="8.8.8.8").get(
            "/api/runs", headers={"X-Authenticated-User": "mallory"}
        )

        assert resp.status_code == 401
        mock_scanner.list_runs.assert_not_called()

    def test_marker_without_cidrs_configured_rejected(self, client_with_auth):
        """Empty TRADING_TRUSTED_PROXY_CIDRS never trusts a client marker."""
        test_client, mock_scanner, _ = client_with_auth
        mock_scanner.list_runs.return_value = []

        resp = test_client.get("/api/runs", headers={"X-Authenticated-User": "mallory"})

        assert resp.status_code == 401
        mock_scanner.list_runs.assert_not_called()

    def test_valid_api_key_beats_untrusted_marker(self, client_with_auth):
        """A valid machine key authorizes even when a forged marker is present."""
        test_client, mock_scanner, _ = client_with_auth
        mock_scanner.list_runs.return_value = []

        resp = test_client.get(
            "/api/runs",
            headers={
                "X-API-Key": "test-secret-key",
                "X-Authenticated-User": "mallory",
            },
        )

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
        """After max_requests POSTs, the next one returns 429 with Retry-After."""
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
        assert "Retry-After" in resp.headers
        assert int(resp.headers["Retry-After"]) >= 1

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
