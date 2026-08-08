"""Tests for credential redaction in server logs (FR-038 / §16).

API keys, proxy markers, provider credentials, and known credential shapes
must never appear in log output. The ``SecretRedactionFilter`` installed by
``create_app`` rewrites log records before any handler formats them.
"""

from __future__ import annotations

import logging
from unittest.mock import patch

from src.main import create_app


def _build_app() -> None:
    """Create an app instance (installs the redaction filter)."""
    with (
        patch("src.main.ResultScanner"),
        patch("src.main.RunService"),
    ):
        create_app()


class TestSecretRedaction:
    """Configured secrets and generic credential shapes are redacted."""

    def test_configured_api_key_redacted(self, caplog, monkeypatch):
        monkeypatch.setenv("TRADING_API_KEY", "super-secret-machine-key")
        _build_app()

        with caplog.at_level(logging.INFO):
            logging.getLogger("src.main").info("request key=super-secret-machine-key")

        assert "super-secret-machine-key" not in caplog.text
        assert "[redacted]" in caplog.text

    def test_configured_key_redacted_when_passed_as_arg(self, caplog, monkeypatch):
        monkeypatch.setenv("TRADING_API_KEY", "arg-passed-secret")
        _build_app()

        with caplog.at_level(logging.INFO):
            logging.getLogger("src.main").info(
                "authorizing with %s", "arg-passed-secret"
            )

        assert "arg-passed-secret" not in caplog.text

    def test_openai_style_key_redacted(self, caplog):
        _build_app()

        with caplog.at_level(logging.INFO):
            logging.getLogger("src.runner").info(
                "provider key sk-abcdefghijklmnopqrstuvwx"
            )

        assert "sk-abcdefghijklmnopqrstuvwx" not in caplog.text
        assert "sk-[redacted]" in caplog.text

    def test_bearer_token_redacted(self, caplog):
        _build_app()

        with caplog.at_level(logging.INFO):
            logging.getLogger("src.scanner").info(
                "Authorization: Bearer abcDEF123.xyz_-7890QWERTYUIO"
            )

        assert "Bearer abcDEF123.xyz_-7890QWERTYUIO" not in caplog.text
        assert "Bearer [redacted]" in caplog.text

    def test_telegram_bot_token_redacted(self, caplog):
        _build_app()

        with caplog.at_level(logging.INFO):
            logging.getLogger("src.main").info(
                "notify bot 123456789:AAabcdefghijklmnopqrstuvwxyz0123456789"
            )

        assert "123456789:AAabcdefghijklmnopqrstuvwxyz0123456789" not in caplog.text

    def test_url_with_credentials_redacted(self, caplog, monkeypatch):
        monkeypatch.setenv(
            "PROVIDER_CONFIG", '{"local": "http://user:pass@127.0.0.1:11434/v1"}'
        )
        _build_app()

        with caplog.at_level(logging.INFO):
            logging.getLogger("src.main").info(
                "calling http://user:pass@127.0.0.1:11434/v1/chat"
            )

        assert "http://user:pass@127.0.0.1:11434/v1/chat" not in caplog.text
        assert "user:pass" not in caplog.text
        assert "[redacted]" in caplog.text

    def test_unconfigured_url_with_userinfo_redacted(self, caplog):
        """The generic URL pattern catches credentials not in the config."""
        _build_app()

        with caplog.at_level(logging.INFO):
            logging.getLogger("src.main").info(
                "endpoint http://alice:hunter2@provider.example/v1"
            )

        assert "http://alice:hunter2@provider.example/v1" not in caplog.text
        assert "http://[redacted]@provider.example/v1" in caplog.text


class TestExceptionRedaction:
    """FR-038: exception tracebacks (``logger.exception``) are redacted too.

    ``record.msg``/``record.args`` are not the only leak path — the rendered
    traceback (``record.exc_info``/``record.exc_text``) embeds the exception
    message verbatim, so a credential raised into ``logger.exception`` must
    never reach log output.
    """

    @staticmethod
    def _log_exception(message: str) -> None:
        try:
            raise ValueError(message)
        except ValueError:
            logging.getLogger("src.main").exception("request failed")

    def test_configured_secret_in_exception_redacted(self, caplog, monkeypatch):
        """A configured API key inside the exception message is redacted."""
        monkeypatch.setenv("TRADING_API_KEY", "traceback-secret-key")
        _build_app()

        with caplog.at_level(logging.ERROR):
            self._log_exception("auth failed for traceback-secret-key")

        assert "traceback-secret-key" not in caplog.text
        assert "[redacted]" in caplog.text

    def test_generic_shape_in_exception_redacted(self, caplog):
        """OpenAI-style keys in exception messages are caught by the pattern."""
        _build_app()

        with caplog.at_level(logging.ERROR):
            self._log_exception("provider rejected sk-abcdefghijklmnopqrstuvwx")

        assert "sk-abcdefghijklmnopqrstuvwx" not in caplog.text
        assert "sk-[redacted]" in caplog.text

    def test_non_secret_exception_text_preserved(self, caplog):
        """Redaction keeps non-secret traceback content intact."""
        _build_app()

        with caplog.at_level(logging.ERROR):
            self._log_exception("disk is full")

        assert "disk is full" in caplog.text
        assert "ValueError: disk is full" in caplog.text
