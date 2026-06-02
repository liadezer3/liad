from __future__ import annotations

import httpx

from app.models import StockProfile
from app.sample_data import get_sample_stock
from app.settings import Settings


class MarketDataService:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def get_profile(self, ticker: str) -> StockProfile:
        profile = get_sample_stock(ticker)

        if not self.settings.alpha_vantage_api_key:
            return profile

        try:
            return await self._enrich_from_alpha_vantage(profile)
        except httpx.HTTPError:
            return profile

    async def _enrich_from_alpha_vantage(self, profile: StockProfile) -> StockProfile:
        base_url = "https://www.alphavantage.co/query"
        params = {
            "function": "OVERVIEW",
            "symbol": profile.ticker,
            "apikey": self.settings.alpha_vantage_api_key,
        }

        async with httpx.AsyncClient(timeout=8) as client:
            overview_response = await client.get(base_url, params=params)
            overview_response.raise_for_status()
            overview = overview_response.json()

            quote_response = await client.get(
                base_url,
                params={
                    "function": "GLOBAL_QUOTE",
                    "symbol": profile.ticker,
                    "apikey": self.settings.alpha_vantage_api_key,
                },
            )
            quote_response.raise_for_status()
            quote = quote_response.json().get("Global Quote", {})

        if not overview or "Symbol" not in overview:
            return profile

        price = float(quote.get("05. price") or profile.price)
        annual_dividend = float(overview.get("DividendPerShare") or profile.annual_dividend)
        shares_outstanding = float(
            overview.get("SharesOutstanding") or profile.shares_outstanding
        )
        beta = float(overview.get("Beta") or profile.beta)

        return profile.model_copy(
            update={
                "company_name": overview.get("Name") or profile.company_name,
                "sector": overview.get("Sector") or profile.sector,
                "industry": overview.get("Industry") or profile.industry,
                "price": price,
                "annual_dividend": annual_dividend,
                "shares_outstanding": shares_outstanding,
                "beta": beta,
                "description": overview.get("Description") or profile.description,
            }
        )
