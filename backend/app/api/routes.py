from fastapi import APIRouter, HTTPException

from app.algorithms.dcf import calculate_dcf
from app.algorithms.ddm import calculate_ddm
from app.schemas import (
    DCFRequest,
    DCFResult,
    DDMRequest,
    DDMResult,
    DividendSafetyRequest,
    DividendSafetyResult,
    JobSearchRequest,
    JobSearchResult,
    StockQuote,
)
from app.services.dividend_safety import analyze_dividend_safety
from app.services.job_scanner import scan_jobs
from app.services.stock_data import fetch_financials_for_valuation, fetch_stock_details

router = APIRouter(tags=["evaluator"])


@router.get("/stocks/{ticker}", response_model=StockQuote)
def get_stock(ticker: str):
    try:
        return fetch_stock_details(ticker)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/valuation/dcf", response_model=DCFResult)
def run_dcf(body: DCFRequest):
    try:
        financials = fetch_financials_for_valuation(body.ticker)
        fcf_history = financials["fcf_history"]
        shares = financials["shares_outstanding"]
        quote = fetch_stock_details(body.ticker)

        intrinsic, projected = calculate_dcf(
            free_cash_flows=fcf_history,
            shares_outstanding=shares,
            discount_rate=body.discount_rate,
            terminal_growth_rate=body.terminal_growth_rate,
            projection_years=body.projection_years,
        )

        price = quote.current_price
        upside = None
        if price and price > 0:
            upside = round((intrinsic - price) / price * 100, 2)

        return DCFResult(
            ticker=body.ticker.upper(),
            intrinsic_value_per_share=intrinsic,
            current_price=price,
            upside_pct=upside,
            projected_fcf=projected,
            assumptions={
                "discount_rate": body.discount_rate,
                "terminal_growth_rate": body.terminal_growth_rate,
                "projection_years": body.projection_years,
                "fcf_history_used": fcf_history,
            },
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/valuation/ddm", response_model=DDMResult)
def run_ddm(body: DDMRequest):
    try:
        financials = fetch_financials_for_valuation(body.ticker)
        quote = fetch_stock_details(body.ticker)
        annual_div = financials["annual_dividend"]

        growth = body.dividend_growth_rate
        if growth is None:
            div_yield = quote.dividend_yield
            if div_yield and div_yield < 1:
                growth = min(max(div_yield * 0.5, 0.02), 0.08)
            else:
                growth = 0.04

        fair_value = calculate_ddm(
            annual_dividend=annual_div,
            required_return=body.required_return,
            dividend_growth_rate=growth,
        )

        price = quote.current_price
        upside = None
        if price and price > 0:
            upside = round((fair_value - price) / price * 100, 2)

        return DDMResult(
            ticker=body.ticker.upper(),
            fair_value_per_share=fair_value,
            current_price=price,
            upside_pct=upside,
            annual_dividend=annual_div,
            growth_rate_used=growth,
            required_return=body.required_return,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/analysis/dividend-safety", response_model=DividendSafetyResult)
def dividend_safety(body: DividendSafetyRequest):
    try:
        return analyze_dividend_safety(body.ticker)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/agents/job-scanner", response_model=JobSearchResult)
def job_scanner(body: JobSearchRequest):
    try:
        return scan_jobs(body)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
