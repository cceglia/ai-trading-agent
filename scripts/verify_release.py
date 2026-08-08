#!/usr/bin/env python3
"""Release-gate preflight for ticket 08 (Docker observability + release gate).

Runs inside the developer container with no real external credentials
(mocked/terminal data only). It verifies, in order:

1.  Shared data root — analyzer and server resolve the same absolute root.
2.  Data-root write/read roundtrip preflight.
3.  AC-014/TEST-014 — analyzer writes a synthetic schema-v2 envelope into the
    shared root and the server scanner immediately discovers the same file.
4.  AC-015 — a legacy fixture is returned as non-operational UNKNOWN with no
    review fields through the read-only legacy adapter.
5.  AC-017 — with an API key configured, ``/api/runs`` is 401 without a key
    and 200 with it; ``/health`` stays reachable without credentials.
6.  NFR §18 — ``/readiness`` distinguishes api/data_root/analyzer/mcp and never
    reports a market signal when MCP is unavailable.

Exit code 0 on success; 1 with a message on the first failure.

Usage:
    python scripts/verify_release.py [--data-dir PATH]
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ANALYZER_DIR = REPO_ROOT / "analyzer"
SERVER_DIR = REPO_ROOT / "server"

_FAILED: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    """Record a PASS/FAIL check."""
    status = "PASS" if ok else "FAIL"
    suffix = f" — {detail}" if detail else ""
    print(f"[{status}] {name}{suffix}")
    if not ok:
        _FAILED.append(name)


def _load_server_src() -> None:
    """Map the top-level ``src`` package to the server package.

    Both analyzer and server are installed editable and register meta-path
    finders that map ``src`` (analyzer's wins). We already imported the
    analyzer modules we need, so ``sys.modules["src"]`` can be re-pointed at
    the server's ``src`` package before any server import.
    """
    import importlib.util
    import sys
    from importlib.machinery import ModuleSpec, SourceFileLoader

    pkg_dir = SERVER_DIR / "src"
    init_path = pkg_dir / "__init__.py"
    loader = SourceFileLoader("src", str(init_path))
    spec = ModuleSpec("src", loader, is_package=True)
    spec.submodule_search_locations = [str(pkg_dir)]
    pkg = importlib.util.module_from_spec(spec)
    sys.modules["src"] = pkg
    loader.exec_module(pkg)


def main() -> int:
    parser = argparse.ArgumentParser(description="Release-gate preflight (ticket 08)")
    parser.add_argument(
        "--data-dir", default=None, help="Override the shared data root"
    )
    args = parser.parse_args()

    # Analyzer Settings reads ``.env`` relative to the CWD; run from the
    # analyzer directory so a repo-root ``.env`` (which carries server-only
    # vars) is never picked up. Environment-variable sources are unaffected.
    os.chdir(ANALYZER_DIR)

    # --- Import analyzer modules first (analyzer's ``src`` wins here) ---
    sys.path.insert(0, str(ANALYZER_DIR))
    from config.settings import Settings as AnalyzerSettings
    from src.output.fs_preflight import verify_data_root_writable
    from src.output.result_models import (
        AnalysisResult,
        OHLCBar,
        SLTPOverlay,
    )
    from src.output.result_writer import ResultWriter
    from src.output.run_metrics import RunMetrics

    sys.path.remove(str(ANALYZER_DIR))

    # --- Now load the server package under ``src`` and import its modules ---
    _load_server_src()
    from fastapi.testclient import TestClient
    from src.main import create_app
    from src.scanner import ResultScanner
    from src.settings import WebSettings

    analyzer_root = AnalyzerSettings().resolved_analysis_cache_dir
    server_root = str(WebSettings().resolved_cache_dir)
    data_root = Path(args.data_dir or server_root)

    print("== Ticket 08 release-gate preflight ==")
    print(f"analyzer root : {analyzer_root}")
    print(f"server root   : {server_root}")
    print(f"data root used: {data_root}")

    # 1. Shared data root (NFR-004 / AC-014)
    if args.data_dir:
        check("shared-root equality (skipped: --data-dir given)", True, data_root)
    else:
        check(
            "shared-root equality (analyzer == server)",
            analyzer_root == server_root,
            f"{analyzer_root} vs {server_root}",
        )

    # 2. Preflight write/read roundtrip on both resolved roots
    analyzer_ok, analyzer_msg = verify_data_root_writable(analyzer_root)
    server_ok, server_msg = verify_data_root_writable(server_root)
    check("analyzer data-root write/read roundtrip", analyzer_ok, analyzer_msg)
    check("server data-root write/read roundtrip", server_ok, server_msg)

    # 3. AC-014/TEST-014: analyzer write -> server scanner immediate discovery
    broker_now = datetime(2026, 7, 26, 8, 30, tzinfo=timezone.utc)
    symbol = "AC014"
    writer = ResultWriter(data_root)
    analysis_result = AnalysisResult(
        symbol=symbol,
        run_id=f"{symbol}-20260726083000",
        started_at=broker_now,
        completed_at=broker_now,
        status="success",
        sl_tp_overlay=SLTPOverlay(),
    )
    result: dict = {
        "analysis_result": analysis_result,
        "errors": [],
        "fatal_error": None,
    }
    ohlc: dict = {
        "D1": [
            OHLCBar(
                time="2026-07-25T17:00",
                open=2350.0,
                high=2370.0,
                low=2345.0,
                close=2365.5,
            )
        ],
    }
    written = writer.write(symbol, result, ohlc, broker_now)
    check("analyzer wrote schema-v2 envelope", written is not None and written.exists())

    scanner = ResultScanner(data_root)
    summary = scanner.list_runs(symbol=symbol)
    check("scanner discovers v2 file immediately", bool(summary), str(summary))
    v2 = scanner.get_run(symbol, "2026", "07", "26", "result-08")
    check(
        "same absolute file is readable as schema v2",
        v2 is not None and v2.get("schema_version") == "2",
        str(written),
    )

    # 4. AC-015: legacy adapter read is read-only, non-operational, review-free
    legacy_path = data_root / "2026" / "07" / "26" / "AC015LEG" / "result-09.json"
    legacy_path.parent.mkdir(parents=True, exist_ok=True)
    legacy_path.write_text(
        '{"symbol": "AC015LEG", "status": "success", "market_context": '
        '{"bias": "bullish"}, "decision": {"action": "buy_setup"}, '
        '"review": {"status": "APPROVED", "approved": true}}',
        encoding="utf-8",
    )
    legacy = scanner.get_run("AC015LEG", "2026", "07", "26", "result-09")
    legacy_facts = (legacy or {}).get("deterministic_facts") or {}
    check(
        "legacy adapter returns non-operational UNKNOWN",
        legacy is not None
        and legacy.get("schema_version") == "legacy"
        and legacy_facts.get("validation_status") == "UNKNOWN"
        and legacy_facts.get("operational") is False,
    )
    check(
        "legacy read drops review fields",
        legacy is not None and "review" not in legacy and "reviewer" not in str(legacy),
    )
    check(
        "legacy read counted",
        scanner.legacy_reads >= 1,
        f"legacy_reads={scanner.legacy_reads}",
    )

    # 5. AC-017: auth is enforced on /api but /health is probe-reachable
    os.environ["TRADING_API_KEY"] = "verify-test-key"
    app = create_app()
    client = TestClient(app)
    unauth = client.get("/api/runs")
    auth_ok = client.get("/api/runs", headers={"X-API-Key": "verify-test-key"})
    health = client.get("/health")
    check(
        "auth: /api/runs 401 without key",
        unauth.status_code == 401,
        f"got {unauth.status_code}",
    )
    check(
        "auth: /api/runs 200 with key",
        auth_ok.status_code == 200,
        f"got {auth_ok.status_code}",
    )
    check(
        "auth: /health reachable without credential",
        health.status_code == 200,
        f"got {health.status_code}",
    )
    del os.environ["TRADING_API_KEY"]

    # 6. NFR §18: readiness distinguishes API/analyzer/MCP; no market signal
    readiness = client.get("/readiness")
    body = readiness.json()
    check(
        "readiness exposes all four checks",
        {"api", "data_root", "analyzer", "mcp"} <= set(body.get("checks", {})),
    )
    check("readiness never emits a market signal", body.get("market_signal") is None)
    check(
        "readiness distinguishes API from MCP",
        body.get("checks", {}).get("api") == "ok"
        and body.get("checks", {}).get("mcp") in ("ok", "unavailable"),
        f"api={body.get('checks', {}).get('api')} mcp={body.get('checks', {}).get('mcp')}",
    )
    if body.get("checks", {}).get("mcp") != "ok":
        check(
            "readiness not ready when MCP unavailable",
            body.get("ready") is False and readiness.status_code == 503,
            f"ready={body.get('ready')} status={readiness.status_code}",
        )

    # Bounded counters still aggregate and emit one summary line
    metrics = RunMetrics()
    metrics.record("AC014", "success", result)
    metrics.llm_calls = 0
    metrics.log_summary()
    check("bounded run metrics aggregate", metrics._outcomes["analysis_success"] == 1)

    # --- Cleanup the probe symbols from the shared root ---
    for cleanup in (
        data_root / "2026" / "07" / "26" / symbol,
        data_root / "2026" / "07" / "26" / "AC015LEG",
    ):
        if cleanup.is_dir():
            for p in sorted(cleanup.rglob("*"), reverse=True):
                if p.is_file():
                    p.unlink()
            cleanup.rmdir()
    print()

    if _FAILED:
        print("PREFLIGHT FAILED:", ", ".join(_FAILED))
        return 1
    print("PREFLIGHT PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
