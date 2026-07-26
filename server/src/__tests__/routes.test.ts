import { describe, it, expect, vi, beforeEach } from "vitest";
import express from "express";
import request from "supertest";
import { ResultScanner } from "../services/scanner.js";
import { RunService } from "../services/runner.js";
import { createRunsRouter } from "../routes/runs.js";
import { createRunRouter } from "../routes/run.js";

// Mock services
vi.mock("../services/scanner.js");
vi.mock("../services/runner.js");

describe("Routes", () => {
  let app: express.Express;
  let mockScanner: any;
  let mockRunner: any;

  beforeEach(() => {
    vi.clearAllMocks();

    mockScanner = {
      listRuns: vi.fn(),
      getRun: vi.fn(),
    };

    mockRunner = {
      runAnalysis: vi.fn(),
    };

    app = express();
    app.use(express.json());
    app.use(
      "/api/runs",
      createRunsRouter(mockScanner as unknown as ResultScanner),
    );
    app.use(
      "/api/run",
      createRunRouter(mockRunner as unknown as RunService),
    );
  });

  describe("GET /api/runs", () => {
    it("returns 200 with run summaries", async () => {
      const mockRuns = [
        {
          symbol: "XAUUSD",
          date: "2026-07-26",
          time: "08-30",
          bias: "bullish",
          confidence: 75,
          action: "buy_setup",
          review_approved: true,
          current_price: 2365.5,
          file_path: "2026/07/26/XAUUSD/result-08-30.json",
        },
      ];
      mockScanner.listRuns.mockResolvedValue(mockRuns);

      const res = await request(app).get("/api/runs");
      expect(res.status).toBe(200);
      expect(res.body).toEqual(mockRuns);
    });

    it("passes query params as filters", async () => {
      mockScanner.listRuns.mockResolvedValue([]);

      await request(app).get(
        "/api/runs?symbol=XAUUSD&from=2026-07-20&to=2026-07-26",
      );
      expect(mockScanner.listRuns).toHaveBeenCalledWith({
        symbol: "XAUUSD",
        from: "2026-07-20",
        to: "2026-07-26",
      });
    });

    it("returns 500 on scanner error", async () => {
      mockScanner.listRuns.mockRejectedValue(new Error("Disk error"));

      const res = await request(app).get("/api/runs");
      expect(res.status).toBe(500);
      expect(res.body).toEqual({ error: "Failed to list runs" });
    });
  });

  describe("GET /api/runs/:symbol/:year/:month/:day/:file", () => {
    it("returns 200 with FullResult", async () => {
      const mockResult = {
        symbol: "XAUUSD",
        status: "success",
        version: "1.0",
      };
      mockScanner.getRun.mockResolvedValue(mockResult);

      const res = await request(app).get(
        "/api/runs/XAUUSD/2026/07/26/result-08-30",
      );
      expect(res.status).toBe(200);
      expect(res.body.symbol).toBe("XAUUSD");
    });

    it("returns 404 when not found", async () => {
      mockScanner.getRun.mockResolvedValue(null);

      const res = await request(app).get(
        "/api/runs/XAUUSD/2026/07/26/result-08-30",
      );
      expect(res.status).toBe(404);
      expect(res.body.error).toBe("Run not found");
    });

    it("returns 500 on scanner error", async () => {
      mockScanner.getRun.mockRejectedValue(new Error("Disk error"));

      const res = await request(app).get(
        "/api/runs/XAUUSD/2026/07/26/result-08-30",
      );
      expect(res.status).toBe(500);
    });
  });

  describe("POST /api/run", () => {
    it("returns 200 with FullResult[]", async () => {
      const mockResults = [
        { symbol: "XAUUSD", status: "success", version: "1.0" },
      ];
      mockRunner.runAnalysis.mockResolvedValue(mockResults);

      const res = await request(app)
        .post("/api/run")
        .send({ symbols: ["XAUUSD"] });
      expect(res.status).toBe(200);
      expect(res.body).toEqual(mockResults);
    });

    it("validates symbols is a non-empty array", async () => {
      const res = await request(app).post("/api/run").send({});
      expect(res.status).toBe(400);
      expect(res.body.error).toBe("symbols must be a non-empty array");
    });

    it("validates each symbol is a non-empty string", async () => {
      const res = await request(app)
        .post("/api/run")
        .send({ symbols: [""] });
      expect(res.status).toBe(400);
    });

    it("rejects symbols with invalid format", async () => {
      mockRunner.runAnalysis.mockResolvedValue([]);
      const res = await request(app).post("/api/run").send({ symbols: ["--help"] });
      expect(res.status).toBe(400);
      expect(res.body.error).toContain("Invalid symbol format");
    });

    it("rejects symbols with special characters", async () => {
      mockRunner.runAnalysis.mockResolvedValue([]);
      const res = await request(app).post("/api/run").send({ symbols: ["XAU/USD"] });
      expect(res.status).toBe(400);
    });

    it("passes model parameter to runner", async () => {
      mockRunner.runAnalysis.mockResolvedValue([]);

      await request(app)
        .post("/api/run")
        .send({ symbols: ["XAUUSD"], model: "gpt-4" });
      expect(mockRunner.runAnalysis).toHaveBeenCalledWith(
        ["XAUUSD"],
        "gpt-4",
      );
    });

    it("returns 500 when analysis fails", async () => {
      mockRunner.runAnalysis.mockRejectedValue(new Error("Python error"));

      const res = await request(app)
        .post("/api/run")
        .send({ symbols: ["XAUUSD"] });
      expect(res.status).toBe(500);
      expect(res.body.error).toBe("Python error");
    });
  });
});
