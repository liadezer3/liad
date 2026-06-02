"""Discounted Cash Flow (DCF) valuation for equity per share."""


def calculate_dcf(
    free_cash_flows: list[float],
    shares_outstanding: float,
    discount_rate: float,
    terminal_growth_rate: float,
    projection_years: int,
) -> tuple[float, list[float]]:
    """
    Project FCF using the latest FCF as base and historical CAGR when available.
    Returns (intrinsic_value_per_share, projected_fcf_list).
    """
    if not free_cash_flows or shares_outstanding <= 0:
        raise ValueError("Insufficient cash flow or share count data for DCF")

    base_fcf = free_cash_flows[-1]
    if len(free_cash_flows) >= 2 and free_cash_flows[0] > 0:
        n = len(free_cash_flows) - 1
        cagr = (free_cash_flows[-1] / free_cash_flows[0]) ** (1 / n) - 1
        growth = max(min(cagr, 0.15), -0.05)
    else:
        growth = 0.03

    projected: list[float] = []
    fcf = base_fcf
    for _ in range(projection_years):
        fcf *= 1 + growth
        projected.append(round(fcf, 2))

    pv_explicit = sum(fcf / (1 + discount_rate) ** (i + 1) for i, fcf in enumerate(projected))

    terminal_fcf = projected[-1] * (1 + terminal_growth_rate)
    if discount_rate <= terminal_growth_rate:
        terminal_growth_rate = discount_rate - 0.01
    terminal_value = terminal_fcf / (discount_rate - terminal_growth_rate)
    pv_terminal = terminal_value / (1 + discount_rate) ** projection_years

    enterprise_value = pv_explicit + pv_terminal
    intrinsic_per_share = enterprise_value / shares_outstanding
    return round(intrinsic_per_share, 2), projected
