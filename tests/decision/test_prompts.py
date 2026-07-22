import re

from src.decision.prompts import (
    DECIDER_SYSTEM_PROMPT,
    REVIEWER_SYSTEM_PROMPT,
    SYNTHESIZER_SYSTEM_PROMPT,
)


class TestSynthesizerPrompt:
    def test_contains_evidence_hierarchy(self):
        assert "Evidence Hierarchy" in SYNTHESIZER_SYSTEM_PROMPT

    def test_contains_primary_market_structure(self):
        assert "Primary market structure" in SYNTHESIZER_SYSTEM_PROMPT

    def test_contains_bias_levels(self):
        for level in ["strong_bullish", "bullish", "neutral", "bearish", "strong_bearish"]:
            assert level in SYNTHESIZER_SYSTEM_PROMPT

    def test_contains_non_negotiable_rules(self):
        assert "Non-negotiable Rules" in SYNTHESIZER_SYSTEM_PROMPT

    def test_no_file_path_references(self):
        assert not re.search(r"[A-Z]:\\", SYNTHESIZER_SYSTEM_PROMPT)
        assert not re.search(r"/home/", SYNTHESIZER_SYSTEM_PROMPT)


class TestDeciderPrompt:
    def test_contains_bias_rules(self):
        assert "strong_bullish" in DECIDER_SYSTEM_PROMPT
        assert "bearish" in DECIDER_SYSTEM_PROMPT

    def test_contains_advisory_only_warning(self):
        assert "advisory only" in DECIDER_SYSTEM_PROMPT.lower()
        assert "entry_authorized" in DECIDER_SYSTEM_PROMPT

    def test_contains_risk_reward_requirement(self):
        assert "2:1" in DECIDER_SYSTEM_PROMPT

    def test_no_file_path_references(self):
        assert not re.search(r"[A-Z]:\\", DECIDER_SYSTEM_PROMPT)
        assert not re.search(r"/home/", DECIDER_SYSTEM_PROMPT)


class TestReviewerPrompt:
    def test_contains_review_criteria(self):
        assert "Risk Management" in REVIEWER_SYSTEM_PROMPT
        assert "Higher-Timeframe" in REVIEWER_SYSTEM_PROMPT

    def test_contains_calendar_check(self):
        assert "Calendar" in REVIEWER_SYSTEM_PROMPT

    def test_contains_structural_validity(self):
        assert "Structural Validity" in REVIEWER_SYSTEM_PROMPT

    def test_no_file_path_references(self):
        assert not re.search(r"[A-Z]:\\", REVIEWER_SYSTEM_PROMPT)
        assert not re.search(r"/home/", REVIEWER_SYSTEM_PROMPT)
