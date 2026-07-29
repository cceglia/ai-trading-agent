"""Integration tests with real file I/O."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.main import create_app


@pytest.fixture
def integration_data(tmp_path: Path, sample_full_result: dict):
    """Create a temporary data directory with fixture JSON files."""
    fpath = tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08.json"
    fpath.parent.mkdir(parents=True)
    fpath.write_text(json.dumps(sample_full_result))
    return tmp_path


@pytest.fixture
def integration_client(integration_data: Path):
    """Create app pointing at the mock data directory."""
    os.environ["TRADING_ANALYSIS_CACHE_DIR"] = str(integration_data)
    try:
        app = create_app()
        yield TestClient(app)
    finally:
        del os.environ["TRADING_ANALYSIS_CACHE_DIR"]


class TestListRunsIntegration:
    """Integration tests for GET /api/runs with real file I/O."""

    def test_returns_fixture_data(self, integration_client):
        resp = integration_client.get("/api/runs")

        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1
        assert data[0]["symbol"] == "XAUUSD"

    def test_filters_by_symbol(self, integration_client):
        resp = integration_client.get("/api/runs?symbol=EURUSD")

        assert resp.status_code == 200
        assert len(resp.json()) == 0

    def test_filters_by_date_range(self, integration_client):
        resp = integration_client.get("/api/runs?from=2026-07-26&to=2026-07-26")

        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1
        assert all(r["date"] == "2026-07-26" for r in data)


class TestGetRunIntegration:
    """Integration tests for GET /api/runs/{symbol}/{year}/{month}/{day}/{file}."""

    def test_returns_full_result(self, integration_client):
        resp = integration_client.get("/api/runs/XAUUSD/2026/07/26/result-08")

        assert resp.status_code == 200
        data = resp.json()
        assert data["symbol"] == "XAUUSD"
        assert data["market_context"]["bias"] == "bullish"
        assert data["decision"]["action"] == "buy_setup"

    def test_returns_404_for_missing(self, integration_client):
        resp = integration_client.get("/api/runs/XAUUSD/2026/07/26/result-99-99")

        assert resp.status_code == 404

    def test_returns_404_for_wrong_symbol(self, integration_client):
        resp = integration_client.get("/api/runs/EURUSD/2026/07/26/result-08")

        assert resp.status_code == 404
