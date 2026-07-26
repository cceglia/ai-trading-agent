import { Router } from "express";
import { ResultScanner } from "../services/scanner.js";

export function createRunsRouter(scanner: ResultScanner): Router {
  const router = Router();

  router.get("/", async (req, res) => {
    try {
      const { symbol, from, to } = req.query;
      const runs = await scanner.listRuns({
        symbol: symbol as string | undefined,
        from: from as string | undefined,
        to: to as string | undefined,
      });
      res.json(runs);
    } catch (err) {
      res.status(500).json({ error: "Failed to list runs" });
    }
  });

  router.get("/:symbol/:year/:month/:day/:file", async (req, res) => {
    try {
      const { symbol, year, month, day, file } = req.params;
      const result = await scanner.getRun(symbol, year, month, day, file);
      if (!result) {
        return res.status(404).json({ error: "Run not found" });
      }
      res.json(result);
    } catch (err) {
      res.status(500).json({ error: "Failed to get run" });
    }
  });

  return router;
}
