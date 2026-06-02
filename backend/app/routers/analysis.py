"""AI dividend-safety analysis endpoint."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..models.schemas import AnalysisRequest, DividendSafetyResult
from ..services import ai_analysis, market_data

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.post("/dividend-safety", response_model=DividendSafetyResult)
def dividend_safety(req: AnalysisRequest) -> DividendSafetyResult:
    """Analyze historical balance sheets for a dividend-safety score."""
    try:
        detail = market_data.get_ticker_detail(req.ticker)
    except market_data.TickerNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ai_analysis.analyze_dividend_safety(detail)
