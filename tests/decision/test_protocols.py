from src.decision.protocols import CalendarProvider, DataSource, StructureAnalyzer


class TestProtocolDefinitions:
    def test_data_source_has_get_candles(self):
        assert hasattr(DataSource, "get_candles")

    def test_data_source_has_get_symbol_price(self):
        assert hasattr(DataSource, "get_symbol_price")

    def test_data_source_has_get_positions(self):
        assert hasattr(DataSource, "get_positions")

    def test_data_source_has_get_pending_orders(self):
        assert hasattr(DataSource, "get_pending_orders")

    def test_data_source_has_get_broker_time(self):
        assert hasattr(DataSource, "get_broker_time")

    def test_calendar_provider_has_fetch_events(self):
        assert hasattr(CalendarProvider, "fetch_events")

    def test_structure_analyzer_has_analyze(self):
        assert hasattr(StructureAnalyzer, "analyze")


class TestRuntimeCheckable:
    def test_data_source_is_runtime_checkable(self):
        assert hasattr(DataSource, "__protocol_attrs__")

    def test_calendar_provider_is_runtime_checkable(self):
        assert hasattr(CalendarProvider, "__protocol_attrs__")

    def test_structure_analyzer_is_runtime_checkable(self):
        assert hasattr(StructureAnalyzer, "__protocol_attrs__")


class TestProtocolConformance:
    def test_concrete_class_satisfies_data_source(self):
        class MockDataSource:
            def get_candles(self, symbol, timeframe, count):
                return ""

            def get_symbol_price(self, symbol):
                return {}

            def get_positions(self, symbol=None):
                return []

            def get_pending_orders(self, symbol=None):
                return []

            def get_broker_time(self):
                from datetime import datetime

                return datetime(2026, 7, 23, 21, 8, 54)

        assert isinstance(MockDataSource(), DataSource)

    def test_concrete_class_satisfies_calendar_provider(self):
        class MockCalendarProvider:
            def fetch_events(self):
                return []

        assert isinstance(MockCalendarProvider(), CalendarProvider)

    def test_concrete_class_satisfies_structure_analyzer(self):
        class MockStructureAnalyzer:
            def analyze(self, snapshots, profile_overrides=None):
                return {}

        assert isinstance(MockStructureAnalyzer(), StructureAnalyzer)

    def test_incomplete_class_fails_data_source(self):
        class IncompleteDataSource:
            def get_candles(self, symbol, timeframe, count):
                return ""

        assert not isinstance(IncompleteDataSource(), DataSource)
