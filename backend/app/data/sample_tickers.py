"""Bundled sample fixtures used as an offline fallback.

These mirror the real shape of the data the live provider returns so the
application is fully functional without network access. Figures are
illustrative approximations of well known dividend-growth companies and
should not be treated as investment advice.
"""

from __future__ import annotations

SAMPLE_TICKERS: dict[str, dict] = {
    "JNJ": {
        "ticker": "JNJ",
        "name": "Johnson & Johnson",
        "sector": "Healthcare",
        "industry": "Drug Manufacturers - General",
        "currency": "USD",
        "exchange": "NYSE",
        "summary": (
            "Johnson & Johnson researches, develops, manufactures and sells a "
            "broad range of healthcare products. It is a Dividend King with "
            "decades of consecutive dividend increases."
        ),
        "price": 152.40,
        "market_cap": 367_000_000_000,
        "shares_outstanding": 2_410_000_000,
        "beta": 0.55,
        "dividend_per_share": 4.96,
        "dividend_yield": 0.0326,
        "payout_ratio": 0.46,
        "five_year_dividend_growth": 0.055,
        "years_of_growth": 62,
        "eps": 9.92,
        "free_cash_flow": 18_000_000_000,
        "free_cash_flow_per_share": 7.47,
        "total_debt": 29_000_000_000,
        "total_cash": 25_000_000_000,
        "balance_sheets": [
            {"year": 2020, "total_assets": 174894, "total_liabilities": 111616, "total_equity": 63278, "current_assets": 51237, "current_liabilities": 42493, "cash_and_equivalents": 25185, "total_debt": 32635, "net_income": 14714, "operating_cash_flow": 23536, "free_cash_flow": 20000, "dividends_paid": 9882},
            {"year": 2021, "total_assets": 182018, "total_liabilities": 107995, "total_equity": 74023, "current_assets": 60979, "current_liabilities": 45226, "cash_and_equivalents": 31100, "total_debt": 33200, "net_income": 20878, "operating_cash_flow": 23394, "free_cash_flow": 19779, "dividends_paid": 10881},
            {"year": 2022, "total_assets": 187378, "total_liabilities": 110574, "total_equity": 76804, "current_assets": 55294, "current_liabilities": 55802, "cash_and_equivalents": 23519, "total_debt": 39000, "net_income": 17941, "operating_cash_flow": 21194, "free_cash_flow": 17000, "dividends_paid": 11760},
            {"year": 2023, "total_assets": 167558, "total_liabilities": 98777, "total_equity": 68781, "current_assets": 53620, "current_liabilities": 52793, "cash_and_equivalents": 21859, "total_debt": 29325, "net_income": 35153, "operating_cash_flow": 22791, "free_cash_flow": 18000, "dividends_paid": 11770},
        ],
    },
    "KO": {
        "ticker": "KO",
        "name": "The Coca-Cola Company",
        "sector": "Consumer Defensive",
        "industry": "Beverages - Non-Alcoholic",
        "currency": "USD",
        "exchange": "NYSE",
        "summary": (
            "The Coca-Cola Company manufactures, markets and sells beverage "
            "concentrates and syrups worldwide. A long standing Dividend King."
        ),
        "price": 61.20,
        "market_cap": 264_000_000_000,
        "shares_outstanding": 4_310_000_000,
        "beta": 0.58,
        "dividend_per_share": 1.94,
        "dividend_yield": 0.0317,
        "payout_ratio": 0.68,
        "five_year_dividend_growth": 0.035,
        "years_of_growth": 62,
        "eps": 2.85,
        "free_cash_flow": 9_500_000_000,
        "free_cash_flow_per_share": 2.20,
        "total_debt": 42_000_000_000,
        "total_cash": 12_000_000_000,
        "balance_sheets": [
            {"year": 2020, "total_assets": 87296, "total_liabilities": 66012, "total_equity": 21284, "current_assets": 19240, "current_liabilities": 14601, "cash_and_equivalents": 6795, "total_debt": 42763, "net_income": 7747, "operating_cash_flow": 9844, "free_cash_flow": 8670, "dividends_paid": 7047},
            {"year": 2021, "total_assets": 94354, "total_liabilities": 69494, "total_equity": 24860, "current_assets": 22545, "current_liabilities": 19950, "cash_and_equivalents": 9684, "total_debt": 40123, "net_income": 9771, "operating_cash_flow": 12625, "free_cash_flow": 11257, "dividends_paid": 7252},
            {"year": 2022, "total_assets": 92763, "total_liabilities": 66937, "total_equity": 25826, "current_assets": 22591, "current_liabilities": 19724, "cash_and_equivalents": 9519, "total_debt": 39149, "net_income": 9542, "operating_cash_flow": 11018, "free_cash_flow": 9532, "dividends_paid": 7616},
            {"year": 2023, "total_assets": 97703, "total_liabilities": 68741, "total_equity": 28962, "current_assets": 26732, "current_liabilities": 23571, "cash_and_equivalents": 9366, "total_debt": 42124, "net_income": 10714, "operating_cash_flow": 11599, "free_cash_flow": 9747, "dividends_paid": 8049},
        ],
    },
    "PG": {
        "ticker": "PG",
        "name": "The Procter & Gamble Company",
        "sector": "Consumer Defensive",
        "industry": "Household & Personal Products",
        "currency": "USD",
        "exchange": "NYSE",
        "summary": (
            "Procter & Gamble provides branded consumer packaged goods. It has "
            "raised its dividend for more than six decades."
        ),
        "price": 167.30,
        "market_cap": 394_000_000_000,
        "shares_outstanding": 2_356_000_000,
        "beta": 0.41,
        "dividend_per_share": 4.03,
        "dividend_yield": 0.0241,
        "payout_ratio": 0.62,
        "five_year_dividend_growth": 0.05,
        "years_of_growth": 68,
        "eps": 6.50,
        "free_cash_flow": 14_000_000_000,
        "free_cash_flow_per_share": 5.94,
        "total_debt": 33_000_000_000,
        "total_cash": 8_000_000_000,
        "balance_sheets": [
            {"year": 2020, "total_assets": 120700, "total_liabilities": 74987, "total_equity": 45713, "current_assets": 27987, "current_liabilities": 32976, "cash_and_equivalents": 16181, "total_debt": 31634, "net_income": 13027, "operating_cash_flow": 17403, "free_cash_flow": 14352, "dividends_paid": 7789},
            {"year": 2021, "total_assets": 119307, "total_liabilities": 72651, "total_equity": 46656, "current_assets": 23439, "current_liabilities": 33132, "cash_and_equivalents": 10288, "total_debt": 30221, "net_income": 14306, "operating_cash_flow": 18371, "free_cash_flow": 15800, "dividends_paid": 8263},
            {"year": 2022, "total_assets": 117208, "total_liabilities": 70554, "total_equity": 46654, "current_assets": 21653, "current_liabilities": 34621, "cash_and_equivalents": 7214, "total_debt": 32430, "net_income": 14742, "operating_cash_flow": 16723, "free_cash_flow": 13634, "dividends_paid": 8770},
            {"year": 2023, "total_assets": 120829, "total_liabilities": 73276, "total_equity": 47553, "current_assets": 21097, "current_liabilities": 35756, "cash_and_equivalents": 8246, "total_debt": 32913, "net_income": 14738, "operating_cash_flow": 16848, "free_cash_flow": 13832, "dividends_paid": 9088},
        ],
    },
    "PEP": {
        "ticker": "PEP",
        "name": "PepsiCo, Inc.",
        "sector": "Consumer Defensive",
        "industry": "Beverages - Non-Alcoholic",
        "currency": "USD",
        "exchange": "NASDAQ",
        "summary": (
            "PepsiCo manufactures, markets, distributes and sells beverages and "
            "convenient foods worldwide. A Dividend King with a diversified "
            "snacks-and-drinks portfolio."
        ),
        "price": 171.50,
        "market_cap": 235_000_000_000,
        "shares_outstanding": 1_374_000_000,
        "beta": 0.52,
        "dividend_per_share": 5.42,
        "dividend_yield": 0.0316,
        "payout_ratio": 0.71,
        "five_year_dividend_growth": 0.07,
        "years_of_growth": 52,
        "eps": 7.62,
        "free_cash_flow": 8_000_000_000,
        "free_cash_flow_per_share": 5.82,
        "total_debt": 44_000_000_000,
        "total_cash": 9_000_000_000,
        "balance_sheets": [
            {"year": 2020, "total_assets": 92918, "total_liabilities": 79366, "total_equity": 13552, "current_assets": 23001, "current_liabilities": 23372, "cash_and_equivalents": 8185, "total_debt": 44034, "net_income": 7120, "operating_cash_flow": 10613, "free_cash_flow": 6402, "dividends_paid": 5509},
            {"year": 2021, "total_assets": 92377, "total_liabilities": 76226, "total_equity": 16151, "current_assets": 21783, "current_liabilities": 26220, "cash_and_equivalents": 5596, "total_debt": 40370, "net_income": 7618, "operating_cash_flow": 11616, "free_cash_flow": 7000, "dividends_paid": 5815},
            {"year": 2022, "total_assets": 92187, "total_liabilities": 74939, "total_equity": 17248, "current_assets": 21916, "current_liabilities": 27083, "cash_and_equivalents": 4954, "total_debt": 39096, "net_income": 8910, "operating_cash_flow": 10811, "free_cash_flow": 5600, "dividends_paid": 6164},
            {"year": 2023, "total_assets": 100495, "total_liabilities": 81857, "total_equity": 18638, "current_assets": 24515, "current_liabilities": 31354, "cash_and_equivalents": 9711, "total_debt": 44159, "net_income": 9074, "operating_cash_flow": 13442, "free_cash_flow": 8000, "dividends_paid": 6682},
        ],
    },
    "MSFT": {
        "ticker": "MSFT",
        "name": "Microsoft Corporation",
        "sector": "Technology",
        "industry": "Software - Infrastructure",
        "currency": "USD",
        "exchange": "NASDAQ",
        "summary": (
            "Microsoft develops and supports software, services, devices and "
            "solutions worldwide. A younger but fast-growing dividend payer."
        ),
        "price": 415.20,
        "market_cap": 3_086_000_000_000,
        "shares_outstanding": 7_434_000_000,
        "beta": 0.90,
        "dividend_per_share": 3.00,
        "dividend_yield": 0.0072,
        "payout_ratio": 0.25,
        "five_year_dividend_growth": 0.10,
        "years_of_growth": 22,
        "eps": 11.80,
        "free_cash_flow": 63_000_000_000,
        "free_cash_flow_per_share": 8.47,
        "total_debt": 47_000_000_000,
        "total_cash": 81_000_000_000,
        "balance_sheets": [
            {"year": 2020, "total_assets": 301311, "total_liabilities": 183007, "total_equity": 118304, "current_assets": 181915, "current_liabilities": 72310, "cash_and_equivalents": 13576, "total_debt": 70998, "net_income": 44281, "operating_cash_flow": 60675, "free_cash_flow": 45234, "dividends_paid": 15137},
            {"year": 2021, "total_assets": 333779, "total_liabilities": 191791, "total_equity": 141988, "current_assets": 184406, "current_liabilities": 88657, "cash_and_equivalents": 14224, "total_debt": 67775, "net_income": 61271, "operating_cash_flow": 76740, "free_cash_flow": 56118, "dividends_paid": 16521},
            {"year": 2022, "total_assets": 364840, "total_liabilities": 198298, "total_equity": 166542, "current_assets": 169684, "current_liabilities": 95082, "cash_and_equivalents": 13931, "total_debt": 61270, "net_income": 72738, "operating_cash_flow": 89035, "free_cash_flow": 65149, "dividends_paid": 18135},
            {"year": 2023, "total_assets": 411976, "total_liabilities": 205753, "total_equity": 206223, "current_assets": 184257, "current_liabilities": 104149, "cash_and_equivalents": 34704, "total_debt": 47237, "net_income": 72361, "operating_cash_flow": 87582, "free_cash_flow": 59475, "dividends_paid": 19800},
        ],
    },
}


def list_sample_tickers() -> list[dict]:
    """Return a lightweight directory of available sample tickers."""
    return [
        {
            "ticker": data["ticker"],
            "name": data["name"],
            "sector": data["sector"],
            "dividend_yield": data["dividend_yield"],
        }
        for data in SAMPLE_TICKERS.values()
    ]
