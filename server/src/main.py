"""FastAPI application entry point — port of the TypeScript Express server."""

from __future__ import annotations

import logging
import re
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from src.middleware.auth import AuthMiddleware
from src.middleware.ratelimit import SlidingWindowRateLimiter
from src.models import BatchResponse, RunRequest, RunSummary
from src.redaction import SecretRedactionFilter
from src.runner import RunService
from src.scanner import ResultScanner
from src.settings import WebSettings

logger = logging.getLogger(__name__)

# Symbol validation regex — matches Node.js behavior
_SYMBOL_RE = re.compile(r"^[A-Z0-9]{1,20}$", re.IGNORECASE)

# Path-component bounds for the detail route (FR-034 / §16): strict formats
# reject path traversal and arbitrary file reads before any disk access.
_YEAR_RE = re.compile(r"^\d{4}$")
_MONTH_RE = re.compile(r"^\d{2}$")
_DAY_RE = re.compile(r"^\d{2}$")
_FILE_RE = re.compile(r"^result-\d{2}$")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

MAX_BATCH_SYMBOLS = 20

# Loggers the server code emits through; the redaction filter is attached to
# each of these (plus the root logger) so no credential reaches a handler.
_APP_LOGGER_NAMES = ("src.main", "src.runner", "src.scanner")


def install_secret_redaction(secrets: tuple[str, ...]) -> None:
    """Attach a fresh redaction filter to the app and root loggers (FR-038).

    Replaces any previously installed filter so the current settings' secrets
    stay authoritative (tests create apps with different credentials).
    """
    redaction_filter = SecretRedactionFilter(secrets)
    targets = [logging.getLogger(name) for name in _APP_LOGGER_NAMES]
    targets.append(logging.getLogger())
    for log_target in targets:
        for existing in [
            f for f in log_target.filters if isinstance(f, SecretRedactionFilter)
        ]:
            log_target.removeFilter(existing)
        log_target.addFilter(redaction_filter)


def validate_symbols(symbols: list[str]) -> list[str]:
    """Validate and normalize a batch symbol list (400 on invalid input).

    Returns the symbols uppercased and deduplicated, preserving first-occurrence
    order — normalization happens exactly once here and the result keys the
    batch response and the analyzer invocation (NFR-006 at-most-N per symbol).
    """
    if not symbols:
        raise HTTPException(status_code=400, detail="symbols must be a non-empty array")
    normalized: list[str] = []
    seen: set[str] = set()
    for sym in symbols:
        if not sym:
            raise HTTPException(
                status_code=400, detail="Each symbol must be a non-empty string"
            )
        if not _SYMBOL_RE.match(sym):
            raise HTTPException(status_code=400, detail="Invalid symbol format")
        upper = sym.upper()
        if upper not in seen:
            seen.add(upper)
            normalized.append(upper)
    return normalized


def validate_date_param(value: str | None, name: str) -> None:
    """Validate a YYYY-MM-DD query filter (400 on malformed input)."""
    if value is None:
        return
    if not _DATE_RE.match(value):
        raise HTTPException(
            status_code=400, detail=f"Invalid {name} (expected YYYY-MM-DD)"
        )
    _year, month, day = value.split("-")
    if not (1 <= int(month) <= 12) or not (1 <= int(day) <= 31):
        raise HTTPException(
            status_code=400, detail=f"Invalid {name} (expected YYYY-MM-DD)"
        )


def validate_run_path_params(
    symbol: str, year: str, month: str, day: str, file: str
) -> None:
    """Validate detail-route path components against traversal and bounded
    formats at the route boundary (400 on any violation)."""
    if not _SYMBOL_RE.match(symbol):
        raise HTTPException(status_code=400, detail="Invalid symbol path component")
    if not _YEAR_RE.match(year):
        raise HTTPException(status_code=400, detail="Invalid year (expected YYYY)")
    if not _MONTH_RE.match(month) or not (1 <= int(month) <= 12):
        raise HTTPException(status_code=400, detail="Invalid month (expected MM 01-12)")
    if not _DAY_RE.match(day) or not (1 <= int(day) <= 31):
        raise HTTPException(status_code=400, detail="Invalid day (expected DD 01-31)")
    if not _FILE_RE.match(file):
        raise HTTPException(
            status_code=400, detail="Invalid result file (expected result-HH)"
        )


def resolve_provider_base_url(
    settings: WebSettings, provider_id: str | None
) -> str | None:
    """Resolve a provider_id to its server-side base URL (FR-039 / DEC-014).

    The request never carries a URL or credentials; unknown provider ids are
    rejected with 400 before the analyzer process is spawned.
    """
    if provider_id is None:
        return None
    url = settings.provider_config.get(provider_id)
    if url is None:
        # Generic stable message: never echo the submitted provider id.
        raise HTTPException(status_code=400, detail="Unknown provider_id")
    return url


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = WebSettings()

    # Install credential redaction before any request can be logged (FR-038).
    # Server-side secrets: the machine API key and configured provider URLs
    # (which may embed credentials). Generic shapes are handled by the filter.
    install_secret_redaction((settings.api_key, *settings.provider_config.values()))

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup: nothing to initialize currently
        yield
        # Shutdown: nothing to clean up currently

    app = FastAPI(title="Trading Analysis Server", lifespan=lifespan)

    # Rate limiter instance (shared across requests)
    rate_limiter = SlidingWindowRateLimiter(
        max_requests=settings.rate_limit_max,
        window_seconds=settings.rate_limit_window,
    )

    # CORS middleware — only explicitly configured origins are allowed.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-API-Key"],
    )

    # Auth middleware: enforced on every /api route when an API key or a
    # trusted proxy CIDR is configured (permissive dev mode otherwise).
    app.add_middleware(  # type: ignore[arg-type]
        AuthMiddleware,
        api_key=settings.api_key,
        trusted_proxy_cidrs=settings.trusted_proxy_cidrs,
    )

    # Create scanner and runner instances
    scanner = ResultScanner(settings.resolved_cache_dir)
    runner = RunService(
        python_cmd=settings.python_cmd,
        analyzer_dir=str(Path(__file__).resolve().parent.parent.parent / "analyzer"),
        data_dir=str(settings.resolved_cache_dir),
    )

    # --- Routes ---

    @app.get("/api/runs")
    async def list_runs(
        symbol: str | None = Query(default=None),
        from_date: str | None = Query(default=None, alias="from"),
        to_date: str | None = Query(default=None, alias="to"),
    ) -> list[RunSummary]:
        if symbol is not None and not _SYMBOL_RE.match(symbol):
            raise HTTPException(status_code=400, detail="Invalid symbol filter")
        validate_date_param(from_date, "from")
        validate_date_param(to_date, "to")
        try:
            return scanner.list_runs(
                symbol=symbol, from_date=from_date, to_date=to_date
            )
        except Exception as e:
            logger.exception("Failed to list runs")
            raise RuntimeError("Failed to list runs") from e

    @app.get("/api/runs/{symbol}/{year}/{month}/{day}/{file}")
    async def get_run(
        symbol: str,
        year: str,
        month: str,
        day: str,
        file: str,
    ) -> dict:
        validate_run_path_params(symbol, year, month, day, file)
        try:
            result = scanner.get_run(symbol, year, month, day, file)
            if result is None:
                raise HTTPException(status_code=404, detail="Run not found")
            return result
        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Failed to get run")
            raise RuntimeError("Failed to get run") from e

    @app.post("/api/run", response_model=BatchResponse)
    async def run_analysis(body: RunRequest, request: Request) -> BatchResponse:
        # Rate limiting check (keyed by client IP)
        client_key = request.client.host if request.client else "unknown"
        if not rate_limiter.is_allowed(client_key):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded",
                headers={
                    "Retry-After": str(rate_limiter.retry_after_seconds(client_key))
                },
            )

        # Validate and normalize symbols once; reject invalid input with 400.
        symbols = validate_symbols(body.symbols)

        # Enforce the batch bound before the analyzer process is spawned (FR-033a).
        if len(symbols) > MAX_BATCH_SYMBOLS:
            raise HTTPException(
                status_code=422,
                detail=f"Maximum {MAX_BATCH_SYMBOLS} symbols per batch",
            )

        # Resolve a configured provider endpoint server-side; no free-form URL.
        base_url = resolve_provider_base_url(settings, body.provider_id)

        try:
            outcome = await runner.run_analysis(
                symbols=symbols, model=body.model, base_url=base_url
            )
        except Exception as e:
            logger.exception("Analysis failed for symbols: %s", symbols)
            raise RuntimeError("Analysis failed") from e

        return BatchResponse(
            status=outcome.status,
            results=outcome.results,
            errors=outcome.errors,
        )

    # Catch-all for unknown /api/* paths (API-002): return a stable 404 JSON
    # for every method instead of falling through to the SPA fallback (which
    # would answer 200 text/html for authenticated requests to a typo'd API
    # path). Registered after the real routes so they keep precedence.
    @app.api_route(
        "/api/{path:path}",
        methods=["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )
    async def api_not_found(path: str):
        raise HTTPException(status_code=404, detail="Not found")

    # --- Error handlers ---
    @app.exception_handler(RuntimeError)
    async def runtime_error_handler(_request, exc: RuntimeError):
        # Messages here are the safe stable strings raised by the routes; the
        # original exception is logged (redacted) before it is re-raised.
        return JSONResponse(status_code=500, content={"error": str(exc)})

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_request, exc):
        # Preserve any explicit headers (e.g. Retry-After on 429).
        headers = dict(exc.headers or {})
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail},
            headers=headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_request, exc: RequestValidationError):
        # Never echo raw request input back (may carry credentials/URLs).
        return JSONResponse(
            status_code=422, content={"error": "Invalid request payload"}
        )

    # --- Static files (production) ---
    ui_dist = Path(__file__).resolve().parent.parent.parent / "ui" / "dist"
    if ui_dist.exists() and (ui_dist / "index.html").exists():
        app.mount(
            "/assets", StaticFiles(directory=str(ui_dist / "assets")), name="assets"
        )

        @app.get("/{full_path:path}")
        async def spa_fallback(full_path: str):
            # Serve index.html for all non-API routes (SPA fallback)
            index = ui_dist / "index.html"
            if index.exists():
                return FileResponse(str(index))
            return HTMLResponse("<h1>Trading Analysis Server</h1>")

    return app


# For uvicorn: uvicorn src.main:app --reload
app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = WebSettings()
    uvicorn.run(app, host=settings.host, port=settings.port)
