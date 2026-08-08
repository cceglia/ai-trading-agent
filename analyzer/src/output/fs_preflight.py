"""Preflight filesystem checks for the analysis CLI (NFR §18 / AC-014)."""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Probe file name used for the data-root write/read roundtrip.
_PROBE_NAME = ".analysis-write-probe"


def verify_data_root_writable(data_root: str | Path) -> tuple[bool, str]:
    """Preflight write/read roundtrip on the analysis data root (AC-014).

    Creates the root (and parents) when missing, writes a small probe file,
    reads it back, and removes it. Returns ``(ok, message)``. A missing or
    unwritable root is a safe failure: the CLI refuses to start rather than
    claim a signal it cannot persist.
    """
    root = Path(data_root)
    probe = root / _PROBE_NAME
    try:
        root.mkdir(parents=True, exist_ok=True)
        probe.write_text("ok", encoding="utf-8")
        content = probe.read_text(encoding="utf-8")
        probe.unlink(missing_ok=True)
        if content == "ok":
            return True, "writable"
        return False, "probe content mismatch"
    except OSError as exc:
        logger.error("Data root preflight failed for %s: %s", root, exc)
        return False, f"unwritable or unavailable: {exc.__class__.__name__}"
