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
from src.models import RunRequest, RunSummary
from src.runner import RunService
from src.scanner import ResultScanner
from src.settings import WebSettings

logger = logging.getLogger(__name__)

# Symbol validation regex — matches Node.js behavior
_SYMBOL_RE = re.compile(r"^[A-Z0-9]{1,20}$", re.IGNORECASE)


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

    @app.post("/api/run")
    async def run_analysis(body: RunRequest, request: Request) -> list[dict]:
        # Rate limiting check (keyed by client IP)
        client_key = request.client.host if request.client else "unknown"
        if not rate_limiter.is_allowed(client_key):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        # Validate symbols
        if not body.symbols:
            raise HTTPException(
                status_code=400, detail="symbols must be a non-empty array"
            )
        for sym in body.symbols:
            if not sym:
                raise HTTPException(
                    status_code=400, detail="Each symbol must be a non-empty string"
                )
            if not _SYMBOL_RE.match(sym):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid symbol format: {sym}",
                )

        try:
            return await runner.run_analysis(symbols=body.symbols, model=body.model)
        except Exception as e:
            logger.exception("Analysis failed for symbols: %s", body.symbols)
            raise RuntimeError(str(e)) from e

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
