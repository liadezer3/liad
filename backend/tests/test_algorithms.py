import pytest

from app.algorithms.dcf import calculate_dcf
from app.algorithms.ddm import calculate_ddm


def test_ddm_gordon_growth():
    # D0=2, g=5%, r=9% => D1=2.1, V = 2.1/0.04 = 52.5
    fair = calculate_ddm(annual_dividend=2.0, required_return=0.09, dividend_growth_rate=0.05)
    assert fair == 52.5


def test_ddm_invalid_growth():
    with pytest.raises(ValueError):
        calculate_ddm(annual_dividend=2.0, required_return=0.05, dividend_growth_rate=0.05)


def test_dcf_positive_value():
    fcf = [1e9, 1.1e9, 1.2e9]
    intrinsic, projected = calculate_dcf(
        free_cash_flows=fcf,
        shares_outstanding=1e9,
        discount_rate=0.10,
        terminal_growth_rate=0.025,
        projection_years=5,
    )
    assert intrinsic > 0
    assert len(projected) == 5


def test_dcf_insufficient_data():
    with pytest.raises(ValueError):
        calculate_dcf([], 1e9, 0.10, 0.025, 5)
