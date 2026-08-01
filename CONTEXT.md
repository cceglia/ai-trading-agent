# Domain Glossary

## LLM Agents

| Term | Definition |
|---|---|
| **Primary LLM** | The LLM client used by the Synthesizer and Decider agents. Configured via `TRADING_OPENAI_*` environment variables. |
| **Reviewer LLM** | The LLM client used by the Reviewer agent. Configured via reviewer-specific environment variables. Can override most primary LLM settings independently. |

## LLM Temperature

| Term | Definition |
|---|---|
| **LLM Temperature** | Float (0.0–2.0) controlling randomness in LLM output. 0.0 = fully deterministic; higher values = more creative/random output. Set independently for the Primary LLM and the Reviewer LLM. |
| **`TRADING_OPENAI_TEMPERATURE`** | Environment variable for the Primary LLM temperature. Default: `0.0`. Maps to `Settings.openai_temperature`. |
| **`TRADING_REVIEWER_TEMPERATURE`** | Environment variable for the Reviewer LLM temperature. Default: `0.0`. Maps to `Settings.reviewer_temperature`. |

## Design Decisions

- **Same temperature for Synthesizer and Decider**: Intentional choice. Both share the Primary LLM client and its temperature. No future split is planned.
- **Reviewer temperature is independent**, not an override of the primary temperature. Both default to `0.0` but are configured via separate env vars.
- **Temperatures are always explicit floats**, never `None`. When not set, `0.0` is used (not the provider default). This ensures reproducibility across different providers.
