"""Route-level tests with mocked scanner/runner."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.main import create_app
from src.models import RunSummary, SymbolError
from src.runner import BatchResult


@pytest.fixture
def sample_summary():
    """Sample RunSummary for route tests."""
    return RunSummary(
        symbol="XAUUSD",
        date="2026-07-26",
        time="08-30",
        bias="bullish",
        confidence=0.85,
        action="buy_setup",
        validation_status="VALID",
        setup_status="READY",
        direction="LONG",
        operational=True,
        file_path="2026/07/26/XAUUSD/result-08.json",
    )


@pytest.fixture
def mock_scanner():
    """Mock ResultScanner."""
    mock = MagicMock()
    mock.list_runs = MagicMock(return_value=[])
    mock.get_run = MagicMock(return_value=None)
    return mock


@pytest.fixture
def mock_runner():
    """Mock RunService returning an empty successful BatchResult."""
    mock = MagicMock()
    mock.run_analysis = AsyncMock(return_value=BatchResult())
    return mock


@pytest.fixture
def client(mock_scanner, mock_runner):
    """Create a test client with mocked scanner and runner."""
    with (
        patch("src.main.ResultScanner", return_value=mock_scanner),
        patch("src.main.RunService", return_value=mock_runner),
    ):
        app = create_app()
    return TestClient(app), mock_scanner, mock_runner


@pytest.fixture
def client_with_provider(monkeypatch, mock_scanner, mock_runner):
    """Create a test client whose server config knows one provider id."""
    monkeypatch.setenv("PROVIDER_CONFIG", '{"local": "http://127.0.0.1:11434/v1"}')
    with (
        patch("src.main.ResultScanner", return_value=mock_scanner),
        patch("src.main.RunService", return_value=mock_runner),
    ):
        app = create_app()
    return TestClient(app), mock_scanner, mock_runner


class TestListRuns:
    """Tests for GET /api/runs."""

    def test_returns_200_with_runs(self, client, sample_summary):
        test_client, mock_scanner, _ = client
        mock_scanner.list_runs.return_value = [sample_summary]

        resp = test_client.get("/api/runs")

        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["symbol"] == "XAUUSD"

    def test_returns_200_empty_list(self, client):
        test_client, _, _ = client

        resp = test_client.get("/api/runs")

        assert resp.status_code == 200
        assert resp.json() == []

    def test_passes_filters(self, client):
        test_client, mock_scanner, _ = client
        mock_scanner.list_runs.return_value = []

        resp = test_client.get("/api/runs?symbol=XAUUSD&from=2026-07-20&to=2026-07-26")

        mock_scanner.list_runs.assert_called_once_with(
            symbol="XAUUSD", from_date="2026-07-20", to_date="2026-07-26"
        )
        assert resp.status_code == 200

    def test_passes_no_filters(self, client):
        test_client, mock_scanner, _ = client
        mock_scanner.list_runs.return_value = []

        test_client.get("/api/runs")

        mock_scanner.list_runs.assert_called_once_with(
            symbol=None, from_date=None, to_date=None
        )

    def test_returns_500_on_error(self, client):
        test_client, mock_scanner, _ = client
        mock_scanner.list_runs.side_effect = Exception("disk error")

        resp = test_client.get("/api/runs")

        assert resp.status_code == 500
        assert "error" in resp.json()

    def test_invalid_symbol_filter_returns_400(self, client):
        test_client, mock_scanner, _ = client

        resp = test_client.get("/api/runs?symbol=..%2F")

        assert resp.status_code == 400
        mock_scanner.list_runs.assert_not_called()

    @pytest.mark.parametrize(
        "bad_date", ["2026-13-40", "2026/07/26", "2026-07", "abcd-ef-gh"]
    )
    def test_invalid_date_filter_returns_400(self, client, bad_date):
        test_client, mock_scanner, _ = client

        resp = test_client.get(f"/api/runs?from={bad_date}")

        assert resp.status_code == 400
        mock_scanner.list_runs.assert_not_called()

    def test_valid_date_filters_accepted(self, client):
        test_client, mock_scanner, _ = client
        mock_scanner.list_runs.return_value = []

        resp = test_client.get("/api/runs?from=2026-07-20&to=2026-07-26")

        assert resp.status_code == 200


class TestGetRun:
    """Tests for GET /api/runs/{symbol}/{year}/{month}/{day}/{file}."""

    def test_returns_200(self, client):
        test_client, mock_scanner, _ = client
        mock_scanner.get_run.return_value = {"symbol": "XAUUSD", "decision": {}}

        resp = test_client.get("/api/runs/XAUUSD/2026/07/26/result-08")

        assert resp.status_code == 200
        assert resp.json()["symbol"] == "XAUUSD"

    def test_returns_404(self, client):
        test_client, mock_scanner, _ = client
        mock_scanner.get_run.return_value = None

        resp = test_client.get("/api/runs/XAUUSD/2026/07/26/result-08")

        assert resp.status_code == 404

    def test_returns_500_on_error(self, client):
        test_client, mock_scanner, _ = client
        mock_scanner.get_run.side_effect = Exception("disk error")

        resp = test_client.get("/api/runs/XAUUSD/2026/07/26/result-08")

        assert resp.status_code == 500

    @pytest.mark.parametrize(
        "path",
        [
            "/api/runs/XAUUSD/2026-07/07/26/result-08",
            "/api/runs/XAUUSD/2026/13/26/result-08",
            "/api/runs/XAUUSD/2026/07/32/result-08",
            "/api/runs/XAUUSD/2026/07/26/result-99-99",
            "/api/runs/XAUUSD/2026/07/26/result-08.json",
            "/api/runs/XAUUSD/2026/%2e%2e/26/result-08",
        ],
    )
    def test_rejects_invalid_path_params_without_scanner_call(self, client, path):
        """Malformed date/file components are rejected at the route boundary
        before any file access (FR-034 / §16)."""
        test_client, mock_scanner, _ = client
        mock_scanner.get_run.return_value = {"symbol": "XAUUSD"}

        resp = test_client.get(path)

        assert resp.status_code == 400
        assert "error" in resp.json()
        mock_scanner.get_run.assert_not_called()

    @pytest.mark.parametrize(
        "path",
        [
            "/api/runs/../../etc/passwd/2026/07/26/result-08",
            "/api/runs/XAUUSD/2026/../../07/26/result-08",
            "/api/runs/..%2F..%2Fetc%2Fpasswd/2026/07/26/result-08",
            "/api/runs/%2e%2e/etc/passwd/2026/07/26/result-08",
        ],
    )
    def test_traversal_attempts_never_reach_scanner(self, client, path):
        """Traversal attempts are absorbed by URL normalization or rejected;
        in no case is the scanner (and thus disk access) invoked."""
        test_client, mock_scanner, _ = client
        mock_scanner.get_run.return_value = {"symbol": "XAUUSD"}

        resp = test_client.get(path)

        assert resp.status_code in (200, 400, 404)
        assert "BEGIN RSA" not in resp.text
        mock_scanner.get_run.assert_not_called()


class TestPostRun:
    """Tests for POST /api/run — batch envelope (FR-033, AC-016/020)."""

    def test_returns_batch_envelope_success(self, client):
        test_client, _, mock_runner = client
        mock_runner.run_analysis.return_value = BatchResult(
            results={"XAUUSD": {"symbol": "XAUUSD"}}, errors={}
        )

        resp = test_client.post("/api/run", json={"symbols": ["XAUUSD"]})

        assert resp.status_code == 200
        assert resp.json() == {
            "status": "success",
            "results": {"XAUUSD": {"symbol": "XAUUSD"}},
            "errors": {},
        }

    def test_returns_partial_envelope(self, client):
        test_client, _, mock_runner = client
        mock_runner.run_analysis.return_value = BatchResult(
            results={"XAUUSD": {"symbol": "XAUUSD"}},
            errors={
                "EURUSD": SymbolError(code="SYMBOL_NO_RESULT", message="no result")
            },
        )

        resp = test_client.post("/api/run", json={"symbols": ["XAUUSD", "EURUSD"]})

        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "partial"
        assert set(data["results"]) == {"XAUUSD"}
        assert data["errors"]["EURUSD"]["code"] == "SYMBOL_NO_RESULT"

    def test_returns_error_envelope(self, client):
        test_client, _, mock_runner = client
        mock_runner.run_analysis.return_value = BatchResult(
            results={},
            errors={"XAUUSD": SymbolError(code="SYMBOL_TIMEOUT", message="timed out")},
        )

        resp = test_client.post("/api/run", json={"symbols": ["XAUUSD"]})

        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "error"
        assert data["results"] == {}
        assert data["errors"]["XAUUSD"]["code"] == "SYMBOL_TIMEOUT"

    def test_empty_symbols_returns_400(self, client):
        test_client, _, _ = client

        resp = test_client.post("/api/run", json={"symbols": []})

        assert resp.status_code == 400

    def test_invalid_symbol_returns_400(self, client):
        test_client, _, _ = client

        resp = test_client.post("/api/run", json={"symbols": ["--help"]})

        assert resp.status_code == 400
        assert "Invalid symbol format" in resp.json()["error"]

    def test_empty_symbol_returns_400(self, client):
        test_client, _, _ = client

        resp = test_client.post("/api/run", json={"symbols": [""]})

        assert resp.status_code == 400

    def test_special_chars_returns_400(self, client):
        test_client, _, _ = client

        resp = test_client.post("/api/run", json={"symbols": ["XAU/USD"]})

        assert resp.status_code == 400

    def test_normalizes_symbols(self, client):
        """Symbols are normalized once for request keys and analyzer args."""
        test_client, _, mock_runner = client
        mock_runner.run_analysis.return_value = BatchResult(
            results={"XAUUSD": {"symbol": "XAUUSD"}}, errors={}
        )

        resp = test_client.post("/api/run", json={"symbols": ["xauusd"]})

        assert resp.status_code == 200
        mock_runner.run_analysis.assert_called_once_with(
            symbols=["XAUUSD"], model=None, base_url=None
        )
        assert list(resp.json()["results"]) == ["XAUUSD"]

    def test_deduplicates_normalized_symbols(self, client):
        """NFR-006: xauusd + XAUUSD are the same symbol and run once."""
        test_client, _, mock_runner = client
        mock_runner.run_analysis.return_value = BatchResult(
            results={"XAUUSD": {"symbol": "XAUUSD"}, "EURUSD": {"symbol": "EURUSD"}},
            errors={},
        )

        resp = test_client.post(
            "/api/run", json={"symbols": ["xauusd", "XAUUSD", "EURUSD"]}
        )

        assert resp.status_code == 200
        mock_runner.run_analysis.assert_called_once_with(
            symbols=["XAUUSD", "EURUSD"], model=None, base_url=None
        )
        assert list(resp.json()["results"]) == ["XAUUSD", "EURUSD"]

    def test_dedupe_keeps_first_occurrence_order(self, client):
        """Dedup preserves first-occurrence order."""
        test_client, _, mock_runner = client
        mock_runner.run_analysis.return_value = BatchResult()

        test_client.post(
            "/api/run", json={"symbols": ["EURUSD", "xauusd", "eurusd", "XAUUSD"]}
        )

        mock_runner.run_analysis.assert_called_once_with(
            symbols=["EURUSD", "XAUUSD"], model=None, base_url=None
        )

    def test_21_symbols_returns_422_before_runner(self, client):
        """FR-033a/AC-020: >20 symbols returns 422 and never spawns the runner."""
        test_client, _, mock_runner = client
        symbols = [f"SYM{i:02d}" for i in range(21)]

        resp = test_client.post("/api/run", json={"symbols": symbols})

        assert resp.status_code == 422
        mock_runner.run_analysis.assert_not_called()

    def test_21_raw_symbols_with_duplicates_accepted(self, client):
        """NFR-006: 21 raw entries that dedupe to 20 distinct symbols pass."""
        test_client, _, mock_runner = client
        mock_runner.run_analysis.return_value = BatchResult()
        symbols = [f"SYM{i:02d}" for i in range(20)]
        symbols.append("SYM00")  # duplicate of an existing entry → 20 distinct

        resp = test_client.post("/api/run", json={"symbols": symbols})

        assert resp.status_code == 200
        mock_runner.run_analysis.assert_called_once()
        assert len(mock_runner.run_analysis.call_args.kwargs["symbols"]) == 20

    def test_20_symbols_accepted(self, client):
        test_client, _, mock_runner = client
        symbols = [f"SYM{i:02d}" for i in range(20)]
        mock_runner.run_analysis.return_value = BatchResult()

        resp = test_client.post("/api/run", json={"symbols": symbols})

        assert resp.status_code == 200
        mock_runner.run_analysis.assert_called_once()

    def test_base_url_rejected(self, client):
        """AC-020: a free-form base_url is rejected before runner spawn."""
        test_client, _, mock_runner = client

        resp = test_client.post(
            "/api/run",
            json={"symbols": ["XAUUSD"], "base_url": "http://evil.example"},
        )

        assert resp.status_code == 422
        mock_runner.run_analysis.assert_not_called()

    def test_unknown_provider_id_returns_400(self, client):
        test_client, _, mock_runner = client

        resp = test_client.post(
            "/api/run", json={"symbols": ["XAUUSD"], "provider_id": "nope"}
        )

        assert resp.status_code == 400
        mock_runner.run_analysis.assert_not_called()

    def test_configured_provider_id_accepted(self, client_with_provider):
        """AC-020: a configured provider id resolves to the server-side URL."""
        test_client, _, mock_runner = client_with_provider
        mock_runner.run_analysis.return_value = BatchResult(
            results={"XAUUSD": {"symbol": "XAUUSD"}}, errors={}
        )

        resp = test_client.post(
            "/api/run", json={"symbols": ["XAUUSD"], "provider_id": "local"}
        )

        assert resp.status_code == 200
        mock_runner.run_analysis.assert_called_once_with(
            symbols=["XAUUSD"], model=None, base_url="http://127.0.0.1:11434/v1"
        )

    def test_passes_model(self, client):
        test_client, _, mock_runner = client
        mock_runner.run_analysis.return_value = BatchResult()

        test_client.post("/api/run", json={"symbols": ["XAUUSD"], "model": "gpt-4"})

        mock_runner.run_analysis.assert_called_once_with(
            symbols=["XAUUSD"], model="gpt-4", base_url=None
        )

    @pytest.mark.parametrize(
        "bad_model",
        [
            "x" * 101,  # too long
            "model with spaces",
            "!@#$%",
            "  ",  # whitespace only
        ],
    )
    def test_invalid_model_rejected_before_runner(self, client, bad_model):
        """NFR-004: over-long/format-violating model ids return 422 pre-spawn."""
        test_client, _, mock_runner = client

        resp = test_client.post(
            "/api/run", json={"symbols": ["XAUUSD"], "model": bad_model}
        )

        assert resp.status_code == 422
        mock_runner.run_analysis.assert_not_called()

    def test_model_with_valid_special_chars_accepted(self, client):
        """Model ids may contain the documented special characters."""
        test_client, _, mock_runner = client
        mock_runner.run_analysis.return_value = BatchResult()

        resp = test_client.post(
            "/api/run", json={"symbols": ["XAUUSD"], "model": "local/llama3:8b"}
        )

        assert resp.status_code == 200
        mock_runner.run_analysis.assert_called_once_with(
            symbols=["XAUUSD"], model="local/llama3:8b", base_url=None
        )

    def test_returns_500_on_failure(self, client):
        test_client, _, mock_runner = client
        mock_runner.run_analysis.side_effect = RuntimeError("analysis failed")

        resp = test_client.post("/api/run", json={"symbols": ["XAUUSD"]})

        assert resp.status_code == 500
        assert resp.json()["error"] == "Analysis failed"

    def test_timeout_does_not_escape_runner(self, client):
        """RunService converts timeouts to per-symbol errors; the route has no
        dedicated 502 handler (the batch envelope carries SYMBOL_TIMEOUT)."""
        test_client, _, mock_runner = client
        mock_runner.run_analysis.side_effect = TimeoutError("timed out")

        resp = test_client.post("/api/run", json={"symbols": ["XAUUSD"]})

        assert resp.status_code == 500
        assert resp.json()["error"] == "Analysis failed"

    def test_multiple_symbols(self, client):
        test_client, _, mock_runner = client
        mock_runner.run_analysis.return_value = BatchResult(
            results={
                "XAUUSD": {"symbol": "XAUUSD"},
                "EURUSD": {"symbol": "EURUSD"},
            },
            errors={},
        )

        resp = test_client.post("/api/run", json={"symbols": ["XAUUSD", "EURUSD"]})

        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert set(data["results"]) == {"XAUUSD", "EURUSD"}

    def test_valid_symbol_pattern(self, client):
        """Symbols must be 1-20 alphanumeric characters."""
        test_client, _, mock_runner = client
        mock_runner.run_analysis.return_value = BatchResult()

        resp = test_client.post("/api/run", json={"symbols": ["XAUUSD", "EURUSD123"]})

        assert resp.status_code == 200


class TestCORS:
    """CORS header verification tests."""

    def _preflight(
        self,
        test_client,
        origin="http://localhost:5173",
        request_method="GET",
        request_headers=None,
    ):
        """Issue an OPTIONS preflight request with standard CORS headers."""
        headers = {
            "Origin": origin,
            "Access-Control-Request-Method": request_method,
        }
        if request_headers is not None:
            headers["Access-Control-Request-Headers"] = request_headers
        return test_client.options("/api/runs", headers=headers)

    def test_cors_methods_restricted(self, client):
        """OPTIONS preflight must return restricted allow-methods."""
        test_client, _, _ = client
        resp = self._preflight(test_client)
        methods = resp.headers.get("access-control-allow-methods", "")
        parts = {m.strip() for m in methods.split(",")}
        assert parts == {"GET", "POST", "OPTIONS"}, f"Got {methods}"

    def test_cors_headers_restricted(self, client):
        """OPTIONS preflight must return restricted allow-headers.

        The middleware includes the simple headers (Accept, Accept-Language,
        Content-Language, Content-Type) plus the configured allow list
        (Authorization, X-API-Key). We verify exact set equality to
        prevent unintended headers.
        """
        test_client, _, _ = client
        resp = self._preflight(
            test_client,
            request_headers="content-type, authorization, x-api-key",
        )
        headers = resp.headers.get("access-control-allow-headers", "")
        parts = {h.strip().lower() for h in headers.split(",")}
        assert parts == {
            "accept",
            "accept-language",
            "authorization",
            "content-language",
            "content-type",
            "x-api-key",
        }, f"Unexpected headers: got {headers}"

    def test_cors_allowed_origin_works(self, client):
        """OPTIONS preflight from a configured origin should echo it back."""
        test_client, _, _ = client
        resp = self._preflight(test_client)
        assert (
            resp.headers.get("access-control-allow-origin") == "http://localhost:5173"
        )

    def test_cors_credentials_enabled(self, client):
        """OPTIONS preflight must include allow-credentials: true."""
        test_client, _, _ = client
        resp = self._preflight(test_client)
        assert resp.headers.get("access-control-allow-credentials") == "true"
