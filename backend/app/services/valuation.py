from __future__ import annotations

import math

from app.services.market_data import FinancialDataset


class ValuationService:
    @staticmethod
    def _safe_div(numerator: float, denominator: float) -> float | None:
        if denominator == 0:
            return None
        return numerator / denominator

    def _latest_free_cash_flow(self, dataset: FinancialDataset) -> float | None:
        if dataset.cashflow.empty:
            return None

        column = dataset.cashflow.columns[0]

        if "Free Cash Flow" in dataset.cashflow.index:
            return float(dataset.cashflow.at["Free Cash Flow", column])

        operating = float(dataset.cashflow.at["Operating Cash Flow", column]) if "Operating Cash Flow" in dataset.cashflow.index else None
        capex = float(dataset.cashflow.at["Capital Expenditure", column]) if "Capital Expenditure" in dataset.cashflow.index else 0.0

        if operating is None:
            return None

        return operating + capex

    def calculate_dcf(
        self,
        dataset: FinancialDataset,
        forecast_years: int,
        fcf_growth_rate: float,
        discount_rate: float,
        terminal_growth_rate: float,
    ) -> dict:
        notes: list[str] = []

        latest_fcf = self._latest_free_cash_flow(dataset)
        if latest_fcf is None or latest_fcf <= 0:
            notes.append("Free cash flow unavailable or non-positive; DCF cannot be computed reliably.")
            return {
                "method": "Discounted Cash Flow (DCF)",
                "intrinsic_value_per_share": None,
                "current_price": dataset.current_price,
                "margin_of_safety": None,
                "assumptions": {
                    "forecast_years": forecast_years,
                    "fcf_growth_rate": fcf_growth_rate,
                    "discount_rate": discount_rate,
                    "terminal_growth_rate": terminal_growth_rate,
                },
                "notes": notes,
            }

        if terminal_growth_rate >= discount_rate:
            notes.append("Terminal growth must be lower than discount rate; adjusted to preserve finite terminal value.")
            terminal_growth_rate = max(discount_rate - 0.01, 0.0)

        projected_cashflows: list[float] = []
        for year in range(1, forecast_years + 1):
            projected_fcf = latest_fcf * math.pow(1 + fcf_growth_rate, year)
            projected_cashflows.append(projected_fcf)

        present_value = sum(
            cf / math.pow(1 + discount_rate, idx + 1) for idx, cf in enumerate(projected_cashflows)
        )

        terminal_cash_flow = projected_cashflows[-1] * (1 + terminal_growth_rate)
        terminal_value = terminal_cash_flow / (discount_rate - terminal_growth_rate)
        discounted_terminal = terminal_value / math.pow(1 + discount_rate, forecast_years)

        enterprise_value = present_value + discounted_terminal
        intrinsic_per_share = None

        if dataset.shares_outstanding and dataset.shares_outstanding > 0:
            intrinsic_per_share = enterprise_value / dataset.shares_outstanding
        else:
            notes.append("Shares outstanding unavailable; returning enterprise-level estimate only.")

        margin_of_safety = None
        if intrinsic_per_share and dataset.current_price:
            margin_of_safety = self._safe_div(intrinsic_per_share - dataset.current_price, dataset.current_price)

        return {
            "method": "Discounted Cash Flow (DCF)",
            "intrinsic_value_per_share": intrinsic_per_share,
            "current_price": dataset.current_price,
            "margin_of_safety": margin_of_safety,
            "assumptions": {
                "forecast_years": forecast_years,
                "fcf_growth_rate": fcf_growth_rate,
                "discount_rate": discount_rate,
                "terminal_growth_rate": terminal_growth_rate,
                "latest_free_cash_flow": latest_fcf,
            },
            "notes": notes,
        }

    def _latest_annual_dividend(self, dataset: FinancialDataset) -> float | None:
        info_dividend = dataset.info.get("dividendRate")
        if isinstance(info_dividend, (float, int)) and info_dividend > 0:
            return float(info_dividend)

        if dataset.dividends.empty:
            return None

        trailing = dataset.dividends.last("365D")
        if trailing.empty:
            trailing = dataset.dividends.tail(4)

        total = float(trailing.sum())
        return total if total > 0 else None

    def calculate_ddm(
        self,
        dataset: FinancialDataset,
        required_return: float,
        dividend_growth_rate: float,
    ) -> dict:
        notes: list[str] = []
        annual_dividend = self._latest_annual_dividend(dataset)

        if annual_dividend is None:
            notes.append("Dividend data unavailable; DDM requires a stable, non-zero dividend history.")
            return {
                "method": "Dividend Discount Model (DDM)",
                "intrinsic_value_per_share": None,
                "current_price": dataset.current_price,
                "margin_of_safety": None,
                "assumptions": {
                    "required_return": required_return,
                    "dividend_growth_rate": dividend_growth_rate,
                },
                "notes": notes,
            }

        if dividend_growth_rate >= required_return:
            notes.append("Dividend growth was capped below required return to keep model stable.")
            dividend_growth_rate = required_return - 0.01

        next_year_dividend = annual_dividend * (1 + dividend_growth_rate)
        intrinsic_per_share = next_year_dividend / (required_return - dividend_growth_rate)

        margin_of_safety = None
        if dataset.current_price:
            margin_of_safety = self._safe_div(intrinsic_per_share - dataset.current_price, dataset.current_price)

        return {
            "method": "Dividend Discount Model (DDM)",
            "intrinsic_value_per_share": intrinsic_per_share,
            "current_price": dataset.current_price,
            "margin_of_safety": margin_of_safety,
            "assumptions": {
                "required_return": required_return,
                "dividend_growth_rate": dividend_growth_rate,
                "annual_dividend": annual_dividend,
            },
            "notes": notes,
        }
