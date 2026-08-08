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

    def test_returns_legacy_result_via_adapter(self, integration_client):
        """The legacy review-based fixture is returned normalized and
        review-free via the read-only legacy adapter (AC-015)."""
        resp = integration_client.get("/api/runs/XAUUSD/2026/07/26/result-08")

        assert resp.status_code == 200
        data = resp.json()
        assert data["schema_version"] == "legacy"
        assert data["symbol"] == "XAUUSD"
        facts = data["deterministic_facts"]
        assert facts["validation_status"] == "UNKNOWN"
        assert facts["operational"] is False
        assert data["decision"]["action"] == "buy_setup"
        assert "review" not in data
        assert "review_approved" not in data

    def test_legacy_result_without_trade_plan_fields_is_usable(
        self, integration_client, integration_data
    ):
        """Legacy files remain readable without inventing a MARKET order."""
        legacy_path = (
            integration_data / "2026" / "07" / "26" / "EURUSD" / "result-09.json"
        )
        legacy_path.parent.mkdir(parents=True)
        legacy_path.write_text(
            json.dumps(
                {
                    "symbol": "EURUSD",
                    "version": "1.0",
                    "run_id": "legacy-eurusd",
                    "status": "success",
                    "market_context": {"bias": "bearish", "confidence": 0.4},
                    "decision": {"action": "no_trade", "reasoning": "legacy"},
                    "review": {"approved": False, "reasoning": "legacy"},
                }
            )
        )

        response = integration_client.get("/api/runs/EURUSD/2026/07/26/result-09")

        assert response.status_code == 200
        data = response.json()
        assert data["schema_version"] == "legacy"
        assert data["deterministic_facts"]["validation_status"] == "UNKNOWN"
        assert data["deterministic_facts"]["operational"] is False
        assert data["decision"]["action"] == "no_trade"
        assert "review" not in data
        assert "order_type" not in data

    def test_v2_result_returned_as_is(self, integration_client, integration_data):
        """A schema-v2 file written by the analyzer is returned verbatim."""
        v2_path = integration_data / "2026" / "07" / "26" / "XAUUSD" / "result-10.json"
        v2_path.parent.mkdir(parents=True, exist_ok=True)
        v2_path.write_text(
            json.dumps(
                {
                    "schema_version": "2",
                    "symbol": "XAUUSD",
                    "run_id": "2026-07-26T10:00:00",
                    "started_at": "2026-07-26T10:00:00",
                    "completed_at": "2026-07-26T10:00:01",
                    "status": "success",
                    "errors": [],
                    "fatal_error": None,
                    "deterministic_facts": {
                        "symbol": "XAUUSD",
                        "timeframes": {},
                        "setup_status": "READY",
                        "direction": "LONG",
                        "trade_direction": "BULLISH",
                        "setup_grade": "AAA",
                        "setup_classification_status": "CLASSIFIED",
                        "setup_lifecycle_status": "TRIGGERED",
                        "entry_plan": {},
                        "rr": {
                            "calculated_rr": 2.0,
                            "minimum_required_rr": 2.0,
                            "rr_pass": True,
                        },
                        "confidence_components": {},
                        "policy": {
                            "execution_status": "ACTIONABLE",
                            "actionable": True,
                            "blockers": [],
                            "reason_codes": [],
                        },
                        "selected_levels": {},
                        "latest_structural_events": {},
                        "latest_liquidity_states": {},
                        "event_history": {},
                        "liquidity_history": {},
                        "validation_status": "VALID",
                        "validation_errors": [],
                        "operational": True,
                        "entry_authorized": False,
                        "bias": "BULLISH",
                        "confidence": 72.0,
                    },
                    "decision": {"action": "buy_setup"},
                    "synthesis": {
                        "status": "SUCCESS",
                        "explanation": "deterministic context is bullish",
                        "risks": [],
                        "confluences": [],
                        "error": None,
                    },
                    "ohlc": {"D1": [], "H4": [], "H1": []},
                }
            )
        )

        response = integration_client.get("/api/runs/XAUUSD/2026/07/26/result-10")

        assert response.status_code == 200
        data = response.json()
        assert data["schema_version"] == "2"
        assert data["deterministic_facts"]["validation_status"] == "VALID"
        assert data["deterministic_facts"]["operational"] is True
        assert data["decision"]["action"] == "buy_setup"
        assert "review" not in data

    def test_returns_404_for_missing(self, integration_client):
        resp = integration_client.get("/api/runs/XAUUSD/2026/07/26/result-99-99")

        assert resp.status_code == 404

    def test_returns_404_for_wrong_symbol(self, integration_client):
        resp = integration_client.get("/api/runs/EURUSD/2026/07/26/result-08")

        assert resp.status_code == 404
