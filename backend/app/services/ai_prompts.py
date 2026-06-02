"""Prompt templates for AI-assisted dividend safety analysis."""

DIVIDEND_SAFETY_SYSTEM = """You are a conservative equity analyst specializing in dividend growth investing.
Evaluate dividend safety using balance sheet trends, payout sustainability, and leverage.
Respond ONLY with valid JSON matching this schema:
{
  "safety_score": <integer 0-100>,
  "rating": "<Excellent|Good|Fair|Weak|At Risk>",
  "summary": "<2-3 sentence plain-language summary>",
  "factors": [
    {"name": "<factor>", "impact": "<positive|neutral|negative>", "detail": "<one sentence>"}
  ]
}
Be data-driven. Penalize rising debt/equity, declining cash, negative retained earnings trends, and payout ratios above 80%."""

DIVIDEND_SAFETY_USER_TEMPLATE = """Analyze dividend safety for {ticker} ({company_name}).

Current metrics:
- Dividend yield: {dividend_yield}
- Annual dividend: ${annual_dividend}
- Payout ratio: {payout_ratio}
- Sector: {sector}

Balance sheet highlights (most recent periods, oldest to newest where two values shown):
{balance_sheet_text}

Provide your JSON assessment."""

RULE_BASED_FACTOR_WEIGHTS = {
    "payout_ratio": 25,
    "debt_to_equity": 25,
    "cash_trend": 20,
    "retained_earnings": 15,
    "fcf_coverage": 15,
}


def format_balance_sheet_for_prompt(highlights: dict) -> str:
    if not highlights:
        return "No balance sheet data available."
    lines = []
    for key, values in highlights.items():
        if len(values) == 1:
            lines.append(f"- {key}: {values[0]:,.0f}" if values[0] else f"- {key}: N/A")
        elif len(values) >= 2:
            v0, v1 = values[0], values[1]
            trend = ""
            if v0 is not None and v1 is not None and v0 != 0:
                pct = (v1 - v0) / abs(v0) * 100
                trend = f" ({pct:+.1f}% change)"
            lines.append(
                f"- {key}: {v0:,.0f} → {v1:,.0f}{trend}"
                if v0 is not None and v1 is not None
                else f"- {key}: {values}"
            )
    return "\n".join(lines)
