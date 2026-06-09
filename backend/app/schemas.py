from pydantic import BaseModel, Field


class DCFRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)
    discount_rate: float = Field(0.10, ge=0.01, le=0.30)
    terminal_growth_rate: float = Field(0.025, ge=0.0, le=0.10)
    projection_years: int = Field(5, ge=3, le=10)


class DDMRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)
    required_return: float = Field(0.09, ge=0.01, le=0.30)
    dividend_growth_rate: float | None = Field(None, ge=0.0, le=0.20)


class DividendSafetyRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)


class StockQuote(BaseModel):
    ticker: str
    name: str
    sector: str | None
    industry: str | None
    current_price: float | None
    dividend_yield: float | None
    dividend_rate: float | None
    payout_ratio: float | None
    trailing_pe: float | None
    market_cap: float | None
    fifty_two_week_high: float | None
    fifty_two_week_low: float | None


class DCFResult(BaseModel):
    ticker: str
    intrinsic_value_per_share: float
    current_price: float | None
    upside_pct: float | None
    projected_fcf: list[float]
    assumptions: dict


class DDMResult(BaseModel):
    ticker: str
    fair_value_per_share: float
    current_price: float | None
    upside_pct: float | None
    annual_dividend: float
    growth_rate_used: float
    required_return: float


class DividendSafetyResult(BaseModel):
    ticker: str
    safety_score: int = Field(..., ge=0, le=100)
    rating: str
    summary: str
    factors: list[dict]
    ai_powered: bool
    balance_sheet_highlights: dict


class JobSearchRequest(BaseModel):
    query: str = Field("software engineer", min_length=1, max_length=120)
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    location_label: str | None = Field(None, max_length=120)
    radius_miles: int = Field(50, ge=5, le=250)
    include_remote: bool = True


class JobListing(BaseModel):
    id: str
    title: str
    company: str
    location: str
    source: str
    source_url: str
    salary_min: int | None
    salary_max: int | None
    salary_currency: str = "USD"
    rating: float = Field(..., ge=0, le=5)
    job_type: str
    remote: bool
    distance_miles: float | None
    posted_at: str
    summary: str


class JobGroup(BaseModel):
    title: str
    location: str
    average_rating: float
    highest_salary: int | None
    jobs: list[JobListing]


class JobSearchResult(BaseModel):
    query: str
    location_label: str
    sources_scanned: list[str]
    total_results: int
    groups: list[JobGroup]
