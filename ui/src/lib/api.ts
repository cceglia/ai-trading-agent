import axios, { type AxiosInstance } from "axios";
import type { RunSummary, FullResult, RunRequest } from "../types";

/**
 * Resolve the API base URL from the `VITE_API_URL` environment variable.
 *
 * This is intentionally a pure function: it does not read `import.meta.env`
 * itself, so it can be unit-tested without stubbing module-level globals.
 * Callers (production code) read the env and pass the value in.
 *
 * Behaviour:
 * - `undefined` / empty / whitespace-only → `""` (same-origin, Vite proxy in dev)
 * - Otherwise → the trimmed value (so accidental trailing spaces in `.env` are dropped)
 */
export function resolveApiBaseURL(value?: string): string {
  return value?.trim() || "";
}

/**
 * Build the default base URL by reading `VITE_API_URL` at the call site.
 * Kept as a separate function so the env lookup is visible and easy to find.
 */
function defaultBaseURL(): string {
  return resolveApiBaseURL(import.meta.env.VITE_API_URL);
}

/**
 * Factory for the shared Axios client. Exposed (alongside the default `api`
 * instance) so tests can verify the wiring without resetting modules.
 */
export function createApiClient(
  baseURL: string = defaultBaseURL()
): AxiosInstance {
  return axios.create({ baseURL });
}

/** Default API client. Uses the Vite proxy in dev (same-origin) and the
 *  FastAPI SPA fallback in production. Override by setting `VITE_API_URL`. */
export const api = createApiClient();

export async function fetchRuns(params?: {
  symbol?: string;
  from?: string;
  to?: string;
}): Promise<RunSummary[]> {
  const { data } = await api.get("/api/runs", { params });
  return data;
}

export async function fetchRunResult(
  symbol: string,
  year: string,
  month: string,
  day: string,
  file: string
): Promise<FullResult> {
  const { data } = await api.get(`/api/runs/${symbol}/${year}/${month}/${day}/${file}`);
  return data;
}

export async function startRun(request: RunRequest): Promise<FullResult[]> {
  const { data } = await api.post("/api/run", request);
  return data;
}
