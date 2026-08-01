"""Tests for main.py entry point — Issue #13 error duplication."""

import sys
from unittest.mock import MagicMock, patch

import pytest


class TestMainErrorDuplication:
    """Duplicate error-printing blocks in main.py (Issue #13).

    The first block (lines 92-96) prints "Warnings/Errors" and the second
    (lines 215-219) prints "Errors". The second block is dead code when
    a fatal error occurs (sys.exit at line 90). But when there is no fatal
    error AND result["errors"] is non-empty, the error text is printed
    twice — once from each block.

    RED: This test asserts that the error message ``"test error"`` appears
    exactly once in stdout. Currently it appears twice (count == 2), so
    ``assert count == 1`` fails.
    """

    @patch("main.Settings")
    @patch("src.analysis.structure_analyzer.MarketStructureEngine")
    @patch("src.calendar.forexfactory.ForexFactoryCalendar")
    @patch("src.data.terminal_data_provider.TerminalDataProvider")
    @patch("main.create_llm_client")
    @patch("src.decision.agents.SynthesizerAgent")
    @patch("src.decision.agents.DeciderAgent")
    @patch("src.decision.agents.ReviewerAgent")
    @patch("src.orchestrator.graph.TradingGraph")
    def test_errors_printed_exactly_once(
        self,
        mock_graph_cls: MagicMock,
        mock_reviewer_cls: MagicMock,
        mock_decider_cls: MagicMock,
        mock_synth_cls: MagicMock,
        mock_llm_client_cls: MagicMock,
        mock_provider_cls: MagicMock,
        mock_calendar_cls: MagicMock,
        mock_analyzer_cls: MagicMock,
        mock_settings_cls: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Verify errors are printed exactly once, not twice.

        mocks:
        - Settings: returns clean defaults so no env vars are needed.
        - All lazy imports inside main(): replaced with MagicMock so
          no real infrastructure is touched.
        - sys.argv: set to ``["main.py", "EURUSD"]`` so argparse
          succeeds.
        - TradingGraph.run(): returns ``{"errors": ["test error"]}``
          so the error-print blocks are exercised without a fatal error.
        """
        # ── Configure Settings mock ──────────────────────────────────
        mock_settings = mock_settings_cls.return_value
        mock_settings.openai_api_key = ""
        mock_settings.openai_base_url = ""
        mock_settings.openai_model = "gpt-4"
        mock_settings.openai_reasoning_effort = ""
        mock_settings.terminal_server_url = ""
        mock_settings.terminal_api_key = ""
        mock_settings.primary_llm_provider = "openai"
        mock_settings.reviewer_llm_provider = "openai"
        mock_settings.cost_per_symbol_limit = 0.05

        # ── Configure TradingGraph mock ──────────────────────────────
        mock_graph = MagicMock()
        mock_graph.run.return_value = {"errors": ["test error"]}
        mock_graph_cls.return_value = mock_graph

        # ── Mock sys.argv to provide required symbol argument ────────
        test_args = ["main.py", "EURUSD"]
        with patch.object(sys, "argv", test_args):
            # Import inside the test so the module is loaded while
            # our patches are in effect.
            from main import main

            main()

        captured = capsys.readouterr()

        # Count how many times the actual error message appears in the
        # output.  The two blocks on lines 92-96 and 215-219 both print
        # the error list, so "test error" appears twice in the current
        # code.  After removing the duplicate block it should appear
        # exactly once.
        count = captured.out.count("test error")

        # RED: currently the error message is printed twice (once by
        # each block), so assert count == 1 fails with count == 2.
        assert count == 1, (
            f"Expected exactly 1 occurrence of 'test error' in stdout, "
            f"got {count}.\n"
            f"The duplicate block (lines 215-219) prints errors a "
            f"second time.\n"
            f"Full stdout:\n{captured.out}"
        )


class TestCreateAgentsTemperatureWiring:
    """Tests that _create_agents wires temperature correctly to both LLM clients.

    The primary client should receive settings.openai_temperature as
    default_temperature. The reviewer client should always receive
    settings.reviewer_temperature as its own independent default_temperature
    (even when it matches the primary — unlike string overrides that use ""
    to mean "inherit from primary").
    """

    def test_primary_client_receives_openai_temperature(self) -> None:
        """Primary client gets openai_temperature as default_temperature."""
        import main
        from src.decision.cost_tracker import CostTracker

        settings = MagicMock()
        settings.openai_api_key = "test-key"
        settings.openai_base_url = ""
        settings.openai_model = "gpt-4o"
        settings.openai_reasoning_effort = ""
        settings.openai_temperature = 0.7
        settings.primary_llm_provider = "openai"

        settings.reviewer_llm_provider = "openai"
        settings.reviewer_model = ""
        settings.reviewer_api_key = ""
        settings.reviewer_base_url = ""
        settings.reviewer_reasoning_effort = ""
        settings.reviewer_model_family_override = ""
        settings.reviewer_model_version_override = ""
        settings.reviewer_temperature = 0.0

        cost_tracker = MagicMock(spec=CostTracker)

        with patch("main.create_llm_client") as mock_create:
            main._create_agents(settings, cost_tracker)

        # Primary client kwargs: should include default_temperature=0.7
        primary_call = mock_create.call_args_list[0]
        assert primary_call.kwargs["default_temperature"] == 0.7, (
            f"Expected default_temperature=0.7 for primary client, "
            f"got {primary_call.kwargs.get('default_temperature')}"
        )

    def test_reviewer_client_receives_reviewer_temperature(self) -> None:
        """Reviewer client gets reviewer_temperature, independent of primary."""
        import main
        from src.decision.cost_tracker import CostTracker

        settings = MagicMock()
        settings.openai_api_key = "test-key"
        settings.openai_base_url = ""
        settings.openai_model = "gpt-4o"
        settings.openai_reasoning_effort = ""
        settings.openai_temperature = 0.7  # different from reviewer
        settings.primary_llm_provider = "openai"

        settings.reviewer_llm_provider = "openai"
        settings.reviewer_model = ""
        settings.reviewer_api_key = ""
        settings.reviewer_base_url = ""
        settings.reviewer_reasoning_effort = ""
        settings.reviewer_model_family_override = ""
        settings.reviewer_model_version_override = ""
        settings.reviewer_temperature = 0.3  # different from primary

        cost_tracker = MagicMock(spec=CostTracker)

        with patch("main.create_llm_client") as mock_create:
            main._create_agents(settings, cost_tracker)

        # Reviewer is the second call to create_llm_client
        reviewer_call = mock_create.call_args_list[1]
        assert reviewer_call.kwargs["default_temperature"] == 0.3, (
            f"Expected default_temperature=0.3 for reviewer client, "
            f"got {reviewer_call.kwargs.get('default_temperature')}"
        )

    def test_primary_and_reviewer_temperatures_are_independent(self) -> None:
        """Changing reviewer temperature does NOT affect primary client."""
        import main
        from src.decision.cost_tracker import CostTracker

        settings = MagicMock()
        settings.openai_api_key = "test-key"
        settings.openai_base_url = ""
        settings.openai_model = "gpt-4o"
        settings.openai_reasoning_effort = ""
        settings.openai_temperature = 0.0
        settings.primary_llm_provider = "openai"

        settings.reviewer_llm_provider = "openai"
        settings.reviewer_model = ""
        settings.reviewer_api_key = ""
        settings.reviewer_base_url = ""
        settings.reviewer_reasoning_effort = ""
        settings.reviewer_model_family_override = ""
        settings.reviewer_model_version_override = ""
        settings.reviewer_temperature = 0.9  # differs from primary

        cost_tracker = MagicMock(spec=CostTracker)

        with patch("main.create_llm_client") as mock_create:
            main._create_agents(settings, cost_tracker)

        primary_call = mock_create.call_args_list[0]
        reviewer_call = mock_create.call_args_list[1]

        assert primary_call.kwargs["default_temperature"] == 0.0
        assert reviewer_call.kwargs["default_temperature"] == 0.9


class TestMainCostLogging:
    """main.py must not log 'Total LLM cost' — that's graph.run()'s job."""

    def test_no_redundant_cost_log(self) -> None:
        """main.py should not log 'Total LLM cost' — graph.run() already does."""
        import inspect

        from main import main as main_fn

        source = inspect.getsource(main_fn)
        assert source.count("Total LLM cost") == 0, (
            "main.py still contains 'Total LLM cost' log line — should be removed"
        )
