export interface StockQuote {
  ticker: string
  name: string
  sector: string | null
  industry: string | null
  current_price: number | null
  dividend_yield: number | null
  dividend_rate: number | null
  payout_ratio: number | null
  trailing_pe: number | null
  market_cap: number | null
  fifty_two_week_high: number | null
  fifty_two_week_low: number | null
}

export interface DCFResult {
  ticker: string
  intrinsic_value_per_share: number
  current_price: number | null
  upside_pct: number | null
  projected_fcf: number[]
  assumptions: Record<string, unknown>
}

export interface DDMResult {
  ticker: string
  fair_value_per_share: number
  current_price: number | null
  upside_pct: number | null
  annual_dividend: number
  growth_rate_used: number
  required_return: number
}

export interface SafetyFactor {
  name: string
  impact: string
  detail: string
}

export interface DividendSafetyResult {
  ticker: string
  safety_score: number
  rating: string
  summary: string
  factors: SafetyFactor[]
  ai_powered: boolean
  balance_sheet_highlights: Record<string, number[]>
}
