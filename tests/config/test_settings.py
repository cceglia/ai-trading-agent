import pytest

from config.settings import Settings


class TestReasoningEffortSettings:
    """Tests for the new openai_reasoning_effort Settings field.

    These tests will fail RED (AttributeError) until the field is implemented.
    """

    def test_reasoning_effort_default_is_empty_string(self, monkeypatch: pytest.MonkeyPatch):
        """openai_reasoning_effort defaults to empty string (not set)."""
        monkeypatch.setenv("TRADING_OPENAI_REASONING_EFFORT", "")
        assert Settings().openai_reasoning_effort == ""

    def test_reasoning_effort_from_env(self, monkeypatch: pytest.MonkeyPatch):
        """TRADING_OPENAI_REASONING_EFFORT env var overrides the default."""
        monkeypatch.setenv("TRADING_OPENAI_REASONING_EFFORT", "high")
        assert Settings().openai_reasoning_effort == "high"


class TestTerminalSettings:
    """Tests for the new terminal_server_url and terminal_api_key Settings fields.

    These tests will fail RED (AttributeError) until the fields are implemented.
    """

    def test_terminal_server_url_default(self):
        """Settings().terminal_server_url returns the default MCP URL."""
        assert Settings().terminal_server_url == "http://127.0.0.1:22346/mcp"

    def test_terminal_api_key_default(self, monkeypatch: pytest.MonkeyPatch):
        """Settings().terminal_api_key returns empty string by default."""
        monkeypatch.setenv("TRADING_TERMINAL_API_KEY", "")
        assert Settings().terminal_api_key == ""

    def test_terminal_api_key_from_env(self, monkeypatch: pytest.MonkeyPatch):
        """TRADING_TERMINAL_API_KEY env var overrides the default."""
        monkeypatch.setenv("TRADING_TERMINAL_API_KEY", "secret-key-123")
        assert Settings().terminal_api_key == "secret-key-123"

    def test_terminal_server_url_from_env(self, monkeypatch: pytest.MonkeyPatch):
        """TRADING_TERMINAL_SERVER_URL env var overrides the default."""
        monkeypatch.setenv("TRADING_TERMINAL_SERVER_URL", "http://custom-url:9999/mcp")
        assert Settings().terminal_server_url == "http://custom-url:9999/mcp"
