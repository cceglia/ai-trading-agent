import { Router } from "express";
import { RunService } from "../services/runner.js";

export function createRunRouter(runner: RunService): Router {
  const router = Router();

  router.post("/", async (req, res) => {
    try {
      const { symbols, model } = req.body;

      if (!symbols || !Array.isArray(symbols) || symbols.length === 0) {
        return res.status(400).json({ error: "symbols must be a non-empty array" });
      }

      if (symbols.some((s: unknown) => typeof s !== "string" || s.trim() === "")) {
        return res.status(400).json({ error: "Each symbol must be a non-empty string" });
      }

      const SYMBOL_PATTERN = /^[A-Z0-9]{1,20}$/i;
      const invalidSymbols = symbols.filter((s: string) => !SYMBOL_PATTERN.test(s));
      if (invalidSymbols.length > 0) {
        return res.status(400).json({
          error: `Invalid symbol format: ${invalidSymbols.join(", ")}. Symbols must be 1-20 alphanumeric characters.`,
        });
      }

      const results = await runner.runAnalysis(symbols, model);
      res.json(results);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      res.status(500).json({ error: message });
    }
  });

  return router;
}
