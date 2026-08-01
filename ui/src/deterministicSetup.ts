import type { FullResult } from "./types";

export function hasCompleteDeterministicSetup(result: FullResult | null): boolean {
  return Boolean(
    result?.deterministic_setup_complete === true &&
      result.order_type != null &&
      result.sl_tp_overlay?.entry_price != null &&
      result.sl_tp_overlay.stop_loss != null &&
      result.sl_tp_overlay.take_profit != null &&
      result.estimated_reward_risk != null
  );
}
