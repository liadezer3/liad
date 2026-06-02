from __future__ import annotations

from app.models import (
    AnalysisAssumptions,
    DcfValuation,
    DdmValuation,
    StockProfile,
    ValuationResult,
)


def _latest_free_cash_flow(profile: StockProfile) -> float:
    return sorted(profile.cash_flows, key=lambda item: item.year)[-1].free_cash_flow


def _latest_net_debt(profile: StockProfile) -> float:
    latest_balance_sheet = sorted(profile.balance_sheets, key=lambda item: item.year)[-1]
    return latest_balance_sheet.total_debt - latest_balance_sheet.cash_and_equivalents


def calculate_dcf(profile: StockProfile, assumptions: AnalysisAssumptions) -> DcfValuation:
    base_fcf = _latest_free_cash_flow(profile)
    projected_cash_flows: list[float] = []
    present_value = 0.0

    for year in range(1, assumptions.projection_years + 1):
        projected = base_fcf * ((1 + assumptions.dcf_growth_rate) ** year)
        projected_cash_flows.append(projected)
        present_value += projected / ((1 + assumptions.discount_rate) ** year)

    terminal_cash_flow = projected_cash_flows[-1] * (1 + assumptions.terminal_growth_rate)
    spread = assumptions.discount_rate - assumptions.terminal_growth_rate
    terminal_value = terminal_cash_flow / spread if spread > 0.005 else 0.0
    terminal_present_value = terminal_value / (
        (1 + assumptions.discount_rate) ** assumptions.projection_years
    )

    enterprise_value = present_value + terminal_present_value
    equity_value = enterprise_value - _latest_net_debt(profile)
    fair_value_per_share = max(equity_value / profile.shares_outstanding, 0)
    margin_of_safety = (fair_value_per_share - profile.price) / profile.price

    return DcfValuation(
        fair_value_per_share=round(fair_value_per_share, 2),
        enterprise_value=round(enterprise_value, 2),
        equity_value=round(equity_value, 2),
        margin_of_safety=round(margin_of_safety, 4),
        projected_cash_flows=[round(value, 2) for value in projected_cash_flows],
        terminal_value=round(terminal_value, 2),
    )


def calculate_ddm(profile: StockProfile, assumptions: AnalysisAssumptions) -> DdmValuation:
    next_year_dividend = profile.annual_dividend * (1 + assumptions.ddm_growth_rate)
    spread = assumptions.required_return - assumptions.ddm_growth_rate
    fair_value = next_year_dividend / spread if spread > 0.0025 else 0.0
    margin_of_safety = (fair_value - profile.price) / profile.price
    implied_yield = next_year_dividend / profile.price

    return DdmValuation(
        fair_value_per_share=round(max(fair_value, 0), 2),
        next_year_dividend=round(next_year_dividend, 2),
        implied_yield=round(implied_yield, 4),
        margin_of_safety=round(margin_of_safety, 4),
    )


def calculate_valuation(
    profile: StockProfile, assumptions: AnalysisAssumptions | None = None
) -> ValuationResult:
    resolved_assumptions = assumptions or AnalysisAssumptions()
    dcf = calculate_dcf(profile, resolved_assumptions)
    ddm = calculate_ddm(profile, resolved_assumptions)

    blended_fair_value = (dcf.fair_value_per_share * 0.65) + (
        ddm.fair_value_per_share * 0.35
    )
    blended_margin = (blended_fair_value - profile.price) / profile.price

    return ValuationResult(
        dcf=dcf,
        ddm=ddm,
        blended_fair_value=round(blended_fair_value, 2),
        blended_margin_of_safety=round(blended_margin, 4),
        assumptions=resolved_assumptions,
    )
