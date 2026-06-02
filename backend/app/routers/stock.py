from fastapi import APIRouter
from app.models.stock import StockOverview
from app.services.stock_service import fetch_overview

router = APIRouter(prefix="/api/stock", tags=["Stock"])


@router.get("/{ticker}", response_model=StockOverview)
def get_stock_overview(ticker: str):
    """Fetch overview data for a given stock ticker."""
    return fetch_overview(ticker)
