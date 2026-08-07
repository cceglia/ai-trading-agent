"""Final decision output assembler.

This module implements :class:`FinalOutputAssembler` as specified in
Section 14 of the multi-timeframe pipeline redesign plan.  The assembler
collects structured state from every stage of the pipeline and produces a
single :class:`~src.output.result_models.AnalysisResult` suitable for
serialisation to JSON and consumption by the web dashboard.

Responsibility boundaries
-------------------------

*Deterministic (authoritative)* — values computed by the deterministic
grading / execution-policy / risk-policy / enforcement engines.  These
always override any conflicting LLM-produced value.

*Interpretive (LLM advisory)* — reasoning strings produced by the synthesizer.
  These fill the ``decision`` field, while deterministic enforcement remains
  authoritative for the final action.

SOLID compliance
----------------

* **SRP** — single responsibility: map pipeline states to a unified output.
* **OCP** — new output fields can be added to
  :class:`~src.output.result_models.AnalysisResult` without modifying the
  assembler's mapping logic.
* **ISP** — focuses solely on output assembly; no grading, no enforcement,
  no policy evaluation.
* **DIP** — depends only on model abstractions (engine state models,
  decision models, output models).
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from src.analysis.market_structure_engine.deterministic_validator import DeterministicValidation
from src.analysis.market_structure_engine.models import (
    DeterministicSetupState,
    ExecutionPolicyState,
    FinalDecisionState,
    RiskPolicyState,
)
from src.decision.models import DecisionOutput
from src.output.result_models import AnalysisResult, SLTPOverlay

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Assembler
# ---------------------------------------------------------------------------


class FinalOutputAssembler:
    """Assembles a single :class:`AnalysisResult` from all pipeline states.

    The assembler is a stateless mapper — it never modifies the input
    objects and produces a new :class:`AnalysisResult` on every call.

    Example usage::

        assembler = FinalOutputAssembler()
        result = assembler.assemble(
            setup=setup_state,
            policy=execution_policy,
            risk=risk_policy,
            decision=llm_decision,
            enforcement=final_state,
        )
        # Override metadata fields as needed:
        result.run_id = "..."
        result.started_at = ...
        result.completed_at = ...
    """

    def assemble(
        self,
        *,
        setup: DeterministicSetupState,
        policy: ExecutionPolicyState,
        risk: RiskPolicyState,
        decision: DecisionOutput,
        enforcement: FinalDecisionState,
        validation: DeterministicValidation | None = None,
    ) -> AnalysisResult:
        """Map all pipeline states into a unified :class:`AnalysisResult`.

        Parameters
        ----------
        setup:
            Classified setup from the deterministic grading stage.
        policy:
            Execution policy derived from the setup and blockers.
        risk:
            Risk policy derived from the setup grade.
        decision:
            LLM decision output (action + reasoning).
        enforcement:
            Final decision state after the enforcement gate.

        Returns
        -------
        AnalysisResult
            Fully populated result.  The caller is responsible for setting
            the execution-metadata fields (``run_id``, ``started_at``,
            ``completed_at``, ``status``) after this call.
        """
        # ── Derive symbol from the LLM decision ────────────────────────
        symbol = decision.symbol

        # ── SL/TP overlay (deterministic prices — authoritative) ──────
        # ``invalidation_price`` is the stop-loss; ``target_price`` is
        # the take-profit level computed by the entry calculator.
        sl_tp_overlay = SLTPOverlay(
            entry_price=setup.entry_price,
            stop_loss=setup.invalidation_price,
            take_profit=setup.target_price,
        )

        # ── Decision output ───────────────────────────────────────────
        # Action comes from the enforcement gate (deterministic).
        # Reasoning comes from the LLM (interpretive).
        final_decision = DecisionOutput(
            symbol=symbol,
            action=enforcement.final_action,
            reasoning=decision.reasoning,
            advisory_levels=decision.advisory_levels,
        )

        # ── Status inference ──────────────────────────────────────────
        # If there are enforcement violations, mark as partial.
        # The caller may override this with "error" or "success".
        status: str = (
            "partial"
            if enforcement.enforcement_violations
            or (validation is not None and not validation.valid)
            else "success"
        )

        # ── Serialise blockers and violations to dicts ────────────────
        execution_blockers: list[dict[str, Any]] = [
            b.model_dump(mode="json") for b in policy.execution_blockers
        ]
        enforcement_violations_list: list[dict[str, Any]] = [
            v.model_dump(mode="json") for v in enforcement.enforcement_violations
        ]

        # ── Assemble ──────────────────────────────────────────────────
        analysis_result = AnalysisResult(
            # Metadata (caller should override these)
            symbol=symbol,
            run_id="",
            started_at=datetime.now(),
            completed_at=datetime.now(),
            status=status,
            # Sub-models
            decision=final_decision,
            sl_tp_overlay=sl_tp_overlay,
            advisory_levels=decision.advisory_levels,
            # Deterministic setup (authoritative)
            setup_grade=setup.setup_grade.value if setup.setup_grade is not None else None,
            setup_classification_status=setup.setup_classification_status.value,
            setup_lifecycle_status=setup.setup_lifecycle_status.value,
            trade_direction=setup.trade_direction.value,
            rejection_codes=[rc.value for rc in setup.rejection_codes],
            estimated_reward_risk=setup.estimated_reward_risk,
            order_type=setup.entry_type.value if setup.entry_type is not None else None,
            deterministic_setup_complete=setup.deterministic_plan_complete,
            # Risk policy
            risk_multiplier=risk.grade_risk_multiplier,
            final_risk_percentage=risk.final_risk_percentage,
            # Execution policy
            execution_status=policy.execution_status.value,
            execution_blockers=execution_blockers,
            # Enforcement
            final_action=enforcement.final_action.value,
            enforcement_violations=enforcement_violations_list,
            validation_status=validation.validation_status if validation else "INVALID",
            validation_errors=list(validation.validation_errors)
            if validation
            else ["validation unavailable"],
            rr=validation.rr if validation else setup.estimated_reward_risk,
            calculated_rr=validation.calculated_rr if validation else setup.estimated_reward_risk,
            minimum_required_rr=validation.minimum_required_rr if validation else 2.0,
            rr_pass=validation.rr_pass if validation else False,
            deterministic_blockers=list(validation.deterministic_blockers)
            if validation
            else execution_blockers,
            reason_codes=list(validation.reason_codes)
            if validation
            else list(setup.rejection_codes),
            setup_status=validation.setup_status if validation else "INVALID",
            direction=validation.direction if validation else "NONE",
            entry_authorized=False,
        )

        logger.debug(
            "Assembled AnalysisResult for %s — action=%s status=%s",
            symbol,
            enforcement.final_action.value,
            status,
        )
        return analysis_result
