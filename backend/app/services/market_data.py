"""Market-data service.

Fetches ticker fundamentals + balance-sheet history from the live provider
(`yfinance`). If the network is unavailable, the ticker is unknown, or the
provider returns incomplete data, it transparently falls back to bundled
sample fixtures so the rest of the application keeps working.
"""

from __future__ import annotations

import math
from typing import Optional

from ..config import get_settings
from ..data.sample_tickers import SAMPLE_TICKERS, list_sample_tickers
from ..models.schemas import BalanceSheetYear, TickerDetail


class TickerNotFoundError(Exception):
    """Raised when a ticker cannot be resolved from live or sample data."""


def _clean(value) -> Optional[float]:
    """Coerce provider values into clean floats (or None)."""
    try:
        if value is None:
            return None
        f = float(value)
        if math.isnan(f) or math.isinf(f):
            return None
        return f
    except (TypeError, ValueError):
        return None


def _from_sample(symbol: str) -> TickerDetail:
    data = SAMPLE_TICKERS[symbol]
    payload = {**data, "is_sample": True}
    payload["balance_sheets"] = [BalanceSheetYear(**b) for b in data["balance_sheets"]]
    return TickerDetail(**payload)


def _try_live(symbol: str) -> Optional[TickerDetail]:
    """Attempt to build a TickerDetail from yfinance. Returns None on failure."""
    try:
        import yfinance as yf
    except Exception:
        return None

    try:
        t = yf.Ticker(symbol)
        info = t.info or {}
        if not info or info.get("regularMarketPrice") is None and info.get("currentPrice") is None:
            return None

        price = _clean(info.get("currentPrice")) or _clean(info.get("regularMarketPrice"))
        if not price:
            return None

        shares = _clean(info.get("sharesOutstanding"))
        dps = _clean(info.get("dividendRate")) or 0.0
        dyield = _clean(info.get("dividendYield"))
        # yfinance sometimes returns yield as a percentage, normalise to fraction
        if dyield and dyield > 1:
            dyield = dyield / 100.0
        if not dyield and price:
            dyield = (dps or 0.0) / price

        fcf = _clean(info.get("freeCashflow"))
        fcf_ps = (fcf / shares) if (fcf and shares) else None

        balance_sheets = _build_balance_sheets(t)

        return TickerDetail(
            ticker=symbol,
            name=info.get("longName") or info.get("shortName") or symbol,
            sector=info.get("sector"),
            industry=info.get("industry"),
            currency=info.get("currency") or "USD",
            exchange=info.get("exchange"),
            summary=info.get("longBusinessSummary"),
            price=price,
            market_cap=_clean(info.get("marketCap")),
            shares_outstanding=shares,
            beta=_clean(info.get("beta")),
            dividend_per_share=dps or 0.0,
            dividend_yield=dyield or 0.0,
            payout_ratio=_clean(info.get("payoutRatio")),
            five_year_dividend_growth=_clean(info.get("fiveYearAvgDividendYield")) and 0.0 or 0.0,
            years_of_growth=None,
            eps=_clean(info.get("trailingEps")),
            free_cash_flow=fcf,
            free_cash_flow_per_share=fcf_ps,
            total_debt=_clean(info.get("totalDebt")),
            total_cash=_clean(info.get("totalCash")),
            balance_sheets=balance_sheets,
            is_sample=False,
        )
    except Exception:
        return None


def _build_balance_sheets(ticker) -> list[BalanceSheetYear]:
    """Best-effort extraction of multi-year balance-sheet history."""
    years: list[BalanceSheetYear] = []
    try:
        bs = ticker.balance_sheet
        cf = ticker.cashflow
        fin = ticker.financials
        if bs is None or bs.empty:
            return years

        def grab(frame, *keys):
            if frame is None or frame.empty:
                return {}
            for key in keys:
                if key in frame.index:
                    return frame.loc[key].to_dict()
            return {}

        total_assets = grab(bs, "Total Assets")
        total_liab = grab(bs, "Total Liabilities Net Minority Interest", "Total Liab")
        equity = grab(bs, "Stockholders Equity", "Total Stockholder Equity")
        cur_assets = grab(bs, "Current Assets", "Total Current Assets")
        cur_liab = grab(bs, "Current Liabilities", "Total Current Liabilities")
        cash = grab(bs, "Cash And Cash Equivalents", "Cash")
        debt = grab(bs, "Total Debt")
        net_income = grab(fin, "Net Income")
        ocf = grab(cf, "Operating Cash Flow", "Total Cash From Operating Activities")
        capex = grab(cf, "Capital Expenditure")
        divs = grab(cf, "Cash Dividends Paid", "Common Stock Dividend Paid")

        for col in bs.columns:
            year = getattr(col, "year", None)
            if year is None:
                continue
            oc = _clean(ocf.get(col)) or 0.0
            cx = _clean(capex.get(col)) or 0.0
            years.append(
                BalanceSheetYear(
                    year=int(year),
                    total_assets=_clean(total_assets.get(col)) or 0.0,
                    total_liabilities=_clean(total_liab.get(col)) or 0.0,
                    total_equity=_clean(equity.get(col)) or 0.0,
                    current_assets=_clean(cur_assets.get(col)) or 0.0,
                    current_liabilities=_clean(cur_liab.get(col)) or 0.0,
                    cash_and_equivalents=_clean(cash.get(col)) or 0.0,
                    total_debt=_clean(debt.get(col)) or 0.0,
                    net_income=_clean(net_income.get(col)) or 0.0,
                    operating_cash_flow=oc,
                    free_cash_flow=oc + cx,  # capex is negative
                    dividends_paid=abs(_clean(divs.get(col)) or 0.0),
                )
            )
        years.sort(key=lambda y: y.year)
    except Exception:
        return []
    return years


def get_ticker_detail(symbol: str) -> TickerDetail:
    """Resolve a ticker to full detail, preferring live data."""
    symbol = symbol.strip().upper()
    settings = get_settings()

    live = _try_live(symbol)
    if live is not None:
        return live

    if settings.enable_sample_fallback and symbol in SAMPLE_TICKERS:
        return _from_sample(symbol)

    raise TickerNotFoundError(
        f"Could not retrieve data for '{symbol}'. Live lookup failed and no "
        f"sample fixture is available."
    )


def get_directory() -> list[dict]:
    """Return the bundled sample-ticker directory for discovery / autocomplete."""
    return list_sample_tickers()
