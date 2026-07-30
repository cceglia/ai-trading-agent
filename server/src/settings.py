"""Server-specific settings using Pydantic BaseSettings."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, EnvSettingsSource


class _CommaDelimitedEnvSource(EnvSettingsSource):
    """Env source that parses comma-separated values for list fields.

    pydantic-settings tries JSON-decoding complex env vars before validators
    run.  This subclass intercepts ``cors_origins`` and splits on ``,`` so
    that operators can set ``CORS_ORIGINS=http://a.com,http://b.com``.
    """

    _COMMA_FIELDS = frozenset({"cors_origins"})

    def prepare_field_value(
        self,
        field_name: str,
        field: Any,
        value: str | None,
        value_is_complex: bool,
    ) -> Any:
        """Split comma-separated env values for known list fields."""
        if field_name in self._COMMA_FIELDS and isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return super().prepare_field_value(field_name, field, value, value_is_complex)


class WebSettings(BaseSettings):
    """Server configuration loaded from environment variables.

    Uses Field(alias=...) for backward-compatible unprefixed names
    (matching the existing Node.js deployment configs).
    Only TRADING_ANALYSIS_CACHE_DIR retains its prefix since it
    is shared with the analyzer.
    """

    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=3000, alias="PORT")
    cors_origins: list[str] = Field(
        default=["http://localhost:5173"], alias="CORS_ORIGINS"
    )
    python_cmd: str = Field(default="python", alias="PYTHON_CMD")
    analysis_cache_dir: str = Field(default="data", alias="TRADING_ANALYSIS_CACHE_DIR")

    # Auth
    api_key: str = Field(default="", alias="TRADING_API_KEY")

    # Rate limiting
    rate_limit_max: int = Field(default=20, alias="TRADING_RATE_LIMIT_MAX")
    rate_limit_window: int = Field(default=60, alias="TRADING_RATE_LIMIT_WINDOW")

    @property
    def resolved_cache_dir(self) -> Path:
        """Resolve ``analysis_cache_dir`` to an absolute path.

        Both the analyzer and server write/read from the same directory tree.
        Relative paths are resolved against the **project root** (the parent
        directory of both ``analyzer/`` and ``server/``) so that the default
        ``"data"`` produces ``<project_root>/data`` regardless of which
        package is the working directory.

        .. code-block:: text

            TRADING_ANALYSIS_CACHE_DIR=data   →  …/data
            TRADING_ANALYSIS_CACHE_DIR=/abs   →  /abs  (unchanged)
        """
        path = Path(self.analysis_cache_dir)
        if path.is_absolute():
            return path
        # Resolve relative to the project root (parent of server/)
        project_root = Path(__file__).resolve().parent.parent.parent
        return project_root / path

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: Any,
        env_settings: Any,
        dotenv_settings: Any,
        file_secret_settings: Any,
    ) -> tuple[Any, ...]:
        """Replace the default EnvSettingsSource with our comma-aware variant."""
        # Build the custom source with same params as the original
        custom_env = _CommaDelimitedEnvSource(
            settings_cls=settings_cls,
            case_sensitive=env_settings.case_sensitive,
            env_prefix=env_settings.env_prefix,
            env_prefix_target=getattr(env_settings, "env_prefix_target", None),
            env_nested_delimiter=env_settings.env_nested_delimiter,
            env_nested_max_split=getattr(env_settings, "env_nested_max_split", None),
            env_ignore_empty=env_settings.env_ignore_empty,
            env_parse_none_str=env_settings.env_parse_none_str,
            env_parse_enums=env_settings.env_parse_enums,
        )
        return (init_settings, custom_env, dotenv_settings, file_secret_settings)

    model_config = {"env_file_encoding": "utf-8", "populate_by_name": True}
