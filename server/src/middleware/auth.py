"""Authentication middleware — validates X-API-Key or trusted proxy marker.

Production contract (FR-035/036, AC-017):

- Every ``/api`` endpoint requires either a valid ``X-API-Key`` (constant-time
  comparison for machine clients) or a proxy-authenticated
  ``X-Authenticated-User`` marker whose request peer address belongs to a
  configured ``TRADING_TRUSTED_PROXY_CIDRS`` network.
- An empty trusted-CIDR setting disables proxy-marker trust (default deny);
  it never means "trust all networks".
- Missing/invalid credentials return a safe 401 before any route executes.
- Non-``/api`` paths (static assets, SPA fallback) are served through the
  trusted proxy and are not blocked here.
- The ``/api`` boundary is case-insensitive: every ``/API``/``/Api`` variant
  is treated as API surface so no path casing can bypass authentication.
- Credential values and raw auth headers are never logged.
"""

from __future__ import annotations

import hmac
import ipaddress
from typing import Any

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

_UNAUTHORIZED_BODY = {"error": "Missing or invalid API key"}


class AuthMiddleware(BaseHTTPMiddleware):
    """Enforce production authentication on every ``/api`` route.

    When neither an API key nor any trusted proxy CIDR is configured, auth is
    explicitly permissive (development mode). Configuring either turns auth on
    for all ``/api`` routes.
    """

    def __init__(
        self,
        app: Any,
        api_key: str = "",
        trusted_proxy_cidrs: list[str] | None = None,
    ) -> None:
        super().__init__(app)
        self._api_key = api_key
        self._trusted_cidrs = tuple(
            ipaddress.ip_network(cidr.strip())
            for cidr in (trusted_proxy_cidrs or [])
            if cidr.strip()
        )
        self._enforced = bool(api_key) or bool(self._trusted_cidrs)

    def _peer_is_trusted(self, request: Request) -> bool:
        """Return True only when the request peer address lies in a trusted CIDR.

        The peer is the address FastAPI sees directly (normally the reverse
        proxy). A non-IP peer or a peer outside every configured network is
        never trusted, so a client-supplied marker cannot spoof identity.
        """
        if not self._trusted_cidrs:
            return False
        host = request.client.host if request.client else None
        if not host:
            return False
        try:
            peer = ipaddress.ip_address(host)
        except ValueError:
            return False
        return any(peer in network for network in self._trusted_cidrs)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Explicit dev mode: no API key and no trusted proxy CIDRs.
        if not self._enforced:
            return await call_next(request)

        # Protect only the API surface; static assets and the SPA fallback are
        # reachable through the trusted proxy. The boundary is case-insensitive
        # so no /API|/Api variant can bypass authentication.
        if not request.url.path.lower().startswith("/api"):
            return await call_next(request)

        api_key = request.headers.get("X-API-Key")
        if self._api_key and api_key and hmac.compare_digest(api_key, self._api_key):
            return await call_next(request)

        marker = request.headers.get("X-Authenticated-User")
        if marker and self._peer_is_trusted(request):
            return await call_next(request)

        # Never log the presented credentials or the raw auth headers.
        return JSONResponse(status_code=401, content=_UNAUTHORIZED_BODY)
