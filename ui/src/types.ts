export interface RunSummary {
  symbol: string;
  date: string;        // YYYY-MM-DD
  time: string;        // HH-MM
  bias: string;
  confidence: number;
  action: string;
  review_approved: boolean;
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
  market_context: MarketContext;
  decision: Decision;
  review: Review;
  ohlc: OHLCData;
  sl_tp_overlay: SLTPOverlay;
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
  entry_price: number | null;
  stop_loss: number | null;
  take_profit: number | null;
  reasoning: string;
  risk_reward_ratio: number | null;
  entry_authorized: false;  // always false — advisory only
}

export interface Review {
  approved: boolean;
  reasoning: string;
  concerns: string[];
  suggested_improvements: string | null;
  risk_management_ok: boolean;
  htf_alignment_ok: boolean;
  calendar_clear: boolean;
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

export interface RunRequest {
  symbols: string[];
  model?: string;
  base_url?: string;
}
