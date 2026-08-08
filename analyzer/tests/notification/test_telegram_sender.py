"""Tests for telegram_sender module."""

import logging
from unittest.mock import MagicMock, patch

import requests as req

from src.notification.telegram_sender import (
    _sanitize_url,
    extract_trade_levels,
    send_trade_notification,
)


class TestSendTradeNotification:
    def test_sends_buy_message(self, sample_decision, sample_context):
        with patch("src.notification.telegram_sender.requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            send_trade_notification(
                symbol="XAUUSD",
                decision=sample_decision,
                context=sample_context,
                web_ui_base_url="http://localhost:3000",
                bot_token="test-token",
                chat_id="test-chat",
            )

            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert "test-token" in call_args[0][0]
            body = call_args[1]["json"]
            assert body["chat_id"] == "test-chat"
            assert "XAUUSD" in body["text"]
            assert "BUY" in body["text"]
            assert "2400" in body["text"]

    def test_sends_sell_message(self, sample_decision, sample_context):
        decision = dict(sample_decision)
        decision["action"] = "sell_setup"
        with patch("src.notification.telegram_sender.requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            send_trade_notification(
                symbol="EURUSD",
                decision=decision,
                context=sample_context,
                web_ui_base_url="http://localhost:3000",
                bot_token="test-token",
                chat_id="test-chat",
            )

            body = mock_post.call_args[1]["json"]
            assert "SELL" in body["text"]
            assert "EURUSD" in body["text"]

    def test_skips_empty_token(self, sample_decision, sample_context):
        with patch("src.notification.telegram_sender.requests.post") as mock_post:
            send_trade_notification(
                symbol="XAUUSD",
                decision=sample_decision,
                context=sample_context,
                web_ui_base_url="http://localhost:3000",
                bot_token="",
                chat_id="test-chat",
            )
            mock_post.assert_not_called()

    def test_skips_empty_chat_id(self, sample_decision, sample_context):
        with patch("src.notification.telegram_sender.requests.post") as mock_post:
            send_trade_notification(
                symbol="XAUUSD",
                decision=sample_decision,
                context=sample_context,
                web_ui_base_url="http://localhost:3000",
                bot_token="test-token",
                chat_id="",
            )
            mock_post.assert_not_called()

    def test_handles_http_error(self, sample_decision, sample_context):
        with patch("src.notification.telegram_sender.requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.raise_for_status.side_effect = Exception("HTTP 500")
            mock_post.return_value = mock_resp

            # Should not raise
            send_trade_notification(
                symbol="XAUUSD",
                decision=sample_decision,
                context=sample_context,
                web_ui_base_url="http://localhost:3000",
                bot_token="test-token",
                chat_id="test-chat",
            )

    def test_handles_network_timeout(self, sample_decision, sample_context):
        with patch("src.notification.telegram_sender.requests.post") as mock_post:
            mock_post.side_effect = req.exceptions.Timeout("timeout")

            # Should not raise
            send_trade_notification(
                symbol="XAUUSD",
                decision=sample_decision,
                context=sample_context,
                web_ui_base_url="http://localhost:3000",
                bot_token="test-token",
                chat_id="test-chat",
            )

    def test_message_contains_all_fields(self, sample_decision, sample_context):
        with patch("src.notification.telegram_sender.requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            send_trade_notification(
                symbol="XAUUSD",
                decision=sample_decision,
                context=sample_context,
                web_ui_base_url="http://localhost:3000",
                bot_token="test-token",
                chat_id="test-chat",
            )

            text = mock_post.call_args[1]["json"]["text"]
            assert "XAUUSD" in text
            assert "Entry:" in text
            assert "SL:" in text
            assert "TP:" in text
            assert "R/R:" in text
            assert "Confidence:" in text
            assert "Bias:" in text
            assert "http://localhost:3000/runs/XAUUSD" in text

    def test_skips_no_trade_action(self, sample_context):
        decision = {"action": "no_trade", "confidence": 0.5}
        with patch("src.notification.telegram_sender.requests.post") as mock_post:
            send_trade_notification(
                symbol="XAUUSD",
                decision=decision,
                context=sample_context,
                web_ui_base_url="http://localhost:3000",
                bot_token="test-token",
                chat_id="test-chat",
            )
            mock_post.assert_not_called()

    # ------------------------------------------------------------------
    # Token sanitisation tests
    # ------------------------------------------------------------------

    @staticmethod
    def _token_safe(pattern: str) -> bool:
        """Return *True* when the token (``test-token``) does **not**
        appear in *pattern*."""
        return "test-token" not in pattern

    def test_token_not_in_log_on_http_error(
        self,
        caplog,
        sample_decision,
        sample_context,
    ):
        caplog.set_level(logging.WARNING)
        with patch("src.notification.telegram_sender.requests.post") as mock_post:
            resp = MagicMock()
            resp.raise_for_status.side_effect = req.exceptions.HTTPError("HTTP 500")
            mock_post.return_value = resp

            send_trade_notification(
                symbol="XAUUSD",
                decision=sample_decision,
                context=sample_context,
                web_ui_base_url="http://localhost:3000",
                bot_token="test-token",
                chat_id="test-chat",
            )

        for record in caplog.records:
            msg = record.getMessage()
            assert self._token_safe(msg), f"Raw token found in log message: {msg!r}"
            assert "bot***" in msg or "***" in msg, f"Sanitised URL marker missing in: {msg!r}"

    def test_token_not_in_log_on_timeout(
        self,
        caplog,
        sample_decision,
        sample_context,
    ):
        caplog.set_level(logging.WARNING)
        with patch("src.notification.telegram_sender.requests.post") as mock_post:
            mock_post.side_effect = req.exceptions.Timeout("connection timed out")

            send_trade_notification(
                symbol="XAUUSD",
                decision=sample_decision,
                context=sample_context,
                web_ui_base_url="http://localhost:3000",
                bot_token="test-token",
                chat_id="test-chat",
            )

        for record in caplog.records:
            msg = record.getMessage()
            assert self._token_safe(msg), f"Raw token found in log message: {msg!r}"
            assert "bot***" in msg or "***" in msg, f"Sanitised URL marker missing in: {msg!r}"

    def test_token_not_in_log_on_connection_error(
        self,
        caplog,
        sample_decision,
        sample_context,
    ):
        caplog.set_level(logging.WARNING)
        with patch("src.notification.telegram_sender.requests.post") as mock_post:
            mock_post.side_effect = req.exceptions.ConnectionError("connection refused")

            send_trade_notification(
                symbol="XAUUSD",
                decision=sample_decision,
                context=sample_context,
                web_ui_base_url="http://localhost:3000",
                bot_token="test-token",
                chat_id="test-chat",
            )

        for record in caplog.records:
            msg = record.getMessage()
            assert self._token_safe(msg), f"Raw token found in log message: {msg!r}"
            assert "bot***" in msg or "***" in msg, f"Sanitised URL marker missing in: {msg!r}"


class TestSanitizeUrl:
    """Unit tests for the ``_sanitize_url`` helper."""

    def test_replaces_token(self):
        url = "https://api.telegram.org/bot123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11/sendMessage"
        sanitized = _sanitize_url(url, "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11")
        assert sanitized == "https://api.telegram.org/bot***/sendMessage"

    def test_no_token_returns_url_unchanged(self):
        url = "https://api.telegram.org/bot/sendMessage"
        sanitized = _sanitize_url(url, "")
        assert sanitized == url

    def test_empty_url(self):
        sanitized = _sanitize_url("", "token")
        assert sanitized == ""

    def test_token_not_in_url(self):
        url = "https://example.com/api"
        sanitized = _sanitize_url(url, "any-token")
        assert sanitized == url


class TestExtractTradeLevels:
    """Tests for the extract_trade_levels helper."""

    def test_reads_from_overlay(self):
        """Overlay values are preferred over decision values."""
        result = {
            "decision": {
                "action": "buy_setup",
                "entry_price": 1.1111,
                "stop_loss": 1.1000,
                "take_profit": 1.1300,
                "risk_reward_ratio": 1.5,
                "confidence": 0.85,
            },
            "sl_tp_overlay": {
                "entry_price": 1.2222,
                "stop_loss": 1.2100,
                "take_profit": 1.2500,
            },
            "estimated_reward_risk": 2.0,
            "market_context": {"bias": "bullish"},
        }

        levels = extract_trade_levels(result)

        assert levels.entry_price == 1.2222
        assert levels.stop_loss == 1.2100
        assert levels.take_profit == 1.2500
        assert levels.risk_reward_ratio == 2.0
        assert levels.confidence == 0.85
        assert levels.bias == "bullish"

    def test_overlay_takes_precedence_over_decision(self):
        """When both overlay and decision have prices, overlay wins."""
        result = {
            "decision": {
                "entry_price": 1.1111,
                "stop_loss": 1.1000,
                "take_profit": 1.1300,
                "risk_reward_ratio": 1.5,
            },
            "sl_tp_overlay": {
                "entry_price": 1.2222,
                "stop_loss": 1.2100,
                "take_profit": 1.2500,
            },
            "estimated_reward_risk": 2.0,
        }

        levels = extract_trade_levels(result)

        assert levels.entry_price == 1.2222
        assert levels.stop_loss == 1.2100
        assert levels.take_profit == 1.2500
        assert levels.risk_reward_ratio == 2.0

    def test_falls_back_to_decision_when_overlay_missing(self):
        """Legacy results without overlay use decision fields."""
        result = {
            "decision": {
                "entry_price": 2400.0,
                "stop_loss": 2380.0,
                "take_profit": 2440.0,
                "risk_reward_ratio": 2.0,
                "confidence": 0.85,
            },
            "market_context": {"bias": "bullish"},
        }

        levels = extract_trade_levels(result)

        assert levels.entry_price == 2400.0
        assert levels.stop_loss == 2380.0
        assert levels.take_profit == 2440.0
        assert levels.risk_reward_ratio == 2.0

    def test_na_defaults_when_no_prices(self):
        """N/A when neither overlay nor decision has price fields."""
        result = {
            "decision": {"action": "buy_setup"},
        }

        levels = extract_trade_levels(result)

        assert levels.entry_price == "N/A"
        assert levels.stop_loss == "N/A"
        assert levels.take_profit == "N/A"
        assert levels.risk_reward_ratio == "N/A"

    def test_result_param_sends_overlay_values(self):
        """send_trade_notification with result= uses extract_trade_levels."""
        result = {
            "analysis_result": {
                "decision": {
                    "action": "buy_setup",
                    "confidence": 0.85,
                },
                "sl_tp_overlay": {
                    "entry_price": 1.2222,
                    "stop_loss": 1.2100,
                    "take_profit": 1.2500,
                },
                "estimated_reward_risk": 2.0,
                "validation_status": "VALID",
                "setup_status": "READY",
                "operational": True,
                "market_context": {"bias": "bullish"},
            }
        }

        with patch("src.notification.telegram_sender.requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            send_trade_notification(
                symbol="EURUSD",
                decision=result["analysis_result"]["decision"],
                context=result["analysis_result"]["market_context"],
                web_ui_base_url="http://localhost:3000",
                bot_token="test-token",
                chat_id="test-chat",
                result=result,
            )

            text = mock_post.call_args[1]["json"]["text"]
            assert "1.2222" in text  # overlay entry, not 1.1111
            assert "1.21" in text  # overlay SL
            assert "1.25" in text  # overlay TP
            assert "2.0" in text  # estimated_reward_risk

    def test_suppresses_legacy_result_even_with_valid_top_level_fields(self, sample_context):
        result = {
            "decision": {"action": "buy_setup"},
            "validation_status": "VALID",
            "setup_status": "READY",
        }

        with patch("src.notification.telegram_sender.requests.post") as mock_post:
            send_trade_notification(
                symbol="XAUUSD",
                decision=result["decision"],
                context=sample_context,
                web_ui_base_url="http://localhost:3000",
                bot_token="test-token",
                chat_id="test-chat",
                result=result,
            )

        mock_post.assert_not_called()

    def test_suppresses_nested_invalid_analysis_result(self, sample_context):
        """A nested analysis_result that is INVALID must never notify."""
        result = {
            "analysis_result": {
                "decision": {"action": "no_trade"},
                "validation_status": "INVALID",
                "setup_status": "INVALID",
                "operational": False,
            }
        }

        with patch("src.notification.telegram_sender.requests.post") as mock_post:
            send_trade_notification(
                symbol="XAUUSD",
                decision=result["analysis_result"]["decision"],
                context=sample_context,
                web_ui_base_url="http://localhost:3000",
                bot_token="test-token",
                chat_id="test-chat",
                result=result,
            )

        mock_post.assert_not_called()

    def test_suppresses_nested_non_actionable_analysis_result(self, sample_context):
        """A nested analysis_result with a no_trade action must never notify,
        even when validation_status is VALID but the result is not
        operational."""
        result = {
            "analysis_result": {
                "decision": {"action": "no_trade"},
                "validation_status": "VALID",
                "setup_status": "READY",
                "operational": False,
            }
        }

        with patch("src.notification.telegram_sender.requests.post") as mock_post:
            send_trade_notification(
                symbol="XAUUSD",
                decision=result["analysis_result"]["decision"],
                context=sample_context,
                web_ui_base_url="http://localhost:3000",
                bot_token="test-token",
                chat_id="test-chat",
                result=result,
            )

        mock_post.assert_not_called()

    def test_suppresses_nested_missing_operational_flag(self, sample_context):
        """A nested analysis_result without operational=True must never notify."""
        result = {
            "analysis_result": {
                "decision": {"action": "buy_setup"},
                "validation_status": "VALID",
                "setup_status": "READY",
            }
        }

        with patch("src.notification.telegram_sender.requests.post") as mock_post:
            send_trade_notification(
                symbol="XAUUSD",
                decision=result["analysis_result"]["decision"],
                context=sample_context,
                web_ui_base_url="http://localhost:3000",
                bot_token="test-token",
                chat_id="test-chat",
                result=result,
            )

        mock_post.assert_not_called()

    def test_degraded_synthesis_marks_explanation_unavailable(self):
        """FR-032: an actionable result with failed synthesis states that
        explanation is unavailable."""
        result = {
            "analysis_result": {
                "decision": {"action": "buy_setup", "confidence": 0.85},
                "sl_tp_overlay": {
                    "entry_price": 1.2222,
                    "stop_loss": 1.2100,
                    "take_profit": 1.2500,
                },
                "estimated_reward_risk": 2.0,
                "validation_status": "VALID",
                "setup_status": "READY",
                "operational": True,
                "synthesis_status": "FAILED",
                "market_context": {},
            }
        }

        with patch("src.notification.telegram_sender.requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            send_trade_notification(
                symbol="EURUSD",
                decision=result["analysis_result"]["decision"],
                context={},
                web_ui_base_url="http://localhost:3000",
                bot_token="test-token",
                chat_id="test-chat",
                result=result,
            )

            text = mock_post.call_args[1]["json"]["text"]
            assert "Explanation: unavailable" in text

    def test_successful_synthesis_omits_unavailable_marker(self):
        result = {
            "analysis_result": {
                "decision": {"action": "buy_setup", "confidence": 0.85},
                "sl_tp_overlay": {
                    "entry_price": 1.2222,
                    "stop_loss": 1.2100,
                    "take_profit": 1.2500,
                },
                "estimated_reward_risk": 2.0,
                "validation_status": "VALID",
                "setup_status": "READY",
                "operational": True,
                "synthesis_status": "SUCCESS",
                "market_context": {},
            }
        }

        with patch("src.notification.telegram_sender.requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            send_trade_notification(
                symbol="EURUSD",
                decision=result["analysis_result"]["decision"],
                context={},
                web_ui_base_url="http://localhost:3000",
                bot_token="test-token",
                chat_id="test-chat",
                result=result,
            )

            text = mock_post.call_args[1]["json"]["text"]
            assert "Explanation: unavailable" not in text

    def test_bias_falls_back_to_deterministic_direction_when_market_context_absent(self):
        """SYNTH-010: v2 results without market_context must show the
        deterministic direction, not an always-neutral default."""
        result = {
            "decision": {"action": "buy_setup"},
            "sl_tp_overlay": {
                "entry_price": 1.2222,
                "stop_loss": 1.2100,
                "take_profit": 1.2500,
            },
            "estimated_reward_risk": 2.0,
            "market_context": {},
            "trade_direction": "BULLISH",
            "direction": "LONG",
        }

        levels = extract_trade_levels(result)

        assert levels.bias == "BULLISH"
        assert levels.confidence == "N/A"

    def test_bias_prefers_market_context_when_present(self):
        """Legacy results keep the explicit market_context bias."""
        result = {
            "decision": {"action": "buy_setup"},
            "sl_tp_overlay": {
                "entry_price": 1.2222,
                "stop_loss": 1.2100,
                "take_profit": 1.2500,
            },
            "estimated_reward_risk": 2.0,
            "market_context": {"bias": "bullish"},
        }

        levels = extract_trade_levels(result)

        assert levels.bias == "bullish"
