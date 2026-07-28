"""Tests for WebSettings environment-variable loading.

The _CommaDelimitedEnvSource handles comma-splitting for ``cors_origins``
when the value comes from an env var.  No model_validator is needed.
"""

from __future__ import annotations

from pathlib import Path

from src.settings import WebSettings


class TestCorsOrigins:
    """CORS_ORIGINS env-var and constructor behaviour."""

    def test_cors_origins_from_env_comma_separated(self, monkeypatch):
        """Given CORS_ORIGINS=http://a.com,http://b.com, settings must
        produce ["http://a.com", "http://b.com"]."""
        monkeypatch.setenv("CORS_ORIGINS", "http://a.com,http://b.com")
        settings = WebSettings()
        assert settings.cors_origins == ["http://a.com", "http://b.com"]

    def test_cors_origins_from_constructor_list(self):
        """Passing a list[str] directly must be accepted as-is."""
        settings = WebSettings(cors_origins=["http://x.com", "http://y.com"])
        assert settings.cors_origins == ["http://x.com", "http://y.com"]

    def test_cors_origins_default(self):
        """With no env var, the default must be used."""
        settings = WebSettings()
        assert settings.cors_origins == ["http://localhost:5173"]

    def test_cors_origins_env_with_trailing_space(self, monkeypatch):
        """Trailing whitespace after commas must be stripped."""
        monkeypatch.setenv("CORS_ORIGINS", "http://a.com , http://b.com")
        settings = WebSettings()
        assert settings.cors_origins == ["http://a.com", "http://b.com"]

    def test_cors_origins_single_value(self, monkeypatch):
        """A single origin without commas must produce a single-element list."""
        monkeypatch.setenv("CORS_ORIGINS", "http://only.com")
        settings = WebSettings()
        assert settings.cors_origins == ["http://only.com"]

    def test_cors_origins_empty_env_yields_empty_list(self, monkeypatch):
        """An empty env var must produce an empty list (no default fallback)."""
        monkeypatch.setenv("CORS_ORIGINS", "")
        settings = WebSettings()
        assert settings.cors_origins == []


class TestResolvedCacheDir:
    """``resolved_cache_dir`` must behave consistently with the analyzer.

    The analyzer resolves ``analysis_cache_dir`` relative to its working
    directory (``analyzer/``).  The server uses the same convention so both
    packages write to the same directory tree.
    """

    @staticmethod
    def _project_root() -> Path:
        """Compute the project root from the test file location.

        Mirror the same traversal the source uses:
        ``server/tests/test_settings.py → parent.parent.parent → project root``.
        """
        return Path(__file__).resolve().parent.parent.parent

    def test_resolved_cache_dir_relative(self):
        """Given ``analysis_cache_dir="data"``, the resolved path must be
        ``<project_root>/analyzer/data``."""
        settings = WebSettings(analysis_cache_dir="data")
        expected = self._project_root() / "analyzer" / "data"
        assert settings.resolved_cache_dir == expected

    def test_resolved_cache_dir_absolute(self):
        """Given an absolute path, ``resolved_cache_dir`` must return it
        unchanged."""
        settings = WebSettings(analysis_cache_dir="/tmp/test_cache")
        assert settings.resolved_cache_dir == Path("/tmp/test_cache")

    def test_resolved_cache_dir_default(self):
        """The default ``analysis_cache_dir`` is ``"data"``, which must
        resolve to ``<project_root>/analyzer/data``."""
        settings = WebSettings()
        expected = self._project_root() / "analyzer" / "data"
        assert settings.resolved_cache_dir == expected

    def test_resolved_cache_dir_relative_from_env(self, monkeypatch):
        """Setting ``TRADING_ANALYSIS_CACHE_DIR`` to a relative value must
        resolve to ``<project_root>/analyzer/<value>``."""
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", "custom/cache")
        settings = WebSettings()
        expected = self._project_root() / "analyzer" / "custom" / "cache"
        assert settings.resolved_cache_dir == expected

    def test_resolved_cache_dir_absolute_from_env(self, monkeypatch):
        """Setting ``TRADING_ANALYSIS_CACHE_DIR`` to an absolute value must
        be returned as-is."""
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", "/var/trade/cache")
        settings = WebSettings()
        assert settings.resolved_cache_dir == Path("/var/trade/cache")
