import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { createApiClient, resolveApiBaseURL } from "../api";

describe("createApiClient", () => {
  beforeEach(() => {
    // Start each case with no env override; tests set what they need.
    vi.stubEnv("VITE_API_URL", "");
  });

  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it("uses an explicit baseURL when one is passed (no env lookup)", () => {
    const client = createApiClient("https://override.example.com");
    expect(client.defaults.baseURL).toBe("https://override.example.com");
  });

  it("falls back to an empty string (same-origin) when env is unset", () => {
    vi.stubEnv("VITE_API_URL", "");
    const client = createApiClient();
    expect(client.defaults.baseURL).toBe("");
  });

  it("falls back to an empty string when env is unset entirely", () => {
    vi.stubEnv("VITE_API_URL", undefined as unknown as string);
    const client = createApiClient();
    // The default parameter still resolves to "" via resolveApiBaseURL.
    expect(client.defaults.baseURL).toBe("");
  });

  it("reads VITE_API_URL from import.meta.env when no baseURL is passed", () => {
    vi.stubEnv("VITE_API_URL", "https://api.example.com");
    const client = createApiClient();
    expect(client.defaults.baseURL).toBe("https://api.example.com");
  });

  it("trims whitespace from VITE_API_URL", () => {
    vi.stubEnv("VITE_API_URL", "  https://api.example.com  ");
    const client = createApiClient();
    expect(client.defaults.baseURL).toBe("https://api.example.com");
  });

  it("the pure resolver and the factory agree on the default value", () => {
    vi.stubEnv("VITE_API_URL", "https://api.example.com");
    const client = createApiClient();
    expect(client.defaults.baseURL).toBe(resolveApiBaseURL("https://api.example.com"));
  });

  it("explicit argument wins over the env value", () => {
    vi.stubEnv("VITE_API_URL", "https://from-env.example.com");
    const client = createApiClient("https://from-arg.example.com");
    expect(client.defaults.baseURL).toBe("https://from-arg.example.com");
  });
});
