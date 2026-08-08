import { describe, expect, it } from "vitest";
import {
  actionLabel,
  entryPlanOverlay,
  formatConfidencePct,
  hasCompleteDeterministicSetup,
  isActionableRun,
  isLegacyRun,
  isLegacySummary,
  isOperationalRun,
  isOperationalSummary,
} from "../deterministicSetup";
import {
  legacyEnvelope,
  legacySummary,
  v2DegradedEnvelope,
  v2InvalidEnvelope,
  v2NoSetupEnvelope,
  v2SuccessEnvelope,
  v2SuccessSummary,
} from "./fixtures";
import type { AnalysisEnvelope } from "../types";

describe("isOperationalRun", () => {
  it("is true only for operational + VALID v2 runs", () => {
    expect(isOperationalRun(v2SuccessEnvelope)).toBe(true);
    expect(isOperationalRun(v2DegradedEnvelope)).toBe(true);
    expect(isOperationalRun(v2InvalidEnvelope)).toBe(false);
    expect(isOperationalRun(v2NoSetupEnvelope)).toBe(false);
    expect(isOperationalRun(legacyEnvelope)).toBe(false);
    expect(isOperationalRun(null)).toBe(false);
  });
});

describe("isOperationalSummary", () => {
  it("is true only for operational + VALID summaries", () => {
    expect(isOperationalSummary(v2SuccessSummary)).toBe(true);
    expect(isOperationalSummary(legacySummary)).toBe(false);
  });
});

describe("isLegacyRun", () => {
  it("flags only schema_version=legacy", () => {
    expect(isLegacyRun(legacyEnvelope)).toBe(true);
    expect(isLegacyRun(v2SuccessEnvelope)).toBe(false);
    expect(isLegacyRun(null)).toBe(false);
  });
});

describe("isLegacySummary", () => {
  it("flags UNKNOWN + non-operational summaries as legacy", () => {
    expect(isLegacySummary(legacySummary)).toBe(true);
    expect(isLegacySummary(v2SuccessSummary)).toBe(false);
  });

  it("does not flag a v2 invalid summary as legacy", () => {
    expect(
      isLegacySummary({
        ...v2SuccessSummary,
        validation_status: "INVALID",
        operational: false,
      })
    ).toBe(false);
  });
});

describe("hasCompleteDeterministicSetup", () => {
  it("requires every deterministic entry-plan price", () => {
    expect(hasCompleteDeterministicSetup(v2SuccessEnvelope)).toBe(true);
    expect(hasCompleteDeterministicSetup(v2DegradedEnvelope)).toBe(true);
    expect(hasCompleteDeterministicSetup(v2InvalidEnvelope)).toBe(false);
    expect(hasCompleteDeterministicSetup(v2NoSetupEnvelope)).toBe(false);
    expect(hasCompleteDeterministicSetup(legacyEnvelope)).toBe(false);
    expect(hasCompleteDeterministicSetup(null)).toBe(false);
  });
});

describe("isActionableRun", () => {
  it("requires operational + VALID + policy actionable", () => {
    expect(isActionableRun(v2SuccessEnvelope)).toBe(true);
    expect(isActionableRun(v2DegradedEnvelope)).toBe(true);
    expect(isActionableRun(v2InvalidEnvelope)).toBe(false);
    expect(isActionableRun(v2NoSetupEnvelope)).toBe(false);
    expect(isActionableRun(legacyEnvelope)).toBe(false);
    expect(isActionableRun(null)).toBe(false);
  });
});

describe("actionLabel", () => {
  it("maps only the canonical v2 actions and never invents states", () => {
    expect(actionLabel("buy_setup")).toBe("Buy setup");
    expect(actionLabel("sell_setup")).toBe("Sell setup");
    expect(actionLabel("no_trade")).toBe("No trade");
    expect(actionLabel("wait_for_setup")).toBe("Unknown");
    expect(actionLabel("unknown")).toBe("Unknown");
    expect(actionLabel("")).toBe("Unknown");
  });
});

describe("formatConfidencePct", () => {
  it("keeps the v2 0-100 deterministic scale (including a score of 1)", () => {
    expect(formatConfidencePct(72)).toBe("72%");
    expect(formatConfidencePct(1)).toBe("1%");
    expect(formatConfidencePct(0)).toBe("0%");
    expect(formatConfidencePct(null)).toBe("N/A");
  });

  it("normalises the legacy 0-1 scale only when flagged as legacy", () => {
    expect(formatConfidencePct(0.85, true)).toBe("85%");
    expect(formatConfidencePct(1, true)).toBe("100%");
    expect(formatConfidencePct(0, true)).toBe("0%");
  });
});

describe("entryPlanOverlay", () => {
  it("projects the deterministic entry plan onto the chart overlay", () => {
    const overlay = entryPlanOverlay(v2SuccessEnvelope);
    expect(overlay.entry_price).toBe(2398.5);
    expect(overlay.stop_loss).toBe(2378.0);
    expect(overlay.take_profit).toBe(2440.0);
  });

  it("returns a null-safe overlay for empty/legacy plans", () => {
    expect(entryPlanOverlay(legacyEnvelope)).toEqual({
      entry_price: null,
      stop_loss: null,
      take_profit: null,
    });
    expect(entryPlanOverlay(null)).toEqual({
      entry_price: null,
      stop_loss: null,
      take_profit: null,
    });
  });

  it("normalises the server legacy entry_plan {} (absent fields) to null", () => {
    const serverLegacyEnvelope: AnalysisEnvelope = {
      ...legacyEnvelope,
      deterministic_facts: {
        ...legacyEnvelope.deterministic_facts,
        entry_plan: {},
      },
    };
    const overlay = entryPlanOverlay(serverLegacyEnvelope);
    expect(overlay).toEqual({
      entry_price: null,
      stop_loss: null,
      take_profit: null,
    });
    expect(hasCompleteDeterministicSetup(serverLegacyEnvelope)).toBe(false);
  });
});
