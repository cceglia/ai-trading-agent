import { describe, it, expect, vi, beforeEach } from "vitest";
import { EventEmitter } from "node:events";

// Mock child_process BEFORE importing runner
vi.mock("node:child_process", () => ({
  spawn: vi.fn(),
}));

import { spawn } from "node:child_process";
import { RunService } from "../services/runner.js";

describe("RunService", () => {
  let mockChild: any;

  beforeEach(() => {
    vi.clearAllMocks();
    mockChild = new EventEmitter();
    mockChild.stdout = new EventEmitter();
    mockChild.stderr = new EventEmitter();
    mockChild.kill = vi.fn();
    (spawn as any).mockReturnValue(mockChild);
  });

  it("spawns process with correct args including -- separator", async () => {
    const runner = new RunService("python", "/analyzer", "/data/runs");

    // Simulate process completion
    setTimeout(() => {
      mockChild.emit("close", 0);
    }, 10);

    const results = await runner.runAnalysis(["XAUUSD", "EURUSD"]);

    expect(spawn).toHaveBeenCalledWith(
      "python",
      ["main.py", "--output-dir", "/data/runs", "--", "XAUUSD", "EURUSD"],
      {
        cwd: "/analyzer",
        stdio: ["ignore", "pipe", "pipe"],
      },
    );

    // Because the mock scanner returns empty list, results should be empty
    expect(results).toEqual([]);
  });

  it("spawns process with model argument", async () => {
    const runner = new RunService("python", "/analyzer", "/data/runs");

    setTimeout(() => {
      mockChild.emit("close", 0);
    }, 10);

    await runner.runAnalysis(["XAUUSD"], "gpt-4");

    expect(spawn).toHaveBeenCalledWith(
      "python",
      [
        "main.py",
        "--output-dir",
        "/data/runs",
        "--model",
        "gpt-4",
        "--",
        "XAUUSD",
      ],
      {
        cwd: "/analyzer",
        stdio: ["ignore", "pipe", "pipe"],
      },
    );
  });

  it("handles non-zero exit code", async () => {
    const runner = new RunService("python", "/analyzer", "/data/runs");

    setTimeout(() => {
      mockChild.stderr.emit("data", Buffer.from("error message"));
      mockChild.emit("close", 1);
    }, 10);

    await expect(runner.runAnalysis(["XAUUSD"])).rejects.toThrow(
      "exited with code 1",
    );
  });

  it("handles spawn error", async () => {
    const runner = new RunService("python", "/analyzer", "/data/runs");

    setTimeout(() => {
      mockChild.emit("error", new Error("ENOENT"));
    }, 10);

    await expect(runner.runAnalysis(["XAUUSD"])).rejects.toThrow("ENOENT");
  });

  it("times out after configured duration", async () => {
    const runner = new RunService("python", "/analyzer", "/data/runs", 50); // 50ms timeout

    // Never emit close — should time out
    await expect(runner.runAnalysis(["XAUUSD"])).rejects.toThrow(
      "timed out",
    );
  }, 10000); // 10s test timeout
});
