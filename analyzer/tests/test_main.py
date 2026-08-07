from unittest.mock import MagicMock, patch


def test_create_agents_creates_one_llm_client_and_one_synthesizer():
    import main
    from src.decision.cost_tracker import CostTracker

    settings = MagicMock(
        openai_api_key="key",
        openai_base_url="",
        openai_model="gpt-4o",
        openai_reasoning_effort="",
        openai_temperature=0.0,
        openai_instructor_mode="json_mode",
        openai_timeout=120.0,
        primary_llm_provider="openai",
    )
    with patch("main.create_llm_client") as create:
        agent = main._create_agents(settings, MagicMock(spec=CostTracker))

    assert agent.__class__.__name__ == "SynthesizerAgent"
    create.assert_called_once()
