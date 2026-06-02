"""Gordon Growth Dividend Discount Model (DDM)."""


def calculate_ddm(
    annual_dividend: float,
    required_return: float,
    dividend_growth_rate: float,
) -> float:
    """
    Fair value = D1 / (r - g) where D1 = D0 * (1 + g).
    """
    if annual_dividend <= 0:
        raise ValueError("Annual dividend must be positive for DDM")
    if required_return <= dividend_growth_rate:
        raise ValueError("Required return must exceed dividend growth rate")

    d1 = annual_dividend * (1 + dividend_growth_rate)
    fair_value = d1 / (required_return - dividend_growth_rate)
    return round(fair_value, 2)
