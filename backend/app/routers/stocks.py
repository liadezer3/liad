"""Stock discovery + ticker detail endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..models.schemas import TickerDetail
from ..services import market_data

router = APIRouter(prefix="/api/stocks", tags=["stocks"])


@router.get("/directory")
def directory() -> list[dict]:
    """List bundled sample tickers for discovery / autocomplete."""
    return market_data.get_directory()


@router.get("/{ticker}", response_model=TickerDetail)
def ticker_detail(ticker: str) -> TickerDetail:
    """Fetch full ticker fundamentals + balance-sheet history."""
    try:
        return market_data.get_ticker_detail(ticker)
    except market_data.TickerNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
