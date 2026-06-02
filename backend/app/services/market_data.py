from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import yfinance as yf


@dataclass
class FinancialDataset:
    ticker: str
    info: dict
    current_price: float | None
    shares_outstanding: float | None
    balance_sheet: pd.DataFrame
    cashflow: pd.DataFrame
    dividends: pd.Series


class MarketDataService:
    def _load_ticker(self, ticker: str) -> yf.Ticker:
        return yf.Ticker(ticker.upper())

    def get_ticker_snapshot(self, ticker: str) -> dict:
        stock = self._load_ticker(ticker)
        info = stock.info or {}

        return {
            "ticker": ticker.upper(),
            "company_name": info.get("longName") or info.get("shortName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "currency": info.get("currency"),
            "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "dividend_yield": info.get("dividendYield"),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
        }

    def get_financial_dataset(self, ticker: str) -> FinancialDataset:
        stock = self._load_ticker(ticker)
        info = stock.info or {}

        current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        shares_outstanding = info.get("sharesOutstanding")

        balance_sheet = stock.balance_sheet.fillna(0) if stock.balance_sheet is not None else pd.DataFrame()
        cashflow = stock.cashflow.fillna(0) if stock.cashflow is not None else pd.DataFrame()
        dividends = stock.dividends.fillna(0) if stock.dividends is not None else pd.Series(dtype=float)

        return FinancialDataset(
            ticker=ticker.upper(),
            info=info,
            current_price=current_price,
            shares_outstanding=shares_outstanding,
            balance_sheet=balance_sheet,
            cashflow=cashflow,
            dividends=dividends,
        )

    @staticmethod
    def dataframe_to_records(df: pd.DataFrame, max_columns: int = 5) -> list[dict]:
        if df.empty:
            return []

        records: list[dict] = []
        columns = list(df.columns[:max_columns])

        for column in columns:
            column_key = column.strftime("%Y-%m-%d") if hasattr(column, "strftime") else str(column)
            record = {"date": column_key}
            for metric in df.index:
                value = df.at[metric, column]
                if value != 0:
                    record[str(metric)] = float(value)
            records.append(record)

        return records
