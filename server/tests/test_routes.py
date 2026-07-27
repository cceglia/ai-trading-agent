"""Route-level tests with mocked scanner/runner."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.main import create_app
from src.models import RunSummary


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
        review_approved=True,
        current_price=2400.0,
        file_path="2026/07/26/XAUUSD/result-08-30.json",
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
    """Mock RunService."""
    mock = MagicMock()
    mock.run_analysis = AsyncMock(return_value=[])
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


class TestGetRun:
    """Tests for GET /api/runs/{symbol}/{year}/{month}/{day}/{file}."""

    def test_returns_200(self, client):
        test_client, mock_scanner, _ = client
        mock_scanner.get_run.return_value = {"symbol": "XAUUSD", "decision": {}}

        resp = test_client.get("/api/runs/XAUUSD/2026/07/26/result-08-30")

        assert resp.status_code == 200
        assert resp.json()["symbol"] == "XAUUSD"

    def test_returns_404(self, client):
        test_client, mock_scanner, _ = client
        mock_scanner.get_run.return_value = None

        resp = test_client.get("/api/runs/XAUUSD/2026/07/26/result-08-30")

        assert resp.status_code == 404

    def test_returns_500_on_error(self, client):
        test_client, mock_scanner, _ = client
        mock_scanner.get_run.side_effect = Exception("disk error")

        resp = test_client.get("/api/runs/XAUUSD/2026/07/26/result-08-30")

        assert resp.status_code == 500


class TestPostRun:
    """Tests for POST /api/run."""

    def test_returns_200(self, client):
        test_client, _, mock_runner = client
        mock_runner.run_analysis.return_value = [{"symbol": "XAUUSD"}]

        resp = test_client.post("/api/run", json={"symbols": ["XAUUSD"]})

        assert resp.status_code == 200
        assert len(resp.json()) == 1

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

    def test_passes_model(self, client):
        test_client, _, mock_runner = client
        mock_runner.run_analysis.return_value = []

        test_client.post("/api/run", json={"symbols": ["XAUUSD"], "model": "gpt-4"})

        mock_runner.run_analysis.assert_called_once_with(
            symbols=["XAUUSD"], model="gpt-4"
        )

    def test_returns_500_on_failure(self, client):
        test_client, _, mock_runner = client
        mock_runner.run_analysis.side_effect = RuntimeError("analysis failed")

        resp = test_client.post("/api/run", json={"symbols": ["XAUUSD"]})

        assert resp.status_code == 500
        assert "analysis failed" in resp.json()["error"]

    def test_multiple_symbols(self, client):
        test_client, _, mock_runner = client
        mock_runner.run_analysis.return_value = [
            {"symbol": "XAUUSD"},
            {"symbol": "EURUSD"},
        ]

        resp = test_client.post("/api/run", json={"symbols": ["XAUUSD", "EURUSD"]})

        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_valid_symbol_pattern(self, client):
        """Symbols must be 1-20 alphanumeric characters."""
        test_client, _, mock_runner = client
        mock_runner.run_analysis.return_value = []

        resp = test_client.post("/api/run", json={"symbols": ["XAUUSD", "EURUSD123"]})

        assert resp.status_code == 200
