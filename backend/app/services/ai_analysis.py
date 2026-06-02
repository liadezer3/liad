"""AI prompt layer for dividend-safety analysis.

The service first derives a set of financial features from the company's
historical balance sheets, then either:

  * sends those features through a structured prompt to an OpenAI-compatible
    LLM (when ``AI_PROVIDER=llm`` and a key is configured), or
  * scores them with a transparent, deterministic heuristic engine.

Both paths return the same :class:`DividendSafetyResult` schema, so the
frontend never has to care which engine produced the answer.
"""

from __future__ import annotations

import json
from typing import Optional

from ..config import get_settings
from ..models.schemas import DividendSafetyResult, SafetyFactor, TickerDetail


# ---------------------------------------------------------------------------
# Feature engineering from historical balance sheets
# ---------------------------------------------------------------------------
def _safe_div(a: Optional[float], b: Optional[float]) -> Optional[float]:
    if a is None or b is None or b == 0:
        return None
    return a / b


def derive_features(detail: TickerDetail) -> dict:
    """Compute the financial signals that drive dividend safety."""
    sheets = sorted(detail.balance_sheets, key=lambda s: s.year)
    latest = sheets[-1] if sheets else None

    features: dict = {
        "payout_ratio": detail.payout_ratio,
        "dividend_yield": detail.dividend_yield,
        "years_of_growth": detail.years_of_growth,
        "five_year_dividend_growth": detail.five_year_dividend_growth,
    }

    if latest:
        features["current_ratio"] = _safe_div(
            latest.current_assets, latest.current_liabilities
        )
        features["debt_to_equity"] = _safe_div(latest.total_debt, latest.total_equity)
        features["fcf_dividend_coverage"] = _safe_div(
            latest.free_cash_flow, latest.dividends_paid
        )
        features["earnings_payout"] = _safe_div(
            latest.dividends_paid, latest.net_income
        )
        features["cash_to_debt"] = _safe_div(
            latest.cash_and_equivalents, latest.total_debt
        )

    # Trend signals across the available history.
    if len(sheets) >= 2:
        first, last = sheets[0], sheets[-1]
        features["fcf_trend_positive"] = last.free_cash_flow >= first.free_cash_flow
        features["dividend_trend_growing"] = last.dividends_paid >= first.dividends_paid
        features["net_income_positive_years"] = sum(
            1 for s in sheets if s.net_income > 0
        )
        features["history_years"] = len(sheets)

    return {k: v for k, v in features.items() if v is not None}


# ---------------------------------------------------------------------------
# Heuristic scoring engine
# ---------------------------------------------------------------------------
def _score_band(score: float) -> str:
    if score >= 85:
        return "Very Safe"
    if score >= 70:
        return "Safe"
    if score >= 50:
        return "Borderline"
    if score >= 30:
        return "At Risk"
    return "Unsafe"


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def heuristic_analysis(detail: TickerDetail, features: dict) -> DividendSafetyResult:
    """Deterministic, explainable dividend-safety scoring."""
    factors: list[SafetyFactor] = []

    # 1. Payout ratio (FCF / earnings based) -------------------------------
    payout = features.get("earnings_payout", features.get("payout_ratio"))
    if payout is not None:
        if payout <= 0.4:
            s, d = 95, f"Low payout ratio ({payout:.0%}) leaves a wide safety margin."
        elif payout <= 0.6:
            s, d = 80, f"Healthy payout ratio ({payout:.0%}) is comfortably covered."
        elif payout <= 0.8:
            s, d = 60, f"Elevated payout ratio ({payout:.0%}) limits flexibility."
        elif payout <= 1.0:
            s, d = 35, f"High payout ratio ({payout:.0%}) is a stretch in a downturn."
        else:
            s, d = 12, f"Payout ratio above 100% ({payout:.0%}) is unsustainable."
        factors.append(SafetyFactor(name="Payout Ratio", score=s, weight=0.28, detail=d))

    # 2. Free-cash-flow dividend coverage ----------------------------------
    cov = features.get("fcf_dividend_coverage")
    if cov is not None:
        if cov >= 2.5:
            s, d = 95, f"FCF covers the dividend {cov:.1f}x over."
        elif cov >= 1.5:
            s, d = 82, f"Solid {cov:.1f}x free-cash-flow dividend coverage."
        elif cov >= 1.0:
            s, d = 58, f"Dividend is only {cov:.1f}x covered by free cash flow."
        else:
            s, d = 22, f"Free cash flow does not cover the dividend ({cov:.1f}x)."
        factors.append(
            SafetyFactor(name="FCF Coverage", score=s, weight=0.24, detail=d)
        )

    # 3. Balance-sheet leverage --------------------------------------------
    dte = features.get("debt_to_equity")
    if dte is not None:
        if dte <= 0.5:
            s, d = 92, f"Conservative leverage (D/E {dte:.2f})."
        elif dte <= 1.0:
            s, d = 75, f"Moderate leverage (D/E {dte:.2f})."
        elif dte <= 2.0:
            s, d = 50, f"Meaningful leverage (D/E {dte:.2f}) adds risk."
        else:
            s, d = 25, f"High leverage (D/E {dte:.2f}) pressures the dividend."
        factors.append(
            SafetyFactor(name="Leverage", score=s, weight=0.18, detail=d)
        )

    # 4. Liquidity (current ratio) -----------------------------------------
    cr = features.get("current_ratio")
    if cr is not None:
        if cr >= 1.5:
            s, d = 90, f"Strong liquidity (current ratio {cr:.2f})."
        elif cr >= 1.0:
            s, d = 68, f"Adequate liquidity (current ratio {cr:.2f})."
        else:
            s, d = 40, f"Thin liquidity (current ratio {cr:.2f})."
        factors.append(
            SafetyFactor(name="Liquidity", score=s, weight=0.12, detail=d)
        )

    # 5. Dividend track record ---------------------------------------------
    yog = features.get("years_of_growth")
    if yog is not None:
        if yog >= 25:
            s, d = 96, f"{yog} consecutive years of dividend growth (aristocrat/king)."
        elif yog >= 10:
            s, d = 82, f"{yog} consecutive years of dividend growth."
        elif yog >= 5:
            s, d = 65, f"{yog} years of dividend growth — building a record."
        else:
            s, d = 45, f"Short {yog}-year dividend-growth record."
        factors.append(
            SafetyFactor(name="Track Record", score=s, weight=0.18, detail=d)
        )

    if not factors:
        # Nothing to score on — return a neutral, low-confidence result.
        return DividendSafetyResult(
            ticker=detail.ticker,
            safety_score=50.0,
            rating="Borderline",
            summary=(
                "Insufficient financial detail was available to assess dividend "
                "safety with confidence."
            ),
            strengths=[],
            risks=["Limited fundamental data available for analysis."],
            factors=[],
            engine="heuristic",
            model=None,
        )

    total_weight = sum(f.weight for f in factors)
    score = sum(f.score * f.weight for f in factors) / total_weight
    score = _clamp(score)

    strengths = [f.detail for f in factors if f.score >= 75]
    risks = [f.detail for f in factors if f.score < 55]

    rating = _score_band(score)
    summary = (
        f"{detail.name} earns a dividend-safety score of {score:.0f}/100 "
        f"({rating}). The assessment blends payout sustainability, free-cash-flow "
        f"coverage, balance-sheet leverage, liquidity and dividend-growth history."
    )

    return DividendSafetyResult(
        ticker=detail.ticker,
        safety_score=round(score, 1),
        rating=rating,
        summary=summary,
        strengths=strengths or ["No standout strengths identified."],
        risks=risks or ["No material red flags identified in the available data."],
        factors=factors,
        engine="heuristic",
        model=None,
    )


# ---------------------------------------------------------------------------
# LLM prompt layer
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = (
    "You are a meticulous equity-income analyst specialising in dividend safety. "
    "You evaluate a company's ability to sustain and grow its dividend using its "
    "historical balance sheets and cash-flow figures. You are objective, cite the "
    "numbers you rely on, and never give personalised investment advice. "
    "Respond ONLY with strict JSON matching the requested schema."
)


def build_user_prompt(detail: TickerDetail, features: dict) -> str:
    """Construct the analysis prompt sent to the LLM."""
    sheets = [s.model_dump() for s in sorted(detail.balance_sheets, key=lambda s: s.year)]
    schema = {
        "safety_score": "number 0-100",
        "rating": "one of: Very Safe | Safe | Borderline | At Risk | Unsafe",
        "summary": "2-3 sentence plain-English assessment",
        "strengths": ["short bullet strings"],
        "risks": ["short bullet strings"],
        "factors": [
            {
                "name": "factor name",
                "score": "number 0-100",
                "weight": "number 0-1",
                "detail": "one sentence explanation citing a metric",
            }
        ],
    }
    return (
        f"Company: {detail.name} ({detail.ticker})\n"
        f"Sector: {detail.sector}; Industry: {detail.industry}\n"
        f"Current price: {detail.price} {detail.currency}\n"
        f"Dividend/share: {detail.dividend_per_share}; "
        f"Yield: {detail.dividend_yield}; "
        f"Payout ratio: {detail.payout_ratio}\n\n"
        f"Derived financial features:\n{json.dumps(features, indent=2)}\n\n"
        f"Historical balance sheets / cash flow (oldest first):\n"
        f"{json.dumps(sheets, indent=2)}\n\n"
        f"Assess dividend safety. Weights across factors should sum to roughly 1.0 "
        f"and the safety_score should be consistent with the weighted factors.\n"
        f"Return JSON exactly in this shape:\n{json.dumps(schema, indent=2)}"
    )


def _llm_analysis(detail: TickerDetail, features: dict) -> Optional[DividendSafetyResult]:
    """Call an OpenAI-compatible chat completion endpoint. None on any failure."""
    settings = get_settings()
    try:
        import httpx

        url = f"{settings.openai_base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": settings.openai_model,
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(detail, features)},
            ],
        }
        with httpx.Client(timeout=45) as client:
            resp = client.post(url, headers=headers, json=body)
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
        parsed = json.loads(content)

        factors = [
            SafetyFactor(
                name=str(f.get("name", "Factor")),
                score=_clamp(float(f.get("score", 0))),
                weight=float(f.get("weight", 0)),
                detail=str(f.get("detail", "")),
            )
            for f in parsed.get("factors", [])
        ]
        return DividendSafetyResult(
            ticker=detail.ticker,
            safety_score=_clamp(float(parsed["safety_score"])),
            rating=parsed.get("rating", _score_band(float(parsed["safety_score"]))),
            summary=str(parsed.get("summary", "")),
            strengths=[str(s) for s in parsed.get("strengths", [])],
            risks=[str(r) for r in parsed.get("risks", [])],
            factors=factors,
            engine="llm",
            model=settings.openai_model,
        )
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------
def analyze_dividend_safety(detail: TickerDetail) -> DividendSafetyResult:
    """Run the AI prompt layer, falling back to the heuristic engine."""
    settings = get_settings()
    features = derive_features(detail)

    if settings.llm_enabled:
        result = _llm_analysis(detail, features)
        if result is not None:
            return result

    return heuristic_analysis(detail, features)
