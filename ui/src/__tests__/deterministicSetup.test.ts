import { describe, expect, it } from "vitest";
import { hasCompleteDeterministicSetup } from "../deterministicSetup";
import type { FullResult } from "../types";

const completeResult: FullResult = {
  version: "1",
  symbol: "EURUSD",
  run_id: "run-1",
  started_at: "2026-01-01T00:00:00Z",
  completed_at: "2026-01-01T00:01:00Z",
  status: "success",
  errors: [],
  fatal_error: null,
  estimated_reward_risk: 2,
  order_type: "LIMIT",
  deterministic_setup_complete: true,
  rejection_codes: [],
  sl_tp_overlay: { entry_price: 1.1, stop_loss: 1.09, take_profit: 1.12 },
};

describe("hasCompleteDeterministicSetup", () => {
  it("requires the completion flag and every deterministic value", () => {
    expect(hasCompleteDeterministicSetup(completeResult)).toBe(true);
    expect(
      hasCompleteDeterministicSetup({
        ...completeResult,
        sl_tp_overlay: { ...completeResult.sl_tp_overlay!, take_profit: null },
      })
    ).toBe(false);
  });

  it("treats a missing result as incomplete", () => {
    expect(hasCompleteDeterministicSetup(null)).toBe(false);
  });
});
