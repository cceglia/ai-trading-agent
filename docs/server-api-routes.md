# Server `/api` route inventory and input boundaries

Reference for ticket 07 (production API auth/security). This is the complete
inventory of FastAPI routes and their input boundaries as of ticket 05.

## Routes

| Method | Path | Query/path params | Request body | Response |
|---|---|---|---|---|
| GET | `/api/runs` | `symbol` (optional), `from` (optional), `to` (optional) | — | `list[RunSummary]` |
| GET | `/api/runs/{symbol}/{year}/{month}/{day}/{file}` | — | — | v2 `AnalysisEnvelope` or normalized legacy envelope |
| POST | `/api/run` | — | `RunRequest` | `BatchResponse` |

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
- **provider_id**: must be a configured server-side provider id
  (`PROVIDER_CONFIG` env, JSON mapping id → OpenAI-compatible base URL);
  unknown ids return HTTP 400. Endpoint URLs and credentials never enter
  request models or responses.

## Status codes

| Code | Condition |
|---|---|
| 200 | Success (GET; batch envelope with `status` = `success`/`partial`/`error`) |
| 400 | Invalid symbols, unknown provider_id, malformed date/file/path params |
| 401 | Missing/invalid `X-API-Key` (only when a key is configured) — ticket 07 extends this |
| 404 | Valid detail path but no result file |
| 422 | Oversized batch (>20 after dedup) or unknown request fields / invalid model |
| 429 | Rate limit exceeded (POST) |
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
