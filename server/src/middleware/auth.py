"""Authentication middleware — validates X-API-Key header."""

from __future__ import annotations

import hmac

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class AuthMiddleware(BaseHTTPMiddleware):
    """Validates the ``X-API-Key`` header against a configured API key.

    When ``api_key`` is empty the middleware is a no-op (dev mode).
    """

    def __init__(self, app, api_key: str = "") -> None:
        super().__init__(app)
        self._api_key = api_key

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Skip auth when no key is configured (dev mode)
        if not self._api_key:
            return await call_next(request)

        # Only protect POST endpoints
        if request.method != "POST":
            return await call_next(request)

        api_key = request.headers.get("X-API-Key")
        if not api_key or not hmac.compare_digest(api_key, self._api_key):
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=401,
                content={"error": "Missing or invalid API key"},
            )

        return await call_next(request)
