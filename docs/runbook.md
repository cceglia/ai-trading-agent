# Operations Runbook — coordinated v2 release gate (ticket 08)

This runbook covers the operational pieces required by the deterministic
market analysis pipeline v2 release gate: shared data-root verification,
proxy trust/header stripping, legacy read behavior, failed-symbol rerun,
health/readiness semantics, and rollout/rollback order.

The analyzer, server, and UI are released **together** as one coordinated v2
release. The server's legacy read adapter must be deployed **before or with**
the v2 writer. There is no feature flag and no dual-write.

## 1. Shared data root

Analyzer and server must resolve **one absolute data directory**. Relative
`TRADING_ANALYSIS_CACHE_DIR` values are resolved against the project root by
both packages:

- Analyzer: `analyzer/config/settings.py::Settings.resolved_analysis_cache_dir`
- Server: `server/src/settings.py::WebSettings.resolved_cache_dir`

Both resolve the default `data` to `<project_root>/data`; inside Docker the
`.env` sets `TRADING_ANALYSIS_CACHE_DIR=/app/data` and both compose files mount
the host `./data` at `/app/data`.

### Verify the shared root

Run inside the developer container:

```bash
python - <<'PY'
import sys
sys.path.insert(0, "/app/analyzer")
from config.settings import Settings as A
sys.path.remove("/app/analyzer")
from src.settings import WebSettings
a = A().resolved_analysis_cache_dir
s = str(WebSettings().resolved_cache_dir)
print("analyzer:", a)
print("server  :", s)
assert a == s, "MISMATCH — analyzer and server disagree on the data root"
print("SHARED ROOT OK:", a)
PY
```

The release-gate preflight automates this plus the write/read roundtrip, the
v2 scan, the legacy adapter read, the auth checks, and the health/readiness
contract:

```bash
python scripts/verify_release.py
```

### Write permissions

The container runs as the host `UID`/`GID` (compose `user: ${UID:-1000}:${GID:-1000}`).
The bind-mounted `./data` must be owned by that UID/GID, otherwise the analyzer
fails to persist and readiness reports `data_root` as not ready.

- Verify: `ls -ldn data` on the host and compare against the container's
  `id -u`/`id -g`.
- A missing or unwritable root fails the preflight safely: the analyzer CLI
  exits non-zero before any run, and `/readiness` returns 503 with
  `checks.data_root` in an `error:` state. No signal is ever claimed.

> **Compose project name:** both `docker-compose.devel.yml` and
> `docker-compose.prod.yml` share the default project name (the directory
> name). Running both stacks at once makes `docker compose ... up` reconcile the
> same `trading-agent` service and replace the running container. Use one stack
> at a time, or set `COMPOSE_PROJECT_NAME` to separate them.

## 2. Health and readiness

The API liveness and the data-source availability are **distinct** (NFR §18):

| Endpoint | Meaning | Status |
|---|---|---|
| `GET /health` | The API process is up and serving. | always `200` while the process runs |
| `GET /readiness` | The API is up **and** the shared data root is writable, the analyzer package + `PYTHON_CMD` are present, and the terminal MCP endpoint is reachable. | `200` only when every check is `ok`; otherwise `503` |

Both routes live **outside** `/api`, so orchestrators and load balancers can
probe them without credentials (`AuthMiddleware` only guards `/api`).

`GET /readiness` returns:

```json
{
  "ready": false,
  "checks": {
    "api": "ok",
    "data_root": "ok",
    "analyzer": "ok",
    "mcp": "unavailable"
  },
  "legacy_reads": 0,
  "market_signal": null
}
```

- `checks.api` is `ok` whenever the API process is alive — availability of the
  API is never conflated with availability of the analyzer or the MCP data
  source.
- `checks.mcp` reflects a lightweight TCP reachability probe of
  `TRADING_TERMINAL_SERVER_URL`. It never sends credentials and never blocks
  longer than the probe timeout.
- `market_signal` is always `null`: a health surface never emits a market
  signal. When the MCP data source is unavailable, `ready` is `false` and the
  status is `503` — an unavailable MCP can never be interpreted as a valid
  market signal.
- `legacy_reads` is a bounded, process-local counter of legacy files adapted
  since the server started (NFR §18).

The Docker `healthcheck` on both compose files probes `/health` (liveness), so
a down/absent MCP data source never marks a running API container unhealthy.

## 3. Proxy trust and header stripping

The API is authenticated at the `/api` boundary with **either** a machine API
key (`X-API-Key`) **or** a proxy-authenticated browser marker
(`X-Authenticated-User`). Both are enforced only when `TRADING_API_KEY` or
`TRADING_TRUSTED_PROXY_CIDRS` is non-empty; with both empty the server is
explicitly permissive (development mode).

- `TRADING_TRUSTED_PROXY_CIDRS` is a comma-separated list of IP networks (for
  example `10.0.0.0/8`). The marker is trusted **only** when the request peer
  address (the socket peer FastAPI sees — normally the reverse proxy) is inside
  one of those networks. The default is empty = deny; it never means
  "trust all".
- The reverse proxy MUST strip any client-supplied `X-Authenticated-User`
  header and rewrite it only after authenticating the user. FastAPI must run
  **without** `--proxy-headers`/`ProxyHeadersMiddleware`, so `request.client`
  is the proxy's socket address; enabling X-Forwarded-For rewriting would
  replace the peer with an untrusted client IP and break the CIDR check.
- `OPTIONS /api/*` preflight requests also require a credential (uniform method
  protection); the proxy must authenticate/forward them or answer CORS itself.
  See `docs/server-api-routes.md` for the full contract.
- API keys and provider credentials are never logged (server-side
  `SecretRedactionFilter`) and never shipped to the browser bundle.

## 4. Legacy read behavior

Legacy (schema-v1, review-based) result files remain readable but are
**never operational**:

- The server's read-only, idempotent `LegacyAdapter` normalizes a legacy file
  to `schema_version="legacy"`, `validation_status="UNKNOWN"`,
  `operational=false`, `entry_authorized=false`, and drops every `review` /
  `reviewer` / decider field.
- Legacy files are **never mutated** and never trigger notifications.
- Each legacy read emits a `WARNING` log line and increments the bounded
  `legacy_reads` counter surfaced by `/readiness`.
- Malformed JSON is skipped with a safe diagnostic; it is never interpreted as
  valid or operational.
- Decommissioning the adapter is a later, explicitly approved migration; it is
  not part of this release.

## 5. Rerunning failed symbols

A failed symbol is a per-symbol error in the batch envelope
(`SYMBOL_TIMEOUT`, `SYMBOL_PROCESS_FAILED`, `SYMBOL_NO_RESULT`) — it never
fails the whole batch. To rerun:

```bash
curl -X POST http://<host>:3000/api/run \
  -H "X-API-Key: $TRADING_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["XAUUSD"]}'
```

- Rerun only the failed symbols; successful symbols are unaffected (symbol
  isolation, NFR-006 at-most-N).
- A symbol whose current run produced no fresh result file is reported as a
  per-symbol error even if a stale file from an earlier run exists
  (missing-result semantics).
- If the failure was infrastructure (`SYMBOL_TIMEOUT` / `SYMBOL_PROCESS_FAILED`),
  first verify the data root is writable and the MCP source is reachable via
  `/readiness`, then retry.
- Batch size is bounded to 20 symbols; larger batches are rejected with 422
  before any analyzer process is spawned.

## 6. Completion diagnostics and bounded counters

Analyzer completion logs include `symbol`, `run_id`, `schema_version`,
`validation_status`, `setup_status`, `action`, `synthesis_status`,
`execution_status`, and a bounded `error_codes` list, with no secrets and no
raw dumps. One bounded LLM call-count/cost record is logged per symbol
(`llm_calls` / `llm_cost`), and a final `Run metrics:` line aggregates
`analysis_success`, `analysis_degraded`, `analysis_invalid`, `analysis_error`,
`llm_calls`, `notifications_sent`, and `notifications_suppressed`. Counters are
process-local and the symbol label set is bounded.

Warnings are emitted for: legacy reads, cache corruption, invalid deterministic
validation (including stale/broken invalidation rejection), and synthesis
failure.

## 7. Rollout and rollback

**Rollout order**

1. Deploy the server (with the legacy adapter) **before or with** the analyzer
   v2 writer and the UI — a single coordinated release is preferred.
2. Configure one shared absolute data root (production `/app/data`).
3. Configure either a machine API key (`TRADING_API_KEY`) or trusted proxy
   CIDRs (`TRADING_TRUSTED_PROXY_CIDRS`) for browser traffic. Do not expose the
   API key to the Vue bundle.
4. Run the preflight checks (`python scripts/verify_release.py`), the full test
   suites, and the UI build before declaring the release ready.

**Rollback**

- Rollback deploys the previous application version while **retaining** all
  data files. v2 files remain readable only by v2/adapter-aware code, so the
  previous server must still include the legacy adapter for mixed trees.
- Do **not** delete legacy files, v2 files, or ADR history during rollback.
- There is no feature flag or dual-write to flip; revert the image and restart.

## 8. Release preflight checklist (evidence for the gate)

Run all of these inside the developer container with mocked
MT5/MCP/LLM/ForexFactory/Telegram/proxy identity only (no real credentials):

```bash
# Analyzer
cd /app/analyzer && mypy src/ && ruff check src/ && pytest
# Server
cd /app/server && python -m pytest
# UI
cd /app/ui && npm run typecheck && npm run test && npm run build
# Release-gate preflight (shared root, roundtrip, v2 scan, legacy read, auth, health)
cd /app && python scripts/verify_release.py
# API liveness in the running container
curl -fsS http://127.0.0.1:3000/health
```

Record the sanitized diff, test counts, LLM call counts before/after, container
logs, and any remaining issues. Do not claim the release complete if the
critical deterministic regression suites (AC-001, AC-004) fail.
