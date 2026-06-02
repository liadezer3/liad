from __future__ import annotations

from pydantic import BaseModel, Field, computed_field


class BalanceSheetSnapshot(BaseModel):
    year: int
    total_assets: float = Field(gt=0)
    total_liabilities: float = Field(ge=0)
    shareholders_equity: float = Field(gt=0)
    cash_and_equivalents: float = Field(ge=0)
    total_debt: float = Field(ge=0)
    current_assets: float = Field(gt=0)
    current_liabilities: float = Field(gt=0)

    @computed_field
    @property
    def debt_to_equity(self) -> float:
        return self.total_debt / self.shareholders_equity

    @computed_field
    @property
    def current_ratio(self) -> float:
        return self.current_assets / self.current_liabilities


class CashFlowSnapshot(BaseModel):
    year: int
    operating_cash_flow: float
    capital_expenditures: float
    dividends_paid: float = Field(ge=0)
    interest_expense: float = Field(ge=0)
    operating_income: float
    net_income: float

    @computed_field
    @property
    def free_cash_flow(self) -> float:
        return self.operating_cash_flow - self.capital_expenditures

    @computed_field
    @property
    def dividend_coverage(self) -> float:
        if self.dividends_paid == 0:
            return 99.0
        return self.free_cash_flow / self.dividends_paid

    @computed_field
    @property
    def payout_ratio(self) -> float:
        if self.net_income <= 0:
            return 1.0
        return self.dividends_paid / self.net_income

    @computed_field
    @property
    def interest_coverage(self) -> float:
        if self.interest_expense == 0:
            return 99.0
        return self.operating_income / self.interest_expense


class DividendHistoryPoint(BaseModel):
    year: int
    dividend_per_share: float = Field(ge=0)


class StockProfile(BaseModel):
    ticker: str
    company_name: str
    sector: str
    industry: str
    currency: str = "USD"
    price: float = Field(gt=0)
    shares_outstanding: float = Field(gt=0)
    annual_dividend: float = Field(ge=0)
    beta: float = Field(gt=0)
    description: str
    balance_sheets: list[BalanceSheetSnapshot]
    cash_flows: list[CashFlowSnapshot]
    dividend_history: list[DividendHistoryPoint]

    @computed_field
    @property
    def dividend_yield(self) -> float:
        return self.annual_dividend / self.price


class AnalysisAssumptions(BaseModel):
    dcf_growth_rate: float = Field(default=0.06, ge=-0.25, le=0.30)
    terminal_growth_rate: float = Field(default=0.025, ge=-0.05, le=0.06)
    discount_rate: float = Field(default=0.09, ge=0.04, le=0.20)
    ddm_growth_rate: float = Field(default=0.045, ge=-0.05, le=0.12)
    required_return: float = Field(default=0.085, ge=0.04, le=0.20)
    projection_years: int = Field(default=5, ge=3, le=10)


class DcfValuation(BaseModel):
    fair_value_per_share: float
    enterprise_value: float
    equity_value: float
    margin_of_safety: float
    projected_cash_flows: list[float]
    terminal_value: float


class DdmValuation(BaseModel):
    fair_value_per_share: float
    next_year_dividend: float
    implied_yield: float
    margin_of_safety: float


class ValuationResult(BaseModel):
    dcf: DcfValuation
    ddm: DdmValuation
    blended_fair_value: float
    blended_margin_of_safety: float
    assumptions: AnalysisAssumptions


class DividendSafetyResult(BaseModel):
    score: int = Field(ge=0, le=100)
    rating: str
    prompt: str
    rationale: list[str]
    strengths: list[str]
    risks: list[str]
    metrics: dict[str, float]


class StockAnalysis(BaseModel):
    profile: StockProfile
    valuation: ValuationResult
    dividend_safety: DividendSafetyResult
