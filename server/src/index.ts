import express from "express";
import cors from "cors";
import { config } from "dotenv";
import { ResultScanner } from "./services/scanner.js";
import { RunService } from "./services/runner.js";
import { createRunsRouter } from "./routes/runs.js";
import { createRunRouter } from "./routes/run.js";
import path from "path";
import fs from "fs";

config();

const app = express();
const allowedOrigins = process.env.CORS_ORIGINS?.split(",") || ["http://localhost:5173"];
app.use(cors({ origin: allowedOrigins }));
app.use(express.json());

const dataDir = process.env.DATA_DIR || "../data/runs";
const scanner = new ResultScanner(dataDir);
const runner = new RunService(
  process.env.PYTHON_CMD || "python",
  process.env.ANALYZER_DIR || ".",
  dataDir
);

app.use("/api/runs", createRunsRouter(scanner));
app.use("/api/run", createRunRouter(runner));

// Serve the built UI in production
if (process.env.NODE_ENV === "production") {
  const __dirname = path.dirname(new URL(import.meta.url).pathname);
  const uiDistPath = path.join(__dirname, "../../ui/dist");
  if (fs.existsSync(uiDistPath)) {
    app.use(express.static(uiDistPath));
    // SPA fallback — must come after API routes
    app.get("*", (req, res) => {
      res.sendFile(path.join(uiDistPath, "index.html"));
    });
  }
}

const port = parseInt(process.env.PORT || "3000", 10);
app.listen(port, () => {
  console.log(`Trading analysis server running on port ${port}`);
});

export default app;
