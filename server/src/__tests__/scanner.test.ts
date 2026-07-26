import { describe, it, expect, beforeEach } from "vitest";
import { mkdir, writeFile, rm } from "node:fs/promises";
import { join } from "node:path";
import { ResultScanner } from "../services/scanner.js";

describe("ResultScanner", () => {
  const testDir = join(process.cwd(), "tmp-test-runs");

  beforeEach(async () => {
    // Clean and recreate test directory
    await rm(testDir, { recursive: true, force: true });
  });

  it("returns empty array when directory does not exist", async () => {
    const scanner = new ResultScanner("/nonexistent/path");
    const runs = await scanner.listRuns();
    expect(runs).toEqual([]);
  });

  it("finds result files in directory tree", async () => {
    // Create: tmp-test-runs/2026/07/26/XAUUSD/result-08-30.json
    const resultPath = join(testDir, "2026", "07", "26", "XAUUSD");
    await mkdir(resultPath, { recursive: true });

    const result = {
      version: "1.0",
      symbol: "XAUUSD",
      run_id: "2026-07-26T08:30:00",
      started_at: "2026-07-26T08:30:00Z",
      completed_at: "2026-07-26T08:31:15Z",
      status: "success",
      errors: [],
      fatal_error: null,
      market_context: {
        symbol: "XAUUSD",
        bias: "bullish",
        confidence: 75,
        reasoning: "test",
        key_levels: [],
        structural_events: [],
        calendar_context: "",
        current_price: 2365.5,
        current_price_time: "2026-07-26T08:29:00",
      },
      decision: {
        symbol: "XAUUSD",
        action: "buy_setup",
        entry_price: 2368,
        stop_loss: 2350,
        take_profit: 2400,
        reasoning: "test",
        risk_reward_ratio: 1.78,
        entry_authorized: false,
      },
      review: {
        approved: true,
        reasoning: "test",
        concerns: [],
        suggested_improvements: null,
        risk_management_ok: true,
        htf_alignment_ok: true,
        calendar_clear: true,
      },
      ohlc: {
        D1: [
          {
            time: "2026-07-25T17:00",
            open: 2350,
            high: 2370,
            low: 2345,
            close: 2365.5,
          },
        ],
        H4: [],
        H1: [],
      },
      sl_tp_overlay: {
        entry_price: 2368,
        stop_loss: 2350,
        take_profit: 2400,
      },
    };

    await writeFile(
      join(resultPath, "result-08-30.json"),
      JSON.stringify(result),
    );

    const scanner = new ResultScanner(testDir);
    const runs = await scanner.listRuns();
    expect(runs).toHaveLength(1);
    expect(runs[0].symbol).toBe("XAUUSD");
    expect(runs[0].bias).toBe("bullish");
    expect(runs[0].confidence).toBe(75);
    expect(runs[0].action).toBe("buy_setup");
    expect(runs[0].review_approved).toBe(true);
  });

  it("filters by symbol", async () => {
    // Create two symbols
    for (const sym of ["XAUUSD", "EURUSD"]) {
      const resultPath = join(testDir, "2026", "07", "26", sym);
      await mkdir(resultPath, { recursive: true });
      const result = {
        version: "1.0",
        symbol: sym,
        run_id: "2026-07-26T08:30:00",
        started_at: "2026-07-26T08:30:00Z",
        completed_at: "2026-07-26T08:31:15Z",
        status: "success",
        errors: [],
        fatal_error: null,
        market_context: {
          symbol: sym,
          bias: "bullish",
          confidence: 75,
          reasoning: "test",
          key_levels: [],
          structural_events: [],
          calendar_context: "",
          current_price: null,
          current_price_time: null,
        },
        decision: {
          symbol: sym,
          action: "no_trade",
          entry_price: null,
          stop_loss: null,
          take_profit: null,
          reasoning: "test",
          risk_reward_ratio: null,
          entry_authorized: false,
        },
        review: {
          approved: true,
          reasoning: "test",
          concerns: [],
          suggested_improvements: null,
          risk_management_ok: true,
          htf_alignment_ok: true,
          calendar_clear: true,
        },
        ohlc: { D1: [], H4: [], H1: [] },
        sl_tp_overlay: {
          entry_price: null,
          stop_loss: null,
          take_profit: null,
        },
      };
      await writeFile(
        join(resultPath, "result-08-30.json"),
        JSON.stringify(result),
      );
    }

    const scanner = new ResultScanner(testDir);
    const runs = await scanner.listRuns({ symbol: "EURUSD" });
    expect(runs).toHaveLength(1);
    expect(runs[0].symbol).toBe("EURUSD");
  });

  it("filters by date range", async () => {
    // Create runs on different dates
    for (const day of ["25", "26", "27"]) {
      const resultPath = join(testDir, "2026", "07", day, "XAUUSD");
      await mkdir(resultPath, { recursive: true });
      const result = {
        version: "1.0",
        symbol: "XAUUSD",
        run_id: `2026-07-${day}T08:30:00`,
        started_at: `2026-07-${day}T08:30:00Z`,
        completed_at: `2026-07-${day}T08:31:15Z`,
        status: "success",
        errors: [],
        fatal_error: null,
        market_context: {
          symbol: "XAUUSD",
          bias: "bullish",
          confidence: 75,
          reasoning: "test",
          key_levels: [],
          structural_events: [],
          calendar_context: "",
          current_price: null,
          current_price_time: null,
        },
        decision: {
          symbol: "XAUUSD",
          action: "no_trade",
          entry_price: null,
          stop_loss: null,
          take_profit: null,
          reasoning: "test",
          risk_reward_ratio: null,
          entry_authorized: false,
        },
        review: {
          approved: true,
          reasoning: "test",
          concerns: [],
          suggested_improvements: null,
          risk_management_ok: true,
          htf_alignment_ok: true,
          calendar_clear: true,
        },
        ohlc: { D1: [], H4: [], H1: [] },
        sl_tp_overlay: {
          entry_price: null,
          stop_loss: null,
          take_profit: null,
        },
      };
      await writeFile(
        join(resultPath, "result-08-30.json"),
        JSON.stringify(result),
      );
    }

    const scanner = new ResultScanner(testDir);
    const runs = await scanner.listRuns({
      from: "2026-07-26",
      to: "2026-07-27",
    });
    expect(runs).toHaveLength(2);
  });

  it("getRun returns null for missing file", async () => {
    const scanner = new ResultScanner(testDir);
    const result = await scanner.getRun(
      "XAUUSD",
      "2026",
      "07",
      "26",
      "result-08-30",
    );
    expect(result).toBeNull();
  });

  it("getRun returns FullResult for valid file", async () => {
    const resultPath = join(testDir, "2026", "07", "26", "XAUUSD");
    await mkdir(resultPath, { recursive: true });
    const resultData = {
      version: "1.0",
      symbol: "XAUUSD",
      run_id: "test",
      started_at: "2026-07-26T08:30:00Z",
      completed_at: "2026-07-26T08:31:15Z",
      status: "success",
      errors: [],
      fatal_error: null,
      market_context: {
        symbol: "XAUUSD",
        bias: "bullish",
        confidence: 75,
        reasoning: "test",
        key_levels: [],
        structural_events: [],
        calendar_context: "",
        current_price: null,
        current_price_time: null,
      },
      decision: {
        symbol: "XAUUSD",
        action: "no_trade",
        entry_price: null,
        stop_loss: null,
        take_profit: null,
        reasoning: "test",
        risk_reward_ratio: null,
        entry_authorized: false,
      },
      review: {
        approved: true,
        reasoning: "test",
        concerns: [],
        suggested_improvements: null,
        risk_management_ok: true,
        htf_alignment_ok: true,
        calendar_clear: true,
      },
      ohlc: { D1: [], H4: [], H1: [] },
      sl_tp_overlay: { entry_price: null, stop_loss: null, take_profit: null },
    };
    await writeFile(
      join(resultPath, "result-08-30.json"),
      JSON.stringify(resultData),
    );

    const scanner = new ResultScanner(testDir);
    const result = await scanner.getRun(
      "XAUUSD",
      "2026",
      "07",
      "26",
      "result-08-30",
    );
    expect(result).not.toBeNull();
    expect(result!.symbol).toBe("XAUUSD");
  });

  it("skips malformed JSON files", async () => {
    const resultPath = join(testDir, "2026", "07", "26", "XAUUSD");
    await mkdir(resultPath, { recursive: true });
    await writeFile(join(resultPath, "result-08-30.json"), "not valid json");

    const scanner = new ResultScanner(testDir);
    const runs = await scanner.listRuns();
    expect(runs).toHaveLength(0);
  });
});
