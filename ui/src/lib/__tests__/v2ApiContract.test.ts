import { describe, it, expect, vi, afterEach } from "vitest";
import { fetchRuns, fetchRunResult, startRun } from "../api";
import * as apiModule from "../api";
import {
  legacySummary,
  v2SuccessEnvelope,
  v2SuccessSummary,
} from "../../__tests__/fixtures";
import type { RunRequest } from "../../types";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("fetchRuns", () => {
  it("returns typed v2 summaries from the list route", async () => {
    const spy = vi
      .spyOn(apiModule.api, "get")
      .mockResolvedValue({ data: [v2SuccessSummary, legacySummary] });
    const runs = await fetchRuns({ symbol: "XAUUSD" });
    expect(spy).toHaveBeenCalledWith("/api/runs", {
      params: { symbol: "XAUUSD" },
    });
    expect(runs).toEqual([v2SuccessSummary, legacySummary]);
    expect(runs[1].validation_status).toBe("UNKNOWN");
    expect(runs[1].operational).toBe(false);
  });
});

describe("fetchRunResult", () => {
  it("returns the typed v2 envelope from the detail route", async () => {
    const spy = vi
      .spyOn(apiModule.api, "get")
      .mockResolvedValue({ data: v2SuccessEnvelope });
    const result = await fetchRunResult("XAUUSD", "2026", "07", "26", "result-08");
    expect(spy).toHaveBeenCalledWith("/api/runs/XAUUSD/2026/07/26/result-08");
    expect(result).toEqual(v2SuccessEnvelope);
  });
});

describe("startRun", () => {
  it("sends a batch request without base_url and returns the batch response", async () => {
    const spy = vi
      .spyOn(apiModule.api, "post")
      .mockResolvedValue({ data: { status: "success", results: { XAUUSD: v2SuccessEnvelope }, errors: {} } });
    const request: RunRequest = { symbols: ["XAUUSD"], provider_id: "default" };
    const response = await startRun(request);
    expect(spy).toHaveBeenCalledWith("/api/run", request);
    expect(response.status).toBe("success");
    expect(response.results.XAUUSD.decision.action).toBe("buy_setup");
  });

  it("never includes base_url in the request body shape", () => {
    const request: RunRequest = { symbols: ["XAUUSD"] };
    expect("base_url" in request).toBe(false);
    expect(request.provider_id).toBeUndefined();
  });
});
