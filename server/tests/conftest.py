"""Shared fixtures for server tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.main import create_app
from src.models import RunSummary
from src.runner import BatchResult, RunService
from src.scanner import ResultScanner


@pytest.fixture
def sample_run_summary() -> RunSummary:
    """Sample RunSummary matching the v2 summary contract."""
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
def sample_full_result() -> dict[str, Any]:
    """Sample legacy (v1 review-based) full result for adapter reads."""
    return {
        "version": "1.0",
        "symbol": "XAUUSD",
        "run_id": "2026-07-26T08:30:00",
        "started_at": "2026-07-26T08:30:00Z",
        "completed_at": "2026-07-26T08:31:15Z",
        "status": "success",
        "errors": [],
        "fatal_error": None,
        "market_context": {
            "symbol": "XAUUSD",
            "bias": "bullish",
            "confidence": 0.85,
            "reasoning": "test",
            "key_levels": [],
            "structural_events": [],
            "calendar_context": "",
            "current_price": 2400.0,
            "current_price_time": "2026-07-26T08:29:00",
        },
        "decision": {
            "symbol": "XAUUSD",
            "action": "buy_setup",
            "entry_price": 2400.0,
            "stop_loss": 2380.0,
            "take_profit": 2440.0,
            "reasoning": "test",
            "risk_reward_ratio": 2.0,
            "entry_authorized": False,
        },
        "review": {
            "status": "APPROVED",
            "reasoning": "Good setup",
            "concerns": [],
            "suggested_improvements": None,
            "risk_management_ok": True,
            "htf_alignment_ok": True,
            "calendar_clear": True,
        },
        "ohlc": {
            "D1": [
                {
                    "time": "2026-07-25T17:00",
                    "open": 2350,
                    "high": 2370,
                    "low": 2345,
                    "close": 2365.5,
                }
            ],
            "H4": [],
            "H1": [],
        },
        "sl_tp_overlay": {
            "entry_price": 2400.0,
            "stop_loss": 2380.0,
            "take_profit": 2440.0,
        },
        "advisory_levels": {
            "entry_price": 2401.0,
            "stop_loss": 2379.0,
            "take_profit": 2441.0,
        },
        "review_advisory_levels": {
            "entry_price": 2402.0,
            "stop_loss": 2378.0,
            "take_profit": 2442.0,
        },
        "estimated_reward_risk": 2.0,
        "order_type": "STOP",
        "deterministic_setup_complete": True,
        "trade_direction": "BULLISH",
    }


@pytest.fixture
def mock_data_dir(tmp_path: Path, sample_full_result: dict) -> Path:
    """Create a temporary data directory with fixture JSON files."""
    fpath = tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08.json"
    fpath.parent.mkdir(parents=True)
    fpath.write_text(json.dumps(sample_full_result))
    return tmp_path


@pytest.fixture
def scanner(mock_data_dir: Path) -> ResultScanner:
    """Create a ResultScanner pointing at the mock data directory."""
    return ResultScanner(mock_data_dir)


@pytest.fixture
def runner() -> RunService:
    """Create a RunService with test defaults."""
    return RunService(
        python_cmd="python3",
        analyzer_dir="/app/analyzer",
        data_dir="/app/data",
        timeout_ms=600_000,
    )


# --- Auth & rate-limit test helpers ---


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
    """Create a test client with mocked scanner and runner (no API key)."""
    with (
        patch("src.main.ResultScanner", return_value=mock_scanner),
        patch("src.main.RunService", return_value=mock_runner),
    ):
        app = create_app()
    return TestClient(app), mock_scanner, mock_runner


@pytest.fixture
def client_with_auth(mock_scanner, mock_runner, monkeypatch):
    """Create a test client with an API key configured.

    The key is set via monkeypatch so ``WebSettings()`` reads it.
    """
    monkeypatch.setenv("TRADING_API_KEY", "test-secret-key")
    from src.main import create_app as _create_app

    with (
        patch("src.main.ResultScanner", return_value=mock_scanner),
        patch("src.main.RunService", return_value=mock_runner),
    ):
        app = _create_app()
    return TestClient(app), mock_scanner, mock_runner
