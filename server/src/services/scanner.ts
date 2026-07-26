import { readdir, readFile, stat } from "node:fs/promises";
import { join, parse as parsePath } from "node:path";
import type { FullResult, RunSummary } from "../types.js";

export class ResultScanner {
  constructor(private dataDir: string) {}

  /**
   * Walk the data directory tree and return a sorted list of run summaries.
   * Returns an empty array if the data directory does not exist.
   */
  async listRuns(filters?: {
    symbol?: string;
    from?: string;
    to?: string;
  }): Promise<RunSummary[]> {
    const runs: RunSummary[] = [];

    try {
      await this._walkDir(this.dataDir, "", runs);
    } catch (err) {
      // If data dir doesn't exist yet, return empty array
      if ((err as NodeJS.ErrnoException).code === "ENOENT") {
        return [];
      }
      throw err;
    }

    // Apply filters
    let filtered = runs;
    if (filters?.symbol) {
      const target = filters.symbol.toUpperCase();
      filtered = filtered.filter((r) => r.symbol === target);
    }
    if (filters?.from) {
      filtered = filtered.filter((r) => r.date >= filters.from!);
    }
    if (filters?.to) {
      filtered = filtered.filter((r) => r.date <= filters.to!);
    }

    // Sort by date desc, then time desc
    filtered.sort((a, b) => {
      const dateCmp = b.date.localeCompare(a.date);
      if (dateCmp !== 0) return dateCmp;
      return b.time.localeCompare(a.time);
    });

    return filtered;
  }

  /**
   * Read a specific result file and return its parsed content.
   * Returns null if the file does not exist or contains malformed JSON.
   */
  async getRun(
    symbol: string,
    year: string,
    month: string,
    day: string,
    file: string,
  ): Promise<FullResult | null> {
    const filePath = join(this.dataDir, year, month, day, symbol, `${file}.json`);
    try {
      const content = await readFile(filePath, "utf-8");
      const parsed: FullResult = JSON.parse(content);
      return parsed;
    } catch (err) {
      if ((err as NodeJS.ErrnoException).code === "ENOENT") {
        return null;
      }
      // Malformed JSON or other read error — return null
      return null;
    }
  }

  /**
   * Recursively walk a directory tree, collecting RunSummary entries
   * from every JSON file found.
   */
  private async _walkDir(
    basePath: string,
    relativePath: string,
    results: RunSummary[],
  ): Promise<void> {
    const dirPath = join(basePath, relativePath);
    let entries: string[];
    try {
      entries = await readdir(dirPath);
    } catch {
      return; // skip unreadable directories
    }

    for (const entry of entries) {
      const fullPath = join(dirPath, entry);
      let entryStat;
      try {
        entryStat = await stat(fullPath);
      } catch {
        continue; // skip entries that can't be stat'd
      }

      if (entryStat.isDirectory()) {
        await this._walkDir(basePath, join(relativePath, entry), results);
      } else if (entry.endsWith(".json")) {
        try {
          const content = await readFile(fullPath, "utf-8");
          const parsed: FullResult = JSON.parse(content);
          results.push(this._toSummary(parsed, join(relativePath, entry)));
        } catch {
          // Skip malformed JSON or files that don't match the FullResult shape
          continue;
        }
      }
    }
  }

  /**
   * Convert a parsed FullResult and its relative file path into a RunSummary.
   *
   * The relative filePath is expected to follow the convention:
   *   YYYY/MM/DD/SYMBOL/result-HH-MM.json
   *
   * The method parses the directory segments to extract date components
   * and the filename to extract the time component, then overlays values
   * from the FullResult payload.
   */
  private _toSummary(result: FullResult, filePath: string): RunSummary {
    // Normalise path separators so the logic works on Windows too
    const parts = filePath.replace(/\\/g, "/").split("/");

    // parts = ["YYYY", "MM", "DD", "SYMBOL", "result-HH-MM.json"]
    const date = parts.length >= 3 ? `${parts[0]}-${parts[1]}-${parts[2]}` : "";

    const fileName = parts[parts.length - 1] ?? "";
    // Strip "result-" prefix and ".json" extension
    const time = fileName.replace(/^result-/, "").replace(/\.json$/, "");

    return {
      symbol: result.symbol,
      date,
      time,
      bias: result.market_context?.bias ?? "unknown",
      confidence: result.market_context?.confidence ?? 0,
      action: result.decision?.action ?? "unknown",
      review_approved: result.review?.approved ?? false,
      current_price: result.market_context?.current_price ?? null,
      file_path: filePath,
    };
  }
}
