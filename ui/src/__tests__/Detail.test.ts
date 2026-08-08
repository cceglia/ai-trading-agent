// @vitest-environment happy-dom
import { describe, it, expect, vi } from "vitest";
import { mount, flushPromises } from "@vue/test-utils";
import Detail from "../views/Detail.vue";
import {
  legacyEnvelope,
  v2DegradedEnvelope,
  v2InvalidEnvelope,
  v2SuccessEnvelope,
} from "./fixtures";
import type { AnalysisEnvelope } from "../types";

const mocks = vi.hoisted(() => ({
  fetchRunResult: vi.fn(),
}));

vi.mock("vue-router", () => ({
  useRoute: () => ({
    params: {
      symbol: "XAUUSD",
      year: "2026",
      month: "07",
      day: "26",
      file: "result-08",
    },
  }),
  useRouter: () => ({ push: vi.fn() }),
}));

vi.mock("../lib/api", () => ({
  fetchRunResult: mocks.fetchRunResult,
}));

async function mountDetail(result: AnalysisEnvelope | null) {
  mocks.fetchRunResult.mockResolvedValue(result);
  const wrapper = mount(Detail, {
    global: {
      stubs: { OhlcChart: true },
    },
  });
  await flushPromises();
  return wrapper;
}

describe("Detail — v2 success", () => {
  const text = mountDetail(v2SuccessEnvelope).then((w) => w.text());

  it("renders deterministic facts and decision as authoritative", async () => {
    const t = await text;
    expect(t).toContain("XAUUSD");
    expect(t).toContain("V2");
    expect(t).toContain("SUCCESS");
    expect(t).toContain("OPERATIONAL");
    expect(t).toContain("VALID");
    expect(t).toContain("READY");
    expect(t).toContain("LONG");
    expect(t).toContain("Buy setup");
    expect(t).toContain("2398.5");
    expect(t).toContain("2378");
    expect(t).toContain("2440");
  });

  it("renders synthesis as a separate presentation section", async () => {
    const t = await text;
    expect(t).toContain("Synthesis");
    expect(t).toContain("deterministic context is bullish");
    expect(t).toContain("unexpected news spike");
    expect(t).toContain("H4 breakout retest");
    expect(t).toContain("SUCCESS");
  });
});

describe("Detail — v2 degraded", () => {
  it("keeps the deterministic action and status authoritative", async () => {
    const wrapper = await mountDetail(v2DegradedEnvelope);
    const t = wrapper.text();
    expect(t).toContain("DEGRADED");
    expect(t).toContain("Sell setup");
    expect(t).toContain("OPERATIONAL");
    expect(t).toContain("VALID");
    expect(t).toContain("SHORT");
  });

  it("shows the synthesis explanation as unavailable", async () => {
    const wrapper = await mountDetail(v2DegradedEnvelope);
    const t = wrapper.text();
    expect(t).toContain("Unavailable");
    expect(t).toContain("synthesizer provider unreachable");
  });
});

describe("Detail — v2 invalid", () => {
  it("renders a non-actionable invalid state", async () => {
    const wrapper = await mountDetail(v2InvalidEnvelope);
    const t = wrapper.text();
    expect(t).toContain("PARTIAL");
    expect(t).toContain("INVALID");
    expect(t).toContain("NON-OPERATIONAL");
    expect(t).toContain("No trade");
    expect(t).toContain("NON_EXECUTABLE");
  });
});

describe("Detail — legacy", () => {
  it("renders legacy as UNKNOWN, NON-OPERATIONAL, review-free", async () => {
    const wrapper = await mountDetail(legacyEnvelope);
    const t = wrapper.text();
    expect(t).toContain("LEGACY");
    expect(t).toContain("UNKNOWN");
    expect(t).toContain("NON-OPERATIONAL");
    expect(t).toContain("No trade");
    expect(t).toContain("SKIPPED");
  });

  it("never renders a review or approval state", async () => {
    const wrapper = await mountDetail(legacyEnvelope);
    expect(wrapper.text()).not.toMatch(/review|approved|APPROVED/i);
  });
});

describe("Detail — NFR-003 bounded histories", () => {
  it("never dumps raw swings or intermediate bar history", async () => {
    const withHistory: AnalysisEnvelope = {
      ...v2SuccessEnvelope,
      deterministic_facts: {
        ...v2SuccessEnvelope.deterministic_facts,
        timeframes: {
          D1: {
            events: { event_history: [{ type: "swing", time: "2026-07-25T17:00" }] },
            levels: { nearest_support: 2350 },
          },
          H1: {
            events: { event_history: Array.from({ length: 60 }, (_, i) => ({ bar: i })) },
          },
        },
        event_history: { H1: Array.from({ length: 60 }, (_, i) => ({ bar: i })) },
        liquidity_history: { H1: Array.from({ length: 60 }, (_, i) => ({ bar: i })) },
      },
    };
    const wrapper = await mountDetail(withHistory);
    const t = wrapper.text();
    expect(t).not.toMatch(/swing/i);
    expect(t).not.toContain("2350");
  });
});
