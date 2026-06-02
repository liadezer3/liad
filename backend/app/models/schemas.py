"""Pydantic request / response models shared across the API."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Market data
# ---------------------------------------------------------------------------
class TickerProfile(BaseModel):
    """Snapshot of a stock ticker and its dividend profile."""

    ticker: str
    name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    currency: str = "USD"
    exchange: Optional[str] = None
    summary: Optional[str] = None

    price: float = Field(..., description="Latest market price per share")
    market_cap: Optional[float] = None
    shares_outstanding: Optional[float] = None
    beta: Optional[float] = None

    # Dividend metrics
    dividend_per_share: float = Field(0.0, description="Trailing annual dividend / share")
    dividend_yield: float = Field(0.0, description="Annual dividend yield as a fraction")
    payout_ratio: Optional[float] = Field(None, description="Dividends / earnings")
    five_year_dividend_growth: float = Field(
        0.0, description="Annualized 5y dividend growth rate (fraction)"
    )
    years_of_growth: Optional[int] = Field(
        None, description="Consecutive years of dividend increases"
    )

    # Fundamentals used by the valuation engine
    eps: Optional[float] = None
    free_cash_flow: Optional[float] = None
    free_cash_flow_per_share: Optional[float] = None
    total_debt: Optional[float] = None
    total_cash: Optional[float] = None

    is_sample: bool = Field(
        False, description="True when served from bundled fixtures (offline fallback)"
    )


class BalanceSheetYear(BaseModel):
    """One fiscal year of condensed balance-sheet / cash-flow figures."""

    year: int
    total_assets: float
    total_liabilities: float
    total_equity: float
    current_assets: float
    current_liabilities: float
    cash_and_equivalents: float
    total_debt: float
    net_income: float
    operating_cash_flow: float
    free_cash_flow: float
    dividends_paid: float


class TickerDetail(TickerProfile):
    """Full ticker payload including multi-year balance-sheet history."""

    balance_sheets: list[BalanceSheetYear] = []


# ---------------------------------------------------------------------------
# Valuation
# ---------------------------------------------------------------------------
class DCFRequest(BaseModel):
    ticker: str
    discount_rate: float = Field(0.09, ge=0.01, le=0.30, description="WACC / required return")
    growth_rate: float = Field(0.08, ge=-0.10, le=0.40, description="Stage-1 FCF growth")
    terminal_growth: float = Field(0.025, ge=0.0, le=0.06)
    projection_years: int = Field(10, ge=3, le=20)


class DCFYear(BaseModel):
    year: int
    projected_fcf: float
    discount_factor: float
    present_value: float


class DCFResult(BaseModel):
    ticker: str
    assumptions: DCFRequest
    projections: list[DCFYear]
    sum_pv_fcf: float
    terminal_value: float
    pv_terminal_value: float
    enterprise_value: float
    equity_value: float
    fair_value_per_share: float
    current_price: float
    upside_pct: float
    verdict: Literal["Undervalued", "Fairly Valued", "Overvalued"]


class DDMRequest(BaseModel):
    ticker: str
    discount_rate: float = Field(0.09, ge=0.01, le=0.30)
    # Two-stage Gordon Growth model
    high_growth_rate: float = Field(0.08, ge=-0.10, le=0.40)
    high_growth_years: int = Field(5, ge=1, le=15)
    terminal_growth: float = Field(0.03, ge=0.0, le=0.06)


class DDMYear(BaseModel):
    year: int
    projected_dividend: float
    present_value: float


class DDMResult(BaseModel):
    ticker: str
    assumptions: DDMRequest
    projections: list[DDMYear]
    pv_high_growth: float
    terminal_value: float
    pv_terminal_value: float
    fair_value_per_share: float
    current_price: float
    upside_pct: float
    verdict: Literal["Undervalued", "Fairly Valued", "Overvalued"]


# ---------------------------------------------------------------------------
# AI dividend-safety analysis
# ---------------------------------------------------------------------------
class AnalysisRequest(BaseModel):
    ticker: str


class SafetyFactor(BaseModel):
    name: str
    score: float = Field(..., ge=0, le=100)
    weight: float
    detail: str


class DividendSafetyResult(BaseModel):
    ticker: str
    safety_score: float = Field(..., ge=0, le=100)
    rating: Literal["Very Safe", "Safe", "Borderline", "At Risk", "Unsafe"]
    summary: str
    strengths: list[str]
    risks: list[str]
    factors: list[SafetyFactor]
    engine: Literal["llm", "heuristic"]
    model: Optional[str] = None
