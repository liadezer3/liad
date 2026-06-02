from __future__ import annotations

from pydantic import BaseModel, Field


class TickerSnapshotResponse(BaseModel):
    ticker: str
    company_name: str | None = None
    sector: str | None = None
    industry: str | None = None
    currency: str | None = None
    current_price: float | None = None
    market_cap: float | None = None
    pe_ratio: float | None = None
    dividend_yield: float | None = None
    fifty_two_week_high: float | None = None
    fifty_two_week_low: float | None = None


class ValuationRequest(BaseModel):
    ticker: str = Field(min_length=1, max_length=10)
    forecast_years: int = Field(default=5, ge=3, le=10)
    fcf_growth_rate: float = Field(default=0.06, ge=-0.2, le=0.3)
    discount_rate: float = Field(default=0.10, gt=0.0, le=0.5)
    terminal_growth_rate: float = Field(default=0.03, ge=0.0, lt=0.1)
    required_return: float = Field(default=0.09, gt=0.0, le=0.5)
    dividend_growth_rate: float = Field(default=0.05, ge=-0.2, lt=0.25)


class ValuationMetric(BaseModel):
    method: str
    intrinsic_value_per_share: float | None = None
    current_price: float | None = None
    margin_of_safety: float | None = None
    assumptions: dict
    notes: list[str]


class ValuationResponse(BaseModel):
    ticker: str
    dcf: ValuationMetric
    ddm: ValuationMetric


class DividendSafetyRequest(BaseModel):
    ticker: str = Field(min_length=1, max_length=10)
    lookback_years: int = Field(default=5, ge=3, le=10)


class DividendSafetyResponse(BaseModel):
    ticker: str
    score: int
    rating: str
    reasoning: list[str]
    prompt: str
    source: str
