# Default the structured output mode to `json_mode`

The analyzer's structured output transport defaults to instructor's `json_mode`
(`response_format={"type": "json_object"}`) instead of `Mode.TOOLS`.

## Context

The structured output transport was hardcoded to `Mode.TOOLS`, which forces a
`tool_choice` on every chat-completions request. The intended replacement
provider rejects forced `tool_choice` under thinking mode (400 "Thinking mode
does not support this tool_choice") and also rejects `response_format:
json_schema` (400 "This response_format type is unavailable now"). Only
`json_mode` is accepted, so the app could not use the replacement provider at
all. A related defect: the OpenAI client was constructed without a timeout, so
a provider that accepted the connection and returned 0 bytes blocked the
pipeline for up to ~40 minutes (600s SDK default × 3 retries) with no log line.

## Decision

- Default `openai_instructor_mode` to `json_mode`, and default the reviewer to
  inherit it (`reviewer_instructor_mode=""`).
- Allow exactly two values: `json_mode` and `tool_call` (the pragmatic set with
  real support among OpenAI-compatible providers). Other values are rejected at
  Settings-parse time to avoid deterministic provider errors on the first LLM
  call.
- Add a per-attempt request timeout (`openai_timeout`, default 120s) applied to
  both the sync and async OpenAI clients. A hung upstream now fails fast with an
  explicit `status=error` analysis result instead of blocking silently.
- A timeout or mode-incompatibility failure does NOT degrade to a deterministic
  NO_TRADE: a NO_TRADE must remain reserved for valid market-condition
  decisions, never for infrastructure failures.

## Consequences

- `json_mode` injects the JSON schema into the prompt and requests
  `response_format={"type": "json_object"}`; the model must return a valid JSON
  object matching the schema.
- Operators can switch transports via `TRADING_OPENAI_INSTRUCTOR_MODE` /
  `TRADING_REVIEWER_INSTRUCTOR_MODE` and tune timeouts via
  `TRADING_OPENAI_TIMEOUT` / `TRADING_REVIEWER_TIMEOUT` without code changes.
- A dead provider surfaces within `timeout × (retries + 1)` seconds at most.
