from __future__ import annotations

from fastapi import APIRouter, Depends

from app.models import AnalysisAssumptions, StockAnalysis
from app.sample_data import available_sample_tickers
from app.services.dividend_safety import analyze_dividend_safety
from app.services.market_data import MarketDataService
from app.services.valuation import calculate_valuation
from app.settings import Settings, get_settings

router = APIRouter(prefix="/api")


def get_market_data_service(
    settings: Settings = Depends(get_settings),
) -> MarketDataService:
    return MarketDataService(settings)


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "dividend-growth-evaluator"}


@router.get("/sample-tickers")
async def sample_tickers() -> dict[str, list[str]]:
    return {"tickers": available_sample_tickers()}


@router.get("/stocks/{ticker}", response_model=StockAnalysis)
async def get_stock_analysis(
    ticker: str,
    market_data: MarketDataService = Depends(get_market_data_service),
) -> StockAnalysis:
    profile = await market_data.get_profile(ticker)
    return StockAnalysis(
        profile=profile,
        valuation=calculate_valuation(profile),
        dividend_safety=analyze_dividend_safety(profile),
    )


@router.post("/stocks/{ticker}/analyze", response_model=StockAnalysis)
async def analyze_stock_with_assumptions(
    ticker: str,
    assumptions: AnalysisAssumptions,
    market_data: MarketDataService = Depends(get_market_data_service),
) -> StockAnalysis:
    profile = await market_data.get_profile(ticker)
    return StockAnalysis(
        profile=profile,
        valuation=calculate_valuation(profile, assumptions),
        dividend_safety=analyze_dividend_safety(profile),
    )
