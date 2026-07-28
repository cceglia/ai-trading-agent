"""Tests for multi-symbol support in main.py."""

import logging
import sys
from unittest.mock import MagicMock, patch

import pytest


class TestArgparseMultiSymbol:
    """Test that argparse accepts multiple symbols via _build_parser."""

    def test_accepts_multiple_symbols(self):
        """_build_parser accepts multiple symbols as nargs+."""
        import main

        parser = main._build_parser()
        with patch.object(sys, "argv", ["main.py", "XAUUSD", "EURUSD", "GBPUSD"]):
            args = parser.parse_args()
            assert args.symbols == ["XAUUSD", "EURUSD", "GBPUSD"]

    def test_accepts_single_symbol(self):
        """_build_parser is backward-compatible with single symbol."""
        import main

        parser = main._build_parser()
        with patch.object(sys, "argv", ["main.py", "XAUUSD"]):
            args = parser.parse_args()
            assert args.symbols == ["XAUUSD"]

    def test_has_output_dir_option(self):
        """--output-dir option is accepted."""
        import main

        parser = main._build_parser()
        with patch.object(sys, "argv", ["main.py", "XAUUSD", "--output-dir", "data"]):
            args = parser.parse_args()
            assert args.output_dir == "data"

    def test_output_dir_default_none(self):
        """--output-dir defaults to None."""
        import main

        parser = main._build_parser()
        with patch.object(sys, "argv", ["main.py", "XAUUSD"]):
            args = parser.parse_args()
            assert args.output_dir is None

    def test_model_option(self):
        """--model option is accepted."""
        import main

        parser = main._build_parser()
        with patch.object(sys, "argv", ["main.py", "XAUUSD", "--model", "gpt-5"]):
            args = parser.parse_args()
            assert args.model == "gpt-5"

    def test_base_url_option(self):
        """--base-url option is accepted."""
        import main

        parser = main._build_parser()
        with patch.object(
            sys, "argv", ["main.py", "XAUUSD", "--base-url", "http://localhost:11434/v1"]
        ):
            args = parser.parse_args()
            assert args.base_url == "http://localhost:11434/v1"

    def test_log_level_option(self):
        """--log-level option defaults to INFO."""
        import main

        parser = main._build_parser()
        with patch.object(sys, "argv", ["main.py", "XAUUSD"]):
            args = parser.parse_args()
            assert args.log_level == "INFO"

    def test_no_symbols_raises_error(self):
        """Calling without any symbols should raise a SystemExit."""
        import main

        parser = main._build_parser()
        with patch.object(sys, "argv", ["main.py"]):
            with pytest.raises(SystemExit):
                parser.parse_args()


class TestMainMultiSymbolExecution:
    """Test that main() loops over all symbols correctly."""

    @patch("main.Settings")
    @patch("main.MarketStructureEngine")
    @patch("main.ForexFactoryCalendar")
    @patch("main.TerminalDataProvider")
    @patch("main.SynthesizerAgent")
    @patch("main.DeciderAgent")
    @patch("main.ReviewerAgent")
    @patch("main.TradingGraph")
    def test_processes_all_symbols(
        self,
        mock_graph_cls: MagicMock,
        mock_reviewer_cls: MagicMock,
        mock_decider_cls: MagicMock,
        mock_synth_cls: MagicMock,
        mock_provider_cls: MagicMock,
        mock_calendar_cls: MagicMock,
        mock_analyzer_cls: MagicMock,
        mock_settings_cls: MagicMock,
    ) -> None:
        """Verify main() calls graph.run() for each symbol."""
        mock_settings = mock_settings_cls.return_value
        mock_settings.openai_api_key = ""
        mock_settings.openai_base_url = ""
        mock_settings.openai_model = "gpt-4"
        mock_settings.openai_reasoning_effort = ""
        mock_settings.terminal_server_url = ""
        mock_settings.terminal_api_key = ""

        mock_graph = MagicMock()
        mock_graph.run.return_value = {"errors": [], "fatal_error": None}
        mock_graph_cls.return_value = mock_graph

        test_args = ["main.py", "XAUUSD", "EURUSD", "GBPUSD"]
        with patch.object(sys, "argv", test_args):
            from main import main

            main()

        assert mock_graph.run.call_count == 3
        symbols_called = [call[0][0] for call in mock_graph.run.call_args_list]
        assert symbols_called == ["XAUUSD", "EURUSD", "GBPUSD"]

    @patch("main.Settings")
    @patch("main.MarketStructureEngine")
    @patch("main.ForexFactoryCalendar")
    @patch("main.TerminalDataProvider")
    @patch("main.SynthesizerAgent")
    @patch("main.DeciderAgent")
    @patch("main.ReviewerAgent")
    @patch("main.TradingGraph")
    def test_handles_one_symbol_failure(
        self,
        mock_graph_cls: MagicMock,
        mock_reviewer_cls: MagicMock,
        mock_decider_cls: MagicMock,
        mock_synth_cls: MagicMock,
        mock_provider_cls: MagicMock,
        mock_calendar_cls: MagicMock,
        mock_analyzer_cls: MagicMock,
        mock_settings_cls: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """When one symbol fails, main() continues with remaining symbols."""
        mock_settings = mock_settings_cls.return_value
        mock_settings.openai_api_key = ""
        mock_settings.openai_base_url = ""
        mock_settings.openai_model = "gpt-4"
        mock_settings.openai_reasoning_effort = ""
        mock_settings.terminal_server_url = ""
        mock_settings.terminal_api_key = ""

        mock_graph = MagicMock()
        # First call succeeds, second call fails, third call succeeds
        mock_graph.run.side_effect = [
            {"errors": [], "fatal_error": None},
            Exception("Connection error"),
            {"errors": [], "fatal_error": None},
        ]
        mock_graph_cls.return_value = mock_graph

        test_args = ["main.py", "XAUUSD", "EURUSD", "GBPUSD"]
        with patch.object(sys, "argv", test_args):
            from main import main

            main()

        assert mock_graph.run.call_count == 3
        captured = capsys.readouterr()
        # The failure should be reported in the summary
        assert "EURUSD: FAILED" in captured.out

    @patch("main.Settings")
    @patch("main.MarketStructureEngine")
    @patch("main.ForexFactoryCalendar")
    @patch("main.TerminalDataProvider")
    @patch("main.SynthesizerAgent")
    @patch("main.DeciderAgent")
    @patch("main.ReviewerAgent")
    @patch("main.TradingGraph")
    def test_output_dir_is_used(
        self,
        mock_graph_cls: MagicMock,
        mock_reviewer_cls: MagicMock,
        mock_decider_cls: MagicMock,
        mock_synth_cls: MagicMock,
        mock_provider_cls: MagicMock,
        mock_calendar_cls: MagicMock,
        mock_analyzer_cls: MagicMock,
        mock_settings_cls: MagicMock,
        tmp_path: pytest.TempPathFactory,
    ) -> None:
        """When --output-dir is given, ResultWriter is used."""
        mock_settings = mock_settings_cls.return_value
        mock_settings.openai_api_key = ""
        mock_settings.openai_base_url = ""
        mock_settings.openai_model = "gpt-4"
        mock_settings.openai_reasoning_effort = ""
        mock_settings.terminal_server_url = ""
        mock_settings.terminal_api_key = ""

        mock_graph = MagicMock()
        from datetime import datetime

        mock_graph.run.return_value = {
            "errors": [],
            "fatal_error": None,
            "broker_now": datetime(2026, 7, 26, 8, 30),
            "structure_analysis": {"_ohlc_bars": {}},
        }
        mock_graph_cls.return_value = mock_graph

        output_dir = str(tmp_path / "runs")
        test_args = ["main.py", "XAUUSD", "--output-dir", output_dir]
        with patch.object(sys, "argv", test_args):
            from main import main

            main()

        # Verify output file was created
        expected = tmp_path / "runs" / "2026" / "07" / "26" / "XAUUSD" / "result-08-30.json"
        assert expected.exists()

    @patch("main.Settings")
    @patch("main.MarketStructureEngine")
    @patch("main.ForexFactoryCalendar")
    @patch("main.TerminalDataProvider")
    @patch("main.SynthesizerAgent")
    @patch("main.DeciderAgent")
    @patch("main.ReviewerAgent")
    @patch("main.TradingGraph")
    def test_handles_broker_now_missing(
        self,
        mock_graph_cls: MagicMock,
        mock_reviewer_cls: MagicMock,
        mock_decider_cls: MagicMock,
        mock_synth_cls: MagicMock,
        mock_provider_cls: MagicMock,
        mock_calendar_cls: MagicMock,
        mock_analyzer_cls: MagicMock,
        mock_settings_cls: MagicMock,
        tmp_path: pytest.TempPathFactory,
    ) -> None:
        """When result has no broker_now, main() uses datetime.now() instead."""
        mock_settings = mock_settings_cls.return_value
        mock_settings.openai_api_key = ""
        mock_settings.openai_base_url = ""
        mock_settings.openai_model = "gpt-4"
        mock_settings.openai_reasoning_effort = ""
        mock_settings.terminal_server_url = ""
        mock_settings.terminal_api_key = ""

        mock_graph = MagicMock()
        # No broker_now in result
        mock_graph.run.return_value = {
            "errors": [],
            "fatal_error": None,
            "structure_analysis": {"_ohlc_bars": {}},
        }
        mock_graph_cls.return_value = mock_graph

        output_dir = str(tmp_path / "runs")
        test_args = ["main.py", "XAUUSD", "--output-dir", output_dir]
        with patch.object(sys, "argv", test_args):
            from main import main

            main()

        # Should create a result file (with some timestamp)
        run_files = list((tmp_path / "runs").rglob("*.json"))
        assert len(run_files) == 1


class TestMainTelegramNotification:
    """Test that --telegram flag triggers notifications for approved setups."""

    @patch("main.Settings")
    @patch("main.MarketStructureEngine")
    @patch("main.ForexFactoryCalendar")
    @patch("main.TerminalDataProvider")
    @patch("main.SynthesizerAgent")
    @patch("main.DeciderAgent")
    @patch("main.ReviewerAgent")
    @patch("main.TradingGraph")
    @patch("main.send_trade_notification")
    def test_telegram_sends_notification_on_approved_setup(
        self,
        mock_send: MagicMock,
        mock_graph_cls: MagicMock,
        mock_reviewer_cls: MagicMock,
        mock_decider_cls: MagicMock,
        mock_synth_cls: MagicMock,
        mock_provider_cls: MagicMock,
        mock_calendar_cls: MagicMock,
        mock_analyzer_cls: MagicMock,
        mock_settings_cls: MagicMock,
    ) -> None:
        """With --telegram flag, notification is sent for approved buy/sell setups."""
        mock_settings = mock_settings_cls.return_value
        mock_settings.openai_api_key = ""
        mock_settings.openai_base_url = ""
        mock_settings.openai_model = "gpt-4"
        mock_settings.openai_reasoning_effort = ""
        mock_settings.terminal_server_url = ""
        mock_settings.terminal_api_key = ""
        mock_settings.telegram_bot_token = "test-token"
        mock_settings.telegram_chat_id = "test-chat-id"
        mock_settings.web_ui_base_url = "http://localhost:3000"

        mock_graph = MagicMock()
        mock_graph.run.return_value = {
            "errors": [],
            "fatal_error": None,
            "decision": {"action": "buy_setup", "entry_price": "1900.00"},
            "market_context": {"bias": "bullish", "confidence": 0.85},
            "review": {"approved": True},
        }
        mock_graph_cls.return_value = mock_graph

        test_args = ["main.py", "XAUUSD", "--telegram"]
        with patch.object(sys, "argv", test_args):
            from main import main

            main()

        mock_send.assert_called_once()
        call_kwargs = mock_send.call_args[1]
        assert call_kwargs["symbol"] == "XAUUSD"
        assert call_kwargs["decision"]["action"] == "buy_setup"
        assert call_kwargs["review"]["approved"] is True

    @patch("main.Settings")
    @patch("main.MarketStructureEngine")
    @patch("main.ForexFactoryCalendar")
    @patch("main.TerminalDataProvider")
    @patch("main.SynthesizerAgent")
    @patch("main.DeciderAgent")
    @patch("main.ReviewerAgent")
    @patch("main.TradingGraph")
    @patch("main.send_trade_notification")
    def test_no_telegram_flag_skips_notification(
        self,
        mock_send: MagicMock,
        mock_graph_cls: MagicMock,
        mock_reviewer_cls: MagicMock,
        mock_decider_cls: MagicMock,
        mock_synth_cls: MagicMock,
        mock_provider_cls: MagicMock,
        mock_calendar_cls: MagicMock,
        mock_analyzer_cls: MagicMock,
        mock_settings_cls: MagicMock,
    ) -> None:
        """Without --telegram flag, no notification code executes."""
        mock_settings = mock_settings_cls.return_value
        mock_settings.openai_api_key = ""
        mock_settings.openai_base_url = ""
        mock_settings.openai_model = "gpt-4"
        mock_settings.openai_reasoning_effort = ""
        mock_settings.terminal_server_url = ""
        mock_settings.terminal_api_key = ""

        mock_graph = MagicMock()
        mock_graph.run.return_value = {
            "errors": [],
            "fatal_error": None,
            "decision": {"action": "buy_setup", "entry_price": "1900.00"},
            "market_context": {"bias": "bullish"},
            "review": {"approved": True},
        }
        mock_graph_cls.return_value = mock_graph

        test_args = ["main.py", "XAUUSD"]
        with patch.object(sys, "argv", test_args):
            from main import main

            main()

        mock_send.assert_not_called()

    @patch("main.Settings")
    @patch("main.MarketStructureEngine")
    @patch("main.ForexFactoryCalendar")
    @patch("main.TerminalDataProvider")
    @patch("main.SynthesizerAgent")
    @patch("main.DeciderAgent")
    @patch("main.ReviewerAgent")
    @patch("main.TradingGraph")
    @patch("main.send_trade_notification")
    def test_telegram_skips_non_trade_action(
        self,
        mock_send: MagicMock,
        mock_graph_cls: MagicMock,
        mock_reviewer_cls: MagicMock,
        mock_decider_cls: MagicMock,
        mock_synth_cls: MagicMock,
        mock_provider_cls: MagicMock,
        mock_calendar_cls: MagicMock,
        mock_analyzer_cls: MagicMock,
        mock_settings_cls: MagicMock,
    ) -> None:
        """With --telegram, notification is NOT sent when action is no_trade."""
        mock_settings = mock_settings_cls.return_value
        mock_settings.openai_api_key = ""
        mock_settings.openai_base_url = ""
        mock_settings.openai_model = "gpt-4"
        mock_settings.openai_reasoning_effort = ""
        mock_settings.terminal_server_url = ""
        mock_settings.terminal_api_key = ""
        mock_settings.telegram_bot_token = "test-token"
        mock_settings.telegram_chat_id = "test-chat-id"

        mock_graph = MagicMock()
        mock_graph.run.return_value = {
            "errors": [],
            "fatal_error": None,
            "decision": {"action": "no_trade"},
            "market_context": {"bias": "neutral"},
            "review": {"approved": True},
        }
        mock_graph_cls.return_value = mock_graph

        test_args = ["main.py", "XAUUSD", "--telegram"]
        with patch.object(sys, "argv", test_args):
            from main import main

            main()

        mock_send.assert_not_called()

    @patch("main.Settings")
    @patch("main.MarketStructureEngine")
    @patch("main.ForexFactoryCalendar")
    @patch("main.TerminalDataProvider")
    @patch("main.SynthesizerAgent")
    @patch("main.DeciderAgent")
    @patch("main.ReviewerAgent")
    @patch("main.TradingGraph")
    @patch("main.send_trade_notification")
    def test_telegram_skips_unapproved_review(
        self,
        mock_send: MagicMock,
        mock_graph_cls: MagicMock,
        mock_reviewer_cls: MagicMock,
        mock_decider_cls: MagicMock,
        mock_synth_cls: MagicMock,
        mock_provider_cls: MagicMock,
        mock_calendar_cls: MagicMock,
        mock_analyzer_cls: MagicMock,
        mock_settings_cls: MagicMock,
    ) -> None:
        """With --telegram, notification is NOT sent when review is not approved."""
        mock_settings = mock_settings_cls.return_value
        mock_settings.openai_api_key = ""
        mock_settings.openai_base_url = ""
        mock_settings.openai_model = "gpt-4"
        mock_settings.openai_reasoning_effort = ""
        mock_settings.terminal_server_url = ""
        mock_settings.terminal_api_key = ""
        mock_settings.telegram_bot_token = "test-token"
        mock_settings.telegram_chat_id = "test-chat-id"

        mock_graph = MagicMock()
        mock_graph.run.return_value = {
            "errors": [],
            "fatal_error": None,
            "decision": {"action": "buy_setup"},
            "market_context": {"bias": "bullish"},
            "review": {"approved": False},
        }
        mock_graph_cls.return_value = mock_graph

        test_args = ["main.py", "XAUUSD", "--telegram"]
        with patch.object(sys, "argv", test_args):
            from main import main

            main()

        mock_send.assert_not_called()

    @patch("main.Settings")
    @patch("main.MarketStructureEngine")
    @patch("main.ForexFactoryCalendar")
    @patch("main.TerminalDataProvider")
    @patch("main.SynthesizerAgent")
    @patch("main.DeciderAgent")
    @patch("main.ReviewerAgent")
    @patch("main.TradingGraph")
    def test_telegram_warning_on_missing_credentials(
        self,
        mock_graph_cls: MagicMock,
        mock_reviewer_cls: MagicMock,
        mock_decider_cls: MagicMock,
        mock_synth_cls: MagicMock,
        mock_provider_cls: MagicMock,
        mock_calendar_cls: MagicMock,
        mock_analyzer_cls: MagicMock,
        mock_settings_cls: MagicMock,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Warning is logged when --telegram is set but token/chat_id are empty."""
        mock_settings = mock_settings_cls.return_value
        mock_settings.openai_api_key = ""
        mock_settings.openai_base_url = ""
        mock_settings.openai_model = "gpt-4"
        mock_settings.openai_reasoning_effort = ""
        mock_settings.terminal_server_url = ""
        mock_settings.terminal_api_key = ""
        mock_settings.telegram_bot_token = ""
        mock_settings.telegram_chat_id = ""

        mock_graph = MagicMock()
        mock_graph.run.return_value = {"errors": [], "fatal_error": None}
        mock_graph_cls.return_value = mock_graph

        test_args = ["main.py", "XAUUSD", "--telegram"]
        with patch.object(sys, "argv", test_args):
            from main import main

            with caplog.at_level(logging.WARNING):
                main()

        assert "--telegram flag set but TRADING_TELEGRAM_BOT_TOKEN" in caplog.text
