from unittest.mock import MagicMock, patch


def test_parser_accepts_multiple_symbols():
    import main

    args = main._build_parser().parse_args(["XAUUSD", "EURUSD"])
    assert args.symbols == ["XAUUSD", "EURUSD"]


def test_initialize_pipeline_passes_only_synthesizer_to_graph(monkeypatch):
    import main

    settings = MagicMock()
    settings.terminal_server_url = ""
    settings.terminal_api_key = ""
    settings.analysis_cache_dir = "data"
    settings.resolved_analysis_cache_dir = "data"
    synthesizer = MagicMock()
    graph = MagicMock()

    monkeypatch.setattr(main, "TerminalDataProvider", MagicMock())
    monkeypatch.setattr(main, "MarketStructureEngine", MagicMock())
    monkeypatch.setattr(main, "ForexFactoryCalendar", MagicMock())
    monkeypatch.setattr(main, "_create_agents", lambda *_: synthesizer)
    monkeypatch.setattr(main, "TradingGraph", graph)

    main._initialize_pipeline(settings, MagicMock())

    assert graph.call_args.kwargs["synthesizer"] is synthesizer
    assert "decider" not in graph.call_args.kwargs
    assert "review" not in graph.call_args.kwargs


def test_initialize_pipeline_writer_uses_resolved_absolute_cache_dir(monkeypatch, tmp_path):
    """ROOT-001 / AC-014: with a RELATIVE TRADING_ANALYSIS_CACHE_DIR the
    writer constructed by ``_initialize_pipeline`` must target the same
    project-root-resolved absolute directory the server scanner reads.

    The raw possibly-relative ``analysis_cache_dir`` (default ``"data"``)
    must never reach ``ResultWriter`` directly: the seam resolves it against
    the project root so analyzer and server share one root.
    """
    from pathlib import Path

    import main
    from config.settings import Settings

    project_root = Path(main.__file__).resolve().parent.parent
    _relative = "custom/cache/probe"
    monkeypatch.setenv("TRADING_ANALYSIS_CACHE_DIR", _relative)
    settings = Settings()

    synthesizer = MagicMock()
    graph = MagicMock()
    monkeypatch.setattr(main, "TerminalDataProvider", MagicMock())
    monkeypatch.setattr(main, "MarketStructureEngine", MagicMock())
    monkeypatch.setattr(main, "ForexFactoryCalendar", MagicMock())
    monkeypatch.setattr(main, "_create_agents", lambda *_: synthesizer)
    monkeypatch.setattr(main, "TradingGraph", graph)

    _graph, writer = main._initialize_pipeline(settings, MagicMock())

    expected = Path(settings.resolved_analysis_cache_dir)
    assert writer.base_dir == expected
    assert writer.base_dir.is_absolute()
    assert writer.base_dir == project_root / "custom" / "cache" / "probe"


def test_telegram_allows_actionable_degraded_analysis_from_nested_result():
    import main

    result = {
        "validation_status": "INVALID",
        "setup_status": "INVALID",
        "operational": False,
        "decision": {"action": "no_trade"},
        "analysis_result": {
            "validation_status": "VALID",
            "setup_status": "READY",
            "operational": True,
            "decision": {"action": "buy_setup"},
            "synthesis_status": "FAILED",
        },
    }
    settings = MagicMock()

    with patch("main.send_trade_notification") as send:
        main._send_telegram_notification("XAUUSD", result, settings)

    send.assert_called_once()


def test_telegram_suppresses_legacy_result_without_nested_analysis_result():
    import main

    result = {
        "validation_status": "VALID",
        "setup_status": "READY",
        "decision": {"action": "buy_setup"},
    }
    settings = MagicMock()

    with patch("main.send_trade_notification") as send:
        main._send_telegram_notification("XAUUSD", result, settings)

    send.assert_not_called()


def test_telegram_suppresses_nested_invalid_analysis_result():
    import main

    result = {
        "analysis_result": {
            "validation_status": "INVALID",
            "setup_status": "INVALID",
            "operational": False,
            "decision": {"action": "no_trade"},
        },
    }
    settings = MagicMock()

    with patch("main.send_trade_notification") as send:
        main._send_telegram_notification("XAUUSD", result, settings)

    send.assert_not_called()


def test_telegram_suppresses_nested_non_actionable_analysis_result():
    import main

    result = {
        "analysis_result": {
            "validation_status": "VALID",
            "setup_status": "READY",
            "operational": False,
            "decision": {"action": "no_trade"},
        },
    }
    settings = MagicMock()

    with patch("main.send_trade_notification") as send:
        main._send_telegram_notification("XAUUSD", result, settings)

    send.assert_not_called()


def _run_single_symbol_with_metrics(
    monkeypatch,
    *,
    telegram_enabled: bool,
    send_result: bool = True,
) -> tuple:
    """Run ``_run_single_symbol`` with a mock graph and metrics.

    ``send_result`` controls what ``_send_telegram_notification`` returns when
    telegram is enabled (True = sent, False = suppressed/ineligible).
    """
    import main
    from src.output.run_metrics import RunMetrics

    graph = MagicMock()
    graph.run.return_value = {
        "analysis_result": {
            "validation_status": "VALID",
            "setup_status": "READY",
            "operational": True,
            "decision": {"action": "buy_setup"},
        },
        "errors": [],
        "fatal_error": None,
    }
    settings = MagicMock()
    metrics = RunMetrics()
    monkeypatch.setattr(main, "_send_telegram_notification", lambda *_: send_result)
    _symbol, status, _data = main._run_single_symbol(
        graph, "XAUUSD", settings, None, telegram_enabled, metrics
    )
    return status, metrics


def test_run_single_symbol_telegram_disabled_records_no_notifications(monkeypatch):
    """METRICS-001: without ``--telegram`` no notification counters are
    recorded. ``notifications_suppressed`` must mean an ineligible result
    (FR-032), not 'telegram disabled'."""
    status, metrics = _run_single_symbol_with_metrics(
        monkeypatch, telegram_enabled=False, send_result=False
    )
    assert status == "success"
    assert metrics.notifications_sent == 0
    assert metrics.notifications_suppressed == 0


def test_run_single_symbol_telegram_enabled_records_sent(monkeypatch):
    status, metrics = _run_single_symbol_with_metrics(
        monkeypatch, telegram_enabled=True, send_result=True
    )
    assert status == "success"
    assert metrics.notifications_sent == 1
    assert metrics.notifications_suppressed == 0


def test_run_single_symbol_telegram_enabled_records_suppressed_ineligible(monkeypatch):
    """With telegram enabled, an ineligible result is a genuine suppression."""
    status, metrics = _run_single_symbol_with_metrics(
        monkeypatch, telegram_enabled=True, send_result=False
    )
    assert status == "success"
    assert metrics.notifications_sent == 0
    assert metrics.notifications_suppressed == 1


def test_print_symbol_summary_uses_deterministic_bias_not_stale_market_context(capsys):
    """SYNTH-010: the CLI summary must show the deterministic direction and
    the LLM synthesis explanation instead of N/A/0 from the absent legacy
    market_context."""
    from datetime import datetime

    import main
    from src.analysis.market_structure_engine.models import DecisionAction
    from src.decision.models import DecisionOutput
    from src.output.result_models import AnalysisResult

    analysis_result = AnalysisResult(
        symbol="XAUUSD",
        run_id="XAUUSD-20260726083000",
        started_at=datetime(2026, 7, 26, 8, 30),
        completed_at=datetime(2026, 7, 26, 8, 31),
        status="success",
        validation_status="VALID",
        setup_status="READY",
        trade_direction="BULLISH",
        direction="LONG",
        final_action="buy_setup",
        synthesis_status="SUCCESS",
        synthesis_explanation="deterministic context is bullish",
        operational=True,
    )
    result = {
        "decision": DecisionOutput(
            symbol="XAUUSD", action=DecisionAction.BUY_SETUP, reasoning="advisory"
        ),
        "analysis_result": analysis_result,
        "final_output": analysis_result.model_dump(mode="json"),
        "errors": [],
        "fatal_error": None,
    }

    main._print_symbol_summary("XAUUSD", result)

    out = capsys.readouterr().out
    assert "Bias       : BULLISH" in out
    assert "Confidence : N/A" in out
    assert "deterministic context is bullish" in out
    assert "Bias       : N/A" not in out
    assert "Bias       : 0" not in out


def test_print_symbol_summary_shows_no_setup_bias_for_no_trade(capsys):
    """A valid no-trade run shows its deterministic neutral direction, never
    a fabricated bullish/bearish bias."""
    from datetime import datetime

    import main
    from src.analysis.market_structure_engine.models import DecisionAction
    from src.decision.models import DecisionOutput
    from src.output.result_models import AnalysisResult

    analysis_result = AnalysisResult(
        symbol="XAUUSD",
        run_id="XAUUSD-20260726083000",
        started_at=datetime(2026, 7, 26, 8, 30),
        completed_at=datetime(2026, 7, 26, 8, 31),
        status="success",
        validation_status="VALID",
        setup_status="NO_SETUP",
        trade_direction="NEUTRAL",
        direction="NONE",
        final_action="no_trade",
        synthesis_status="SUCCESS",
        synthesis_explanation="no actionable setup",
        operational=False,
    )
    result = {
        "decision": DecisionOutput(
            symbol="XAUUSD", action=DecisionAction.NO_TRADE, reasoning="advisory"
        ),
        "analysis_result": analysis_result,
        "final_output": analysis_result.model_dump(mode="json"),
        "errors": [],
        "fatal_error": None,
    }

    main._print_symbol_summary("XAUUSD", result)

    out = capsys.readouterr().out
    assert "Bias       : NEUTRAL" in out
    assert "Confidence : N/A" in out
