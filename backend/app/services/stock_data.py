import yfinance as yf

from app.schemas import StockQuote


def _safe_float(value) -> float | None:
    if value is None:
        return None
    try:
        f = float(value)
        if f != f:  # NaN
            return None
        return f
    except (TypeError, ValueError):
        return None


def fetch_stock_details(ticker: str) -> StockQuote:
    symbol = ticker.upper().strip()
    stock = yf.Ticker(symbol)
    info = stock.info or {}

    return StockQuote(
        ticker=symbol,
        name=info.get("longName") or info.get("shortName") or symbol,
        sector=info.get("sector"),
        industry=info.get("industry"),
        current_price=_safe_float(info.get("currentPrice") or info.get("regularMarketPrice")),
        dividend_yield=_safe_float(info.get("dividendYield")),
        dividend_rate=_safe_float(info.get("dividendRate")),
        payout_ratio=_safe_float(info.get("payoutRatio")),
        trailing_pe=_safe_float(info.get("trailingPE")),
        market_cap=_safe_float(info.get("marketCap")),
        fifty_two_week_high=_safe_float(info.get("fiftyTwoWeekHigh")),
        fifty_two_week_low=_safe_float(info.get("fiftyTwoWeekLow")),
    )


def fetch_financials_for_valuation(ticker: str) -> dict:
    """Pull cash flow, balance sheet, and share data for valuation & safety analysis."""
    symbol = ticker.upper().strip()
    stock = yf.Ticker(symbol)
    info = stock.info or {}

    cashflow = stock.cashflow
    balance = stock.balance_sheet

    fcf_history: list[float] = []
    if cashflow is not None and not cashflow.empty:
        fcf_row = None
        for label in ("Free Cash Flow", "Operating Cash Flow"):
            if label in cashflow.index:
                fcf_row = cashflow.loc[label]
                break
        if fcf_row is not None:
            for col in sorted(cashflow.columns):
                val = _safe_float(fcf_row.get(col))
                if val is not None:
                    fcf_history.append(val)

    shares = _safe_float(info.get("sharesOutstanding")) or 0.0
    dividend_rate = _safe_float(info.get("dividendRate")) or 0.0
    payout_ratio = _safe_float(info.get("payoutRatio"))

    balance_highlights = _extract_balance_sheet_highlights(balance)

    return {
        "info": info,
        "fcf_history": fcf_history,
        "shares_outstanding": shares,
        "annual_dividend": dividend_rate,
        "payout_ratio": payout_ratio,
        "balance_sheet_highlights": balance_highlights,
        "balance_sheet_raw": balance_highlights,
    }


def _extract_balance_sheet_highlights(balance) -> dict:
    if balance is None or balance.empty:
        return {}

    def latest_two(row_name: str) -> list[float | None]:
        if row_name not in balance.index:
            return []
        row = balance.loc[row_name]
        vals = []
        for col in sorted(balance.columns)[-2:]:
            vals.append(_safe_float(row.get(col)))
        return vals

    keys = [
        "Total Debt",
        "Stockholders Equity",
        "Cash And Cash Equivalents",
        "Retained Earnings",
        "Total Assets",
        "Total Liabilities Net Minority Interest",
    ]
    highlights: dict = {}
    for key in keys:
        series = latest_two(key)
        if series:
            highlights[key] = series
    return highlights
