# Deterministic decision, validation, and single Synthesizer

## Status

Accepted

## Context

The previous pipeline used separate synthesizer, decider, and reviewer LLM
roles. This allowed an LLM to participate in facts that are reproducibly
calculable from closed OHLC data and created a second LLM review/retry loop.

## Decision

The canonical pipeline is:

```text
closed OHLC
→ deterministic market analysis
→ deterministic grading, risk, and policy
→ deterministic validation
→ deterministic decision
→ one Synthesizer LLM call
→ final deterministic validation
→ final output
```

The deterministic domain owns structure, events, liquidity, levels, RR,
blockers, setup status, direction, and action. The only LLM role is
`Synthesizer`, which produces explanation and presentation text. Reviewer and
decider concepts are removed from the core domain. Validation failures produce
structured invalid results and never trigger another LLM call.

`DecisionAction` remains backward-compatible with the existing serialized
values `BUY_SETUP`, `SELL_SETUP`, and `no_trade`; `INVALID` is a validation
status, not an action.

## Consequences

- Results are reproducible and safe to backtest without an LLM.
- The maximum number of LLM calls per analysis is one.
- `validation_status` and `validation_errors` replace review status and review
  attempts in the canonical contract.
- Legacy review fields, if temporarily accepted at an API boundary, must not
  enter the core domain.
