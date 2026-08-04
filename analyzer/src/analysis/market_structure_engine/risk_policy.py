"""Deterministic risk policy creation for the multi-timeframe pipeline.

This module implements ``build_risk_policy()`` as specified in Section 5.2
of the multi-timeframe pipeline redesign plan. It maps a setup grade to
its grade-specific risk multiplier and minimum reward-to-risk threshold,
then constructs an immutable :class:`RiskPolicyState`.

The module is purely deterministic — no LLM calls, no I/O, no external
dependencies beyond the models module for type definitions.

Grade-specific values (Section 7):

    ========================  ===============  =================
    Grade                     Min R/R          Risk Multiplier
    ========================  ===============  =================
    AAA                       2.0              1.0
    AA                        2.0              0.5
    COUNTERTREND              2.5              0.25
    ========================  ===============  =================
"""

from __future__ import annotations

from .models import RiskPolicyState, SetupGrade

# ---------------------------------------------------------------------------
# Grade-specific risk configuration
# ---------------------------------------------------------------------------
# Each entry maps a SetupGrade to (min_reward_risk, risk_multiplier).
# The lookup table is intentionally kept as a plain dict so that adding
# new grades (or overriding defaults) requires zero structural changes.
# ---------------------------------------------------------------------------

GRADE_RISK_TABLE: dict[SetupGrade, tuple[float, float]] = {
    SetupGrade.AAA: (2.0, 1.0),
    SetupGrade.AA: (2.0, 0.5),
    SetupGrade.COUNTERTREND: (2.5, 0.25),
}

# Sensible defaults used when a grade is not present in the table.
_DEFAULT_MIN_RR: float = 1.0
_DEFAULT_RISK_MULTIPLIER: float = 1.0


def build_risk_policy(
    *,
    setup_grade: SetupGrade | None,
    base_risk_percentage: float,
    estimated_reward_risk: float | None,
) -> RiskPolicyState:
    """Create a :class:`RiskPolicyState` from a setup grade and risk config.

    The function looks up the grade-specific risk multiplier and minimum
    reward-to-risk threshold, then populates a frozen ``RiskPolicyState``.
    The computed fields ``final_risk_percentage`` and ``risk_reward_ok`` are
    derived automatically by the model.

    When *setup_grade* is ``None`` (a NO_SETUP — no candidate was generated),
    the multiplier is ``0.0`` so no operational risk is allocated. Fabricating
    a grade here would produce an apparently-valid risk allocation for a setup
    that does not exist (regression: result-23.json, US100.cash).

    Args:
        setup_grade: Quality grade assigned to the setup (AAA, AA,
            COUNTERTREND), or ``None`` when no setup was classified.
        base_risk_percentage: Base risk per trade as a percentage of
            account equity (e.g. 1.0 for 1 %).
        estimated_reward_risk: Deterministically calculated reward-to-risk
            ratio for the setup, or ``None`` when not yet available.

    Returns:
        An immutable ``RiskPolicyState`` with all fields populated.

    Raises:
        ValueError: If *base_risk_percentage* is negative.
    """
    if base_risk_percentage < 0:
        raise ValueError(f"base_risk_percentage must be non-negative, got {base_risk_percentage}")

    if setup_grade is None:
        min_rr, multiplier = _DEFAULT_MIN_RR, 0.0
    else:
        min_rr, multiplier = GRADE_RISK_TABLE.get(
            setup_grade, (_DEFAULT_MIN_RR, _DEFAULT_RISK_MULTIPLIER)
        )

    return RiskPolicyState(
        base_risk_percentage=base_risk_percentage,
        grade_risk_multiplier=multiplier,
        minimum_reward_risk=min_rr,
        estimated_reward_risk=estimated_reward_risk,
    )
