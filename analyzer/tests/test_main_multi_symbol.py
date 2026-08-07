from unittest.mock import MagicMock


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
