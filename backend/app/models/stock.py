from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class StockOverview(BaseModel):
    ticker: str
    name: str
    sector: str
    industry: str
    current_price: float
    market_cap: Optional[float]
    pe_ratio: Optional[float]
    forward_pe: Optional[float]
    dividend_yield: Optional[float]
    annual_dividend: Optional[float]
    payout_ratio: Optional[float]
    five_year_avg_dividend_yield: Optional[float]
    dividend_growth_rate_5y: Optional[float]
    beta: Optional[float]
    fifty_two_week_high: Optional[float]
    fifty_two_week_low: Optional[float]
    description: Optional[str]
    website: Optional[str]


class DCFInput(BaseModel):
    ticker: str
    discount_rate: float = Field(default=0.10, ge=0.01, le=0.5, description="WACC / required rate of return")
    terminal_growth_rate: float = Field(default=0.03, ge=0.0, le=0.1, description="Long-term growth rate")
    projection_years: int = Field(default=10, ge=3, le=20)


class DCFResult(BaseModel):
    ticker: str
    current_price: float
    intrinsic_value: float
    margin_of_safety: float
    upside_downside_pct: float
    free_cash_flows: list[float]
    terminal_value: float
    discount_rate: float
    terminal_growth_rate: float
    projection_years: int
    revenue_growth_rate: float
    fcf_margin: float


class DDMInput(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    ticker: str
    required_rate_of_return: float = Field(default=0.10, ge=0.01, le=0.5)
    dividend_growth_rate: Optional[float] = Field(default=None, description="Override auto-calculated growth rate")
    model_type: str = Field(default="gordon", pattern="^(gordon|multi_stage)$")
    high_growth_rate: Optional[float] = Field(default=None)
    high_growth_years: Optional[int] = Field(default=5)


class DDMResult(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    ticker: str
    current_price: float
    intrinsic_value: float
    margin_of_safety: float
    upside_downside_pct: float
    last_dividend: float
    dividend_growth_rate: float
    required_rate_of_return: float
    model_type: str


class DividendSafetyInput(BaseModel):
    ticker: str


class DividendSafetyResult(BaseModel):
    ticker: str
    safety_score: int = Field(ge=0, le=100, description="0-100 score, higher is safer")
    safety_grade: str
    summary: str
    strengths: list[str]
    risks: list[str]
    payout_ratio: Optional[float]
    debt_to_equity: Optional[float]
    interest_coverage: Optional[float]
    free_cash_flow_payout: Optional[float]
    dividend_cagr_5y: Optional[float]
    years_of_dividend_growth: Optional[int]
    raw_metrics: dict
