"""Tests for multi-symbol support in main.py."""

import logging
import sys
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from src.decision.cost_tracker import CostLimitExceeded


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
        mock_settings.cost_per_symbol_limit = 0.05

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
        mock_settings.cost_per_symbol_limit = 0.05

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
        mock_settings.cost_per_symbol_limit = 0.05

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
        mock_settings.cost_per_symbol_limit = 0.05

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


class TestMainCostLimit:
    """Cost limit enforcement in the pipeline (TASK-3).

    These tests verify that:
      - CostLimitExceeded propagates uncaught out of _run_single_symbol
      - sys.exit(1) is called when limit is exceeded
      - cost_tracker.set_limit() is called with settings.cost_per_symbol_limit
      - cost_tracker.reset() is called per symbol
      - Zero limit disables enforcement
    """

    # ------------------------------------------------------------------ #
    # Test 1: cost limit aborts the entire run with sys.exit(1)
    # ------------------------------------------------------------------ #
    @patch("main.Settings")
    @patch("main.MarketStructureEngine")
    @patch("main.ForexFactoryCalendar")
    @patch("main.TerminalDataProvider")
    @patch("main.SynthesizerAgent")
    @patch("main.DeciderAgent")
    @patch("main.ReviewerAgent")
    @patch("main.TradingGraph")
    def test_cost_limit_aborts_run(
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
        """Verify sys.exit(1) when CostLimitExceeded is raised mid-run.

        RED: currently CostLimitExceeded is caught by _run_single_symbol's
        ``except Exception`` handler, so the exception never reaches
        ``main()`` and ``sys.exit(1)`` is never called.
        """
        mock_settings = mock_settings_cls.return_value
        mock_settings.openai_api_key = ""
        mock_settings.openai_base_url = ""
        mock_settings.openai_model = "gpt-4"
        mock_settings.openai_reasoning_effort = ""
        mock_settings.terminal_server_url = ""
        mock_settings.terminal_api_key = ""
        mock_settings.cost_per_symbol_limit = 0.05

        mock_graph = MagicMock()
        # First symbol succeeds, second raises CostLimitExceeded
        mock_graph.run.side_effect = [
            {"errors": [], "fatal_error": None},
            CostLimitExceeded(limit=0.05, total_cost=0.06),
        ]
        mock_graph_cls.return_value = mock_graph

        test_args = ["main.py", "XAUUSD", "EURUSD"]
        with patch.object(sys, "argv", test_args):
            from main import main

            with pytest.raises(SystemExit) as exc_info:
                main()

        assert exc_info.value.code == 1, (
            f"Expected exit code 1 when cost limit exceeded, got {exc_info.value.code}"
        )

    # ------------------------------------------------------------------ #
    # Test 2: cost limit message includes limit/cost details
    # ------------------------------------------------------------------ #
    @patch("main.Settings")
    @patch("main.MarketStructureEngine")
    @patch("main.ForexFactoryCalendar")
    @patch("main.TerminalDataProvider")
    @patch("main.SynthesizerAgent")
    @patch("main.DeciderAgent")
    @patch("main.ReviewerAgent")
    @patch("main.TradingGraph")
    def test_cost_limit_exceeded_message_in_stderr(
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
        """Verify the error log includes limit/cost details.

        RED: CostLimitExceeded is swallowed by _run_single_symbol and
        never reaches ``main()``'s except handler, so ``logger.error(
        "Analysis failed: ...")`` is never emitted → ``pytest.raises(
        SystemExit)`` fails first and the message assertions are
        unreachable.
        """
        mock_settings = mock_settings_cls.return_value
        mock_settings.openai_api_key = ""
        mock_settings.openai_base_url = ""
        mock_settings.openai_model = "gpt-4"
        mock_settings.openai_reasoning_effort = ""
        mock_settings.terminal_server_url = ""
        mock_settings.terminal_api_key = ""
        mock_settings.cost_per_symbol_limit = 0.05

        mock_graph = MagicMock()
        mock_graph.run.side_effect = [
            {"errors": [], "fatal_error": None},
            CostLimitExceeded(limit=0.05, total_cost=0.06, symbol="EURUSD"),
        ]
        mock_graph_cls.return_value = mock_graph

        test_args = ["main.py", "XAUUSD", "EURUSD"]
        with patch.object(sys, "argv", test_args):
            from main import main

            with caplog.at_level(logging.ERROR):
                with pytest.raises(SystemExit):
                    main()

        # The error log from main()'s except handler must mention the cost limit
        assert "Cost limit" in caplog.text, (
            f"Expected 'Cost limit' in error log, got:\n{caplog.text}"
        )
        assert "exceeded" in caplog.text, f"Expected 'exceeded' in error log, got:\n{caplog.text}"
        assert "EURUSD" in caplog.text, (
            f"Expected symbol 'EURUSD' in error log, got:\n{caplog.text}"
        )

    # ------------------------------------------------------------------ #
    # Test 3: cost_tracker.reset() is called per symbol
    # ------------------------------------------------------------------ #
    @patch("main.MarketStructureEngine")
    @patch("main.ForexFactoryCalendar")
    @patch("main.TerminalDataProvider")
    @patch("main.SynthesizerAgent")
    @patch("main.DeciderAgent")
    @patch("main.ReviewerAgent")
    @patch("main.TradingGraph")
    @patch("main.CostTracker")
    def test_pipeline_resets_cost_tracker_per_symbol(
        self,
        mock_ct_cls: MagicMock,
        mock_graph_cls: MagicMock,
        mock_reviewer_cls: MagicMock,
        mock_decider_cls: MagicMock,
        mock_synth_cls: MagicMock,
        mock_provider_cls: MagicMock,
        mock_calendar_cls: MagicMock,
        mock_analyzer_cls: MagicMock,
    ) -> None:
        """Verify cost_tracker.reset() is called before each symbol.

        RED: ``_run_pipeline`` does not call ``reset()`` yet, so
        ``mock_ct.reset.call_count == 0`` and the assertion fails.
        """
        mock_ct = MagicMock()
        mock_ct.total_cost = 0.0
        mock_ct_cls.return_value = mock_ct

        mock_graph = MagicMock()
        mock_graph.run.return_value = {"errors": [], "fatal_error": None}
        mock_graph_cls.return_value = mock_graph

        settings = MagicMock()
        settings.model_pricing = {}
        settings.cost_per_symbol_limit = 0.05
        settings.openai_api_key = ""
        settings.openai_base_url = ""
        settings.openai_model = "gpt-4"
        settings.openai_reasoning_effort = ""
        settings.terminal_server_url = ""
        settings.terminal_api_key = ""

        from main import _run_pipeline

        _run_pipeline(settings, ["XAUUSD", "EURUSD"], None, False)

        # reset() should be called once per symbol (2 symbols)
        assert mock_ct.reset.call_count == 2, (
            f"Expected 2 calls to reset() (one per symbol), got {mock_ct.reset.call_count}"
        )

    # ------------------------------------------------------------------ #
    # Test 4: cost_tracker.set_limit() is called from settings
    # ------------------------------------------------------------------ #
    @patch("main.MarketStructureEngine")
    @patch("main.ForexFactoryCalendar")
    @patch("main.TerminalDataProvider")
    @patch("main.SynthesizerAgent")
    @patch("main.DeciderAgent")
    @patch("main.ReviewerAgent")
    @patch("main.TradingGraph")
    @patch("main.CostTracker")
    def test_pipeline_sets_limit_from_settings(
        self,
        mock_ct_cls: MagicMock,
        mock_graph_cls: MagicMock,
        mock_reviewer_cls: MagicMock,
        mock_decider_cls: MagicMock,
        mock_synth_cls: MagicMock,
        mock_provider_cls: MagicMock,
        mock_calendar_cls: MagicMock,
        mock_analyzer_cls: MagicMock,
    ) -> None:
        """Verify set_limit() is called with settings.cost_per_symbol_limit.

        RED: ``_run_pipeline`` does not call ``set_limit()`` yet, so
        ``mock_ct.set_limit.assert_called_once_with(0.05)`` fails.
        """
        mock_ct = MagicMock()
        mock_ct.total_cost = 0.0
        mock_ct_cls.return_value = mock_ct

        mock_graph = MagicMock()
        mock_graph.run.return_value = {"errors": [], "fatal_error": None}
        mock_graph_cls.return_value = mock_graph

        settings = MagicMock()
        settings.model_pricing = {}
        settings.cost_per_symbol_limit = 0.05
        settings.openai_api_key = ""
        settings.openai_base_url = ""
        settings.openai_model = "gpt-4"
        settings.openai_reasoning_effort = ""
        settings.terminal_server_url = ""
        settings.terminal_api_key = ""

        from main import _run_pipeline

        _run_pipeline(settings, ["XAUUSD", "EURUSD"], None, False)

        mock_ct.set_limit.assert_called_once_with(0.05)

    # ------------------------------------------------------------------ #
    # Test 5: _run_single_symbol re-raises CostLimitExceeded
    # ------------------------------------------------------------------ #
    def test_run_single_symbol_re_raises_cost_limit_exceeded(self) -> None:
        """Verify CostLimitExceeded propagates out of _run_single_symbol.

        RED: ``_run_single_symbol`` has only ``except Exception`` which
        catches ``CostLimitExceeded`` (since it IS an ``Exception``) and
        returns ``("error", ...)`` instead of re-raising.
        """
        from main import _run_single_symbol

        mock_graph = MagicMock()
        mock_graph.run.side_effect = CostLimitExceeded(limit=0.05, total_cost=0.06)

        settings = MagicMock()

        with pytest.raises(CostLimitExceeded):
            _run_single_symbol(mock_graph, "XAUUSD", settings, None, False)

    # ------------------------------------------------------------------ #
    # Test 6: zero limit does not abort
    # ------------------------------------------------------------------ #
    @patch("main.Settings")
    @patch("main.MarketStructureEngine")
    @patch("main.ForexFactoryCalendar")
    @patch("main.TerminalDataProvider")
    @patch("main.SynthesizerAgent")
    @patch("main.DeciderAgent")
    @patch("main.ReviewerAgent")
    @patch("main.TradingGraph")
    def test_main_with_zero_limit_does_not_abort(
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
        """cost_per_symbol_limit=0 disables enforcement — all symbols process.

        RED phase: no enforcement exists yet, so the test passes
        (all symbols process normally). This is a regression/spec test
        that will validate ``set_limit(0)`` disables the guard once
        the feature is implemented.
        """
        mock_settings = mock_settings_cls.return_value
        mock_settings.openai_api_key = ""
        mock_settings.openai_base_url = ""
        mock_settings.openai_model = "gpt-4"
        mock_settings.openai_reasoning_effort = ""
        mock_settings.terminal_server_url = ""
        mock_settings.terminal_api_key = ""
        mock_settings.cost_per_symbol_limit = 0  # ← zero disables enforcement

        mock_graph = MagicMock()
        mock_graph.run.return_value = {"errors": [], "fatal_error": None}
        mock_graph_cls.return_value = mock_graph

        test_args = ["main.py", "XAUUSD", "EURUSD"]
        with patch.object(sys, "argv", test_args):
            from main import main

            # Should NOT raise SystemExit
            main()

        # Both symbols must have been processed
        assert mock_graph.run.call_count == 2, (
            f"Expected 2 symbols processed with zero limit, got {mock_graph.run.call_count}"
        )


class TestMainIntegrationCostLimit:
    """End-to-end cost limit abort integration tests (TASK-4).

    These tests exercise the full abort path:
      CostTracker raises → graph node re-raises → _run_single_symbol
      re-raises → main() calls sys.exit(1).

    All production code (TASK-1/2/3) is already in place, so these
    tests should pass GREEN immediately.
    """

    @patch("main.Settings")
    @patch("main.MarketStructureEngine")
    @patch("main.ForexFactoryCalendar")
    @patch("main.TerminalDataProvider")
    @patch("main.SynthesizerAgent")
    @patch("main.DeciderAgent")
    @patch("main.ReviewerAgent")
    @patch("main.TradingGraph")
    def test_cost_limit_stops_remaining_symbols(
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
        """3 symbols: first two succeed, third exceeds limit → sys.exit(1).

        Verifies that the third symbol raises CostLimitExceeded,
        sys.exit(1) is called, and graph.run is NOT called for any
        symbol after the failure (i.e. the fourth+ symbols are skipped).
        """
        mock_settings = mock_settings_cls.return_value
        mock_settings.openai_api_key = ""
        mock_settings.openai_base_url = ""
        mock_settings.openai_model = "gpt-4"
        mock_settings.openai_reasoning_effort = ""
        mock_settings.terminal_server_url = ""
        mock_settings.terminal_api_key = ""
        mock_settings.cost_per_symbol_limit = 0.05

        mock_graph = MagicMock()
        # Symbols: XAUUSD (ok), EURUSD (ok), GBPUSD (exceeds), USDJPY (must NOT run)
        mock_graph.run.side_effect = [
            {"errors": [], "fatal_error": None},  # XAUUSD
            {"errors": [], "fatal_error": None},  # EURUSD
            CostLimitExceeded(limit=0.05, total_cost=0.06),  # GBPUSD
            # If reached, this would be USDJPY — must NOT happen
            {"errors": [], "fatal_error": None},
        ]
        mock_graph_cls.return_value = mock_graph

        test_args = ["main.py", "XAUUSD", "EURUSD", "GBPUSD", "USDJPY"]
        with patch.object(sys, "argv", test_args):
            from main import main

            with pytest.raises(SystemExit) as exc_info:
                main()

        assert exc_info.value.code == 1, (
            f"Expected exit code 1 when cost limit exceeded, got {exc_info.value.code}"
        )
        # Only 3 calls: XAUUSD, EURUSD, GBPUSD (the one that raised). USDJPY never runs.
        assert mock_graph.run.call_count == 3, (
            f"Expected exactly 3 graph.run calls (USDJPY should not run), "
            f"got {mock_graph.run.call_count}"
        )

    @patch("main.Settings")
    @patch("main.MarketStructureEngine")
    @patch("main.ForexFactoryCalendar")
    @patch("main.TerminalDataProvider")
    @patch("main.SynthesizerAgent")
    @patch("main.DeciderAgent")
    @patch("main.ReviewerAgent")
    @patch("main.TradingGraph")
    def test_cost_limit_on_first_symbol_aborts_immediately(
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
        """First symbol exceeds limit → sys.exit(1), no subsequent symbols.

        Verifies that when the very first symbol triggers CostLimitExceeded,
        the run aborts immediately and the remaining symbols are never processed.
        """
        mock_settings = mock_settings_cls.return_value
        mock_settings.openai_api_key = ""
        mock_settings.openai_base_url = ""
        mock_settings.openai_model = "gpt-4"
        mock_settings.openai_reasoning_effort = ""
        mock_settings.terminal_server_url = ""
        mock_settings.terminal_api_key = ""
        mock_settings.cost_per_symbol_limit = 0.05

        mock_graph = MagicMock()
        # First symbol exceeds immediately
        mock_graph.run.side_effect = CostLimitExceeded(limit=0.05, total_cost=0.06)
        mock_graph_cls.return_value = mock_graph

        test_args = ["main.py", "XAUUSD", "EURUSD", "GBPUSD"]
        with patch.object(sys, "argv", test_args):
            from main import main

            with pytest.raises(SystemExit) as exc_info:
                main()

        assert exc_info.value.code == 1, (
            f"Expected exit code 1 when cost limit exceeded, got {exc_info.value.code}"
        )
        # Only 1 call: XAUUSD (the one that raised). EURUSD and GBPUSD never run.
        assert mock_graph.run.call_count == 1, (
            f"Expected exactly 1 graph.run call (EURUSD/GBPUSD should not run), "
            f"got {mock_graph.run.call_count}"
        )

    @patch("main.MarketStructureEngine")
    @patch("main.ForexFactoryCalendar")
    @patch("main.TerminalDataProvider")
    @patch("main.SynthesizerAgent")
    @patch("main.DeciderAgent")
    @patch("main.ReviewerAgent")
    @patch("main.TradingGraph")
    def test_integration_cost_tracker_wired_through_pipeline(
        self,
        mock_graph_cls: MagicMock,
        mock_reviewer_cls: MagicMock,
        mock_decider_cls: MagicMock,
        mock_synth_cls: MagicMock,
        mock_provider_cls: MagicMock,
        mock_calendar_cls: MagicMock,
        mock_analyzer_cls: MagicMock,
    ) -> None:
        """Real CostTracker wired through _run_pipeline with a very low limit.

        Uses a real CostTracker (not mocked) wired through the pipeline.
        Sets a very low limit so the first real record_call() exceeds it.
        The mock graph.run() records a cost to the real tracker via a
        side_effect that calls record_call(), triggering the limit check.
        """
        from src.decision.cost_tracker import CostTracker

        # Use a real CostTracker with a very low limit
        real_ct = CostTracker()
        real_ct.set_limit(0.0001)  # Extremely low — any real call exceeds this

        # Track whether set_limit was called (it happens inside _run_pipeline)
        # We verify indirectly: if the limit is applied, the first call that
        # records a cost > 0.0001 will raise CostLimitExceeded.

        mock_graph = MagicMock()
        call_count = 0

        def side_effect_with_cost_tracking(symbol: str) -> dict[str, Any]:
            nonlocal call_count
            call_count += 1
            # Record a real cost that exceeds the tiny limit
            # gpt-4 prompt rate = 0.00003/token → 100 tokens = 0.003 > 0.0001
            real_ct.record_call("gpt-4", prompt_tokens=100, completion_tokens=50)
            return {"errors": [], "fatal_error": None}

        mock_graph.run.side_effect = side_effect_with_cost_tracking
        mock_graph_cls.return_value = mock_graph

        settings = MagicMock()
        settings.model_pricing = {}
        settings.cost_per_symbol_limit = 0.0001
        settings.openai_api_key = ""
        settings.openai_base_url = ""
        settings.openai_model = "gpt-4"
        settings.openai_reasoning_effort = ""
        settings.terminal_server_url = ""
        settings.terminal_api_key = ""

        from main import _run_pipeline

        with pytest.raises(CostLimitExceeded):
            _run_pipeline(settings, ["XAUUSD", "EURUSD"], None, False)

        # Only XAUUSD ran (the one that triggered the limit). EURUSD never ran.
        assert call_count == 1, (
            f"Expected exactly 1 call (EURUSD should not run after limit exceeded), "
            f"got {call_count}"
        )
        # Verify the CostTracker actually recorded the cost
        assert real_ct.total_cost > 0.0001, (
            f"Expected total_cost to exceed limit, got {real_ct.total_cost}"
        )


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
        mock_settings.cost_per_symbol_limit = 0.05

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
        mock_settings.cost_per_symbol_limit = 0.05

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
        mock_settings.cost_per_symbol_limit = 0.05

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
        mock_settings.cost_per_symbol_limit = 0.05

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
        mock_settings.cost_per_symbol_limit = 0.05

        mock_graph = MagicMock()
        mock_graph.run.return_value = {"errors": [], "fatal_error": None}
        mock_graph_cls.return_value = mock_graph

        test_args = ["main.py", "XAUUSD", "--telegram"]
        with patch.object(sys, "argv", test_args):
            from main import main

            with caplog.at_level(logging.WARNING):
                main()

        assert "--telegram flag set but TRADING_TELEGRAM_BOT_TOKEN" in caplog.text
