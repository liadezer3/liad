from __future__ import annotations

from statistics import mean

from app.models import DividendSafetyResult, StockProfile


def _trend(values: list[float]) -> float:
    if len(values) < 2 or values[0] == 0:
        return 0.0
    return (values[-1] - values[0]) / abs(values[0])


def _score_range(value: float, excellent: float, weak: float, reverse: bool = False) -> int:
    if reverse:
        if value <= excellent:
            return 100
        if value >= weak:
            return 0
        return round((weak - value) / (weak - excellent) * 100)

    if value >= excellent:
        return 100
    if value <= weak:
        return 0
    return round((value - weak) / (excellent - weak) * 100)


def build_balance_sheet_prompt(profile: StockProfile) -> str:
    latest_sheet = sorted(profile.balance_sheets, key=lambda item: item.year)[-1]
    latest_cash_flow = sorted(profile.cash_flows, key=lambda item: item.year)[-1]
    history_rows = "\n".join(
        (
            f"- {sheet.year}: assets ${sheet.total_assets:,.0f}, "
            f"debt/equity {sheet.debt_to_equity:.2f}, current ratio "
            f"{sheet.current_ratio:.2f}"
        )
        for sheet in sorted(profile.balance_sheets, key=lambda item: item.year)
    )

    return (
        "You are an equity research analyst specializing in dividend growth "
        "quality. Evaluate whether the company can safely maintain and grow its "
        "dividend using the historical balance sheet and cash-flow data below. "
        "Focus on leverage, liquidity, free-cash-flow dividend coverage, payout "
        "ratio, interest coverage, and dividend growth consistency. Return a "
        "0-100 dividend safety score, a rating, strengths, risks, and a concise "
        "rationale.\n\n"
        f"Company: {profile.company_name} ({profile.ticker})\n"
        f"Sector: {profile.sector}\n"
        f"Annual dividend/share: ${profile.annual_dividend:.2f}\n"
        f"Dividend yield: {profile.dividend_yield:.2%}\n"
        f"Latest debt/equity: {latest_sheet.debt_to_equity:.2f}\n"
        f"Latest current ratio: {latest_sheet.current_ratio:.2f}\n"
        f"Latest FCF dividend coverage: {latest_cash_flow.dividend_coverage:.2f}x\n"
        f"Latest payout ratio: {latest_cash_flow.payout_ratio:.2%}\n"
        f"Latest interest coverage: {latest_cash_flow.interest_coverage:.2f}x\n\n"
        "Historical balance sheet trend:\n"
        f"{history_rows}"
    )


def analyze_dividend_safety(profile: StockProfile) -> DividendSafetyResult:
    balance_sheets = sorted(profile.balance_sheets, key=lambda item: item.year)
    cash_flows = sorted(profile.cash_flows, key=lambda item: item.year)
    dividends = sorted(profile.dividend_history, key=lambda item: item.year)

    latest_sheet = balance_sheets[-1]
    latest_cash_flow = cash_flows[-1]
    debt_to_equity_values = [item.debt_to_equity for item in balance_sheets]
    current_ratios = [item.current_ratio for item in balance_sheets]
    coverage_values = [item.dividend_coverage for item in cash_flows]
    payout_values = [item.payout_ratio for item in cash_flows]
    interest_values = [item.interest_coverage for item in cash_flows]
    dividend_values = [item.dividend_per_share for item in dividends]

    fcf_coverage_score = _score_range(mean(coverage_values), excellent=2.5, weak=1.0)
    payout_score = _score_range(mean(payout_values), excellent=0.45, weak=0.9, reverse=True)
    leverage_score = _score_range(
        mean(debt_to_equity_values), excellent=0.7, weak=2.5, reverse=True
    )
    liquidity_score = _score_range(mean(current_ratios), excellent=1.8, weak=0.9)
    interest_score = _score_range(mean(interest_values), excellent=10.0, weak=3.0)
    dividend_growth_score = _score_range(
        _trend(dividend_values), excellent=0.25, weak=0.0
    )

    weighted_score = round(
        fcf_coverage_score * 0.30
        + payout_score * 0.20
        + leverage_score * 0.20
        + liquidity_score * 0.10
        + interest_score * 0.10
        + dividend_growth_score * 0.10
    )

    if weighted_score >= 85:
        rating = "Very Safe"
    elif weighted_score >= 70:
        rating = "Safe"
    elif weighted_score >= 55:
        rating = "Borderline"
    else:
        rating = "At Risk"

    strengths: list[str] = []
    risks: list[str] = []

    if latest_cash_flow.dividend_coverage >= 2:
        strengths.append("Free cash flow covers the dividend by more than 2x.")
    else:
        risks.append("Free-cash-flow dividend coverage is below the preferred 2x buffer.")

    if latest_cash_flow.payout_ratio <= 0.65:
        strengths.append("Latest payout ratio leaves room for reinvestment and shocks.")
    else:
        risks.append("Latest payout ratio consumes a large share of earnings.")

    if latest_sheet.debt_to_equity <= 1:
        strengths.append("Balance sheet leverage is conservative relative to equity.")
    else:
        risks.append("Debt-to-equity is elevated and should be monitored.")

    if latest_sheet.current_ratio >= 1.2:
        strengths.append("Current assets exceed near-term liabilities by a healthy margin.")
    else:
        risks.append("Current ratio is thin, reducing short-term flexibility.")

    if all(
        current.dividend_per_share >= previous.dividend_per_share
        for previous, current in zip(dividends, dividends[1:])
    ):
        strengths.append("Dividend per share has grown or held steady across the sample.")
    else:
        risks.append("Dividend history includes a cut or interruption in the sample period.")

    rationale = [
        (
            f"The weighted score is driven most by average FCF dividend coverage "
            f"of {mean(coverage_values):.2f}x and payout ratio of "
            f"{mean(payout_values):.1%}."
        ),
        (
            f"Historical leverage averaged {mean(debt_to_equity_values):.2f}x "
            f"debt/equity while liquidity averaged {mean(current_ratios):.2f}x."
        ),
        (
            f"Interest coverage averaged {mean(interest_values):.1f}x, indicating "
            "how much operating income cushions financing costs."
        ),
    ]

    return DividendSafetyResult(
        score=max(0, min(100, weighted_score)),
        rating=rating,
        prompt=build_balance_sheet_prompt(profile),
        rationale=rationale,
        strengths=strengths,
        risks=risks,
        metrics={
            "average_fcf_dividend_coverage": round(mean(coverage_values), 2),
            "latest_fcf_dividend_coverage": round(latest_cash_flow.dividend_coverage, 2),
            "average_payout_ratio": round(mean(payout_values), 4),
            "latest_payout_ratio": round(latest_cash_flow.payout_ratio, 4),
            "average_debt_to_equity": round(mean(debt_to_equity_values), 2),
            "latest_debt_to_equity": round(latest_sheet.debt_to_equity, 2),
            "average_current_ratio": round(mean(current_ratios), 2),
            "latest_current_ratio": round(latest_sheet.current_ratio, 2),
            "dividend_growth_over_period": round(_trend(dividend_values), 4),
        },
    )
