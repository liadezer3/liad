from fastapi import APIRouter
from app.models.stock import DCFInput, DCFResult, DDMInput, DDMResult
from app.services.stock_service import compute_dcf, compute_ddm

router = APIRouter(prefix="/api/valuation", tags=["Valuation"])


@router.post("/dcf", response_model=DCFResult)
def dcf_valuation(body: DCFInput):
    """Compute Discounted Cash Flow intrinsic value for a stock."""
    return compute_dcf(
        symbol=body.ticker,
        discount_rate=body.discount_rate,
        terminal_growth_rate=body.terminal_growth_rate,
        projection_years=body.projection_years,
    )


@router.post("/ddm", response_model=DDMResult)
def ddm_valuation(body: DDMInput):
    """Compute Dividend Discount Model intrinsic value for a stock."""
    return compute_ddm(
        symbol=body.ticker,
        required_rate=body.required_rate_of_return,
        dividend_growth_override=body.dividend_growth_rate,
        model_type=body.model_type,
        high_growth_rate=body.high_growth_rate,
        high_growth_years=body.high_growth_years or 5,
    )
