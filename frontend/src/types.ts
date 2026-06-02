export type BalanceSheetSnapshot = {
  year: number;
  total_assets: number;
  total_liabilities: number;
  shareholders_equity: number;
  cash_and_equivalents: number;
  total_debt: number;
  current_assets: number;
  current_liabilities: number;
  debt_to_equity: number;
  current_ratio: number;
};

export type CashFlowSnapshot = {
  year: number;
  operating_cash_flow: number;
  capital_expenditures: number;
  dividends_paid: number;
  interest_expense: number;
  operating_income: number;
  net_income: number;
  free_cash_flow: number;
  dividend_coverage: number;
  payout_ratio: number;
  interest_coverage: number;
};

export type DividendHistoryPoint = {
  year: number;
  dividend_per_share: number;
};

export type StockProfile = {
  ticker: string;
  company_name: string;
  sector: string;
  industry: string;
  currency: string;
  price: number;
  shares_outstanding: number;
  annual_dividend: number;
  beta: number;
  description: string;
  dividend_yield: number;
  balance_sheets: BalanceSheetSnapshot[];
  cash_flows: CashFlowSnapshot[];
  dividend_history: DividendHistoryPoint[];
};

export type AnalysisAssumptions = {
  dcf_growth_rate: number;
  terminal_growth_rate: number;
  discount_rate: number;
  ddm_growth_rate: number;
  required_return: number;
  projection_years: number;
};

export type DcfValuation = {
  fair_value_per_share: number;
  enterprise_value: number;
  equity_value: number;
  margin_of_safety: number;
  projected_cash_flows: number[];
  terminal_value: number;
};

export type DdmValuation = {
  fair_value_per_share: number;
  next_year_dividend: number;
  implied_yield: number;
  margin_of_safety: number;
};

export type ValuationResult = {
  dcf: DcfValuation;
  ddm: DdmValuation;
  blended_fair_value: number;
  blended_margin_of_safety: number;
  assumptions: AnalysisAssumptions;
};

export type DividendSafetyResult = {
  score: number;
  rating: string;
  prompt: string;
  rationale: string[];
  strengths: string[];
  risks: string[];
  metrics: Record<string, number>;
};

export type StockAnalysis = {
  profile: StockProfile;
  valuation: ValuationResult;
  dividend_safety: DividendSafetyResult;
};
