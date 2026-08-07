# Superseded: simplify reviewer configuration names

> **Status: Superseded** by ADR 0003. The Reviewer LLM no longer exists in the
> canonical architecture.

The reviewer provider setting remains `TRADING_REVIEWER_LLM_PROVIDER`, while the other active reviewer environment variables drop the redundant `LLM` segment. Unused reviewer timeout and provider-retry settings are removed because neither was wired into the LLM client; old names are not retained as aliases to keep the configuration surface explicit.
