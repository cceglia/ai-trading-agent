import { describe, it, expect } from "vitest";
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join, relative } from "node:path";

/**
 * FR-037 / NFR-005 — browser code must not embed or transmit a machine API
 * key. This scans the UI source tree (and the built bundle when present) for
 * secret names and secret-looking values. No credentials are printed.
 */

const UI_ROOT = join(__dirname, "..", "..");
const SRC_DIR = join(UI_ROOT, "src");
const DIST_DIR = join(UI_ROOT, "dist");

/** Files we never scan: lockfiles and our own scan definitions. */
const SKIP_SUFFIXES = [".json", ".map"];
const SKIP_FILES = ["secretScan.test.ts"];

const FORBIDDEN_PATTERNS: RegExp[] = [
  // Server-side secret environment variable names must never reach the browser.
  /TRADING_API_KEY/,
  // API-key header wiring in browser code (auth is server/proxy-only).
  /\bX-API-Key\b/i,
  // OpenAI-style and common provider bearer tokens.
  /sk-[A-Za-z0-9]{16,}/,
  // Inline Authorization: Bearer with a concrete-looking token.
  /["']Authorization["']\s*:\s*["']Bearer\s+[A-Za-z0-9._-]{20,}/,
  // Provider endpoint URLs with inline credentials.
  /https?:\/\/[^/\s]+:[^@\s]{6,}@/,
];

function walk(dir: string): string[] {
  const out: string[] = [];
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) {
      out.push(...walk(full));
    } else {
      out.push(full);
    }
  }
  return out;
}

/** True when the path exists and is a directory. `dist/` is gitignored, so a
 *  clean checkout/container must not throw when it is absent. */
function isDirectory(dir: string): boolean {
  return existsSync(dir) && statSync(dir).isDirectory();
}

function collectTargets(): string[] {
  const targets: string[] = [];
  if (isDirectory(SRC_DIR)) {
    for (const file of walk(SRC_DIR)) {
      if (SKIP_SUFFIXES.some((s) => file.endsWith(s))) continue;
      if (SKIP_FILES.some((f) => file.endsWith(f))) continue;
      targets.push(file);
    }
  }
  if (isDirectory(DIST_DIR)) {
    for (const file of walk(DIST_DIR)) {
      if (file.endsWith(".map")) continue;
      targets.push(file);
    }
  }
  return targets;
}

describe("FR-037 — no secret API key in browser source or bundle", () => {
  const targets = collectTargets();
  const findings: string[] = [];

  for (const target of targets) {
    const content = readFileSync(target, "utf-8");
    for (const pattern of FORBIDDEN_PATTERNS) {
      const match = content.match(pattern);
      if (match) {
        findings.push(
          `${relative(UI_ROOT, target)} matched ${pattern} at ${match.index}`
        );
      }
    }
  }

  it("scans a non-empty set of source files", () => {
    const sourceFiles = targets.filter((t) => t.startsWith(SRC_DIR));
    expect(sourceFiles.length).toBeGreaterThan(5);
  });

  it("finds no secret key names or values", () => {
    expect(findings).toEqual([]);
  });
});
