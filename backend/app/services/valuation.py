"""Financial valuation engine: Discounted Cash Flow and Dividend Discount Model."""

from __future__ import annotations

from ..models.schemas import (
    DCFRequest,
    DCFResult,
    DCFYear,
    DDMRequest,
    DDMResult,
    DDMYear,
    TickerDetail,
)


def _verdict(upside_pct: float) -> str:
    if upside_pct >= 15:
        return "Undervalued"
    if upside_pct <= -15:
        return "Overvalued"
    return "Fairly Valued"


def run_dcf(detail: TickerDetail, req: DCFRequest) -> DCFResult:
    """Two-stage Discounted Cash Flow on free cash flow per share.

    Stage 1 grows FCF/share at `growth_rate` for `projection_years`, then a
    Gordon-growth terminal value capitalises the final year's cash flow at
    `terminal_growth`. Everything is discounted back at `discount_rate`.
    """
    if req.discount_rate <= req.terminal_growth:
        raise ValueError("discount_rate must be greater than terminal_growth")

    fcf_ps = detail.free_cash_flow_per_share
    if not fcf_ps and detail.free_cash_flow and detail.shares_outstanding:
        fcf_ps = detail.free_cash_flow / detail.shares_outstanding
    if not fcf_ps or fcf_ps <= 0:
        # Fall back to EPS as a proxy for owner earnings when FCF is unavailable.
        fcf_ps = detail.eps or 0.0
    if fcf_ps <= 0:
        raise ValueError("Insufficient cash-flow data to run a DCF for this ticker")

    projections: list[DCFYear] = []
    sum_pv = 0.0
    current_fcf = fcf_ps
    last_fcf = fcf_ps
    for year in range(1, req.projection_years + 1):
        current_fcf = current_fcf * (1 + req.growth_rate)
        discount_factor = 1 / ((1 + req.discount_rate) ** year)
        pv = current_fcf * discount_factor
        sum_pv += pv
        last_fcf = current_fcf
        projections.append(
            DCFYear(
                year=year,
                projected_fcf=round(current_fcf, 4),
                discount_factor=round(discount_factor, 6),
                present_value=round(pv, 4),
            )
        )

    terminal_value = (last_fcf * (1 + req.terminal_growth)) / (
        req.discount_rate - req.terminal_growth
    )
    pv_terminal = terminal_value / ((1 + req.discount_rate) ** req.projection_years)

    # Per-share basis: equity value per share = PV(FCF) + PV(terminal) adjusted
    # for net cash/debt per share.
    net_cash_ps = 0.0
    if detail.shares_outstanding:
        net_cash = (detail.total_cash or 0.0) - (detail.total_debt or 0.0)
        net_cash_ps = net_cash / detail.shares_outstanding

    enterprise_value = sum_pv + pv_terminal
    equity_value = enterprise_value + net_cash_ps
    fair_value = max(equity_value, 0.0)

    upside = ((fair_value - detail.price) / detail.price * 100) if detail.price else 0.0

    return DCFResult(
        ticker=detail.ticker,
        assumptions=req,
        projections=projections,
        sum_pv_fcf=round(sum_pv, 4),
        terminal_value=round(terminal_value, 4),
        pv_terminal_value=round(pv_terminal, 4),
        enterprise_value=round(enterprise_value, 4),
        equity_value=round(equity_value, 4),
        fair_value_per_share=round(fair_value, 2),
        current_price=round(detail.price, 2),
        upside_pct=round(upside, 2),
        verdict=_verdict(upside),
    )


def run_ddm(detail: TickerDetail, req: DDMRequest) -> DDMResult:
    """Two-stage Dividend Discount Model (multi-stage Gordon Growth)."""
    if req.discount_rate <= req.terminal_growth:
        raise ValueError("discount_rate must be greater than terminal_growth")

    dividend = detail.dividend_per_share
    if not dividend or dividend <= 0:
        raise ValueError(
            f"{detail.ticker} does not pay a dividend, so the DDM is not applicable"
        )

    projections: list[DDMYear] = []
    pv_high = 0.0
    current_div = dividend
    for year in range(1, req.high_growth_years + 1):
        current_div = current_div * (1 + req.high_growth_rate)
        pv = current_div / ((1 + req.discount_rate) ** year)
        pv_high += pv
        projections.append(
            DDMYear(
                year=year,
                projected_dividend=round(current_div, 4),
                present_value=round(pv, 4),
            )
        )

    # Terminal value at end of high-growth stage using Gordon Growth.
    terminal_dividend = current_div * (1 + req.terminal_growth)
    terminal_value = terminal_dividend / (req.discount_rate - req.terminal_growth)
    pv_terminal = terminal_value / ((1 + req.discount_rate) ** req.high_growth_years)

    fair_value = pv_high + pv_terminal
    upside = ((fair_value - detail.price) / detail.price * 100) if detail.price else 0.0

    return DDMResult(
        ticker=detail.ticker,
        assumptions=req,
        projections=projections,
        pv_high_growth=round(pv_high, 4),
        terminal_value=round(terminal_value, 4),
        pv_terminal_value=round(pv_terminal, 4),
        fair_value_per_share=round(fair_value, 2),
        current_price=round(detail.price, 2),
        upside_pct=round(upside, 2),
        verdict=_verdict(upside),
    )
