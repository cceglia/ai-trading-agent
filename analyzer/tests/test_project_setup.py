import os
import re
from pathlib import Path


class TestProjectFiles:
    def test_pyproject_toml_exists(self):
        assert os.path.exists("pyproject.toml")

    def test_env_template_exists(self):
        assert os.path.exists("../.env.template")

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


class TestNoReviewerDeciderResidue:
    """TEST-013 / AC-013: the single-synthesizer graph must not retain any
    reviewer/decider/review-attempt concept in core source.

    The DeciderAgent/ReviewerAgent and their retry loop were removed from the
    core pipeline. This static search fails if any reference resurfaces in the
    non-test source tree.
    """

    _CORE_SOURCE_DIRS = ("src", "config")
    _CORE_SOURCE_FILES = ("main.py",)

    def _core_source_files(self) -> list[Path]:
        root = Path(__file__).resolve().parent.parent
        files: list[Path] = []
        for dirname in self._CORE_SOURCE_DIRS:
            files.extend((root / dirname).rglob("*.py"))
        for filename in self._CORE_SOURCE_FILES:
            path = root / filename
            if path.is_file():
                files.append(path)
        return files

    def test_core_source_has_no_reviewer_or_decider_references(self):
        pattern = re.compile(r"reviewer|decider|BLOCKED_BY_REVIEW", re.IGNORECASE)
        offending: list[str] = []
        for path in self._core_source_files():
            try:
                content = path.read_text(encoding="utf-8")
            except OSError:
                continue
            for line_no, line in enumerate(content.splitlines(), start=1):
                if pattern.search(line):
                    offending.append(f"{path.name}:{line_no}: {line.strip()}")
        assert not offending, "reviewer/decider references remain in core source:\n" + "\n".join(
            offending
        )
