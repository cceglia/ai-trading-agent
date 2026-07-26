import { spawn } from "node:child_process";
import { FullResult } from "../types.js";
import { ResultScanner } from "./scanner.js";

/**
 * Service that spawns the Python analyzer as a child process,
 * waits for it to complete, and reads back the written result files.
 */
export class RunService {
  private timeoutMs: number;

  constructor(
    private pythonCmd: string,
    private analyzerDir: string,
    private dataDir: string,
    timeoutMs: number = 600_000, // 10 minutes default
  ) {
    this.timeoutMs = timeoutMs;
  }

  /**
   * Run analysis for the given symbols by spawning the Python analyzer.
   *
   * @param symbols - List of ticker symbols to analyze (e.g. ["EURUSD", "GBPUSD"])
   * @param model  - Optional model identifier passed as --model to the Python script
   * @returns The parsed FullResult for each requested symbol
   * @throws If the Python process times out, exits with non-zero code, or cannot be spawned
   */
  async runAnalysis(symbols: string[], model?: string): Promise<FullResult[]> {
    const args = ["--output-dir", this.dataDir];
    if (model) {
      args.push("--model", model);
    }
    args.push("--", ...symbols);

    await this._spawnProcess(args);
    return this._readResults(symbols);
  }

  /**
   * Spawn the Python process and wait for it to complete.
   * On timeout the process is killed and the promise rejects.
   * On non-zero exit the promise rejects with captured stderr.
   */
  private _spawnProcess(args: string[]): Promise<void> {
    return new Promise((resolve, reject) => {
      const child = spawn(this.pythonCmd, ["main.py", ...args], {
        cwd: this.analyzerDir,
        stdio: ["ignore", "pipe", "pipe"],
      });

      const timer = setTimeout(() => {
        child.kill();
        reject(
          new Error(
            `Python process timed out after ${this.timeoutMs}ms`,
          ),
        );
      }, this.timeoutMs);

      let stderr = "";

      child.stdout.on("data", (_data: Buffer) => {
        // Consume stdout (logging output from the Python process)
      });

      child.stderr.on("data", (data: Buffer) => {
        stderr += data.toString();
      });

      child.on("close", (code) => {
        clearTimeout(timer);

        if (code === 0) {
          resolve();
        } else {
          reject(
            new Error(
              `Python process exited with code ${code}: ${stderr}`,
            ),
          );
        }
      });

      child.on("error", (err) => {
        clearTimeout(timer);
        reject(err);
      });
    });
  }

  /**
   * Walk the data directory through the ResultScanner and pick the
   * most recent result file for each requested symbol.
   */
  private async _readResults(symbols: string[]): Promise<FullResult[]> {
    const scanner = new ResultScanner(this.dataDir);
    const allRuns = await scanner.listRuns();

    const symbolSet = new Set(symbols.map((s) => s.toUpperCase()));

    // Pick the newest run per symbol (listRuns returns newest-first)
    const results: FullResult[] = [];
    const seenSymbols = new Set<string>();

    for (const run of allRuns) {
      if (seenSymbols.has(run.symbol)) continue;
      if (!symbolSet.has(run.symbol)) continue;

      seenSymbols.add(run.symbol);

      const [year, month, day] = run.date.split("-");
      const fullResult = await scanner.getRun(
        run.symbol,
        year,
        month,
        day,
        `result-${run.time}`,
      );

      if (fullResult) {
        results.push(fullResult);
      }
    }

    return results;
  }
}
