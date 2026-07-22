import logging

from src.logging_config import setup_logging


class TestSetupLogging:
    def test_sets_root_logger_level(self):
        setup_logging("WARNING")
        assert logging.getLogger().level == logging.WARNING

    def test_sets_info_level(self):
        setup_logging("INFO")
        assert logging.getLogger().level == logging.INFO

    def test_sets_debug_level(self):
        setup_logging("DEBUG")
        assert logging.getLogger().level == logging.DEBUG

    def test_adds_handler(self):
        initial_count = len(logging.getLogger().handlers)
        setup_logging("INFO")
        assert len(logging.getLogger().handlers) >= initial_count
