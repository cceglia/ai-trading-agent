"""Health and readiness endpoint tests (NFR §18 / ticket 08)."""

from __future__ import annotations

import asyncio
import sys
import threading
import time
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from src.health import HealthService
from src.main import create_app
from src.scanner import ResultScanner


@pytest.fixture
def health_env(tmp_path: Path, monkeypatch):
    """Configure env so create_app targets a tmp data root and known MCP URL."""
    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("TRADING_TERMINAL_SERVER_URL", "http://127.0.0.1:9/mcp")
    monkeypatch.setenv("PYTHON_CMD", sys.executable)
    monkeypatch.setenv("TRADING_API_KEY", "")
    monkeypatch.setenv("TRADING_TRUSTED_PROXY_CIDRS", "")
    return tmp_path


def _make_client(monkeypatch, *, mcp_ok: bool, api_key: str = "") -> TestClient:
    """Build a TestClient with a controllable MCP probe."""
    monkeypatch.setenv("TRADING_API_KEY", api_key)
    monkeypatch.setattr("src.health._default_mcp_probe", lambda url: mcp_ok)
    return TestClient(create_app())


class TestHealth:
    def test_health_reports_api_liveness(self, health_env, monkeypatch):
        client = _make_client(monkeypatch, mcp_ok=False)
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok", "service": "api"}

    def test_health_is_not_blocked_by_auth(self, health_env, monkeypatch):
        """/health lives outside /api, so it needs no credential while the
        /api surface stays protected (docs/server-api-routes.md)."""
        client = _make_client(monkeypatch, mcp_ok=False, api_key="secret-key")
        assert client.get("/health").status_code == 200
        assert client.get("/api/runs").status_code == 401
        assert (
            client.get("/api/runs", headers={"X-API-Key": "secret-key"}).status_code
            == 200
        )


class TestReadiness:
    def test_readiness_ready_when_all_checks_ok(self, health_env, monkeypatch):
        client = _make_client(monkeypatch, mcp_ok=True)
        resp = client.get("/readiness")
        assert resp.status_code == 200
        body = resp.json()
        assert body["ready"] is True
        assert body["checks"] == {
            "api": "ok",
            "data_root": "ok",
            "analyzer": "ok",
            "mcp": "ok",
        }
        assert body["market_signal"] is None

    def test_readiness_mcp_unavailable_is_503_and_never_a_signal(
        self, health_env, monkeypatch
    ):
        """An unavailable MCP must make readiness degraded/unavailable and must
        never be reported as a valid market signal (NFR §18)."""
        client = _make_client(monkeypatch, mcp_ok=False)
        resp = client.get("/readiness")
        assert resp.status_code == 503
        body = resp.json()
        assert body["ready"] is False
        assert body["checks"]["api"] == "ok"  # API availability is distinct
        assert body["checks"]["mcp"] == "unavailable"
        assert body["checks"]["data_root"] == "ok"
        assert body["market_signal"] is None

    def test_readiness_unwritable_data_root_is_not_ready(self, tmp_path, monkeypatch):
        file = tmp_path / "not-a-dir"
        file.write_text("x")
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", str(file / "sub"))
        monkeypatch.setenv("TRADING_TERMINAL_SERVER_URL", "http://127.0.0.1:9/mcp")
        monkeypatch.setenv("PYTHON_CMD", sys.executable)
        monkeypatch.setenv("TRADING_API_KEY", "")
        monkeypatch.setattr("src.health._default_mcp_probe", lambda url: True)
        resp = TestClient(create_app()).get("/readiness")
        assert resp.status_code == 503
        body = resp.json()
        assert body["ready"] is False
        assert body["checks"]["data_root"].startswith("error:")
        assert body["market_signal"] is None

    def test_readiness_reports_legacy_read_counter(self, tmp_path, monkeypatch):
        """Bounded ``legacy_reads`` counter feeds the readiness payload."""
        legacy = tmp_path / "2026" / "07" / "26" / "XAUUSD" / "result-08.json"
        legacy.parent.mkdir(parents=True)
        legacy.write_text('{"symbol": "XAUUSD", "status": "success"}')
        scanner = ResultScanner(tmp_path)
        assert scanner.get_run("XAUUSD", "2026", "07", "26", "result-08") is not None
        analyzer_dir = tmp_path / "analyzer"
        analyzer_dir.mkdir()
        (analyzer_dir / "main.py").write_text("")
        service = HealthService(
            data_root=tmp_path / "data",
            analyzer_dir=analyzer_dir,
            python_cmd=sys.executable,
            mcp_url="http://127.0.0.1:9/mcp",
            mcp_probe=lambda url: True,
            scanner=scanner,
        )
        report = service.check()
        assert report.ready is True
        assert report.legacy_reads == 1

    def test_readiness_runs_blocking_checks_off_event_loop(
        self, health_env, monkeypatch
    ):
        """HEALTH-001: the disk probe and synchronous TCP connect must not run
        on the event loop thread; ``check()`` is deferred to a worker thread.
        A middleware records the event-loop thread; the MCP probe must run on
        a different thread (proof the route stays non-blocking)."""
        loop_thread: dict[str, int] = {}
        probe_thread: dict[str, int] = {}

        def probe(url: str) -> bool:
            probe_thread["ident"] = threading.get_ident()
            return True

        monkeypatch.setattr("src.health._default_mcp_probe", probe)
        app = create_app()

        @app.middleware("http")
        async def record_loop_thread(request, call_next):
            loop_thread["ident"] = threading.get_ident()
            return await call_next(request)

        resp = TestClient(app).get("/readiness")
        assert resp.status_code == 200
        assert loop_thread["ident"] != probe_thread["ident"]

    async def test_readiness_offloads_blocking_check_so_other_routes_stay_responsive(
        self, health_env, monkeypatch
    ):
        """HEALTH-001: while /readiness blocks on a slow MCP probe, /health
        must still answer immediately — evidence the event loop is not stalled."""

        def slow_probe(url: str) -> bool:
            time.sleep(1.0)
            return True

        monkeypatch.setattr("src.health._default_mcp_probe", slow_probe)
        app = create_app()
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            readiness_task = asyncio.create_task(client.get("/readiness"))
            await asyncio.sleep(0.05)
            health_task = asyncio.create_task(client.get("/health"))
            done, _ = await asyncio.wait(
                {readiness_task, health_task},
                return_when=asyncio.FIRST_COMPLETED,
            )
            # /health must win: it is served by the event loop while /readiness
            # is blocked in a worker thread.
            assert health_task in done
            assert readiness_task not in done
            assert health_task.result().status_code == 200


class TestHealthServiceAnalyzerCheck:
    def test_analyzer_missing_directory(self, tmp_path):
        service = HealthService(
            data_root=tmp_path,
            analyzer_dir=tmp_path / "missing",
            python_cmd=sys.executable,
            mcp_url="",
            mcp_probe=lambda url: True,
        )
        report = service.check()
        assert report.checks["analyzer"].startswith("error:")
        assert report.ready is False

    def test_analyzer_missing_main_py(self, tmp_path):
        analyzer_dir = tmp_path / "analyzer"
        analyzer_dir.mkdir()
        service = HealthService(
            data_root=tmp_path,
            analyzer_dir=analyzer_dir,
            python_cmd=sys.executable,
            mcp_url="",
            mcp_probe=lambda url: True,
        )
        report = service.check()
        assert report.checks["analyzer"] == "error:analyzer main.py missing"

    def test_analyzer_missing_python_cmd(self, tmp_path):
        analyzer_dir = tmp_path / "analyzer"
        analyzer_dir.mkdir()
        (analyzer_dir / "main.py").write_text("")
        service = HealthService(
            data_root=tmp_path,
            analyzer_dir=analyzer_dir,
            python_cmd="definitely-not-a-real-command-xyz",
            mcp_url="",
            mcp_probe=lambda url: True,
        )
        report = service.check()
        assert report.checks["analyzer"] == "error:PYTHON_CMD not found"
