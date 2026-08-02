import { describe, it, expect } from "vitest";
import { resolveApiBaseURL } from "../api";

describe("resolveApiBaseURL", () => {
  it("returns an empty string when the value is undefined", () => {
    expect(resolveApiBaseURL(undefined)).toBe("");
  });

  it("returns an empty string when the value is empty", () => {
    expect(resolveApiBaseURL("")).toBe("");
  });

  it("returns an empty string when the value is only whitespace", () => {
    expect(resolveApiBaseURL("   ")).toBe("");
    expect(resolveApiBaseURL("\t\n")).toBe("");
  });

  it("returns the trimmed value when given a normal URL", () => {
    expect(resolveApiBaseURL("https://api.example.com")).toBe(
      "https://api.example.com"
    );
  });

  it("trims surrounding whitespace from a configured URL", () => {
    expect(resolveApiBaseURL("  https://api.example.com  ")).toBe(
      "https://api.example.com"
    );
  });

  it("treats a single-space string as empty (no accidental cross-origin requests)", () => {
    expect(resolveApiBaseURL(" ")).toBe("");
  });
});
