"""Shared fixtures for server tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.models import RunSummary
from src.runner import RunService
from src.scanner import ResultScanner


@pytest.fixture
def sample_run_summary() -> RunSummary:
    """Sample RunSummary matching the Python model shape."""
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
def sample_full_result() -> dict:
    """Sample FullResult matching AnalysisResult.model_dump(mode='json') shape."""
    return {
        "symbol": "XAUUSD",
        "version": "1.0",
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
            "approved": True,
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
    }


@pytest.fixture
def mock_data_dir(tmp_path: Path, sample_full_result: dict) -> Path:
    """Create a temporary data directory with fixture JSON files."""
    fpath = tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08-30.json"
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
