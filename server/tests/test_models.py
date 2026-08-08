"""Tests for the typed v2 request/batch models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.models import BatchResponse, RunRequest, SymbolError


class TestRunRequest:
    """POST /api/run request contract (FR-039 / DEC-014)."""

    def test_accepts_symbols_and_optional_ids(self):
        req = RunRequest(symbols=["XAUUSD"], model="gpt-4o", provider_id="local")
        assert req.symbols == ["XAUUSD"]
        assert req.model == "gpt-4o"
        assert req.provider_id == "local"

    def test_accepts_minimal_request(self):
        req = RunRequest(symbols=["XAUUSD"])
        assert req.model is None
        assert req.provider_id is None

    def test_rejects_free_form_base_url(self):
        """A free-form ``base_url`` must be rejected (FR-039)."""
        with pytest.raises(ValidationError):
            RunRequest(symbols=["XAUUSD"], base_url="http://evil.example")

    def test_rejects_unknown_extra_fields(self):
        """Unknown fields are forbidden — the contract is strict."""
        with pytest.raises(ValidationError):
            RunRequest(symbols=["XAUUSD"], api_key="secret")

    @pytest.mark.parametrize(
        "bad_model",
        [
            "x" * 101,  # over length bound
            "with space",
            "!@#$%",
            "",  # empty after strip
            "   ",  # whitespace only
        ],
    )
    def test_rejects_unbounded_or_invalid_model(self, bad_model):
        """NFR-004: model is bounded in length and character format."""
        with pytest.raises(ValidationError):
            RunRequest(symbols=["XAUUSD"], model=bad_model)

    def test_accepts_model_with_valid_special_chars(self):
        req = RunRequest(symbols=["XAUUSD"], model="local/llama3:8b-v1.5")
        assert req.model == "local/llama3:8b-v1.5"

    def test_accepts_none_model(self):
        req = RunRequest(symbols=["XAUUSD"], model=None)
        assert req.model is None


class TestSymbolError:
    """Per-symbol error envelope (§12.3)."""

    def test_fields(self):
        err = SymbolError(code="SYMBOL_TIMEOUT", message="analysis timed out")
        assert err.code == "SYMBOL_TIMEOUT"
        assert err.message == "analysis timed out"


class TestBatchResponse:
    """Batch envelope contract (§12.3, FR-033)."""

    def test_success_envelope(self):
        resp = BatchResponse(
            status="success",
            results={"XAUUSD": {"symbol": "XAUUSD"}},
            errors={},
        )
        assert resp.status == "success"
        assert resp.results["XAUUSD"]["symbol"] == "XAUUSD"

    def test_partial_envelope(self):
        resp = BatchResponse(
            status="partial",
            results={"XAUUSD": {"symbol": "XAUUSD"}},
            errors={
                "EURUSD": SymbolError(code="SYMBOL_NO_RESULT", message="no result")
            },
        )
        assert resp.status == "partial"
        assert resp.errors["EURUSD"].code == "SYMBOL_NO_RESULT"

    def test_rejects_unknown_status(self):
        with pytest.raises(ValidationError):
            BatchResponse(status="maybe", results={}, errors={})
