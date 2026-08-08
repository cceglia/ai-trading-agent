/**
 * Schema-v2 UI contracts matching the typed v2 server API (ticket 05 / #19).
 *
 * These types mirror the server's `RunSummary` and the analyzer's
 * `AnalysisEnvelope` exactly. No legacy flat fields (`version`, `review`,
 * `review_approved`, …) are part of the public contract: legacy runs are
 * normalised server-side to `schema_version="legacy"` with UNKNOWN and
 * non-operational state (INV-013 / INV-015).
 */

// ── List summary ─────────────────────────────────────────────────────
export interface RunSummary {
  symbol: string;
  date: string; // YYYY-MM-DD
  time: string; // HH — derived from result-HH.json naming
  bias: string;
  confidence: number;
  action: string;
  validation_status: string;
  setup_status: string;
  direction: string;
  operational: boolean;
  file_path: string; // relative path from the data directory
}

// ── Detail envelope ──────────────────────────────────────────────────
export type SchemaVersion = "2" | "legacy";
export type EnvelopeStatus = "success" | "degraded" | "partial" | "error";

export type V2Action = "buy_setup" | "sell_setup" | "no_trade";
export type SynthesisStatus = "SUCCESS" | "FAILED" | "SKIPPED";
export type ValidationStatus = "VALID" | "INVALID" | "UNKNOWN";
export type SetupStatus = "READY" | "NO_SETUP" | "INVALID" | "UNKNOWN";
export type Direction = "LONG" | "SHORT" | "NONE" | "UNKNOWN";

/**
 * Deterministic entry plan. Every field is optional: the server legacy
 * adapter emits `entry_plan: {}` (fields absent), while the v2 writer emits
 * the full shape. Missing fields render as N/A, never as guessed values.
 */
export interface EntryPlan {
  current_price?: number | null;
  entry_type?: string | null;
  entry_price?: number | null;
  entry_zone_low?: number | null;
  entry_zone_high?: number | null;
  trigger_level?: number | null;
  invalidation_level_id?: string | null;
  invalidation_timeframe?: string | null;
  invalidation_price?: number | null;
  target_price?: number | null;
  estimated_reward_risk?: number | null;
}

export interface RRInfo {
  calculated_rr: number | null;
  minimum_required_rr: number;
  rr_pass: boolean;
}

export interface PolicyFacts {
  execution_status: string | null;
  actionable: boolean;
  blockers: Record<string, unknown>[];
  reason_codes: string[];
}

export interface DeterministicFacts {
  symbol: string;
  timeframes: Record<string, unknown>;
  setup_status: SetupStatus;
  direction: Direction;
  trade_direction: string;
  setup_grade: string | null;
  setup_classification_status: string;
  setup_lifecycle_status: string;
  entry_plan: EntryPlan;
  rr: RRInfo;
  confidence_components: Record<string, unknown>;
  policy: PolicyFacts;
  selected_levels: Record<string, unknown>;
  latest_structural_events: Record<string, unknown>;
  latest_liquidity_states: Record<string, unknown>;
  event_history: Record<string, unknown>;
  liquidity_history: Record<string, unknown>;
  validation_status: ValidationStatus;
  validation_errors: string[];
  operational: boolean;
  entry_authorized: false;
  bias: string | null;
  confidence: number | null;
}

export interface DecisionBlock {
  action: V2Action;
}

export interface SynthesisBlock {
  status: SynthesisStatus;
  explanation: string | null;
  risks: string[];
  confluences: string[];
  error: string | null;
}

export interface OHLCBar {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
}

export interface OHLCData {
  D1: OHLCBar[];
  H4: OHLCBar[];
  H1: OHLCBar[];
}

/** Chart overlay projection derived from the deterministic entry plan. */
export interface SLTPOverlay {
  entry_price: number | null;
  stop_loss: number | null;
  take_profit: number | null;
}

export interface AnalysisEnvelope {
  schema_version: SchemaVersion;
  symbol: string;
  run_id: string;
  started_at: string;
  completed_at: string;
  status: EnvelopeStatus;
  errors: string[];
  fatal_error: string | null;
  deterministic_facts: DeterministicFacts;
  decision: DecisionBlock;
  synthesis: SynthesisBlock;
  ohlc: OHLCData;
}

// ── Batch run request/response (POST /api/run) ───────────────────────
export interface RunRequest {
  symbols: string[];
  model?: string;
  provider_id?: string;
}

export interface SymbolError {
  code: string;
  message: string;
}

export type BatchStatus = "success" | "partial" | "error";

export interface BatchResponse {
  status: BatchStatus;
  results: Record<string, AnalysisEnvelope>;
  errors: Record<string, SymbolError>;
}
