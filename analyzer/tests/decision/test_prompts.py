import re

from src.decision.prompts import SYNTHESIZER_SYSTEM_PROMPT


class TestSynthesizerPrompt:
    def test_contains_evidence_hierarchy(self):
        assert "Evidence hierarchy" in SYNTHESIZER_SYSTEM_PROMPT

    def test_contains_deterministic_authority_rules(self):
        assert "Deterministic grading" in SYNTHESIZER_SYSTEM_PROMPT
        assert "entry_authorized is always false" in SYNTHESIZER_SYSTEM_PROMPT

    def test_contains_supported_bias_and_current_price_requirements(self):
        assert "seven supported bias levels" in SYNTHESIZER_SYSTEM_PROMPT
        assert "current_price" in SYNTHESIZER_SYSTEM_PROMPT

    def test_no_file_path_references(self):
        assert not re.search(r"[A-Z]:\\", SYNTHESIZER_SYSTEM_PROMPT)
        assert not re.search(r"/home/", SYNTHESIZER_SYSTEM_PROMPT)
