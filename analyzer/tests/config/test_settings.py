import pytest

from config.settings import Settings


class TestResolvedAnalysisCacheDir:
    """Tests for the ``resolved_analysis_cache_dir`` property.

    Both the analyzer and server write/read from the same directory tree.
    Relative paths are resolved against the **project root** (the parent
    directory of ``analyzer/``) so that the default ``"data"`` produces
    ``<project_root>/data`` regardless of which package is the working
    directory.
    """

    @staticmethod
    def _project_root():
        """Compute the project root from the test file location.

        Mirror the same traversal the source uses:
        ``analyzer/tests/config/test_settings.py → parent.parent.parent.parent → project root``.
        """
        from pathlib import Path

        return Path(__file__).resolve().parent.parent.parent.parent

    def test_default_resolves_to_project_root_data(self, monkeypatch: pytest.MonkeyPatch):
        """Default ``analysis_cache_dir="data"`` resolves to ``<project_root>/data``."""
        monkeypatch.delenv("TRADING_ANALYSIS_CACHE_DIR", raising=False)
        settings = Settings()
        expected = str(self._project_root() / "data")
        assert settings.resolved_analysis_cache_dir == expected

    def test_relative_path_resolves_from_project_root(self, monkeypatch: pytest.MonkeyPatch):
        """A relative path resolves against the project root, not CWD."""
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", "custom/cache")
        settings = Settings()
        expected = str(self._project_root() / "custom" / "cache")
        assert settings.resolved_analysis_cache_dir == expected

    def test_absolute_path_returned_unchanged(self, monkeypatch: pytest.MonkeyPatch):
        """An absolute path is returned as-is."""
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", "/tmp/test_cache")
        settings = Settings()
        assert settings.resolved_analysis_cache_dir == "/tmp/test_cache"

    def test_absolute_path_from_env(self, monkeypatch: pytest.MonkeyPatch):
        """Setting ``TRADING_ANALYSIS_CACHE_DIR`` to an absolute value must
        be returned as-is."""
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", "/var/trade/cache")
        settings = Settings()
        assert settings.resolved_analysis_cache_dir == "/var/trade/cache"

    def test_matches_server_default(self, monkeypatch: pytest.MonkeyPatch):
        """Analyzer and server must resolve the same default to the same path."""
        import importlib
        import sys

        monkeypatch.delenv("TRADING_ANALYSIS_CACHE_DIR", raising=False)
        analyzer_path = Settings().resolved_analysis_cache_dir

        # Import server settings from sibling package using importlib to avoid
        # collision with the analyzer's own ``src`` package.
        server_settings_path = str(self._project_root() / "server" / "src" / "settings.py")
        spec = importlib.util.spec_from_file_location("server_src_settings", server_settings_path)
        if spec is None or spec.loader is None:
            pytest.skip("Could not load server settings module")
        mod = importlib.util.module_from_spec(spec)
        sys.modules["server_src_settings"] = mod
        try:
            spec.loader.exec_module(mod)
            server_path = str(mod.WebSettings().resolved_cache_dir)
            assert analyzer_path == server_path
        finally:
            sys.modules.pop("server_src_settings", None)


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


class TestOpenAITemperatureSettings:
    """Tests for the openai_temperature Settings field.

    These tests verify that the field is properly defined, has the correct
    default, and respects env-var overrides within the 0.0–2.0 range.
    """

    def test_openai_temperature_default_is_zero(self, monkeypatch: pytest.MonkeyPatch):
        """openai_temperature defaults to 0.0."""
        monkeypatch.delenv("TRADING_OPENAI_TEMPERATURE", raising=False)
        assert Settings().openai_temperature == 0.0

    def test_openai_temperature_from_env(self, monkeypatch: pytest.MonkeyPatch):
        """TRADING_OPENAI_TEMPERATURE env var overrides the default."""
        monkeypatch.setenv("TRADING_OPENAI_TEMPERATURE", "0.7")
        assert Settings().openai_temperature == 0.7

    def test_openai_temperature_zero(self, monkeypatch: pytest.MonkeyPatch):
        """openai_temperature = 0.0 is valid (lower bound)."""
        monkeypatch.setenv("TRADING_OPENAI_TEMPERATURE", "0.0")
        assert Settings().openai_temperature == 0.0

    def test_openai_temperature_two(self, monkeypatch: pytest.MonkeyPatch):
        """openai_temperature = 2.0 is valid (upper bound)."""
        monkeypatch.setenv("TRADING_OPENAI_TEMPERATURE", "2.0")
        assert Settings().openai_temperature == 2.0

    def test_openai_temperature_one(self, monkeypatch: pytest.MonkeyPatch):
        """openai_temperature = 1.0 is valid (mid-range)."""
        monkeypatch.setenv("TRADING_OPENAI_TEMPERATURE", "1.0")
        assert Settings().openai_temperature == 1.0


class TestTerminalSettings:
    """Tests for the new terminal_server_url and terminal_api_key Settings fields.

    These tests will fail RED (AttributeError) until the fields are implemented.
    """

    def test_terminal_server_url_default(self, monkeypatch: pytest.MonkeyPatch):
        """Settings().terminal_server_url returns the default MCP URL."""
        # Ensure the default is used regardless of env (Docker sets host.docker.internal)
        monkeypatch.setenv("TRADING_TERMINAL_SERVER_URL", "http://127.0.0.1:22346/mcp")
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
        """Default model_pricing contains 'gpt-4o' with new format keys."""
        settings = Settings()
        assert "gpt-4o" in settings.model_pricing
        entry = settings.model_pricing["gpt-4o"]
        assert "input_per_million" in entry
        assert "cached_input_per_million" in entry
        assert "output_per_million" in entry

    def test_model_pricing_from_env_json(self, monkeypatch: pytest.MonkeyPatch):
        """TRADING_MODEL_PRICING JSON env var overrides the default (new format)."""
        monkeypatch.setenv(
            "TRADING_MODEL_PRICING",
            '{"gpt-4o": {"input_per_million": 2.5, '
            '"cached_input_per_million": 1.25, "output_per_million": 10.0}}',
        )
        settings = Settings()
        assert settings.model_pricing == {
            "gpt-4o": {
                "input_per_million": 2.5,
                "cached_input_per_million": 1.25,
                "output_per_million": 10.0,
            },
        }

    def test_model_pricing_invalid_env(self, monkeypatch: pytest.MonkeyPatch):
        """Invalid JSON raises a validation error."""
        monkeypatch.setenv("TRADING_MODEL_PRICING", "not-valid-json")
        with pytest.raises(Exception):
            Settings()

    def test_model_pricing_values_positive(self):
        """All price values in model_pricing are >= 0."""
        settings = Settings()
        for model, prices in settings.model_pricing.items():
            for key in ("input_per_million", "cached_input_per_million", "output_per_million"):
                val = prices.get(key)
                if val is not None:
                    assert val >= 0, f"{model} {key} must be >= 0, got {val}"

    def test_zero_price_accepted(self, monkeypatch):
        """Price of exactly 0.0 is accepted silently (valid configuration)."""
        monkeypatch.setenv(
            "TRADING_MODEL_PRICING",
            '{"test-model": {"input_per_million": 0.0, '
            '"cached_input_per_million": 0.0, "output_per_million": 0.01}}',
        )
        settings = Settings()
        assert settings.model_pricing["test-model"]["input_per_million"] == 0.0
        assert settings.model_pricing["test-model"]["cached_input_per_million"] == 0.0

    def test_boolean_price_rejected(self, monkeypatch):
        """Boolean as a price value is rejected."""
        monkeypatch.setenv(
            "TRADING_MODEL_PRICING",
            '{"test-model": {"input_per_million": true, "output_per_million": 0.01}}',
        )
        with pytest.raises(Exception):
            Settings()

    def test_negative_price_rejected(self, monkeypatch):
        """Negative price is rejected."""
        monkeypatch.setenv(
            "TRADING_MODEL_PRICING",
            '{"test-model": {"input_per_million": -1.0, "output_per_million": 0.01}}',
        )
        with pytest.raises(ValueError, match="negative"):
            Settings()

    def test_nan_price_rejected(self, monkeypatch):
        """NaN price is rejected."""
        monkeypatch.setenv(
            "TRADING_MODEL_PRICING",
            '{"test-model": {"input_per_million": NaN, "output_per_million": 0.01}}',
        )
        with pytest.raises(Exception):
            Settings()

    def test_inf_price_rejected(self, monkeypatch):
        """Infinity price is rejected."""
        monkeypatch.setenv(
            "TRADING_MODEL_PRICING",
            '{"test-model": {"input_per_million": Infinity, "output_per_million": 0.01}}',
        )
        with pytest.raises(Exception):
            Settings()

    def test_no_commented_pricing_lines(self):
        """config/settings.py should not contain commented-out pricing entries."""
        import inspect

        from config.settings import Settings

        source = inspect.getsource(Settings)
        # Check for any remaining commented-out pricing lines
        assert '# "DeepSeek' not in source, "Commented-out pricing line should be removed"


class TestOpenAIInstructorModeAndTimeout:
    """Tests for the primary LLM instructor_mode and timeout Settings fields.

    These tests will fail RED (AttributeError / missing validator) until the
    fields are implemented in config/settings.py.
    """

    def test_instructor_mode_default_is_json_mode(self, monkeypatch: pytest.MonkeyPatch):
        """openai_instructor_mode defaults to 'json_mode'."""
        monkeypatch.delenv("TRADING_OPENAI_INSTRUCTOR_MODE", raising=False)
        assert Settings().openai_instructor_mode == "json_mode"

    def test_instructor_mode_accepts_json_mode(self, monkeypatch: pytest.MonkeyPatch):
        """'json_mode' is a valid value."""
        monkeypatch.setenv("TRADING_OPENAI_INSTRUCTOR_MODE", "json_mode")
        assert Settings().openai_instructor_mode == "json_mode"

    def test_instructor_mode_accepts_tool_call(self, monkeypatch: pytest.MonkeyPatch):
        """'tool_call' is a valid value."""
        monkeypatch.setenv("TRADING_OPENAI_INSTRUCTOR_MODE", "tool_call")
        assert Settings().openai_instructor_mode == "tool_call"

    def test_instructor_mode_rejects_unknown_value(self, monkeypatch: pytest.MonkeyPatch):
        """An unsupported instructor_mode value is rejected at parse time."""
        monkeypatch.setenv("TRADING_OPENAI_INSTRUCTOR_MODE", "json_schema_mode")
        with pytest.raises(ValueError, match="instructor_mode"):
            Settings()

    def test_instructor_mode_rejects_empty_string(self, monkeypatch: pytest.MonkeyPatch):
        """An empty primary instructor_mode is a misconfiguration and is rejected."""
        monkeypatch.setenv("TRADING_OPENAI_INSTRUCTOR_MODE", "")
        with pytest.raises(ValueError, match="instructor_mode"):
            Settings()

    def test_timeout_default_is_120(self, monkeypatch: pytest.MonkeyPatch):
        """openai_timeout defaults to 120.0 seconds."""
        monkeypatch.delenv("TRADING_OPENAI_TIMEOUT", raising=False)
        assert Settings().openai_timeout == 120.0

    def test_timeout_from_env(self, monkeypatch: pytest.MonkeyPatch):
        """TRADING_OPENAI_TIMEOUT env var overrides the default."""
        monkeypatch.setenv("TRADING_OPENAI_TIMEOUT", "45")
        assert Settings().openai_timeout == 45.0

    def test_timeout_rejects_non_positive(self, monkeypatch: pytest.MonkeyPatch):
        """A timeout <= 0 would fail every request instantly — reject it."""
        monkeypatch.setenv("TRADING_OPENAI_TIMEOUT", "0")
        with pytest.raises(ValueError):
            Settings()


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
