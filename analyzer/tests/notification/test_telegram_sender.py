"""Tests for telegram_sender module."""

from unittest.mock import MagicMock, patch

import requests as req

from src.notification.telegram_sender import send_trade_notification


class TestSendTradeNotification:
    def test_sends_buy_message(self, sample_decision, sample_context, sample_review):
        with patch("src.notification.telegram_sender.requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            send_trade_notification(
                symbol="XAUUSD",
                decision=sample_decision,
                context=sample_context,
                review=sample_review,
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

    def test_sellsend_message(self, sample_decision, sample_context, sample_review):
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
                review=sample_review,
                web_ui_base_url="http://localhost:3000",
                bot_token="test-token",
                chat_id="test-chat",
            )

            body = mock_post.call_args[1]["json"]
            assert "SELL" in body["text"]
            assert "EURUSD" in body["text"]

    def test_skips_empty_token(self, sample_decision, sample_context, sample_review):
        with patch("src.notification.telegram_sender.requests.post") as mock_post:
            send_trade_notification(
                symbol="XAUUSD",
                decision=sample_decision,
                context=sample_context,
                review=sample_review,
                web_ui_base_url="http://localhost:3000",
                bot_token="",
                chat_id="test-chat",
            )
            mock_post.assert_not_called()

    def test_skips_empty_chat_id(self, sample_decision, sample_context, sample_review):
        with patch("src.notification.telegram_sender.requests.post") as mock_post:
            send_trade_notification(
                symbol="XAUUSD",
                decision=sample_decision,
                context=sample_context,
                review=sample_review,
                web_ui_base_url="http://localhost:3000",
                bot_token="test-token",
                chat_id="",
            )
            mock_post.assert_not_called()

    def test_handles_http_error(self, sample_decision, sample_context, sample_review):
        with patch("src.notification.telegram_sender.requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.raise_for_status.side_effect = Exception("HTTP 500")
            mock_post.return_value = mock_resp

            # Should not raise
            send_trade_notification(
                symbol="XAUUSD",
                decision=sample_decision,
                context=sample_context,
                review=sample_review,
                web_ui_base_url="http://localhost:3000",
                bot_token="test-token",
                chat_id="test-chat",
            )

    def test_handles_network_timeout(self, sample_decision, sample_context, sample_review):
        with patch("src.notification.telegram_sender.requests.post") as mock_post:
            mock_post.side_effect = req.exceptions.Timeout("timeout")

            # Should not raise
            send_trade_notification(
                symbol="XAUUSD",
                decision=sample_decision,
                context=sample_context,
                review=sample_review,
                web_ui_base_url="http://localhost:3000",
                bot_token="test-token",
                chat_id="test-chat",
            )

    def test_message_contains_all_fields(self, sample_decision, sample_context, sample_review):
        with patch("src.notification.telegram_sender.requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            send_trade_notification(
                symbol="XAUUSD",
                decision=sample_decision,
                context=sample_context,
                review=sample_review,
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

    def test_skips_no_trade_action(self, sample_context, sample_review):
        decision = {"action": "no_trade", "confidence": 0.5}
        with patch("src.notification.telegram_sender.requests.post") as mock_post:
            send_trade_notification(
                symbol="XAUUSD",
                decision=decision,
                context=sample_context,
                review=sample_review,
                web_ui_base_url="http://localhost:3000",
                bot_token="test-token",
                chat_id="test-chat",
            )
            mock_post.assert_not_called()
