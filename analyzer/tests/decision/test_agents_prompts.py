from unittest.mock import MagicMock

from src.decision.agents import SynthesizerAgent
from src.decision.models import SynthesisResponse
from src.decision.usage import LLMUsage


def test_synthesizer_prompt_treats_deterministic_facts_as_authoritative():
    client = MagicMock()
    client.model_identity.raw_model_identifier = "gpt-4o"
    client.generate_structured_sync.return_value = (
        SynthesisResponse(explanation="deterministic context"),
        LLMUsage(),
    )

    SynthesizerAgent(client).synthesize(
        {}, [], "EURUSD", deterministic_setup="setup", risk_policy="risk", execution_policy="policy"
    )

    messages = client.generate_structured_sync.call_args.kwargs["messages"]
    assert "deterministic" in messages[0]["content"].lower()
    assert "authoritative" in messages[1]["content"].lower()
