"""Credential redaction for server logs (FR-038 / §16).

A :class:`SecretRedactionFilter` rewrites log records before any handler
formats them, replacing configured secret values (API key, provider endpoint
URLs/credentials) and known credential shapes (OpenAI-style keys, bearer
tokens, Telegram bot tokens, URL userinfo) with a stable placeholder.
"""

from __future__ import annotations

import logging
import re
import traceback

_REDACTED = "[redacted]"

# Generic credential shapes that must never appear in logs regardless of the
# exact configured value. Patterns are applied in order.
_GENERIC_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    # OpenAI-compatible API keys.
    (re.compile(r"sk-[A-Za-z0-9]{16,}"), f"sk-{_REDACTED}"),
    # Authorization: Bearer tokens.
    (
        re.compile(r"Bearer\s+[A-Za-z0-9._~+/=-]{20,}", re.IGNORECASE),
        f"Bearer {_REDACTED}",
    ),
    # Telegram bot tokens (digits:alphanumeric).
    (re.compile(r"\b\d{8,10}:AA[0-9A-Za-z_-]{30,}\b"), _REDACTED),
    # URLs with embedded userinfo credentials.
    (re.compile(r"(https?://)[^/\s@:]+(:[^/\s@]+)?@"), rf"\g<1>{_REDACTED}@"),
)


class SecretRedactionFilter(logging.Filter):
    """Redact configured secrets and credential shapes from log records.

    Mutates ``record.msg``/``record.args`` in place so every handler attached
    downstream (including test capture handlers) sees only redacted output.
    Exception tracebacks are handled too: an already-rendered
    ``record.exc_text`` is redacted directly, and an unrendered
    ``record.exc_info`` is rendered, redacted, and nulled so the formatter
    never re-renders the original traceback into output (FR-038).
    """

    def __init__(self, secrets: tuple[str, ...] = ()) -> None:
        super().__init__()
        self._literal = tuple(secret for secret in secrets if secret)

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        record.msg = self._redact(message)
        record.args = ()
        if record.exc_text:
            record.exc_text = self._redact(record.exc_text)
        if record.exc_info:
            rendered = "".join(traceback.format_exception(*record.exc_info))
            record.exc_text = self._redact(rendered)
            record.exc_info = None
        return True

    def _redact(self, text: str) -> str:
        for secret in self._literal:
            text = text.replace(secret, _REDACTED)
        for pattern, replacement in _GENERIC_PATTERNS:
            text = pattern.sub(replacement, text)
        return text
