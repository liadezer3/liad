from fastapi import APIRouter
from app.models.stock import DividendSafetyInput, DividendSafetyResult
from app.services.ai_service import analyze_dividend_safety

router = APIRouter(prefix="/api/analysis", tags=["AI Analysis"])


@router.post("/dividend-safety", response_model=DividendSafetyResult)
def dividend_safety_analysis(body: DividendSafetyInput):
    """Use AI to analyze dividend safety based on balance sheet and financial metrics."""
    return analyze_dividend_safety(body.ticker)
