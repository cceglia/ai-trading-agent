from unittest.mock import MagicMock

from src.decision.agents import SynthesizerAgent
from src.decision.models import SynthesisResponse
from src.decision.usage import LLMUsage


def test_only_synthesizer_agent_is_exposed():
    import src.decision.agents as agents

    assert {name for name in dir(agents) if name.endswith("Agent")} == {"SynthesizerAgent"}


def test_synthesizer_uses_injected_client_once():
    client = MagicMock()
    client.model_identity.raw_model_identifier = "gpt-4o"
    expected = SynthesisResponse(explanation="deterministic context")
    client.generate_structured_sync.return_value = (expected, LLMUsage())

    result = SynthesizerAgent(client).synthesize({}, [], "EURUSD")

    assert result is expected
    client.generate_structured_sync.assert_called_once()
