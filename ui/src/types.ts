export interface RunSummary {
  symbol: string;
  date: string;        // YYYY-MM-DD
  time: string;        // HH-MM
  bias: string;
  confidence: number;
  action: string;
  validation_status: "VALID" | "INVALID";
  current_price: number | null;
  file_path: string;   // relative path from data/runs/
}

export interface FullResult {
  version: string;
  symbol: string;
  run_id: string;
  started_at: string;
  completed_at: string;
  status: "success" | "partial" | "error";
  errors: string[];
  fatal_error: string | null;
  market_context?: MarketContext | null;
  decision?: Decision | null;
  ohlc?: OHLCData;
  sl_tp_overlay?: SLTPOverlay | null;
  advisory_levels?: AdvisoryLevels | null;
  validation_status?: "VALID" | "INVALID";
  validation_errors?: string[];
  rr?: number | null;
  calculated_rr?: number | null;
  minimum_required_rr?: number;
  rr_pass?: boolean;
  deterministic_blockers?: Record<string, unknown>[];
  reason_codes?: string[];
  setup_status?: "READY" | "NO_SETUP" | "INVALID";
  direction?: "LONG" | "SHORT" | "NONE";
  entry_authorized?: false;
  estimated_reward_risk: number | null;
  order_type?: "MARKET" | "LIMIT" | "STOP" | null;
  deterministic_setup_complete?: boolean;
  rejection_codes: string[];
}

export interface MarketContext {
  symbol: string;
  bias: string;
  confidence: number;
  reasoning: string;
  key_levels: string[];
  structural_events: string[];
  calendar_context: string;
  current_price: number | null;
  current_price_time: string | null;
}

export interface Decision {
  symbol: string;
  action: string;
  reasoning: string;
}

export interface OHLCData {
  D1: OHLCBar[];
  H4: OHLCBar[];
  H1: OHLCBar[];
}

export interface OHLCBar {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
}

export interface SLTPOverlay {
  entry_price: number | null;
  stop_loss: number | null;
  take_profit: number | null;
}

export interface AdvisoryLevels {
  entry_price: number | null;
  stop_loss: number | null;
  take_profit: number | null;
}

export interface RunRequest {
  symbols: string[];
  model?: string;
  base_url?: string;
}
