import json
from typing import Optional
from fastapi import HTTPException
from openai import OpenAI, APIError
from app.config import settings
from app.services.stock_service import fetch_balance_sheet_metrics


def _grade_score(score: int) -> str:
    if score >= 85:
        return "A+"
    elif score >= 75:
        return "A"
    elif score >= 65:
        return "B+"
    elif score >= 55:
        return "B"
    elif score >= 45:
        return "C+"
    elif score >= 35:
        return "C"
    else:
        return "D"


SYSTEM_PROMPT = """You are a professional dividend growth investing analyst. 
Your task is to evaluate a stock's dividend safety based on its financial metrics.
Respond ONLY with valid JSON in the exact schema provided. Do not add any prose outside the JSON."""

ANALYSIS_PROMPT_TEMPLATE = """Analyze the dividend safety for {ticker} using the following financial metrics:

{metrics_json}

Return a JSON object with this exact structure:
{{
  "safety_score": <integer 0-100, where 100 is perfectly safe>,
  "summary": "<2-3 sentence plain-English summary of dividend safety>",
  "strengths": ["<strength 1>", "<strength 2>", ...],
  "risks": ["<risk 1>", "<risk 2>", ...]
}}

Scoring guide:
- 85-100: Very safe; well-covered by earnings and FCF, long growth streak, low debt
- 65-84: Safe; adequately covered, moderate debt, consistent history
- 45-64: Moderate; coverage is adequate but may be stressed in downturns
- 25-44: Risky; payout ratio high, debt elevated, limited growth history
- 0-24: Very risky or likely to be cut

Provide 3-5 bullet items each for strengths and risks. Be concise and specific to the numbers provided.
If a metric is missing (null), note it as unknown and weigh available evidence accordingly."""


def analyze_dividend_safety(symbol: str) -> dict:
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=503,
            detail="OpenAI API key not configured. Set OPENAI_API_KEY in your environment.",
        )

    metrics = fetch_balance_sheet_metrics(symbol)

    # Format metrics for prompt
    def fmt(v, pct=False):
        if v is None:
            return "N/A"
        if pct:
            return f"{v * 100:.1f}%"
        return f"{v:.2f}"

    metrics_summary = {
        "Payout Ratio (earnings-based)": fmt(metrics.get("payout_ratio"), pct=True),
        "FCF Payout Ratio": fmt(metrics.get("free_cash_flow_payout"), pct=True),
        "Dividend Yield": fmt(metrics.get("dividend_yield"), pct=True),
        "Annual Dividend Per Share": fmt(metrics.get("annual_dividend")),
        "Dividend CAGR (5yr)": fmt(metrics.get("dividend_cagr_5y"), pct=True),
        "Consecutive Years of Dividend Growth": str(metrics.get("years_of_dividend_growth") or "N/A"),
        "Debt-to-Equity Ratio": fmt(metrics.get("debt_to_equity")),
        "Interest Coverage Ratio": fmt(metrics.get("interest_coverage")),
        "Current Ratio": fmt(metrics.get("current_ratio")),
        "Quick Ratio": fmt(metrics.get("quick_ratio")),
        "Return on Equity (ROE)": fmt(metrics.get("return_on_equity"), pct=True),
        "Return on Assets (ROA)": fmt(metrics.get("return_on_assets"), pct=True),
        "Profit Margin": fmt(metrics.get("profit_margin"), pct=True),
        "Operating Margin": fmt(metrics.get("operating_margin"), pct=True),
        "Revenue Growth (YoY)": fmt(metrics.get("revenue_growth"), pct=True),
        "Earnings Growth (YoY)": fmt(metrics.get("earnings_growth"), pct=True),
    }

    prompt = ANALYSIS_PROMPT_TEMPLATE.format(
        ticker=symbol.upper(),
        metrics_json=json.dumps(metrics_summary, indent=2),
    )

    try:
        client = OpenAI(api_key=settings.openai_api_key)
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content
        parsed = json.loads(raw)
    except APIError as e:
        raise HTTPException(status_code=502, detail=f"OpenAI API error: {e}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=502, detail="AI returned invalid JSON.")

    score = int(parsed.get("safety_score", 50))
    score = max(0, min(100, score))

    return {
        "ticker": symbol.upper(),
        "safety_score": score,
        "safety_grade": _grade_score(score),
        "summary": parsed.get("summary", ""),
        "strengths": parsed.get("strengths", []),
        "risks": parsed.get("risks", []),
        "payout_ratio": metrics.get("payout_ratio"),
        "debt_to_equity": metrics.get("debt_to_equity"),
        "interest_coverage": metrics.get("interest_coverage"),
        "free_cash_flow_payout": metrics.get("free_cash_flow_payout"),
        "dividend_cagr_5y": metrics.get("dividend_cagr_5y"),
        "years_of_dividend_growth": metrics.get("years_of_dividend_growth"),
        "raw_metrics": metrics,
    }
