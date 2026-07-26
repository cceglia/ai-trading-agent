from __future__ import annotations

from typing import Any


class EngineError(Exception):
    """Base class for deterministic engine errors."""

    code = "ENGINE_ERROR"

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        return {"error_code": self.code, "message": self.message, "details": self.details}


class ValidationError(EngineError):
    code = "VALIDATION_ERROR"


class UnsupportedTimeframeError(ValidationError):
    code = "UNSUPPORTED_TIMEFRAME"


class TimeframeMismatchError(ValidationError):
    code = "TIMEFRAME_MISMATCH"


class InsufficientDataError(ValidationError):
    code = "INSUFFICIENT_DATA"


class UnverifiedClosureError(ValidationError):
    code = "UNVERIFIED_CANDLE_CLOSURE"


class ExternalDerivedValuesError(ValidationError):
    code = "EXTERNAL_DERIVED_VALUES_NOT_ALLOWED"


class ParentContextError(ValidationError):
    code = "INVALID_PARENT_CONTEXT"
