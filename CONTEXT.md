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

## Analysis Runs

| Term | Definition |
|---|---|
| **Fatal analysis failure** | An analysis attempt that cannot produce usable market context and a decision. It is diagnostic information, not a reportable analysis run. |

## Trade Levels

| Term | Definition |
|---|---|
| **Planned entry / open** | The deterministic setup's `entry_price`. It is distinct from the latest market price and from an OHLC candle's `open` value. |
| **Deterministic stop loss** | The setup's `invalidation_price`, authoritative for risk and execution geometry. |
| **Deterministic take profit** | The setup's `target_price`, authoritative for risk and execution geometry. |
| **Advisory level** | An entry, stop-loss, or take-profit level proposed or discussed by an LLM. It must remain visibly separate from deterministic levels and cannot authorize execution. |
| **Incomplete setup** | A setup whose deterministic entry, stop-loss, or take-profit values are missing. It is non-actionable; advisory suggestions may be shown only as advisory text or levels. |
| **Structured advisory level** | An advisory price carried in an explicit LLM output field. Numeric advisory levels are never extracted from free-form reasoning or review prose. |
| **Authoritative chart overlay** | A deterministic entry, stop-loss, or take-profit level shown on the price chart. Advisory levels are displayed separately and are not chart overlays by default. |
| **Order type** | The deterministic, direction-aware execution classification for a planned entry: `MARKET`, `LIMIT`, or `STOP`. It uses trade direction plus planned entry versus canonical current price. The LLM may explain it but cannot override it. |
| **Market order** | An entry intended at the current market price; represented when planned entry equals the canonical current price. |
| **Limit order** | An entry intended at a more favorable price than the canonical current price: below current price for a buy or above current price for a sell. |
| **Stop order** | An entry intended after price moves through a confirmation level: above current price for a buy or below current price for a sell. |
| **Unavailable order type** | The order type when planned entry or canonical current price is missing. It is not a `MARKET` fallback and makes the setup non-actionable. |
| **Generic order type** | The result-level `MARKET`, `LIMIT`, or `STOP` value stored alongside `trade_direction`; side-specific broker order names are derived only at an execution boundary. |
| **Immutable order-type context** | The deterministic order type supplied to the LLM for explanation and consistency checks. The LLM cannot alter the canonical value. |
