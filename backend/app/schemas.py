from pydantic import BaseModel, Field


class DCFRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)
    discount_rate: float = Field(0.10, ge=0.01, le=0.30)
    terminal_growth_rate: float = Field(0.025, ge=0.0, le=0.10)
    projection_years: int = Field(5, ge=3, le=10)


class DDMRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)
    required_return: float = Field(0.09, ge=0.01, le=0.30)
    dividend_growth_rate: float | None = Field(None, ge=0.0, le=0.20)


class DividendSafetyRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)


class StockQuote(BaseModel):
    ticker: str
    name: str
    sector: str | None
    industry: str | None
    current_price: float | None
    dividend_yield: float | None
    dividend_rate: float | None
    payout_ratio: float | None
    trailing_pe: float | None
    market_cap: float | None
    fifty_two_week_high: float | None
    fifty_two_week_low: float | None


class DCFResult(BaseModel):
    ticker: str
    intrinsic_value_per_share: float
    current_price: float | None
    upside_pct: float | None
    projected_fcf: list[float]
    assumptions: dict


class DDMResult(BaseModel):
    ticker: str
    fair_value_per_share: float
    current_price: float | None
    upside_pct: float | None
    annual_dividend: float
    growth_rate_used: float
    required_return: float


class DividendSafetyResult(BaseModel):
    ticker: str
    safety_score: int = Field(..., ge=0, le=100)
    rating: str
    summary: str
    factors: list[dict]
    ai_powered: bool
    balance_sheet_highlights: dict
