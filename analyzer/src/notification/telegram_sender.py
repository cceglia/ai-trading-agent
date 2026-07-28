"""Telegram notification sender — best-effort, never blocks the pipeline."""

import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)


def _sanitize_url(url: str, token: str) -> str:
    """Replace the bot token in a Telegram API URL with ``***``."""
    if token:
        return url.replace(token, "***")
    return url


def send_trade_notification(
    symbol: str,
    decision: dict[str, Any],
    context: dict[str, Any],
    review: dict[str, Any],
    web_ui_base_url: str,
    bot_token: str,
    chat_id: str,
) -> None:
    """Send a compact trade notification to Telegram.

    Best-effort: logs warning on failure, never raises.
    """
    if not bot_token or not chat_id:
        logger.warning("Telegram notification skipped: bot_token or chat_id is empty")
        return

    action = decision.get("action", "no_trade")
    if action == "buy_setup":
        emoji = "\U0001f7e2 BUY"
    elif action == "sell_setup":
        emoji = "\U0001f534 SELL"
    else:
        return  # Only notify for buy/sell setups

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
