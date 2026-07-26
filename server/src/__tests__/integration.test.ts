import { describe, it, expect, beforeEach } from "vitest";
import { mkdir, writeFile, rm } from "node:fs/promises";
import { join } from "node:path";
import express from "express";
import request from "supertest";
import { ResultScanner } from "../services/scanner.js";
import { createRunsRouter } from "../routes/runs.js";

describe("Server Integration", () => {
  const testDir = join(process.cwd(), "tmp-int-test");

  beforeEach(async () => {
    await rm(testDir, { recursive: true, force: true });
  });

  async function createFixture() {
    // Create fixture data for XAUUSD and EURUSD
    for (const sym of ["XAUUSD", "EURUSD"]) {
      const resultPath = join(testDir, "2026", "07", "26", sym);
      await mkdir(resultPath, { recursive: true });
      const result = {
        version: "1.0",
        symbol: sym,
        run_id: `2026-07-26T08:30:00`,
        started_at: "2026-07-26T08:30:00Z",
        completed_at: "2026-07-26T08:31:15Z",
        status: "success",
        errors: [],
        fatal_error: null,
        market_context: {
          symbol: sym, bias: "bullish", confidence: 75, reasoning: "test",
          key_levels: ["2350", "2400"], structural_events: [], calendar_context: "",
          current_price: 2365.5, current_price_time: "2026-07-26T08:29:00",
        },
        decision: {
          symbol: sym, action: "buy_setup", entry_price: 2368, stop_loss: 2350,
          take_profit: 2400, reasoning: "test", risk_reward_ratio: 1.78, entry_authorized: false,
        },
        review: {
          approved: true, reasoning: "test", concerns: [],
          suggested_improvements: null, risk_management_ok: true,
          htf_alignment_ok: true, calendar_clear: true,
        },
        ohlc: {
          D1: [{ time: "2026-07-25T17:00", open: 2350, high: 2370, low: 2345, close: 2365.5 }],
          H4: [], H1: [],
        },
        sl_tp_overlay: { entry_price: 2368, stop_loss: 2350, take_profit: 2400 },
      };
      await writeFile(join(resultPath, "result-08-30.json"), JSON.stringify(result));
    }
  }

  it("GET /api/runs returns fixture data as RunSummary[]", async () => {
    await createFixture();
    const scanner = new ResultScanner(testDir);
    const app = express();
    app.use("/api/runs", createRunsRouter(scanner));

    const res = await request(app).get("/api/runs");
    expect(res.status).toBe(200);
    expect(Array.isArray(res.body)).toBe(true);
    expect(res.body.length).toBe(2);

    // Verify both symbols are present (order is filesystem-dependent)
    const symbols = res.body.map((r: any) => r.symbol);
    expect(symbols).toContain("XAUUSD");
    expect(symbols).toContain("EURUSD");

    // Verify shape and values on either run
    const xauRun = res.body.find((r: any) => r.symbol === "XAUUSD");
    expect(xauRun).toBeDefined();
    expect(xauRun.bias).toBe("bullish");
    expect(xauRun.confidence).toBe(75);
    expect(xauRun.action).toBe("buy_setup");
    expect(xauRun.review_approved).toBe(true);
  });

  it("GET /api/runs?symbol=XAUUSD filters correctly", async () => {
    await createFixture();
    const scanner = new ResultScanner(testDir);
    const app = express();
    app.use("/api/runs", createRunsRouter(scanner));

    const res = await request(app).get("/api/runs?symbol=XAUUSD");
    expect(res.status).toBe(200);
    expect(res.body.length).toBe(1);
    expect(res.body[0].symbol).toBe("XAUUSD");
  });

  it("GET /api/runs/:symbol/:year/:month/:day/:file returns FullResult", async () => {
    await createFixture();
    const scanner = new ResultScanner(testDir);
    const app = express();
    app.use("/api/runs", createRunsRouter(scanner));

    const res = await request(app).get("/api/runs/XAUUSD/2026/07/26/result-08-30");
    expect(res.status).toBe(200);
    expect(res.body.symbol).toBe("XAUUSD");
    expect(res.body.version).toBe("1.0");
    expect(res.body.market_context.bias).toBe("bullish");
    expect(res.body.decision.entry_authorized).toBe(false);
    expect(res.body.ohlc.D1.length).toBe(1);
    expect(res.body.sl_tp_overlay.entry_price).toBe(2368);
  });

  it("GET /api/runs/:... returns 404 for missing run", async () => {
    const scanner = new ResultScanner(testDir);
    const app = express();
    app.use("/api/runs", createRunsRouter(scanner));

    const res = await request(app).get("/api/runs/XAUUSD/2020/01/01/result-00-00");
    expect(res.status).toBe(404);
  });
});
