import json
import re

from openai import OpenAI

from app.config import settings
from app.schemas import DividendSafetyResult
from app.services.ai_prompts import (
    DIVIDEND_SAFETY_SYSTEM,
    DIVIDEND_SAFETY_USER_TEMPLATE,
    format_balance_sheet_for_prompt,
)
from app.services.stock_data import fetch_financials_for_valuation, fetch_stock_details


def analyze_dividend_safety(ticker: str) -> DividendSafetyResult:
    quote = fetch_stock_details(ticker)
    financials = fetch_financials_for_valuation(ticker)
    highlights = financials.get("balance_sheet_highlights") or {}

    if settings.openai_api_key:
        result = _analyze_with_ai(quote, financials, highlights)
        result.balance_sheet_highlights = highlights
        return result

    result = _analyze_rule_based(quote, financials, highlights)
    result.balance_sheet_highlights = highlights
    return result


def _analyze_with_ai(quote, financials, highlights) -> DividendSafetyResult:
    client = OpenAI(api_key=settings.openai_api_key)
    user_prompt = DIVIDEND_SAFETY_USER_TEMPLATE.format(
        ticker=quote.ticker,
        company_name=quote.name,
        dividend_yield=f"{(quote.dividend_yield or 0) * 100:.2f}%"
        if quote.dividend_yield and quote.dividend_yield < 1
        else f"{quote.dividend_yield or 0:.2f}%",
        annual_dividend=financials.get("annual_dividend") or 0,
        payout_ratio=f"{(quote.payout_ratio or 0) * 100:.1f}%"
        if quote.payout_ratio and quote.payout_ratio <= 1
        else f"{quote.payout_ratio or 'N/A'}",
        sector=quote.sector or "Unknown",
        balance_sheet_text=format_balance_sheet_for_prompt(highlights),
    )

    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": DIVIDEND_SAFETY_SYSTEM},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content or "{}"
    parsed = json.loads(content)

    return DividendSafetyResult(
        ticker=quote.ticker,
        safety_score=int(parsed.get("safety_score", 50)),
        rating=str(parsed.get("rating", "Fair")),
        summary=str(parsed.get("summary", "")),
        factors=list(parsed.get("factors", [])),
        ai_powered=True,
        balance_sheet_highlights=highlights,
    )


def _analyze_rule_based(quote, financials, highlights) -> DividendSafetyResult:
    score = 70
    factors: list[dict] = []

    payout = quote.payout_ratio
    if payout is not None:
        pr = payout if payout > 1 else payout * 100
        if pr > 80:
            score -= 25
            factors.append(
                {
                    "name": "Payout ratio",
                    "impact": "negative",
                    "detail": f"Payout ratio of {pr:.1f}% leaves little margin for dividend growth.",
                }
            )
        elif pr < 60:
            score += 10
            factors.append(
                {
                    "name": "Payout ratio",
                    "impact": "positive",
                    "detail": f"Payout ratio of {pr:.1f}% suggests room to sustain and grow dividends.",
                }
            )
        else:
            factors.append(
                {
                    "name": "Payout ratio",
                    "impact": "neutral",
                    "detail": f"Payout ratio of {pr:.1f}% is moderate.",
                }
            )

    debt = highlights.get("Total Debt", [])
    equity = highlights.get("Stockholders Equity", [])
    if debt and equity and debt[-1] and equity[-1] and equity[-1] > 0:
        de = debt[-1] / equity[-1]
        if de > 1.5:
            score -= 20
            factors.append(
                {
                    "name": "Leverage",
                    "impact": "negative",
                    "detail": f"Debt-to-equity approx. {de:.2f} indicates elevated leverage.",
                }
            )
        elif de < 0.5:
            score += 10
            factors.append(
                {
                    "name": "Leverage",
                    "impact": "positive",
                    "detail": f"Conservative debt-to-equity approx. {de:.2f}.",
                }
            )

    cash = highlights.get("Cash And Cash Equivalents", [])
    if len(cash) >= 2 and cash[0] is not None and cash[1] is not None:
        if cash[1] < cash[0]:
            score -= 10
            factors.append(
                {
                    "name": "Cash position",
                    "impact": "negative",
                    "detail": "Cash and equivalents declined versus the prior period.",
                }
            )
        else:
            score += 5
            factors.append(
                {
                    "name": "Cash position",
                    "impact": "positive",
                    "detail": "Cash and equivalents improved versus the prior period.",
                }
            )

    re = highlights.get("Retained Earnings", [])
    if len(re) >= 2 and re[0] is not None and re[1] is not None and re[1] < re[0]:
        score -= 10
        factors.append(
            {
                "name": "Retained earnings",
                "impact": "negative",
                "detail": "Retained earnings trended lower, which can pressure future payouts.",
            }
        )

    fcf = financials.get("fcf_history") or []
    div = financials.get("annual_dividend") or 0
    shares = financials.get("shares_outstanding") or 0
    if fcf and div > 0 and shares > 0:
        total_div = div * shares
        if fcf[-1] < total_div:
            score -= 15
            factors.append(
                {
                    "name": "FCF coverage",
                    "impact": "negative",
                    "detail": "Latest free cash flow does not fully cover aggregate dividends paid.",
                }
            )
        else:
            score += 10
            factors.append(
                {
                    "name": "FCF coverage",
                    "impact": "positive",
                    "detail": "Free cash flow covers aggregate dividend obligations.",
                }
            )

    score = max(0, min(100, score))
    rating = _score_to_rating(score)
    summary = (
        f"Rule-based analysis for {quote.ticker} ({quote.name}) yields a safety score of {score}/100 ({rating}). "
        "Set OPENAI_API_KEY for AI-enhanced balance sheet interpretation."
    )

    return DividendSafetyResult(
        ticker=quote.ticker,
        safety_score=score,
        rating=rating,
        summary=summary,
        factors=factors,
        ai_powered=False,
        balance_sheet_highlights=highlights,
    )


def _score_to_rating(score: int) -> str:
    if score >= 85:
        return "Excellent"
    if score >= 70:
        return "Good"
    if score >= 55:
        return "Fair"
    if score >= 40:
        return "Weak"
    return "At Risk"
