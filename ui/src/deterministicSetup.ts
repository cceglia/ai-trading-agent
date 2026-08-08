import type {
  AnalysisEnvelope,
  RunSummary,
  SLTPOverlay,
  V2Action,
} from "./types";

/** True when the result is a normalised legacy (v1 review-based) envelope. */
export function isLegacyRun(result: AnalysisEnvelope | null): boolean {
  return result?.schema_version === "legacy";
}

/**
 * Summary-level legacy marker (FR-034 / INV-013). The summary contract has no
 * schema field, but the server legacy adapter always emits UNKNOWN validation
 * and non-operational state, and the v2 writer never emits UNKNOWN — so this
 * pair reliably identifies a legacy summary.
 */
export function isLegacySummary(run: RunSummary): boolean {
  return (
    run.validation_status === "UNKNOWN" && run.operational === false
  );
}

/**
 * Deterministic operational gate (INV-013): a run is operational only when
 * the facts say so AND validation is VALID. Legacy runs are UNKNOWN and
 * never operational.
 */
export function isOperationalRun(result: AnalysisEnvelope | null): boolean {
  if (!result) return false;
  const facts = result.deterministic_facts;
  return facts.operational === true && facts.validation_status === "VALID";
}

/** Summary-level operational gate (no nested envelope available). */
export function isOperationalSummary(run: RunSummary): boolean {
  return run.operational === true && run.validation_status === "VALID";
}

/**
 * True when the deterministic entry plan carries every price and the
 * estimated reward-to-risk. Missing optional facts render as N/A, never
 * guessed — an incomplete plan is not complete just because prose exists.
 */
export function hasCompleteDeterministicSetup(
  result: AnalysisEnvelope | null
): boolean {
  if (!result) return false;
  const plan = result.deterministic_facts.entry_plan;
  return (
    plan.entry_price != null &&
    plan.invalidation_price != null &&
    plan.target_price != null &&
    plan.estimated_reward_risk != null
  );
}

/**
 * A run is actionable only when it is operational and the deterministic
 * execution policy is actionable. Never infers action from explanation text.
 */
export function isActionableRun(result: AnalysisEnvelope | null): boolean {
  if (!result) return false;
  return (
    isOperationalRun(result) &&
    result.deterministic_facts.policy.actionable === true
  );
}

/** Chart overlay projected from the deterministic entry plan. */
export function entryPlanOverlay(
  result: AnalysisEnvelope | null
): SLTPOverlay {
  const plan = result?.deterministic_facts.entry_plan;
  if (!plan) {
    return { entry_price: null, stop_loss: null, take_profit: null };
  }
  return {
    entry_price: plan.entry_price ?? null,
    stop_loss: plan.invalidation_price ?? null,
    take_profit: plan.target_price ?? null,
  };
}

/**
 * Canonical action label. Only ``buy_setup``/``sell_setup``/``no_trade`` are
 * valid; anything else (including removed ``wait_for_setup``) renders as
 * unknown rather than introducing a state the contract does not define.
 */
export function actionLabel(action: string): string {
  switch (action as V2Action) {
    case "buy_setup":
      return "Buy setup";
    case "sell_setup":
      return "Sell setup";
    case "no_trade":
      return "No trade";
    default:
      return "Unknown";
  }
}

/**
 * Display percentage for the confidence value. The server passes confidence
 * through without rescaling: v2 carries the deterministic 0–100 score while
 * legacy carries a 0–1 interpretive value. `isLegacy` disambiguates the two
 * scales (a v2 deterministic score of exactly 1 is 1%, not 100%), derived
 * from the validation/schema context of the run being displayed.
 */
export function formatConfidencePct(
  confidence: number | null,
  isLegacy = false
): string {
  if (confidence == null) return "N/A";
  const value =
    isLegacy && confidence > 0 && confidence <= 1 ? confidence * 100 : confidence;
  return `${Math.round(value)}%`;
}
