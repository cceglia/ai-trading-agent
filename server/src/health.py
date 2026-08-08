"""Health and readiness checks for the Trading Analysis server.

Readiness distinguishes the API process itself from the analyzer runtime and
the terminal MCP data source (NFR §18 / ticket 08):

- ``api`` — this process is up and serving requests (always ``ok`` on a 200).
- ``data_root`` — the shared analysis root resolves, exists, and passes a
  write/read roundtrip preflight (NFR-004 / AC-014).
- ``analyzer`` — the analyzer package (``main.py``) and the configured
  ``PYTHON_CMD`` are present, so runs can be spawned.
- ``mcp`` — the terminal MCP endpoint accepts a TCP connection. An
  unavailable MCP is reported as ``mcp=unavailable`` and makes the service
  *not ready*; it is never reported as a valid market signal.

The endpoints live outside ``/api`` so infrastructure probes need no
credentials (``AuthMiddleware`` only guards the ``/api`` surface, see
``docs/server-api-routes.md``).
"""

from __future__ import annotations

import logging
import shutil
import socket
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Probe file name used for the data-root write/read roundtrip.
_PROBE_NAME = ".health-write-probe"


def _default_mcp_probe(url: str, timeout: float = 1.5) -> bool:
    """Return True only when *url*'s host:port accepts a TCP connection.

    The probe is deliberately a lightweight connection test: it never sends
    credentials, never blocks longer than *timeout*, and only proves
    reachability of the data source. It is used to distinguish MCP
    availability from API availability for readiness reporting.
    """
    parsed = urlparse(url)
    host = parsed.hostname
    if not host:
        return False
    try:
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
    except ValueError:
        return False
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def verify_data_root_writable(data_root: Path) -> tuple[bool, str]:
    """Preflight write/read roundtrip on the shared analysis root (AC-014).

    Creates the root (and parents) when missing, writes a small probe file,
    reads it back, and removes it. Returns ``(ok, message)``. A missing or
    unwritable root is a safe failure: no result or signal is claimed, and
    readiness reports the degradation.
    """
    probe = data_root / _PROBE_NAME
    try:
        data_root.mkdir(parents=True, exist_ok=True)
        probe.write_text("ok", encoding="utf-8")
        content = probe.read_text(encoding="utf-8")
        probe.unlink(missing_ok=True)
        if content == "ok":
            return True, "writable"
        return False, "probe content mismatch"
    except OSError as exc:
        logger.error("Data root preflight failed for %s: %s", data_root, exc)
        return False, f"unwritable or unavailable: {exc.__class__.__name__}"


@dataclass(frozen=True)
class HealthReport:
    """Immutable snapshot of one readiness evaluation (NFR §18)."""

    checks: dict[str, str]
    legacy_reads: int = 0

    @property
    def ready(self) -> bool:
        """True only when every check reports ``ok``."""
        return set(self.checks.values()) == {"ok"}


class HealthService:
    """Evaluate server, analyzer, and MCP availability (NFR §18)."""

    def __init__(
        self,
        data_root: Path,
        analyzer_dir: Path,
        python_cmd: str,
        mcp_url: str,
        mcp_probe: Callable[[str], bool] | None = None,
        scanner: Any | None = None,
    ) -> None:
        self._data_root = Path(data_root)
        self._analyzer_dir = Path(analyzer_dir)
        self._python_cmd = python_cmd
        self._mcp_url = mcp_url
        self._mcp_probe = mcp_probe or _default_mcp_probe
        self._scanner = scanner

    def check(self) -> HealthReport:
        """Evaluate all checks and return a snapshot.

        Note: this is a blocking call — it performs a disk write/read
        roundtrip and a synchronous TCP connect (up to 1.5s). Async callers
        must defer it (e.g. ``await asyncio.to_thread(service.check)``) so the
        event loop stays responsive (HEALTH-001).
        """
        checks: dict[str, str] = {}

        ok, msg = verify_data_root_writable(self._data_root)
        checks["data_root"] = "ok" if ok else f"error:{msg}"

        checks["analyzer"] = self._analyzer_check()
        checks["api"] = "ok"
        checks["mcp"] = "ok" if self._mcp_probe(self._mcp_url) else "unavailable"

        legacy_reads = getattr(self._scanner, "legacy_reads", 0) if self._scanner else 0
        return HealthReport(checks=checks, legacy_reads=int(legacy_reads))

    def _analyzer_check(self) -> str:
        if not self._analyzer_dir.is_dir():
            return "error:analyzer directory missing"
        if not (self._analyzer_dir / "main.py").is_file():
            return "error:analyzer main.py missing"
        if shutil.which(self._python_cmd) is None:
            return "error:PYTHON_CMD not found"
        return "ok"
