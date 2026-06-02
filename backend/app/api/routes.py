from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    DividendSafetyRequest,
    DividendSafetyResponse,
    TickerSnapshotResponse,
    ValuationRequest,
    ValuationResponse,
)
from app.services.ai_dividend import DividendSafetyAIService
from app.services.market_data import MarketDataService
from app.services.valuation import ValuationService

router = APIRouter(tags=["Dividend Growth Evaluator"])

market_data_service = MarketDataService()
valuation_service = ValuationService()
ai_dividend_service = DividendSafetyAIService()


@router.get('/health')
def health() -> dict:
    return {"status": "ok"}


@router.get('/ticker/{ticker}', response_model=TickerSnapshotResponse)
def ticker_snapshot(ticker: str) -> TickerSnapshotResponse:
    try:
        snapshot = market_data_service.get_ticker_snapshot(ticker)
        return TickerSnapshotResponse(**snapshot)
    except Exception as exc:  # pragma: no cover - external data errors
        raise HTTPException(status_code=400, detail=f"Unable to load ticker {ticker}: {exc}") from exc


@router.post('/valuation', response_model=ValuationResponse)
def valuation(request: ValuationRequest) -> ValuationResponse:
    ticker = request.ticker.upper()

    try:
        dataset = market_data_service.get_financial_dataset(ticker)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=400, detail=f"Unable to load financial dataset for {ticker}: {exc}") from exc

    dcf = valuation_service.calculate_dcf(
        dataset=dataset,
        forecast_years=request.forecast_years,
        fcf_growth_rate=request.fcf_growth_rate,
        discount_rate=request.discount_rate,
        terminal_growth_rate=request.terminal_growth_rate,
    )

    ddm = valuation_service.calculate_ddm(
        dataset=dataset,
        required_return=request.required_return,
        dividend_growth_rate=request.dividend_growth_rate,
    )

    return ValuationResponse(ticker=ticker, dcf=dcf, ddm=ddm)


@router.post('/dividend-safety', response_model=DividendSafetyResponse)
def dividend_safety(request: DividendSafetyRequest) -> DividendSafetyResponse:
    ticker = request.ticker.upper()

    try:
        dataset = market_data_service.get_financial_dataset(ticker)
        result = ai_dividend_service.analyze(
            ticker=ticker,
            dataset=dataset,
            lookback_years=request.lookback_years,
        )
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=400, detail=f"Unable to evaluate dividend safety for {ticker}: {exc}") from exc

    return DividendSafetyResponse(**result)
