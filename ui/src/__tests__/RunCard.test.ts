// @vitest-environment happy-dom
import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import RunCard from "../components/RunCard.vue";
import { legacySummary, v2SuccessSummary } from "./fixtures";

describe("RunCard", () => {
  it("renders v2 deterministic summary facts for an operational run", () => {
    const wrapper = mount(RunCard, { props: { run: v2SuccessSummary } });
    const text = wrapper.text();
    expect(text).toContain("XAUUSD");
    expect(text).toContain("2026-07-26");
    expect(text).toContain("Buy setup");
    expect(text).toContain("VALID");
    expect(text).toContain("READY");
    expect(text).toContain("LONG");
    expect(text).toContain("OPERATIONAL");
    expect(text).toContain("72%");
  });

  it("renders a legacy summary as UNKNOWN and NON-OPERATIONAL", () => {
    const wrapper = mount(RunCard, { props: { run: legacySummary } });
    const text = wrapper.text();
    expect(text).toContain("UNKNOWN");
    expect(text).toContain("NON-OPERATIONAL");
    expect(text).toContain("No trade");
    expect(text).toContain("85%");
  });

  it("renders a v2 deterministic score of exactly 1 as 1% (not a legacy 100%)", () => {
    const wrapper = mount(RunCard, {
      props: {
        run: { ...v2SuccessSummary, confidence: 1 },
      },
    });
    const text = wrapper.text();
    expect(text).toContain("1%");
    expect(text).not.toContain("100%");
  });

  it("never renders a review or approval state", () => {
    const wrapper = mount(RunCard, { props: { run: legacySummary } });
    expect(wrapper.text()).not.toMatch(/review|approved|APPROVED/i);
  });
});
