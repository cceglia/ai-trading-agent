"""FastAPI application entry point — port of the TypeScript Express server."""

from __future__ import annotations

import logging
import re
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from src.middleware.auth import AuthMiddleware
from src.middleware.ratelimit import SlidingWindowRateLimiter
from src.models import BatchResponse, RunRequest, RunSummary
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
            raise HTTPException(status_code=400, detail=f"Invalid symbol format: {sym}")
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
        raise HTTPException(
            status_code=400, detail=f"Unknown provider_id: {provider_id}"
        )
    return url


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = WebSettings()

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

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-API-Key"],
    )

    # Auth middleware (conditional — no-op when api_key is empty)
    app.add_middleware(AuthMiddleware, api_key=settings.api_key)  # type: ignore[arg-type]

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
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

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

    # --- Error handlers ---
    @app.exception_handler(RuntimeError)
    async def runtime_error_handler(request, exc: RuntimeError):
        return JSONResponse(status_code=500, content={"error": str(exc)})

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_request, exc):
        return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

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
