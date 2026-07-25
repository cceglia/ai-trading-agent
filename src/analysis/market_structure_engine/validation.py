from __future__ import annotations

from copy import deepcopy
from typing import Any

from .config import SUPPORTED_TIMEFRAMES, TimeframeProfile
from .errors import (
    ExternalDerivedValuesError,
    InsufficientDataError,
    TimeframeMismatchError,
    UnsupportedTimeframeError,
    UnverifiedClosureError,
    ValidationError,
)
from .utils import finite_number, parse_iso_timestamp

_ALLOWED_TOP_LEVEL = {
    "schema_version",
    "source",
    "market",
    "timeframe",
    "requested_timeframe",
    "returned_timeframe",
    "retrieved_at",
    "latest_closed_candle_time",
    "candle_closure_verified",
    "bars",
}
_ALLOWED_SOURCE = {"type", "server", "tool", "request_id"}
_ALLOWED_MARKET = {"symbol", "provider"}
_ALLOWED_BAR = {"open_time", "open", "high", "low", "close", "closed"}
_FORBIDDEN_DERIVED = {
    "indicators",
    "indicator_values",
    "technical_values",
    "swings",
    "structure",
    "levels",
    "liquidity",
    "volume",
    "volumes",
    "ohlcv",
}


def validate_snapshot(snapshot: dict[str, Any], profile: TimeframeProfile) -> dict[str, Any]:
    if not isinstance(snapshot, dict):
        raise ValidationError("Snapshot must be a JSON object.")

    unknown = sorted(set(snapshot) - _ALLOWED_TOP_LEVEL)
    forbidden = sorted(set(snapshot) & _FORBIDDEN_DERIVED)
    if forbidden:
        raise ExternalDerivedValuesError(
            "Only raw closed OHLC bars are accepted; external derived values are forbidden.",
            details={"forbidden_fields": forbidden},
        )
    if unknown:
        raise ExternalDerivedValuesError(
            "Snapshot contains fields outside the strict OHLC contract.",
            details={"unknown_fields": unknown},
        )

    source = snapshot.get("source")
    if not isinstance(source, dict) or source.get("type") != "TRADINGVIEW_MCP":
        raise ValidationError("source.type must be TRADINGVIEW_MCP.")
    source_unknown = sorted(set(source) - _ALLOWED_SOURCE)
    if source_unknown:
        raise ValidationError("Unsupported source field(s).", details={"fields": source_unknown})

    market = snapshot.get("market")
    if not isinstance(market, dict):
        raise ValidationError("market must be an object.")
    market_unknown = sorted(set(market) - _ALLOWED_MARKET)
    if market_unknown:
        raise ValidationError("Unsupported market field(s).", details={"fields": market_unknown})
    if not str(market.get("symbol", "")).strip() or not str(market.get("provider", "")).strip():
        raise ValidationError("market.symbol and market.provider are required.")

    requested = str(snapshot.get("requested_timeframe") or snapshot.get("timeframe") or "").upper()
    returned = str(snapshot.get("returned_timeframe") or snapshot.get("timeframe") or "").upper()
    if requested not in SUPPORTED_TIMEFRAMES:
        raise UnsupportedTimeframeError(
            f"Supported timeframes are D1, H4 and H1; received {requested!r}."
        )
    if returned != requested or requested != profile.timeframe:
        raise TimeframeMismatchError(
            "Requested, returned and configured timeframes must match.",
            details={"requested": requested, "returned": returned, "profile": profile.timeframe},
        )

    if snapshot.get("candle_closure_verified") is not True:
        raise UnverifiedClosureError(
            "The latest candle closure was not verified through TradingView MCP."
        )

    for timestamp_field in ("retrieved_at", "latest_closed_candle_time"):
        value = snapshot.get(timestamp_field)
        if not isinstance(value, str) or not value:
            raise ValidationError(f"{timestamp_field} is required.")
        try:
            parse_iso_timestamp(value)
        except ValueError as exc:
            raise ValidationError(f"{timestamp_field} must be ISO-8601.") from exc

    bars = snapshot.get("bars")
    if not isinstance(bars, list):
        raise ValidationError("bars must be an array.")
    if len(bars) < profile.minimum_bars:
        raise InsufficientDataError(
            f"{profile.timeframe} requires at least {profile.minimum_bars} closed bars.",
            details={"received": len(bars), "minimum": profile.minimum_bars},
        )
    if len(bars) > profile.maximum_bars:
        bars = bars[-profile.maximum_bars :]

    normalized_bars: list[dict[str, Any]] = []
    previous_time = None
    for index, raw in enumerate(bars):
        if not isinstance(raw, dict):
            raise ValidationError("Each bar must be an object.", details={"bar_index": index})
        unknown_bar = sorted(set(raw) - _ALLOWED_BAR)
        if unknown_bar:
            raise ExternalDerivedValuesError(
                "Bars may contain only open_time, open, high, low, close and closed.",
                details={"bar_index": index, "unknown_fields": unknown_bar},
            )
        if raw.get("closed") is not True:
            raise UnverifiedClosureError(
                "Every input bar must be closed.", details={"bar_index": index}
            )
        timestamp = raw.get("open_time")
        if not isinstance(timestamp, str) or not timestamp:
            raise ValidationError("open_time is required.", details={"bar_index": index})
        try:
            parsed = parse_iso_timestamp(timestamp)
        except ValueError as exc:
            raise ValidationError("Invalid bar timestamp.", details={"bar_index": index}) from exc
        if previous_time is not None and parsed <= previous_time:
            raise ValidationError(
                "Bars must be strictly ordered from oldest to newest.",
                details={"bar_index": index},
            )
        previous_time = parsed

        values: dict[str, float] = {}
        for field in ("open", "high", "low", "close"):
            value = raw.get(field)
            if not finite_number(value):
                raise ValidationError(
                    f"Bar {field} must be a finite number.", details={"bar_index": index}
                )
            values[field] = float(value)  # type: ignore[arg-type]
        if values["high"] < max(values["open"], values["close"], values["low"]):
            raise ValidationError("Bar high is inconsistent.", details={"bar_index": index})
        if values["low"] > min(values["open"], values["close"], values["high"]):
            raise ValidationError("Bar low is inconsistent.", details={"bar_index": index})
        normalized_bars.append(
            {
                "open_time": timestamp,
                **values,
                "closed": True,
            }
        )

    latest = normalized_bars[-1]["open_time"]
    declared_latest = snapshot["latest_closed_candle_time"]
    if latest != declared_latest:
        raise ValidationError(
            "latest_closed_candle_time must equal the final bar open_time.",
            details={"declared": declared_latest, "final_bar": latest},
        )

    result = deepcopy(snapshot)
    result["timeframe"] = requested
    result["requested_timeframe"] = requested
    result["returned_timeframe"] = returned
    result["bars"] = normalized_bars
    return result
