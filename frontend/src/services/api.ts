import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
});

// ── Types ───────────────────────────────────────────────────────────────────

export interface StockOverview {
  ticker: string;
  name: string;
  sector: string;
  industry: string;
  current_price: number;
  market_cap: number | null;
  pe_ratio: number | null;
  forward_pe: number | null;
  dividend_yield: number | null;
  annual_dividend: number | null;
  payout_ratio: number | null;
  five_year_avg_dividend_yield: number | null;
  dividend_growth_rate_5y: number | null;
  beta: number | null;
  fifty_two_week_high: number | null;
  fifty_two_week_low: number | null;
  description: string | null;
  website: string | null;
}

export interface DCFInput {
  ticker: string;
  discount_rate: number;
  terminal_growth_rate: number;
  projection_years: number;
}

export interface DCFResult {
  ticker: string;
  current_price: number;
  intrinsic_value: number;
  margin_of_safety: number;
  upside_downside_pct: number;
  free_cash_flows: number[];
  terminal_value: number;
  discount_rate: number;
  terminal_growth_rate: number;
  projection_years: number;
  revenue_growth_rate: number;
  fcf_margin: number;
}

export interface DDMInput {
  ticker: string;
  required_rate_of_return: number;
  dividend_growth_rate?: number | null;
  model_type: "gordon" | "multi_stage";
  high_growth_rate?: number | null;
  high_growth_years?: number | null;
}

export interface DDMResult {
  ticker: string;
  current_price: number;
  intrinsic_value: number;
  margin_of_safety: number;
  upside_downside_pct: number;
  last_dividend: number;
  dividend_growth_rate: number;
  required_rate_of_return: number;
  model_type: string;
}

export interface DividendSafetyResult {
  ticker: string;
  safety_score: number;
  safety_grade: string;
  summary: string;
  strengths: string[];
  risks: string[];
  payout_ratio: number | null;
  debt_to_equity: number | null;
  interest_coverage: number | null;
  free_cash_flow_payout: number | null;
  dividend_cagr_5y: number | null;
  years_of_dividend_growth: number | null;
  raw_metrics: Record<string, number | null>;
}

// ── API calls ────────────────────────────────────────────────────────────────

export const getStockOverview = (ticker: string) =>
  api.get<StockOverview>(`/api/stock/${ticker.toUpperCase()}`).then((r) => r.data);

export const runDCF = (body: DCFInput) =>
  api.post<DCFResult>("/api/valuation/dcf", body).then((r) => r.data);

export const runDDM = (body: DDMInput) =>
  api.post<DDMResult>("/api/valuation/ddm", body).then((r) => r.data);

export const getDividendSafety = (ticker: string) =>
  api
    .post<DividendSafetyResult>("/api/analysis/dividend-safety", { ticker: ticker.toUpperCase() })
    .then((r) => r.data);
