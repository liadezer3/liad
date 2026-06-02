import yfinance as yf
import numpy as np
import pandas as pd
from typing import Optional
from fastapi import HTTPException


def _safe_float(value) -> Optional[float]:
    """Safely convert a value to float, returning None on failure."""
    try:
        if value is None or (isinstance(value, float) and np.isnan(value)):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def get_ticker(symbol: str) -> yf.Ticker:
    ticker = yf.Ticker(symbol.upper())
    info = ticker.info
    if not info or info.get("regularMarketPrice") is None and info.get("currentPrice") is None:
        raise HTTPException(status_code=404, detail=f"Ticker '{symbol}' not found or has no price data.")
    return ticker


def fetch_overview(symbol: str) -> dict:
    ticker = get_ticker(symbol)
    info = ticker.info

    current_price = _safe_float(info.get("currentPrice") or info.get("regularMarketPrice"))

    # Compute 5-year dividend CAGR
    dividend_growth_5y = _compute_dividend_cagr(ticker, years=5)

    return {
        "ticker": symbol.upper(),
        "name": info.get("longName") or info.get("shortName") or symbol.upper(),
        "sector": info.get("sector") or "N/A",
        "industry": info.get("industry") or "N/A",
        "current_price": current_price or 0.0,
        "market_cap": _safe_float(info.get("marketCap")),
        "pe_ratio": _safe_float(info.get("trailingPE")),
        "forward_pe": _safe_float(info.get("forwardPE")),
        "dividend_yield": _safe_float(info.get("dividendYield")),
        "annual_dividend": _safe_float(info.get("dividendRate")),
        "payout_ratio": _safe_float(info.get("payoutRatio")),
        "five_year_avg_dividend_yield": _safe_float(info.get("fiveYearAvgDividendYield")),
        "dividend_growth_rate_5y": dividend_growth_5y,
        "beta": _safe_float(info.get("beta")),
        "fifty_two_week_high": _safe_float(info.get("fiftyTwoWeekHigh")),
        "fifty_two_week_low": _safe_float(info.get("fiftyTwoWeekLow")),
        "description": info.get("longBusinessSummary"),
        "website": info.get("website"),
    }


def _compute_dividend_cagr(ticker: yf.Ticker, years: int = 5) -> Optional[float]:
    """Compute the dividend CAGR over the given number of years using historical dividends."""
    try:
        divs = ticker.dividends
        if divs is None or len(divs) == 0:
            return None

        divs.index = divs.index.tz_localize(None)
        cutoff = pd.Timestamp.now() - pd.DateOffset(years=years)
        recent = divs[divs.index >= cutoff]
        old = divs[divs.index < cutoff]

        if len(recent) == 0:
            return None

        annual_recent = recent.resample("YE").sum().iloc[-1] if len(recent) >= 4 else recent.sum()
        if len(old) == 0:
            return None
        annual_old = old.resample("YE").sum().iloc[-1] if len(old) >= 4 else old.sum()

        if annual_old <= 0:
            return None

        cagr = (annual_recent / annual_old) ** (1 / years) - 1
        return round(float(cagr), 4)
    except Exception:
        return None


def compute_dcf(
    symbol: str,
    discount_rate: float = 0.10,
    terminal_growth_rate: float = 0.03,
    projection_years: int = 10,
) -> dict:
    ticker = get_ticker(symbol)
    info = ticker.info

    current_price = _safe_float(info.get("currentPrice") or info.get("regularMarketPrice"))
    if current_price is None:
        raise HTTPException(status_code=422, detail="Cannot retrieve current price.")

    shares = _safe_float(info.get("sharesOutstanding"))
    if not shares:
        raise HTTPException(status_code=422, detail="Cannot retrieve shares outstanding.")

    # Get Free Cash Flow from cash flow statement
    cashflow = ticker.cashflow
    if cashflow is None or cashflow.empty:
        raise HTTPException(status_code=422, detail="No cash flow data available for DCF analysis.")

    # Rows may vary by ticker; try common labels
    def _get_row(df: pd.DataFrame, *labels: str) -> Optional[pd.Series]:
        for label in labels:
            matches = [col for col in df.index if label.lower() in col.lower()]
            if matches:
                return df.loc[matches[0]]
        return None

    operating_cf_row = _get_row(cashflow, "Operating Cash Flow", "Total Cash From Operating Activities")
    capex_row = _get_row(cashflow, "Capital Expenditure", "Capital Expenditures")

    if operating_cf_row is None:
        raise HTTPException(status_code=422, detail="Cannot extract operating cash flow for DCF.")

    operating_cfs = operating_cf_row.dropna().values.astype(float)
    capex_vals = capex_row.dropna().values.astype(float) if capex_row is not None else np.zeros(len(operating_cfs))

    min_len = min(len(operating_cfs), len(capex_vals))
    if min_len == 0:
        raise HTTPException(status_code=422, detail="Insufficient cash flow history for DCF.")

    historical_fcfs = operating_cfs[:min_len] + np.abs(capex_vals[:min_len])  # capex is negative

    if len(historical_fcfs) == 0 or historical_fcfs[0] <= 0:
        raise HTTPException(status_code=422, detail="Latest Free Cash Flow is zero or negative; DCF not meaningful.")

    # Revenue growth rate estimation
    income = ticker.income_stmt
    revenue_growth = 0.05  # default fallback
    if income is not None and not income.empty:
        rev_row = _get_row(income, "Total Revenue")
        if rev_row is not None:
            revs = rev_row.dropna().values.astype(float)
            if len(revs) >= 2 and revs[-1] > 0:
                revenue_growth = float((revs[0] / revs[-1]) ** (1 / (len(revs) - 1)) - 1)
                revenue_growth = max(min(revenue_growth, 0.30), -0.10)

    # FCF margin
    base_fcf = historical_fcfs[0]
    fcf_margin = float(base_fcf / shares)  # FCF per share

    # Project FCF for N years
    growth_rate = min(revenue_growth, 0.20)  # cap aggressive growth
    projected_fcfs = []
    for year in range(1, projection_years + 1):
        # Gradual decay toward terminal growth
        y_growth = growth_rate + (terminal_growth_rate - growth_rate) * (year / projection_years)
        projected_fcfs.append(base_fcf * ((1 + y_growth) ** year))

    # Terminal value
    terminal_fcf = projected_fcfs[-1] * (1 + terminal_growth_rate)
    terminal_value = terminal_fcf / (discount_rate - terminal_growth_rate)

    # Discount all cash flows
    pv_fcfs = [cf / ((1 + discount_rate) ** (i + 1)) for i, cf in enumerate(projected_fcfs)]
    pv_terminal = terminal_value / ((1 + discount_rate) ** projection_years)

    total_pv = sum(pv_fcfs) + pv_terminal
    intrinsic_value = total_pv / shares

    margin_of_safety = (intrinsic_value - current_price) / intrinsic_value if intrinsic_value > 0 else 0
    upside_pct = (intrinsic_value - current_price) / current_price * 100 if current_price > 0 else 0

    return {
        "ticker": symbol.upper(),
        "current_price": current_price,
        "intrinsic_value": round(intrinsic_value, 2),
        "margin_of_safety": round(margin_of_safety, 4),
        "upside_downside_pct": round(upside_pct, 2),
        "free_cash_flows": [round(float(v) / shares, 2) for v in projected_fcfs],
        "terminal_value": round(float(pv_terminal), 2),
        "discount_rate": discount_rate,
        "terminal_growth_rate": terminal_growth_rate,
        "projection_years": projection_years,
        "revenue_growth_rate": round(revenue_growth, 4),
        "fcf_margin": round(fcf_margin, 4),
    }


def compute_ddm(
    symbol: str,
    required_rate: float = 0.10,
    dividend_growth_override: Optional[float] = None,
    model_type: str = "gordon",
    high_growth_rate: Optional[float] = None,
    high_growth_years: int = 5,
) -> dict:
    ticker = get_ticker(symbol)
    info = ticker.info

    current_price = _safe_float(info.get("currentPrice") or info.get("regularMarketPrice"))
    if current_price is None:
        raise HTTPException(status_code=422, detail="Cannot retrieve current price.")

    last_dividend = _safe_float(info.get("dividendRate"))
    if not last_dividend or last_dividend <= 0:
        raise HTTPException(status_code=422, detail="This stock does not pay dividends; DDM is not applicable.")

    # Determine growth rate
    if dividend_growth_override is not None:
        g = dividend_growth_override
    else:
        g = _compute_dividend_cagr(ticker, years=5) or 0.05

    # Clamp growth below discount rate
    if g >= required_rate:
        g = required_rate - 0.01

    if model_type == "gordon":
        # Gordon Growth Model: P = D1 / (r - g)
        d1 = last_dividend * (1 + g)
        intrinsic_value = d1 / (required_rate - g)
    else:
        # Multi-stage DDM
        hg = high_growth_rate if high_growth_rate is not None else min(g * 2, 0.20)
        if hg >= required_rate:
            hg = required_rate - 0.01
        terminal_g = g

        pv_dividends = 0.0
        dividend = last_dividend
        for year in range(1, high_growth_years + 1):
            dividend = dividend * (1 + hg)
            pv_dividends += dividend / ((1 + required_rate) ** year)

        # Terminal value at end of high-growth phase
        d_terminal = dividend * (1 + terminal_g)
        tv = d_terminal / (required_rate - terminal_g)
        pv_terminal = tv / ((1 + required_rate) ** high_growth_years)
        intrinsic_value = pv_dividends + pv_terminal

    margin_of_safety = (intrinsic_value - current_price) / intrinsic_value if intrinsic_value > 0 else 0
    upside_pct = (intrinsic_value - current_price) / current_price * 100 if current_price > 0 else 0

    return {
        "ticker": symbol.upper(),
        "current_price": current_price,
        "intrinsic_value": round(intrinsic_value, 2),
        "margin_of_safety": round(margin_of_safety, 4),
        "upside_downside_pct": round(upside_pct, 2),
        "last_dividend": last_dividend,
        "dividend_growth_rate": round(g, 4),
        "required_rate_of_return": required_rate,
        "model_type": model_type,
    }


def fetch_balance_sheet_metrics(symbol: str) -> dict:
    """Extract key financial ratios and balance sheet data for AI analysis."""
    ticker = get_ticker(symbol)
    info = ticker.info

    # Balance sheet
    bs = ticker.balance_sheet
    income = ticker.income_stmt
    cashflow = ticker.cashflow

    metrics = {}

    metrics["payout_ratio"] = _safe_float(info.get("payoutRatio"))
    metrics["dividend_yield"] = _safe_float(info.get("dividendYield"))
    metrics["annual_dividend"] = _safe_float(info.get("dividendRate"))

    # Debt-to-equity
    metrics["debt_to_equity"] = _safe_float(info.get("debtToEquity"))

    # Current ratio
    metrics["current_ratio"] = _safe_float(info.get("currentRatio"))

    # Interest coverage (EBIT / Interest Expense)
    interest_coverage = None
    if income is not None and not income.empty:
        def _get_row(df, *labels):
            for label in labels:
                matches = [c for c in df.index if label.lower() in c.lower()]
                if matches:
                    return df.loc[matches[0]]
            return None

        ebit_row = _get_row(income, "EBIT", "Earnings Before Interest")
        interest_row = _get_row(income, "Interest Expense")
        if ebit_row is not None and interest_row is not None:
            ebit_vals = ebit_row.dropna().values
            int_vals = interest_row.dropna().values
            if len(ebit_vals) > 0 and len(int_vals) > 0:
                ebit = float(ebit_vals[0])
                interest = abs(float(int_vals[0]))
                if interest > 0:
                    interest_coverage = round(ebit / interest, 2)

    metrics["interest_coverage"] = interest_coverage

    # FCF payout ratio
    fcf_payout = None
    if cashflow is not None and not cashflow.empty:
        def _get_row_cf(df, *labels):
            for label in labels:
                matches = [c for c in df.index if label.lower() in c.lower()]
                if matches:
                    return df.loc[matches[0]]
            return None

        op_cf_row = _get_row_cf(cashflow, "Operating Cash Flow", "Total Cash From Operating Activities")
        capex_row = _get_row_cf(cashflow, "Capital Expenditure")
        shares = _safe_float(info.get("sharesOutstanding"))
        annual_div = _safe_float(info.get("dividendRate"))

        if op_cf_row is not None and shares and annual_div:
            op_cf = float(op_cf_row.dropna().values[0])
            capex = float(capex_row.dropna().values[0]) if capex_row is not None else 0
            fcf = op_cf + capex  # capex is negative
            total_divs = annual_div * shares
            if fcf > 0:
                fcf_payout = round(total_divs / fcf, 4)

    metrics["free_cash_flow_payout"] = fcf_payout

    # Dividend CAGR
    metrics["dividend_cagr_5y"] = _compute_dividend_cagr(ticker, years=5)

    # Years of consecutive dividend growth (heuristic from history)
    metrics["years_of_dividend_growth"] = _count_consecutive_dividend_growth_years(ticker)

    # Additional for AI context
    metrics["revenue_growth"] = _safe_float(info.get("revenueGrowth"))
    metrics["earnings_growth"] = _safe_float(info.get("earningsGrowth"))
    metrics["profit_margin"] = _safe_float(info.get("profitMargins"))
    metrics["operating_margin"] = _safe_float(info.get("operatingMargins"))
    metrics["return_on_equity"] = _safe_float(info.get("returnOnEquity"))
    metrics["return_on_assets"] = _safe_float(info.get("returnOnAssets"))
    metrics["quick_ratio"] = _safe_float(info.get("quickRatio"))
    metrics["total_debt"] = _safe_float(info.get("totalDebt"))
    metrics["total_cash"] = _safe_float(info.get("totalCash"))

    return metrics


def _count_consecutive_dividend_growth_years(ticker: yf.Ticker) -> Optional[int]:
    """Count years of consecutive annual dividend increases."""
    try:
        divs = ticker.dividends
        if divs is None or len(divs) == 0:
            return None
        divs.index = divs.index.tz_localize(None)
        annual = divs.resample("YE").sum()
        if len(annual) < 2:
            return None
        annual = annual[annual > 0]
        count = 0
        for i in range(len(annual) - 1, 0, -1):
            if annual.iloc[i] > annual.iloc[i - 1]:
                count += 1
            else:
                break
        return count
    except Exception:
        return None
