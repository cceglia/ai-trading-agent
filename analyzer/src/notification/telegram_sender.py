"""Telegram notification sender — best-effort, never blocks the pipeline."""

import logging
from dataclasses import dataclass
from typing import Any

import requests

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TelegramTradeLevels:
    """Trade levels for Telegram notification."""

    entry_price: float | str
    stop_loss: float | str
    take_profit: float | str
    risk_reward_ratio: float | str
    confidence: float | str
    bias: str


def extract_trade_levels(result: dict[str, Any]) -> TelegramTradeLevels:
    """Extract trade levels from a pipeline result dict.

    Reads from ``sl_tp_overlay`` (deterministic engine) with explicit
    fallback to legacy ``decision`` price fields for old results.
    R/R comes from ``estimated_reward_risk`` with fallback to
    ``decision.risk_reward_ratio``.
    """
    decision = result.get("decision") or {}
    overlay = result.get("sl_tp_overlay") or {}
    context = result.get("market_context") or result.get("context") or {}

    # Entry price: prefer overlay, fallback to legacy decision field
    entry_price = overlay.get("entry_price")
    if entry_price is None:
        entry_price = decision.get("entry_price", "N/A")

    # Stop loss: prefer overlay, fallback to legacy decision field
    stop_loss = overlay.get("stop_loss")
    if stop_loss is None:
        stop_loss = decision.get("stop_loss", "N/A")

    # Take profit: prefer overlay, fallback to legacy decision field
    take_profit = overlay.get("take_profit")
    if take_profit is None:
        take_profit = decision.get("take_profit", "N/A")

    # R/R: prefer deterministic estimated_reward_risk, fallback to decision field
    rr = result.get("estimated_reward_risk")
    if rr is None:
        rr = decision.get("risk_reward_ratio", "N/A")

    confidence = decision.get("confidence", 0)
    bias = context.get("bias", "neutral")

    return TelegramTradeLevels(
        entry_price=entry_price or "N/A",
        stop_loss=stop_loss or "N/A",
        take_profit=take_profit or "N/A",
        risk_reward_ratio=rr or "N/A",
        confidence=confidence,
        bias=bias,
    )


def _sanitize_url(url: str, token: str) -> str:
    """Replace the bot token in a Telegram API URL with ``***``."""
    if token:
        return url.replace(token, "***")
    return url


def send_trade_notification(
    symbol: str,
    decision: dict[str, Any],
    context: dict[str, Any],
    web_ui_base_url: str,
    bot_token: str,
    chat_id: str,
    *,
    result: dict[str, Any] | None = None,
) -> None:
    """Send a compact trade notification to Telegram.

    Best-effort: logs warning on failure, never raises.

    When *result* is provided, trade levels are extracted via
    :func:`extract_trade_levels` (overlay-first with legacy fallback).
    """
    if not bot_token or not chat_id:
        logger.warning("Telegram notification skipped: bot_token or chat_id is empty")
        return

    action = decision.get("action", "no_trade")
    if result is not None and result.get("validation_status") != "VALID":
        return

    if action == "buy_setup":
        emoji = "\U0001f7e2 BUY"
    elif action == "sell_setup":
        emoji = "\U0001f534 SELL"
    else:
        return  # Only notify for buy/sell setups

    if result is not None:
        levels = extract_trade_levels(result)
        entry = levels.entry_price
        sl = levels.stop_loss
        tp = levels.take_profit
        rr = levels.risk_reward_ratio
        confidence = levels.confidence
        bias = levels.bias
    else:
        # Legacy path: read directly from decision dict
        entry = decision.get("entry_price", "N/A")
        sl = decision.get("stop_loss", "N/A")
        tp = decision.get("take_profit", "N/A")
        rr = decision.get("risk_reward_ratio", "N/A")
        confidence = decision.get("confidence", 0)
        bias = context.get("bias", "neutral")

    if isinstance(confidence, int | float):
        confidence = f"{confidence * 100:.0f}%"

    message = (
        f"{emoji} {symbol}\n"
        f"Action: {action}\n"
        f"Entry: {entry}\n"
        f"SL: {sl} | TP: {tp}\n"
        f"R/R: {rr}\n"
        f"Confidence: {confidence} | Bias: {bias}\n"
        f"{web_ui_base_url}/runs/{symbol}"
    )

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    safe_url = _sanitize_url(url, bot_token)
    payload = {"chat_id": chat_id, "text": message}

    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        logger.info("Telegram notification sent for %s", symbol)
    except Exception as e:
        logger.warning(
            "Failed to send Telegram notification for %s: %s | URL: %s",
            symbol,
            type(e).__name__,
            safe_url,
        )
