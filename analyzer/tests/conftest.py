from types import SimpleNamespace

import pytest

from src.decision.models import (
    BiasLevel,
    DecisionAction,
    DecisionOutput,
    MarketContextSummary,
    ReviewVerdict,
)


@pytest.fixture(autouse=True)
def reset_candle_cache_settings():
    """Reset the _settings sentinel in candle_cache before each test.

    Tests use monkeypatch to set env vars (TRADING_D1_CLOSE_TIME, etc.)
    and expect _get_settings() to pick up those changes. Without resetting
    the module-level sentinel, the cached Settings instance from a prior
    test would shadow monkeypatched env vars.
    """
    from src.analysis.candle_cache import reload_settings

    reload_settings()
    yield
    reload_settings()


@pytest.fixture(autouse=True)
def reset_synthesizer_cache_settings():
    """Reset the _settings sentinel in synthesizer_cache before each test.

    Mirrors ``reset_candle_cache_settings`` above. Tests that monkeypatch
    env vars (TRADING_ANALYSIS_CACHE_DIR, TRADING_SYNTHESIZER_CACHE_ENABLED)
    need the sentinel cleared so that ``_get_settings()`` picks up changes.
    """
    import src.decision.synthesizer_cache

    src.decision.synthesizer_cache._settings = None
    yield
    src.decision.synthesizer_cache._settings = None


@pytest.fixture
def sample_market_context():
    return MarketContextSummary(
        symbol="EURUSD",
        bias=BiasLevel.BULLISH,
        confidence=75.0,
        reasoning="Primary structure bullish with recent BOS",
        key_levels=["1.0850", "1.0900"],
        structural_events=["Bullish BOS at 1.0850"],
    )


@pytest.fixture
def sample_decision():
    return DecisionOutput(
        symbol="EURUSD",
        action=DecisionAction.BUY_SETUP,
        entry_price=1.0875,
        stop_loss=1.0825,
        take_profit=1.0975,
        reasoning="Bullish structure with good R/R",
        risk_reward_ratio=2.0,
        entry_authorized=False,
    )


@pytest.fixture
def sample_review():
    return ReviewVerdict(
        approved=True,
        reasoning="All criteria met",
        concerns=[],
        suggested_improvements=None,
    )


# ---------------------------------------------------------------------------
# Response factory for agent and parser tests
# ---------------------------------------------------------------------------


def make_raw_response(
    *,
    # Responses API style (primary paths)
    input_tokens: int = 100,
    output_tokens: int = 50,
    total_tokens: int = 150,
    cached_input_tokens: int | None = None,
    reasoning_tokens: int | None = None,
    # Chat Completions style (fallback paths — explicit override)
    prompt_tokens: int | None = None,
    completion_tokens: int | None = None,
    cached_prompt_tokens: int | None = None,
    reasoning_completion_tokens: int | None = None,
    # Controls
    responses_api: bool = True,
    usage_none: bool = False,
    dict_response: bool = False,
) -> SimpleNamespace | dict:
    """Build a mock provider response with controlled usage fields.

    The returned object has a ``.usage`` attribute (or a ``"usage"`` key
    when *dict_response* is ``True``).  Defaults to Responses API style.

    Parameters
    ----------
    input_tokens, output_tokens, total_tokens:
        Token counts for the primary (Responses API) naming convention.
    cached_input_tokens:
        Sets ``usage.input_tokens_details.cached_tokens`` (or prompt equivalent).
    reasoning_tokens:
        Sets ``usage.output_tokens_details.reasoning_tokens`` (or completion equivalent).
    prompt_tokens, completion_tokens:
        Explicit overrides for Chat Completions naming.  When *responses_api* is
        ``False`` these default to *input_tokens* / *output_tokens*.
    cached_prompt_tokens, reasoning_completion_tokens:
        Details for Chat Completions naming.
    responses_api:
        If ``True`` (default) builds ``input_tokens`` / ``output_tokens`` style.
        If ``False`` builds ``prompt_tokens`` / ``completion_tokens`` style.
    usage_none:
        If ``True``, sets ``usage = None``.
    dict_response:
        If ``True``, returns plain ``dict`` objects instead of ``SimpleNamespace``.
    """
    if usage_none:
        if dict_response:
            return {}
        return SimpleNamespace(usage=None)

    # Build details sub-objects only when values are provided
    if responses_api:
        details_in = (
            SimpleNamespace(cached_tokens=cached_input_tokens)
            if cached_input_tokens is not None
            else None
        )
        details_out = (
            SimpleNamespace(reasoning_tokens=reasoning_tokens)
            if reasoning_tokens is not None
            else None
        )
        usage_obj = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "input_tokens_details": details_in,
            "output_tokens_details": details_out,
        }
    else:
        pt = prompt_tokens if prompt_tokens is not None else input_tokens
        ct = completion_tokens if completion_tokens is not None else output_tokens
        prompt_details = (
            SimpleNamespace(cached_tokens=cached_prompt_tokens)
            if cached_prompt_tokens is not None
            else None
        )
        completion_details = (
            SimpleNamespace(reasoning_tokens=reasoning_completion_tokens)
            if reasoning_completion_tokens is not None
            else None
        )
        usage_obj = {
            "prompt_tokens": pt,
            "completion_tokens": ct,
            "total_tokens": total_tokens,
            "prompt_tokens_details": prompt_details,
            "completion_tokens_details": completion_details,
        }

    if dict_response:
        return {"usage": usage_obj}

    # Convert dict-of-dicts to nested SimpleNamespace
    return SimpleNamespace(usage=_dict_to_sns(usage_obj))


def _dict_to_sns(d: dict) -> SimpleNamespace:
    """Recursively convert a dict to a SimpleNamespace."""
    result = {}
    for k, v in d.items():
        if isinstance(v, dict):
            result[k] = _dict_to_sns(v)
        elif v is None:
            result[k] = None
        else:
            result[k] = v
    return SimpleNamespace(**result)
