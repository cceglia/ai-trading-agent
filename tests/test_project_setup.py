import os

import pytest


class TestProjectFiles:
    def test_pyproject_toml_exists(self):
        assert os.path.exists("pyproject.toml")

    def test_env_template_exists(self):
        assert os.path.exists(".env.template")

    def test_src_directory_exists(self):
        assert os.path.isdir("src")

    def test_src_init_exists(self):
        assert os.path.exists("src/__init__.py")

    def test_decision_module_exists(self):
        assert os.path.isdir("src/decision")

    def test_data_module_exists(self):
        assert os.path.isdir("src/data")

    def test_calendar_module_exists(self):
        assert os.path.isdir("src/calendar")

    def test_orchestrator_module_exists(self):
        assert os.path.isdir("src/orchestrator")

    def test_analysis_module_exists(self):
        assert os.path.isdir("src/analysis")
