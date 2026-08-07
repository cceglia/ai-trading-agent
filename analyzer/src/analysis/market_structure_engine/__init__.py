__version__ = "6.0.0"

from .config import PROFILES, SUPPORTED_TIMEFRAMES, TimeframeProfile, get_profile
from .deterministic_validator import (
    DeterministicValidation,
    DeterministicValidator,
    validate_deterministic_facts,
)
from .engine import analyze_multi_timeframe, analyze_snapshot
from .errors import InvalidTradeDirectionError, StructureSchemaError
from .models import SetupRejectionCode

__all__ = [
    "PROFILES",
    "SUPPORTED_TIMEFRAMES",
    "TimeframeProfile",
    "get_profile",
    "analyze_snapshot",
    "analyze_multi_timeframe",
    "InvalidTradeDirectionError",
    "StructureSchemaError",
    "SetupRejectionCode",
    "DeterministicValidation",
    "DeterministicValidator",
    "validate_deterministic_facts",
]
