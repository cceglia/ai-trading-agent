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


class TestModelPricingSettings:
    """Tests for the new model_pricing Settings field.

    These tests will fail RED (AttributeError) until the field is implemented.
    """

    def test_model_pricing_default_is_dict(self):
        """model_pricing defaults to a non-empty dict."""
        settings = Settings()
        assert isinstance(settings.model_pricing, dict)
        assert len(settings.model_pricing) > 0

    def test_model_pricing_has_gpt_4o(self):
        """Default model_pricing contains 'gpt-4o' with 'prompt' and 'completion' keys."""
        settings = Settings()
        assert "gpt-4o" in settings.model_pricing
        entry = settings.model_pricing["gpt-4o"]
        assert "prompt" in entry
        assert "completion" in entry

    def test_model_pricing_from_env_json(self, monkeypatch: pytest.MonkeyPatch):
        """TRADING_MODEL_PRICING JSON env var overrides the default."""
        monkeypatch.setenv(
            "TRADING_MODEL_PRICING",
            '{"gpt-4o": {"prompt": 0.01, "completion": 0.03}}',
        )
        settings = Settings()
        assert settings.model_pricing == {"gpt-4o": {"prompt": 0.01, "completion": 0.03}}

    def test_model_pricing_invalid_env(self, monkeypatch: pytest.MonkeyPatch):
        """Invalid JSON raises a validation error or falls back to default."""
        monkeypatch.setenv("TRADING_MODEL_PRICING", "not-valid-json")
        with pytest.raises(Exception):
            Settings()

    def test_model_pricing_values_positive(self):
        """All price values in model_pricing are > 0."""
        settings = Settings()
        for model, prices in settings.model_pricing.items():
            assert prices["prompt"] > 0, f"{model} prompt price must be positive"
            assert prices["completion"] > 0, f"{model} completion price must be positive"

    def test_zero_price_logs_warning(self, monkeypatch, caplog):
        """Price of exactly 0.0 should log a warning but not be rejected."""
        import logging

        caplog.set_level(logging.WARNING)
        monkeypatch.setenv(
            "TRADING_MODEL_PRICING",
            '{"test-model": {"prompt": 0.0, "completion": 0.01}}',
        )
        settings = Settings()
        # Should be accepted (not raise)
        assert settings.model_pricing["test-model"]["prompt"] == 0.0
        # Should log warning
        assert "zero" in caplog.text.lower() or "0.0" in caplog.text

    def test_no_commented_pricing_lines(self):
        """config/settings.py should not contain commented-out pricing entries."""
        import inspect

        from config.settings import Settings

        source = inspect.getsource(Settings)
        # Check for the specific commented-out DeepSeek line
        assert '# "DeepSeek-V4-Flash"' not in source, "Commented-out pricing line should be removed"


class TestSynthesizerCacheEnabled:
    """Tests for the new synthesizer_cache_enabled Settings field.

    RED phase: these tests will fail RED (AttributeError) until the field is
    implemented in config/settings.py. The pattern mirrors the existing
    TestModelPricingSettings class (notably test_model_pricing_invalid_env)
    for consistency in how invalid env-var values are handled.
    """

    def test_synthesizer_cache_enabled_default_true(self, monkeypatch: pytest.MonkeyPatch):
        """synthesizer_cache_enabled defaults to True when no env var is set."""
        monkeypatch.delenv("TRADING_SYNTHESIZER_CACHE_ENABLED", raising=False)
        assert Settings().synthesizer_cache_enabled is True

    def test_synthesizer_cache_enabled_env_true(self, monkeypatch: pytest.MonkeyPatch):
        """TRADING_SYNTHESIZER_CACHE_ENABLED=true yields True."""
        monkeypatch.setenv("TRADING_SYNTHESIZER_CACHE_ENABLED", "true")
        assert Settings().synthesizer_cache_enabled is True

    def test_synthesizer_cache_enabled_env_false(self, monkeypatch: pytest.MonkeyPatch):
        """TRADING_SYNTHESIZER_CACHE_ENABLED=false yields False."""
        monkeypatch.setenv("TRADING_SYNTHESIZER_CACHE_ENABLED", "false")
        assert Settings().synthesizer_cache_enabled is False

    def test_synthesizer_cache_enabled_env_0(self, monkeypatch: pytest.MonkeyPatch):
        """TRADING_SYNTHESIZER_CACHE_ENABLED=0 yields False (bool coercion)."""
        monkeypatch.setenv("TRADING_SYNTHESIZER_CACHE_ENABLED", "0")
        assert Settings().synthesizer_cache_enabled is False

    def test_synthesizer_cache_enabled_env_invalid_falls_back_or_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        """Invalid TRADING_SYNTHESIZER_CACHE_ENABLED value either raises or falls back to default.

        Mirrors the existing TestModelPricingSettings.test_model_pricing_invalid_env
        pattern: a non-boolean value should not silently coerce to True/False.
        """
        monkeypatch.setenv("TRADING_SYNTHESIZER_CACHE_ENABLED", "banana")
        with pytest.raises(Exception):
            Settings()
