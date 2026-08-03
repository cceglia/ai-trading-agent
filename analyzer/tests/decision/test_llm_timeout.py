"""Regression test: a non-responding LLM upstream fails fast with LLMClientError.

Issue #13: the analyzer pipeline hung indefinitely at the first LLM call
because the OpenAI client was constructed without a ``timeout`` — a provider
that accepts the connection and returns 0 bytes could block the pipeline for
~40 minutes with no log line and no error.

This test points the real :class:`OpenAIProviderAdapter` at a local TCP
server that accepts connections but never responds, with a short per-attempt
timeout, and asserts :class:`LLMClientError` is raised within a bounded time.
No real provider, key, or network is used.
"""

from __future__ import annotations

import socket
import threading
import time
from typing import Any

import pytest
from pydantic import BaseModel

from src.decision.llm_client import LLMClientError, OpenAIProviderAdapter


class _Echo(BaseModel):
    """Minimal response model for the structured output call."""

    value: str


class _HangingServer:
    """TCP server that accepts connections but never sends a response."""

    def __init__(self) -> None:
        self._stop = threading.Event()
        self._connections: list[socket.socket] = []
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind(("127.0.0.1", 0))
        self._sock.listen(5)
        self.port = self._sock.getsockname()[1]
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    def _serve(self) -> None:
        while not self._stop.is_set():
            try:
                conn, _ = self._sock.accept()
            except OSError:
                break
            # Accept the connection but never read from or respond to it, so
            # the client's read timeout is the only way the request can end.
            self._connections.append(conn)

    def close(self) -> None:
        self._stop.set()
        try:
            self._sock.close()
        except OSError:
            pass
        for conn in self._connections:
            try:
                conn.close()
            except OSError:
                pass


@pytest.fixture
def hanging_server() -> Any:
    server = _HangingServer()
    yield server
    server.close()


class TestTimeoutAgainstHangingUpstream:
    """A non-responding upstream must raise LLMClientError within a bounded time."""

    def test_sync_call_fails_fast_with_llm_client_error(self, hanging_server) -> None:
        adapter = OpenAIProviderAdapter(
            api_key="test-key",
            base_url=f"http://127.0.0.1:{hanging_server.port}/v1",
            model="gpt-4o",
            instructor_mode="json_mode",
            timeout=0.5,
            default_max_retries=0,
        )

        started = time.monotonic()
        with pytest.raises(LLMClientError):
            adapter.generate_structured_sync(
                messages=[{"role": "user", "content": "hello"}],
                response_model=_Echo,
            )
        elapsed = time.monotonic() - started

        # Generous bound: a 0.5s per-attempt timeout (plus SDK-internal retries)
        # surfaces in a few seconds at most — never the ~40 minute hang from
        # the original defect.
        assert elapsed < 30, f"hang: LLM call blocked for {elapsed:.1f}s"
