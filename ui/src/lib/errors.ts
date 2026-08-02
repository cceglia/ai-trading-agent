import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";

/** Cap for serialised unrecognised response bodies. */
const MAX_BODY_CHARS = 200;
/** Cap for plain-string response bodies. */
const MAX_STRING_CHARS = 500;

/** A minimal structural type for the request config we read from an AxiosError. */
interface MinimalRequestConfig {
  url?: string;
  baseURL?: string;
  params?: unknown;
  method?: unknown;
}

/**
 * Build a display-safe request URL from an Axios error config.
 *
 * Prefers `axios.getUri(config)` because it normalises baseURL + url + params
 * without producing missing or duplicate slashes. Falls back to a manual
 * join when the helper is unavailable, and to "(unknown URL)" when both
 * baseURL and url are empty/missing.
 */
function buildRequestURL(config: MinimalRequestConfig | undefined): string {
  if (!config) return "(unknown URL)";
  try {
    const composed = axios.getUri(config as InternalAxiosRequestConfig);
    if (composed) return composed;
  } catch {
    // Fall through to the manual join below.
  }
  const base = (config.baseURL ?? "").toString();
  const url = (config.url ?? "").toString();
  if (!base && !url) return "(unknown URL)";
  if (!base) return url;
  if (!url) return base;
  const trimmedBase = base.replace(/\/+$/, "");
  const trimmedUrl = url.replace(/^\/+/, "");
  return `${trimmedBase}/${trimmedUrl}`;
}

/** Cap a string at `max` characters, appending an ellipsis when truncated. */
function capString(s: string, max: number): string {
  return s.length > max ? `${s.slice(0, max)}…` : s;
}

/**
 * Best-effort JSON serialiser. Returns `""` on any failure or for values
 * that would serialise to `undefined`. Never returns `"[object Object]"`.
 */
function safeStringify(data: unknown, maxChars: number): string {
  if (data === undefined) return "";
  try {
    const text = JSON.stringify(data);
    if (text === undefined) return "";
    return capString(text, maxChars);
  } catch {
    return "";
  }
}

/** Heuristic for HTML error pages (proxy errors, default 502 pages, etc.). */
function looksLikeHTML(s: string): boolean {
  const trimmed = s.trimStart();
  return trimmed.startsWith("<!DOCTYPE") || trimmed.startsWith("<html") || trimmed.startsWith("<HTML");
}

/**
 * Format the response body of an Axios error into a single-line human
 * message. Recognised shapes:
 *
 * - `data.detail` as a string (FastAPI HTTPException with the default handler)
 * - `data.detail` as an array of `{type, loc, msg, input}` (FastAPI RequestValidationError)
 * - `data.error` as a string (FastAPI custom error handlers in this project)
 * - `data.message` as a string
 * - `data` itself being a plain string
 *
 * Anything else is serialised with a length cap. HTML bodies are replaced
 * with a generic "non-JSON error body" message. Returns `null` when no
 * usable detail is present.
 */
function extractErrorDetail(data: unknown): string | null {
  if (data === null || data === undefined) return null;

  if (typeof data === "string") {
    if (looksLikeHTML(data)) return "(non-JSON error body)";
    return capString(data, MAX_STRING_CHARS);
  }

  if (Array.isArray(data)) {
    const items = data
      .map((item) => {
        if (item && typeof item === "object") {
          const obj = item as Record<string, unknown>;
          const loc = Array.isArray(obj.loc) ? obj.loc.join(".") : "";
          const msg = typeof obj.msg === "string" ? obj.msg : safeStringify(item, MAX_BODY_CHARS);
          return loc ? `${loc}: ${msg}` : msg;
        }
        if (typeof item === "string") return item;
        return safeStringify(item, MAX_BODY_CHARS);
      })
      .filter((s) => s && s.length > 0)
      .join("; ");
    return items || null;
  }

  if (typeof data === "object") {
    const obj = data as Record<string, unknown>;

    if ("detail" in obj) {
      const detail = extractErrorDetail(obj.detail);
      if (detail) return detail;
    }
    if (typeof obj.message === "string") return capString(obj.message, MAX_STRING_CHARS);
    if (typeof obj.error === "string") return capString(obj.error, MAX_STRING_CHARS);
    // Unrecognised object body: serialise it as a last resort, with a length cap.
    const serialised = safeStringify(data, MAX_BODY_CHARS);
    if (serialised && serialised !== "null") return serialised;
  }

  return null;
}

/**
 * Normalise any thrown value (typically from an Axios call) into a
 * user-friendly string for the UI. `fallback` is the prefix used when no
 * specific information is available.
 *
 * Examples (assuming fallback = "Failed to load runs"):
 * - Axios 400 with body `{detail: "Invalid symbol"}` →
 *     "Failed to load runs: 400 Bad Request — Invalid symbol (/api/runs)"
 * - Axios network failure (no response) →
 *     "Failed to load runs: network error — could not reach /api/runs"
 * - Generic `throw new Error("boom")` →
 *     "Failed to load runs: boom"
 */
export function formatApiError(err: unknown, fallback: string): string {
  if (axios.isAxiosError(err)) {
    const e = err as AxiosError;
    const url = buildRequestURL(e.config as MinimalRequestConfig | undefined);

    if (e.response) {
      const detail = extractErrorDetail(e.response.data);
      const status = e.response.status;
      const statusText = e.response.statusText || "Request failed";
      if (detail) {
        return `${fallback}: ${status} ${statusText} — ${detail} (${url})`;
      }
      return `${fallback}: ${status} ${statusText} (${url})`;
    }

    // No response. `ERR_NETWORK` is axios's canonical signal for
    // a network-level failure (server down, CORS preflight rejected,
    // DNS error, offline, etc.). Any other axios error without a
    // response is treated as a request-level error and shown verbatim.
    const code = (e.code as string | undefined) ?? "";
    if (code === "ERR_NETWORK") {
      return `${fallback}: network error — could not reach the server (${url})`;
    }
    return `${fallback}: ${e.message} (${url})`;
  }

  if (err instanceof Error) {
    return `${fallback}: ${err.message}`;
  }

  if (typeof err === "string") {
    return `${fallback}: ${err}`;
  }

  if (err === null || err === undefined) {
    return fallback;
  }

  const serialised = safeStringify(err, MAX_BODY_CHARS);
  return serialised ? `${fallback}: ${serialised}` : fallback;
}
