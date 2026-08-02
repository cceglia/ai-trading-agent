import { describe, it, expect } from "vitest";
import { AxiosError } from "axios";
import { formatApiError } from "../errors";

/** Build a real AxiosError instance for tests so axios.isAxiosError() returns true. */
function makeAxiosError(opts: {
  status?: number;
  statusText?: string;
  data?: unknown;
  url?: string;
  baseURL?: string;
  code?: string;
  hasResponse?: boolean;
  hasRequest?: boolean;
  message?: string;
}): AxiosError {
  const config = {
    url: opts.url ?? "/api/runs",
    baseURL: opts.baseURL ?? "",
  } as unknown as import("axios").InternalAxiosRequestConfig;

  const response = opts.hasResponse === false
    ? undefined
    : {
        status: opts.status ?? 500,
        statusText: opts.statusText ?? "Server Error",
        data: opts.data,
        headers: {},
        config,
        statusText_: opts.statusText ?? "Server Error",
      };

  return new AxiosError(
    opts.message ?? "Request failed",
    opts.code,
    config,
    opts.hasRequest === false ? undefined : {},
    response as unknown as import("axios").AxiosResponse
  );
}

describe("formatApiError — Axios errors with a response", () => {
  it("uses data.detail as a string (FastAPI HTTPException default handler)", () => {
    const err = makeAxiosError({
      status: 400,
      statusText: "Bad Request",
      data: { detail: "Invalid symbol format: BAD" },
    });
    const msg = formatApiError(err, "Failed to load runs");
    expect(msg).toBe(
      "Failed to load runs: 400 Bad Request — Invalid symbol format: BAD (/api/runs)"
    );
  });

  it("uses data.error as a string (this project's custom error handlers)", () => {
    const err = makeAxiosError({
      status: 500,
      statusText: "Internal Server Error",
      data: { error: "Failed to list runs" },
    });
    const msg = formatApiError(err, "Failed to load runs");
    expect(msg).toBe(
      "Failed to load runs: 500 Internal Server Error — Failed to list runs (/api/runs)"
    );
  });

  it("uses data.message when present", () => {
    const err = makeAxiosError({
      status: 400,
      statusText: "Bad Request",
      data: { message: "Symbol required" },
    });
    const msg = formatApiError(err, "Failed to load runs");
    expect(msg).toContain("Symbol required");
    expect(msg).toContain("400 Bad Request");
  });

  it("formats FastAPI validation error arrays as 'loc: msg; ...'", () => {
    const err = makeAxiosError({
      status: 422,
      statusText: "Unprocessable Entity",
      data: {
        detail: [
          { type: "missing", loc: ["body", "symbols"], msg: "Field required", input: {} },
          { type: "value_error", loc: ["body", "symbols", 0], msg: "must be string", input: 42 },
        ],
      },
    });
    const msg = formatApiError(err, "Run failed");
    expect(msg).toContain("body.symbols: Field required");
    expect(msg).toContain("body.symbols.0: must be string");
    expect(msg).toContain("422 Unprocessable Entity");
  });

  it("handles a plain string response body", () => {
    const err = makeAxiosError({
      status: 502,
      statusText: "Bad Gateway",
      data: "upstream unavailable",
    });
    const msg = formatApiError(err, "Failed to load runs");
    expect(msg).toBe(
      "Failed to load runs: 502 Bad Gateway — upstream unavailable (/api/runs)"
    );
  });

  it("replaces an HTML error body with a generic message (no full HTML leak)", () => {
    const err = makeAxiosError({
      status: 502,
      statusText: "Bad Gateway",
      data: "<!DOCTYPE html><html><body><h1>502 Bad Gateway</h1>nginx/1.25.0</body></html>",
    });
    const msg = formatApiError(err, "Failed to load runs");
    expect(msg).toBe(
      "Failed to load runs: 502 Bad Gateway — (non-JSON error body) (/api/runs)"
    );
    expect(msg).not.toContain("<html");
    expect(msg).not.toContain("nginx");
  });

  it("never returns '[object Object]' for an unrecognised object body", () => {
    const err = makeAxiosError({
      status: 500,
      statusText: "Internal Server Error",
      data: { some: "weird", nested: { shape: 1 } },
    });
    const msg = formatApiError(err, "Failed to load runs");
    expect(msg).not.toContain("[object Object]");
    expect(msg).toContain("500 Internal Server Error");
    // The serialised form must be present.
    expect(msg).toContain('"some"');
  });

  it("omits the detail suffix when the body is null", () => {
    const err = makeAxiosError({
      status: 500,
      statusText: "Internal Server Error",
      data: null,
    });
    const msg = formatApiError(err, "Failed to load runs");
    expect(msg).toBe(
      "Failed to load runs: 500 Internal Server Error (/api/runs)"
    );
  });

  it("includes the request URL in the message", () => {
    const err = makeAxiosError({
      status: 404,
      statusText: "Not Found",
      data: { detail: "Run not found" },
      url: "/api/runs/XAUUSD/2026/07/29/result-23.json",
    });
    const msg = formatApiError(err, "Failed to load run result");
    expect(msg).toContain("/api/runs/XAUUSD/2026/07/29/result-23.json");
  });

  it("composes baseURL + url when both are present, without double slashes", () => {
    const err = makeAxiosError({
      status: 400,
      statusText: "Bad Request",
      data: { detail: "x" },
      baseURL: "https://api.example.com/",
      url: "/api/runs",
    });
    const msg = formatApiError(err, "Failed to load runs");
    // No double slash; the path is preserved.
    expect(msg).toContain("https://api.example.com/api/runs");
    expect(msg).not.toContain("api.example.com//api");
  });
});

describe("formatApiError — Axios errors without a response", () => {
  it("reports a network error for ERR_NETWORK with no response", () => {
    const err = makeAxiosError({
      code: "ERR_NETWORK",
      hasResponse: false,
      url: "/api/runs",
    });
    const msg = formatApiError(err, "Failed to load runs");
    expect(msg).toBe(
      "Failed to load runs: network error — could not reach the server (/api/runs)"
    );
  });

  it("falls back to axios message when no request and no code", () => {
    const err = makeAxiosError({
      hasResponse: false,
      hasRequest: false,
      message: "Browser denied request",
    });
    const msg = formatApiError(err, "Failed to load runs");
    expect(msg).toContain("Browser denied request");
    expect(msg).toContain("(/api/runs)");
  });
});

describe("formatApiError — non-Axios throws", () => {
  it("uses Error.message for a generic Error", () => {
    const msg = formatApiError(new Error("boom"), "Failed to load runs");
    expect(msg).toBe("Failed to load runs: boom");
  });

  it("uses the string itself when err is a string", () => {
    const msg = formatApiError("literal failure", "Failed to load runs");
    expect(msg).toBe("Failed to load runs: literal failure");
  });

  it("falls back to the bare prefix for unknown values", () => {
    const msg = formatApiError({ weird: 1 }, "Failed to load runs");
    expect(msg).toContain("Failed to load runs");
    // No "[object Object]" in the message.
    expect(msg).not.toContain("[object Object]");
  });

  it("falls back to the bare prefix for null", () => {
    expect(formatApiError(null, "Failed to load runs")).toBe("Failed to load runs");
  });

  it("falls back to the bare prefix for undefined", () => {
    expect(formatApiError(undefined, "Failed to load runs")).toBe("Failed to load runs");
  });
});
