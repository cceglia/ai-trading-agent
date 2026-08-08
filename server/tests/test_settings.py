"""Tests for WebSettings environment-variable loading.

The _CommaDelimitedEnvSource handles comma-splitting for ``cors_origins``
when the value comes from an env var.  No model_validator is needed.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

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


class TestProviderConfig:
    """``PROVIDER_CONFIG`` maps a server-side provider id to an endpoint URL.

    Endpoint URLs and credentials stay entirely server-side (FR-039 / DEC-014);
    the API accepts a ``provider_id``, never a free-form ``base_url``.
    """

    def test_provider_config_from_env_json(self, monkeypatch):
        monkeypatch.setenv("PROVIDER_CONFIG", '{"local": "http://127.0.0.1:11434/v1"}')
        settings = WebSettings()
        assert settings.provider_config == {"local": "http://127.0.0.1:11434/v1"}

    def test_provider_config_default_empty(self):
        settings = WebSettings()
        assert settings.provider_config == {}


class TestTrustedProxyCidrs:
    """``TRADING_TRUSTED_PROXY_CIDRS`` configures the trusted proxy sources.

    FR-036 / DEC-008: comma-separated CIDRs; an empty value disables
    proxy-marker authentication rather than trusting all networks.
    """

    def test_default_is_empty(self):
        settings = WebSettings()
        assert settings.trusted_proxy_cidrs == []

    def test_cidrs_from_env_comma_separated(self, monkeypatch):
        monkeypatch.setenv("TRADING_TRUSTED_PROXY_CIDRS", "10.0.0.0/8,192.168.1.0/24")
        settings = WebSettings()
        assert settings.trusted_proxy_cidrs == ["10.0.0.0/8", "192.168.1.0/24"]

    def test_cidrs_strip_whitespace(self, monkeypatch):
        monkeypatch.setenv("TRADING_TRUSTED_PROXY_CIDRS", "10.0.0.0/8 , 192.168.1.0/24")
        settings = WebSettings()
        assert settings.trusted_proxy_cidrs == ["10.0.0.0/8", "192.168.1.0/24"]

    def test_single_cidr(self, monkeypatch):
        monkeypatch.setenv("TRADING_TRUSTED_PROXY_CIDRS", "172.16.0.0/12")
        settings = WebSettings()
        assert settings.trusted_proxy_cidrs == ["172.16.0.0/12"]

    def test_empty_env_yields_empty_list(self, monkeypatch):
        monkeypatch.setenv("TRADING_TRUSTED_PROXY_CIDRS", "")
        settings = WebSettings()
        assert settings.trusted_proxy_cidrs == []


class TestTrustedProxyCidrValidation:
    """CONFIG-001: invalid CIDRs fail at settings load with a clear error.

    Previously an invalid ``TRADING_TRUSTED_PROXY_CIDRS`` value survived
    settings parsing and crashed later inside ``AuthMiddleware``/``create_app``
    with an opaque ``ValueError``. Validation is moved to settings load and
    still fails closed.
    """

    def test_invalid_cidr_from_constructor_raises_clear_error(self):
        with pytest.raises(ValidationError, match="Invalid CIDR"):
            WebSettings(trusted_proxy_cidrs=["not-a-cidr"])

    def test_invalid_cidr_from_env_raises_clear_error(self, monkeypatch):
        monkeypatch.setenv("TRADING_TRUSTED_PROXY_CIDRS", "10.0.0.0/8,not-a-cidr")
        with pytest.raises(ValidationError, match="Invalid CIDR"):
            WebSettings()

    def test_error_identifies_the_bad_value(self):
        with pytest.raises(ValidationError, match="not-a-cidr"):
            WebSettings(trusted_proxy_cidrs=["10.0.0.0/8", "not-a-cidr"])

    def test_valid_cidrs_still_accepted(self):
        settings = WebSettings(trusted_proxy_cidrs=["10.0.0.0/8", "::1/128"])
        assert settings.trusted_proxy_cidrs == ["10.0.0.0/8", "::1/128"]


class TestResolvedCacheDir:
    """``resolved_cache_dir`` must resolve relative paths from the project root.

    Both the analyzer and server write/read from the same directory tree.
    Relative paths are resolved against the **project root** (the parent
    directory of both ``analyzer/`` and ``server/``) so that the default
    ``"data"`` produces ``<project_root>/data`` regardless of which package
    is the working directory.
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
        ``<project_root>/data``."""
        settings = WebSettings(analysis_cache_dir="data")
        expected = self._project_root() / "data"
        assert settings.resolved_cache_dir == expected

    def test_resolved_cache_dir_absolute(self):
        """Given an absolute path, ``resolved_cache_dir`` must return it
        unchanged."""
        settings = WebSettings(analysis_cache_dir="/tmp/test_cache")
        assert settings.resolved_cache_dir == Path("/tmp/test_cache")

    def test_resolved_cache_dir_default(self):
        """The default ``analysis_cache_dir`` is ``"data"``, which must
        resolve to ``<project_root>/data``."""
        settings = WebSettings()
        expected = self._project_root() / "data"
        assert settings.resolved_cache_dir == expected

    def test_resolved_cache_dir_relative_from_env(self, monkeypatch):
        """Setting ``TRADING_ANALYSIS_CACHE_DIR`` to a relative value must
        resolve to ``<project_root>/<value>``."""
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", "custom/cache")
        settings = WebSettings()
        expected = self._project_root() / "custom" / "cache"
        assert settings.resolved_cache_dir == expected

    def test_resolved_cache_dir_absolute_from_env(self, monkeypatch):
        """Setting ``TRADING_ANALYSIS_CACHE_DIR`` to an absolute value must
        be returned as-is."""
        monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", "/var/trade/cache")
        settings = WebSettings()
        assert settings.resolved_cache_dir == Path("/var/trade/cache")

    def test_resolved_cache_dir_matches_analyzer(self):
        """Analyzer and server must resolve the same default to the same path."""
        import sys

        server_path = str(self.resolved_cache_dir_default())

        analyzer_dir = str(self._project_root() / "analyzer")
        if analyzer_dir not in sys.path:
            sys.path.insert(0, analyzer_dir)
        try:
            from config.settings import Settings

            analyzer_path = Settings().resolved_analysis_cache_dir
            assert server_path == analyzer_path
        finally:
            if analyzer_dir in sys.path:
                sys.path.remove(analyzer_dir)

    def resolved_cache_dir_default(self) -> Path:
        """Helper: return the default resolved cache dir."""
        return WebSettings().resolved_cache_dir
