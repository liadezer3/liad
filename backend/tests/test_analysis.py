from app.models import AnalysisAssumptions
from app.sample_data import get_sample_stock
from app.services.dividend_safety import analyze_dividend_safety
from app.services.valuation import calculate_valuation


def test_valuation_returns_positive_fair_values() -> None:
    profile = get_sample_stock("MSFT")
    valuation = calculate_valuation(profile, AnalysisAssumptions())

    assert valuation.dcf.fair_value_per_share > 0
    assert valuation.ddm.fair_value_per_share > 0
    assert valuation.blended_fair_value > 0
    assert len(valuation.dcf.projected_cash_flows) == 5


def test_dividend_safety_includes_prompt_and_score() -> None:
    profile = get_sample_stock("KO")
    safety = analyze_dividend_safety(profile)

    assert 0 <= safety.score <= 100
    assert safety.rating in {"Very Safe", "Safe", "Borderline", "At Risk"}
    assert "equity research analyst" in safety.prompt
    assert safety.rationale
