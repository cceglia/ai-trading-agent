# Domain Glossary

## Analysis Pipeline

| Term | Definition |
|---|---|
| **Closed candle** | An OHLC candle whose closure has been verified and which is the only candle eligible for deterministic analysis. |
| **Deterministic facts** | Values calculated exclusively from closed OHLC data, configured formulas, and deterministic policy: structure, events, liquidity, levels, RR, grading, blockers, and geometry. |
| **Deterministic decision** | The machine-readable setup outcome derived from deterministic facts and policy. It selects `BUY_SETUP`, `SELL_SETUP`, or `no_trade`; it is not produced by an LLM. |
| **Invalid analysis** | A deterministic result that violates an invariant or cannot be trusted. It is distinct from `NO_SETUP`, which is a valid analysis with no opportunity. |
| **Deterministic validation** | The invariant-checking stage that produces `validation_status` and `validation_errors` before and after the Synthesizer boundary. It never retries through an LLM. |
| **Synthesizer** | The single LLM agent. It explains deterministic facts and risks in readable prose; it cannot change facts, decisions, blockers, or validation outcomes. |

## Setup and Decision

| Term | Definition |
|---|---|
| **Setup status** | Deterministic classification: `READY`, `NO_SETUP`, or `INVALID`. `NO_SETUP` means valid analysis without an opportunity; `INVALID` means the analysis is untrusted. |
| **Direction** | Canonical human-facing direction: `LONG`, `SHORT`, or `NONE`. It is derived from deterministic trade direction. |
| **Decision action** | Existing serialized enum values `BUY_SETUP`, `SELL_SETUP`, and `no_trade`. `INVALID` is never an action value. |
| **Blocker** | A deterministic machine-readable reason that prevents or limits a setup. A `READY` setup cannot contain blockers. |
| **Validation status** | `VALID` or `INVALID`, representing invariant validity rather than trade availability. |
| **Validation errors** | Machine-readable or stable error descriptions explaining why deterministic facts are invalid. |

## Structural Events

| Term | Definition |
|---|---|
| **Event history** | Chronologically ordered structural or liquidity interactions, including failed and later confirmed events. History is never replaced by the latest state. |
| **Latest event** | The most recent relevant event in chronological history for the requested scope. |
| **Current state** | The state obtained by replaying valid chronological transitions over an event history. |
| **BOS** | A confirmed structural break in the same directional regime that existed immediately before the event. |
| **CHoCH** | A confirmed structural break opposite to the immediately preceding directional regime. |
| **Structural break / unclassified break** | A confirmed directional break observed while the prior regime is `RANGE`, `TRANSITION`, or `UNKNOWN`; it updates the regime without inventing BOS or CHoCH. |
| **Structural scope** | The immutable provenance of an event: `PRIMARY` or `INTERNAL`. It cannot be reinterpreted downstream. |

## Liquidity and Levels

| Term | Definition |
|---|---|
| **Liquidity event history** | All valid pool transitions, such as sweep, reclaim, acceptance beyond, and later reclaim. |
| **Liquidity current state** | The state after the last valid transition for a pool. |
| **Freshness** | Deterministic level validity based on age and interaction history. Only `FRESH` and `TESTED` levels within the timeframe age limit can be automatic invalidation candidates. |
| **Historical level** | A retained level that may explain context but is not automatically eligible for stop/invalidation selection. |
| **Eligible invalidation** | A level satisfying freshness, age, break, reclaim, and acceptance constraints for deterministic stop selection. |

## Risk and LLM Boundary

| Term | Definition |
|---|---|
| **Minimum RR** | The single deterministic threshold `2.0`, shared by context, risk policy, execution policy, validator, and Synthesizer input. |
| **RR pass** | Deterministic boolean indicating calculated RR is mathematically valid and at least the minimum RR. |
| **LLM boundary** | The point after deterministic validation where only already-calculated facts are supplied to the Synthesizer. |
| **Advisory explanation** | Synthesizer prose that describes facts and risks without authority to modify them. |

## Analysis Runs

| Term | Definition |
|---|---|
| **Fatal analysis failure** | An infrastructure or processing failure that cannot produce a usable analysis result. It is distinct from deterministic `INVALID` analysis. |
