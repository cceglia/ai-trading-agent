# Server `/api` route inventory and input boundaries

Reference for ticket 07 (production API auth/security). This is the complete
inventory of FastAPI routes and their input boundaries as of ticket 05, plus
the production authentication/redaction contract added by ticket 07.

## Authentication and security contract (ticket 07)

Every `/api` route requires one of two credentials whenever auth is enforced
(`TRADING_API_KEY` set **or** `TRADING_TRUSTED_PROXY_CIDRS` set). With both
empty, the server is explicitly permissive (development mode).

- **Machine clients** — `X-API-Key` header, compared with `hmac.compare_digest`
  (constant-time). Missing or invalid key → HTTP 401 before any route/analyzer
  work.
- **Browser/proxy clients** — `X-Authenticated-User` header, trusted **only**
  when the request peer address (`request.client`, the direct socket peer)
  belongs to one of the comma-separated CIDRs in `TRADING_TRUSTED_PROXY_CIDRS`.
  - Default is empty → proxy-marker authentication is disabled (deny), never
    trust-all.
  - A forged marker, a client-supplied marker without proxy rewrite, or a
    marker from an untrusted peer → HTTP 401.
  - The reverse proxy MUST strip any client-supplied `X-Authenticated-User`
    and rewrite it only after authenticating the user. Run FastAPI **without**
    `--proxy-headers`/`ProxyHeadersMiddleware` so `request.client` is the
    reverse proxy's socket address; enabling X-Forwarded-For rewriting would
    replace the peer with an untrusted client IP and break the CIDR check.
- **Non-`/api` paths** (static assets, SPA fallback) are served through the
  trusted proxy and are not blocked by auth. The `/api` boundary is
  **case-insensitive**: `/API`/`/Api` variants are treated as API surface, so
  no path casing can bypass authentication (a missing credential is 401 even
  for `/API/runs`).
- **Redaction** — API keys, proxy markers, provider endpoint URLs/credentials,
  OpenAI-style keys, bearer tokens, Telegram bot tokens, and URL userinfo are
  redacted from all logs (app + root loggers) via `SecretRedactionFilter`;
  errors and responses carry only stable safe messages.
- **CORS** — Only the explicitly configured `CORS_ORIGINS` are allowed, with
  `allow_credentials=True` and methods `GET`/`POST`/`OPTIONS`. Because
  `AuthMiddleware` runs outside `CORSMiddleware`, an `OPTIONS /api/*`
  preflight without a valid credential returns **401 with no
  `Access-Control-Allow-*` headers**. The reverse proxy MUST therefore
  authenticate the preflight (forward `X-API-Key`/rewrite the trusted marker
  for it) or answer CORS itself before forwarding the browser request; the
  FastAPI server deliberately never answers a preflight without a credential
  (uniform method protection, no preflight bypass).

## Routes

| Method | Path | Query/path params | Request body | Response |
|---|---|---|---|---|
| GET | `/api/runs` | `symbol` (optional), `from` (optional), `to` (optional) | — | `list[RunSummary]` |
| GET | `/api/runs/{symbol}/{year}/{month}/{day}/{file}` | — | — | v2 `AnalysisEnvelope` or normalized legacy envelope |
| POST | `/api/run` | — | `RunRequest` | `BatchResponse` |
| any | `/api/{path:path}` | — | — | 404 JSON `{"error": "Not found"}` for unknown API paths (never the SPA fallback) |

## Input boundaries (validated at the route boundary, before any analyzer/disk access)

- **symbol** (`POST symbols`, `GET /api/runs?symbol=`, detail path):
  `^[A-Z0-9]{1,20}$` (case-insensitive). POST symbols are uppercased once and
  deduplicated (first occurrence wins, e.g. `xauusd` + `XAUUSD` run once) and
  key both the batch response and the analyzer invocation (NFR-006 at-most-N).
- **batch size** (`POST /api/run`): 1–20 symbols after dedup; 21+ returns
  HTTP 422 before the runner is spawned.
- **date filters** (`from`/`to`): `^\d{4}-\d{2}-\d{2}$` with month 01–12 and
  day 01–31; violations return HTTP 400.
- **detail path** (`/api/runs/{symbol}/{year}/{month}/{day}/{file}`):
  - `symbol`: `^[A-Z0-9]{1,20}$`
  - `year`: `^\d{4}$`
  - `month`: `^\d{2}$` (01–12)
  - `day`: `^\d{2}$` (01–31)
  - `file`: `^result-\d{2}$` (matches the `result-HH.json` writer naming)
  - violations return HTTP 400; a valid-but-missing file returns 404.
- **request body** (`RunRequest`): `symbols: list[str]` (required), optional
  `model: str`, optional `provider_id: str`. Unknown fields — including any
  free-form `base_url` — are rejected with HTTP 422 (`extra="forbid"`).
- **model**: bound to 1–100 chars of `[A-Za-z0-9][A-Za-z0-9._:/+-]*`; empty,
  over-long, or format-violating values are rejected with HTTP 422.
- **provider_id**: bound to 1–32 chars of `[A-Za-z0-9][A-Za-z0-9._-]*`; empty,
  over-long, or format-violating values are rejected with HTTP 422. Must be a
  configured server-side provider id (`PROVIDER_CONFIG` env, JSON mapping id →
  OpenAI-compatible base URL); unknown ids return HTTP 400 with a generic
  message that never echoes the submitted id. Endpoint URLs and credentials
  never enter request models or responses.

## Status codes

| Code | Condition |
|---|---|
| 200 | Success (GET; batch envelope with `status` = `success`/`partial`/`error`) |
| 400 | Invalid symbols, unknown provider_id, malformed date/file/path params |
| 401 | Missing/invalid `X-API-Key` or untrusted/forged `X-Authenticated-User` |
| 404 | Valid detail path but no result file; unknown `/api/*` path (`{"error": "Not found"}`) |
| 422 | Oversized batch (>20 after dedup) or unknown request fields / invalid model |
| 429 | Rate limit exceeded (POST) — includes `Retry-After` header |
| 500 | Unexpected server failure (`{"error": "..."}` generic, no internals) |

## Batch envelope

`POST /api/run` returns `{"status", "results", "errors"}` where `results` maps
normalized symbol → full v2/legacy envelope and `errors` maps failed symbol →
`{"code", "message"}` (safe codes `SYMBOL_TIMEOUT`, `SYMBOL_PROCESS_FAILED`,
`SYMBOL_NO_RESULT`). `status` is `success`/`partial`/`error` per FR-033.
Process stderr is never surfaced (may contain credentials); error messages
never include exception internals.

Timeouts and process failures never escape `RunService`: they are converted to
per-symbol errors in the batch envelope, so no HTTP 502 is produced. A symbol
whose current run produced no fresh result file is a per-symbol error even if
a stale result file from an earlier run exists (missing-result semantics).
