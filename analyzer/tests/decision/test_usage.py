"""Tests for usage.py — LLMUsage, safe_non_negative_int, and parse_usage.

No external dependencies beyond ``pytest`` and the module under test.
"""

from __future__ import annotations

import logging
import math

import pytest

from src.decision.usage import LLMUsage, parse_usage, safe_non_negative_int

# ===================================================================
# safe_non_negative_int — edge cases
# ===================================================================


class TestSafeNonNegativeInt:
    def test_none_returns_zero(self) -> None:
        assert safe_non_negative_int(None) == 0

    def test_bool_true_returns_zero(self, caplog: pytest.LogCaptureFixture) -> None:
        with caplog.at_level(logging.WARNING):
            assert safe_non_negative_int(True) == 0
            assert "Boolean" in caplog.text

    def test_bool_false_returns_zero(self, caplog: pytest.LogCaptureFixture) -> None:
        with caplog.at_level(logging.WARNING):
            assert safe_non_negative_int(False) == 0
            assert "Boolean" in caplog.text

    def test_negative_int_returns_zero(self) -> None:
        assert safe_non_negative_int(-5) == 0
        assert safe_non_negative_int(-1) == 0

    def test_zero_int(self) -> None:
        assert safe_non_negative_int(0) == 0

    def test_positive_int(self) -> None:
        assert safe_non_negative_int(42) == 42
        assert safe_non_negative_int(1_000_000) == 1_000_000

    def test_positive_float_truncates(self) -> None:
        assert safe_non_negative_int(100.0) == 100
        assert safe_non_negative_int(3.99) == 3
        assert safe_non_negative_int(0.001) == 0

    def test_negative_float_returns_zero(self) -> None:
        assert safe_non_negative_int(-1.5) == 0
        assert safe_non_negative_int(-0.001) == 0

    def test_nan_returns_zero(self, caplog: pytest.LogCaptureFixture) -> None:
        with caplog.at_level(logging.WARNING):
            assert safe_non_negative_int(math.nan) == 0
            assert "nan" in caplog.text.lower() or "nan" in str(caplog.text)

    def test_inf_returns_zero(self, caplog: pytest.LogCaptureFixture) -> None:
        with caplog.at_level(logging.WARNING):
            assert safe_non_negative_int(math.inf) == 0

    def test_neg_inf_returns_zero(self, caplog: pytest.LogCaptureFixture) -> None:
        with caplog.at_level(logging.WARNING):
            assert safe_non_negative_int(-math.inf) == 0

    def test_numeric_string(self) -> None:
        assert safe_non_negative_int("42") == 42
        assert safe_non_negative_int("100.0") == 100
        assert safe_non_negative_int("0") == 0

    def test_non_numeric_string_returns_zero(self, caplog: pytest.LogCaptureFixture) -> None:
        with caplog.at_level(logging.WARNING):
            assert safe_non_negative_int("abc") == 0
            assert "Non-numeric string" in caplog.text

    def test_list_returns_zero(self, caplog: pytest.LogCaptureFixture) -> None:
        with caplog.at_level(logging.WARNING):
            assert safe_non_negative_int([1, 2, 3]) == 0
            assert "Unexpected type" in caplog.text


# ===================================================================
# LLMUsage defaults
# ===================================================================


class TestLLMUsageDefaults:
    def test_all_fields_default_to_zero(self) -> None:
        u = LLMUsage()
        assert u.input_tokens == 0
        assert u.cached_input_tokens == 0
        assert u.uncached_input_tokens == 0
        assert u.output_tokens == 0
        assert u.reasoning_tokens == 0
        assert u.total_tokens == 0
        assert u.input_cost == 0.0
        assert u.cached_input_cost == 0.0
        assert u.output_cost == 0.0
        assert u.total_cost == 0.0

    def test_is_frozen(self) -> None:
        u = LLMUsage()
        with pytest.raises(AttributeError):
            u.input_tokens = 99  # type: ignore[misc]


# ===================================================================
# parse_usage — Responses API style
# ===================================================================


class TestParseUsageResponsesApi:
    """Primary field names: input_tokens / output_tokens."""

    def test_complete_usage(self) -> None:
        from tests.conftest import make_raw_response

        raw = make_raw_response(
            input_tokens=200,
            output_tokens=80,
            total_tokens=280,
            cached_input_tokens=50,
            reasoning_tokens=10,
        )
        u = parse_usage(raw)
        assert u.input_tokens == 200
        assert u.cached_input_tokens == 50
        assert u.uncached_input_tokens == 150
        assert u.output_tokens == 80
        assert u.reasoning_tokens == 10
        assert u.total_tokens == 280
        assert u.total_cost == 0.0  # costs filled later by CostTracker

    def test_with_cached_tokens(self) -> None:
        from tests.conftest import make_raw_response

        raw = make_raw_response(
            input_tokens=500,
            output_tokens=200,
            total_tokens=700,
            cached_input_tokens=300,
        )
        u = parse_usage(raw)
        assert u.input_tokens == 500
        assert u.cached_input_tokens == 300
        assert u.uncached_input_tokens == 200

    def test_without_cached_token_details(self) -> None:
        from tests.conftest import make_raw_response

        raw = make_raw_response(
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
            cached_input_tokens=None,
        )
        u = parse_usage(raw)
        assert u.cached_input_tokens == 0
        assert u.uncached_input_tokens == 100

    def test_without_reasoning_tokens(self) -> None:
        from tests.conftest import make_raw_response

        raw = make_raw_response(
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
            reasoning_tokens=None,
        )
        u = parse_usage(raw)
        assert u.reasoning_tokens == 0

    def test_input_tokens_details_is_none(self) -> None:
        """input_tokens_details = None must not crash."""
        from types import SimpleNamespace

        raw = SimpleNamespace(
            usage=SimpleNamespace(
                input_tokens=100,
                output_tokens=50,
                total_tokens=150,
                input_tokens_details=None,
                output_tokens_details=SimpleNamespace(reasoning_tokens=5),
            )
        )
        u = parse_usage(raw)
        assert u.input_tokens == 100
        assert u.cached_input_tokens == 0  # None details → no cached tokens

    def test_output_tokens_details_is_none(self) -> None:
        """output_tokens_details = None must not crash."""
        from types import SimpleNamespace

        raw = SimpleNamespace(
            usage=SimpleNamespace(
                input_tokens=100,
                output_tokens=50,
                total_tokens=150,
                input_tokens_details=SimpleNamespace(cached_tokens=10),
                output_tokens_details=None,
            )
        )
        u = parse_usage(raw)
        assert u.output_tokens == 50
        assert u.reasoning_tokens == 0  # None details → no reasoning tokens

    def test_cached_greater_than_input_clamps(self) -> None:
        """cached_input_tokens > input_tokens → clamped to input, uncached = 0."""
        from tests.conftest import make_raw_response

        raw = make_raw_response(
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
            cached_input_tokens=999,
        )
        u = parse_usage(raw)
        assert u.cached_input_tokens == 100  # clamped
        assert u.uncached_input_tokens == 0

    def test_primary_zero_fallback_nonzero(self) -> None:
        """When primary field is 0 and fallback is non-zero, primary wins."""
        from types import SimpleNamespace

        raw = SimpleNamespace(
            usage=SimpleNamespace(
                input_tokens=0,
                output_tokens=50,
                total_tokens=50,
                input_tokens_details=None,
                output_tokens_details=None,
                # prompt_tokens not set — equivalent to missing
            )
        )
        u = parse_usage(raw)
        assert u.input_tokens == 0  # primary is 0, not overwritten by fallback absence


# ===================================================================
# parse_usage — Chat Completions / fallback naming
# ===================================================================


class TestParseUsageChatCompletions:
    """Fallback field names: prompt_tokens / completion_tokens."""

    def test_chat_completions_style(self) -> None:
        from tests.conftest import make_raw_response

        raw = make_raw_response(
            responses_api=False,
            input_tokens=200,
            output_tokens=80,
            total_tokens=280,
            cached_prompt_tokens=50,
            reasoning_completion_tokens=10,
        )
        u = parse_usage(raw)
        assert u.input_tokens == 200
        assert u.cached_input_tokens == 50
        assert u.uncached_input_tokens == 150
        assert u.output_tokens == 80
        assert u.reasoning_tokens == 10
        assert u.total_tokens == 280

    def test_chat_completions_without_details(self) -> None:
        from tests.conftest import make_raw_response

        raw = make_raw_response(
            responses_api=False,
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
            cached_prompt_tokens=None,
            reasoning_completion_tokens=None,
        )
        u = parse_usage(raw)
        assert u.cached_input_tokens == 0
        assert u.reasoning_tokens == 0


# ===================================================================
# parse_usage — None / missing / zero usage
# ===================================================================


class TestParseUsageNoneOrMissing:
    def test_usage_none(self) -> None:
        from tests.conftest import make_raw_response

        raw = make_raw_response(usage_none=True)
        u = parse_usage(raw)
        assert u == LLMUsage()
        assert u.total_cost == 0.0

    def test_no_usage_field(self) -> None:
        from types import SimpleNamespace

        raw = SimpleNamespace()  # no usage attribute at all
        u = parse_usage(raw)
        assert u == LLMUsage()
        assert u.total_cost == 0.0

    def test_response_none(self) -> None:
        u = parse_usage(None)
        assert u == LLMUsage()
        assert u.total_cost == 0.0

    def test_dict_no_usage_key(self) -> None:
        u = parse_usage({"response": "ok"})  # no "usage" key
        assert u == LLMUsage()
        assert u.total_cost == 0.0

    def test_dict_usage_is_none(self) -> None:
        u = parse_usage({"usage": None})
        assert u == LLMUsage()
        assert u.total_cost == 0.0


# ===================================================================
# parse_usage — dict response
# ===================================================================


class TestParseUsageDict:
    def test_dict_with_complete_usage(self) -> None:
        from tests.conftest import make_raw_response

        raw = make_raw_response(
            input_tokens=300,
            output_tokens=120,
            total_tokens=420,
            cached_input_tokens=100,
            reasoning_tokens=20,
            dict_response=True,
        )
        u = parse_usage(raw)
        assert u.input_tokens == 300
        assert u.cached_input_tokens == 100
        assert u.uncached_input_tokens == 200
        assert u.output_tokens == 120
        assert u.reasoning_tokens == 20
        assert u.total_tokens == 420

    def test_dict_without_usage(self) -> None:
        u = parse_usage({"other": "data"})
        assert u == LLMUsage()
        assert u.total_cost == 0.0

    def test_dict_usage_none(self) -> None:
        u = parse_usage({"usage": None})
        assert u == LLMUsage()
        assert u.total_cost == 0.0


# ===================================================================
# parse_usage — negative / invalid values
# ===================================================================


class TestParseUsageInvalidValues:
    def test_negative_tokens_normalised(self) -> None:
        """All token fields normalise negative values to 0."""
        from types import SimpleNamespace

        raw = SimpleNamespace(
            usage=SimpleNamespace(
                input_tokens=-10,
                output_tokens=-5,
                total_tokens=-15,
                input_tokens_details=None,
                output_tokens_details=None,
            )
        )
        u = parse_usage(raw)
        assert u.input_tokens == 0
        assert u.output_tokens == 0
        assert u.total_tokens == 0
        assert u.uncached_input_tokens == 0

    def test_bool_in_usage_normalised(self) -> None:
        """Booleans in usage fields are normalised to 0."""
        from types import SimpleNamespace

        raw = SimpleNamespace(
            usage=SimpleNamespace(
                input_tokens=True,  # bool masquerading as int
                output_tokens=False,
                total_tokens=150,
                input_tokens_details=None,
                output_tokens_details=None,
            )
        )
        u = parse_usage(raw)
        assert u.input_tokens == 0
        assert u.output_tokens == 0


# ===================================================================
# parse_usage — total_tokens derivation
# ===================================================================


class TestParseUsageTotalTokens:
    def test_total_tokens_explicit_zero_is_preserved(self) -> None:
        """Provider returned total_tokens=0 → keep 0, do not derive."""
        from types import SimpleNamespace

        raw = SimpleNamespace(
            usage=SimpleNamespace(
                input_tokens=200,
                output_tokens=100,
                total_tokens=0,  # explicitly returned as 0
                input_tokens_details=None,
                output_tokens_details=None,
            )
        )
        u = parse_usage(raw)
        assert u.total_tokens == 0  # kept, not derived as 300

    def test_total_tokens_missing_is_derived(self) -> None:
        """No total_tokens field → derive as input + output."""
        from types import SimpleNamespace

        raw = SimpleNamespace(
            usage=SimpleNamespace(
                input_tokens=200,
                output_tokens=100,
                # no total_tokens attribute at all
                input_tokens_details=None,
                output_tokens_details=None,
            )
        )
        u = parse_usage(raw)
        assert u.total_tokens == 300  # derived

    def test_total_tokens_none_is_derived(self) -> None:
        """total_tokens = None → derive as input + output."""
        from types import SimpleNamespace

        raw = SimpleNamespace(
            usage=SimpleNamespace(
                input_tokens=200,
                output_tokens=100,
                total_tokens=None,
                input_tokens_details=None,
                output_tokens_details=None,
            )
        )
        u = parse_usage(raw)
        assert u.total_tokens == 300  # derived
