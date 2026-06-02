"""Valuation endpoints: Discounted Cash Flow and Dividend Discount Model."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..models.schemas import DCFRequest, DCFResult, DDMRequest, DDMResult
from ..services import market_data, valuation

router = APIRouter(prefix="/api/valuation", tags=["valuation"])


@router.post("/dcf", response_model=DCFResult)
def dcf(req: DCFRequest) -> DCFResult:
    try:
        detail = market_data.get_ticker_detail(req.ticker)
    except market_data.TickerNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    try:
        return valuation.run_dcf(detail, req)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/ddm", response_model=DDMResult)
def ddm(req: DDMRequest) -> DDMResult:
    try:
        detail = market_data.get_ticker_detail(req.ticker)
    except market_data.TickerNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    try:
        return valuation.run_ddm(detail, req)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
