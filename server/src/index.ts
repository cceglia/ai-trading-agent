import express from "express";
import cors from "cors";
import { config } from "dotenv";
import { ResultScanner } from "./services/scanner.js";
import { RunService } from "./services/runner.js";
import { createRunsRouter } from "./routes/runs.js";
import { createRunRouter } from "./routes/run.js";

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

const port = parseInt(process.env.PORT || "3000", 10);
app.listen(port, () => {
  console.log(`Trading analysis server running on port ${port}`);
});

export default app;
