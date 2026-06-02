from __future__ import annotations

from copy import deepcopy

from app.models import (
    BalanceSheetSnapshot,
    CashFlowSnapshot,
    DividendHistoryPoint,
    StockProfile,
)


_SAMPLE_STOCKS: dict[str, StockProfile] = {
    "MSFT": StockProfile(
        ticker="MSFT",
        company_name="Microsoft Corporation",
        sector="Technology",
        industry="Software - Infrastructure",
        currency="USD",
        price=425.00,
        shares_outstanding=7_430_000_000,
        annual_dividend=3.32,
        beta=0.89,
        description=(
            "Microsoft develops cloud, productivity, operating system, gaming, "
            "and AI infrastructure products for enterprise and consumer markets."
        ),
        balance_sheets=[
            BalanceSheetSnapshot(
                year=2020,
                total_assets=301_311_000_000,
                total_liabilities=183_007_000_000,
                shareholders_equity=118_304_000_000,
                cash_and_equivalents=136_527_000_000,
                total_debt=70_998_000_000,
                current_assets=181_915_000_000,
                current_liabilities=72_310_000_000,
            ),
            BalanceSheetSnapshot(
                year=2021,
                total_assets=333_779_000_000,
                total_liabilities=191_791_000_000,
                shareholders_equity=141_988_000_000,
                cash_and_equivalents=130_334_000_000,
                total_debt=67_775_000_000,
                current_assets=184_406_000_000,
                current_liabilities=88_657_000_000,
            ),
            BalanceSheetSnapshot(
                year=2022,
                total_assets=364_840_000_000,
                total_liabilities=198_298_000_000,
                shareholders_equity=166_542_000_000,
                cash_and_equivalents=104_749_000_000,
                total_debt=61_270_000_000,
                current_assets=169_684_000_000,
                current_liabilities=95_082_000_000,
            ),
            BalanceSheetSnapshot(
                year=2023,
                total_assets=411_976_000_000,
                total_liabilities=205_753_000_000,
                shareholders_equity=206_223_000_000,
                cash_and_equivalents=111_262_000_000,
                total_debt=59_965_000_000,
                current_assets=184_257_000_000,
                current_liabilities=104_149_000_000,
            ),
            BalanceSheetSnapshot(
                year=2024,
                total_assets=512_163_000_000,
                total_liabilities=243_686_000_000,
                shareholders_equity=268_477_000_000,
                cash_and_equivalents=75_531_000_000,
                total_debt=67_127_000_000,
                current_assets=159_734_000_000,
                current_liabilities=125_286_000_000,
            ),
        ],
        cash_flows=[
            CashFlowSnapshot(
                year=2020,
                operating_cash_flow=60_675_000_000,
                capital_expenditures=15_441_000_000,
                dividends_paid=15_137_000_000,
                interest_expense=2_591_000_000,
                operating_income=52_959_000_000,
                net_income=44_281_000_000,
            ),
            CashFlowSnapshot(
                year=2021,
                operating_cash_flow=76_740_000_000,
                capital_expenditures=20_622_000_000,
                dividends_paid=16_521_000_000,
                interest_expense=2_346_000_000,
                operating_income=69_916_000_000,
                net_income=61_271_000_000,
            ),
            CashFlowSnapshot(
                year=2022,
                operating_cash_flow=89_035_000_000,
                capital_expenditures=23_886_000_000,
                dividends_paid=18_552_000_000,
                interest_expense=2_063_000_000,
                operating_income=83_383_000_000,
                net_income=72_738_000_000,
            ),
            CashFlowSnapshot(
                year=2023,
                operating_cash_flow=87_582_000_000,
                capital_expenditures=28_107_000_000,
                dividends_paid=20_226_000_000,
                interest_expense=1_968_000_000,
                operating_income=88_523_000_000,
                net_income=72_361_000_000,
            ),
            CashFlowSnapshot(
                year=2024,
                operating_cash_flow=118_548_000_000,
                capital_expenditures=44_477_000_000,
                dividends_paid=21_771_000_000,
                interest_expense=2_935_000_000,
                operating_income=109_433_000_000,
                net_income=88_136_000_000,
            ),
        ],
        dividend_history=[
            DividendHistoryPoint(year=2020, dividend_per_share=2.04),
            DividendHistoryPoint(year=2021, dividend_per_share=2.24),
            DividendHistoryPoint(year=2022, dividend_per_share=2.48),
            DividendHistoryPoint(year=2023, dividend_per_share=2.72),
            DividendHistoryPoint(year=2024, dividend_per_share=3.00),
            DividendHistoryPoint(year=2025, dividend_per_share=3.32),
        ],
    ),
    "KO": StockProfile(
        ticker="KO",
        company_name="The Coca-Cola Company",
        sector="Consumer Defensive",
        industry="Beverages - Non-Alcoholic",
        currency="USD",
        price=63.00,
        shares_outstanding=4_310_000_000,
        annual_dividend=1.94,
        beta=0.58,
        description=(
            "The Coca-Cola Company owns a global portfolio of sparkling, water, "
            "sports drink, coffee, tea, juice, and nutrition brands."
        ),
        balance_sheets=[
            BalanceSheetSnapshot(
                year=2020,
                total_assets=87_296_000_000,
                total_liabilities=66_012_000_000,
                shareholders_equity=21_284_000_000,
                cash_and_equivalents=11_196_000_000,
                total_debt=40_125_000_000,
                current_assets=19_240_000_000,
                current_liabilities=14_601_000_000,
            ),
            BalanceSheetSnapshot(
                year=2021,
                total_assets=94_354_000_000,
                total_liabilities=69_494_000_000,
                shareholders_equity=24_860_000_000,
                cash_and_equivalents=12_625_000_000,
                total_debt=41_344_000_000,
                current_assets=22_545_000_000,
                current_liabilities=19_950_000_000,
            ),
            BalanceSheetSnapshot(
                year=2022,
                total_assets=92_763_000_000,
                total_liabilities=68_284_000_000,
                shareholders_equity=24_479_000_000,
                cash_and_equivalents=11_018_000_000,
                total_debt=39_743_000_000,
                current_assets=22_077_000_000,
                current_liabilities=19_724_000_000,
            ),
            BalanceSheetSnapshot(
                year=2023,
                total_assets=97_703_000_000,
                total_liabilities=71_281_000_000,
                shareholders_equity=26_422_000_000,
                cash_and_equivalents=12_798_000_000,
                total_debt=42_763_000_000,
                current_assets=24_672_000_000,
                current_liabilities=23_571_000_000,
            ),
            BalanceSheetSnapshot(
                year=2024,
                total_assets=102_410_000_000,
                total_liabilities=74_900_000_000,
                shareholders_equity=27_510_000_000,
                cash_and_equivalents=13_250_000_000,
                total_debt=43_100_000_000,
                current_assets=25_100_000_000,
                current_liabilities=22_800_000_000,
            ),
        ],
        cash_flows=[
            CashFlowSnapshot(
                year=2020,
                operating_cash_flow=9_844_000_000,
                capital_expenditures=1_177_000_000,
                dividends_paid=7_047_000_000,
                interest_expense=1_437_000_000,
                operating_income=9_231_000_000,
                net_income=7_747_000_000,
            ),
            CashFlowSnapshot(
                year=2021,
                operating_cash_flow=12_625_000_000,
                capital_expenditures=1_367_000_000,
                dividends_paid=7_252_000_000,
                interest_expense=1_597_000_000,
                operating_income=10_308_000_000,
                net_income=9_771_000_000,
            ),
            CashFlowSnapshot(
                year=2022,
                operating_cash_flow=11_018_000_000,
                capital_expenditures=1_484_000_000,
                dividends_paid=7_606_000_000,
                interest_expense=1_460_000_000,
                operating_income=12_248_000_000,
                net_income=9_542_000_000,
            ),
            CashFlowSnapshot(
                year=2023,
                operating_cash_flow=11_599_000_000,
                capital_expenditures=1_852_000_000,
                dividends_paid=7_955_000_000,
                interest_expense=1_527_000_000,
                operating_income=13_209_000_000,
                net_income=10_714_000_000,
            ),
            CashFlowSnapshot(
                year=2024,
                operating_cash_flow=12_050_000_000,
                capital_expenditures=1_900_000_000,
                dividends_paid=8_250_000_000,
                interest_expense=1_650_000_000,
                operating_income=13_900_000_000,
                net_income=11_100_000_000,
            ),
        ],
        dividend_history=[
            DividendHistoryPoint(year=2020, dividend_per_share=1.64),
            DividendHistoryPoint(year=2021, dividend_per_share=1.68),
            DividendHistoryPoint(year=2022, dividend_per_share=1.76),
            DividendHistoryPoint(year=2023, dividend_per_share=1.84),
            DividendHistoryPoint(year=2024, dividend_per_share=1.94),
            DividendHistoryPoint(year=2025, dividend_per_share=2.04),
        ],
    ),
    "JNJ": StockProfile(
        ticker="JNJ",
        company_name="Johnson & Johnson",
        sector="Healthcare",
        industry="Drug Manufacturers - General",
        currency="USD",
        price=148.00,
        shares_outstanding=2_410_000_000,
        annual_dividend=4.96,
        beta=0.52,
        description=(
            "Johnson & Johnson develops pharmaceuticals and medical technology "
            "products serving hospitals, clinicians, and patients worldwide."
        ),
        balance_sheets=[
            BalanceSheetSnapshot(
                year=2020,
                total_assets=174_894_000_000,
                total_liabilities=111_616_000_000,
                shareholders_equity=63_278_000_000,
                cash_and_equivalents=25_185_000_000,
                total_debt=32_635_000_000,
                current_assets=51_237_000_000,
                current_liabilities=42_493_000_000,
            ),
            BalanceSheetSnapshot(
                year=2021,
                total_assets=182_018_000_000,
                total_liabilities=107_995_000_000,
                shareholders_equity=74_023_000_000,
                cash_and_equivalents=31_608_000_000,
                total_debt=33_025_000_000,
                current_assets=60_979_000_000,
                current_liabilities=45_226_000_000,
            ),
            BalanceSheetSnapshot(
                year=2022,
                total_assets=187_378_000_000,
                total_liabilities=111_574_000_000,
                shareholders_equity=75_804_000_000,
                cash_and_equivalents=23_530_000_000,
                total_debt=39_251_000_000,
                current_assets=58_544_000_000,
                current_liabilities=55_352_000_000,
            ),
            BalanceSheetSnapshot(
                year=2023,
                total_assets=167_558_000_000,
                total_liabilities=98_100_000_000,
                shareholders_equity=69_458_000_000,
                cash_and_equivalents=23_262_000_000,
                total_debt=30_583_000_000,
                current_assets=49_964_000_000,
                current_liabilities=43_860_000_000,
            ),
            BalanceSheetSnapshot(
                year=2024,
                total_assets=180_104_000_000,
                total_liabilities=103_760_000_000,
                shareholders_equity=76_344_000_000,
                cash_and_equivalents=24_900_000_000,
                total_debt=31_700_000_000,
                current_assets=53_800_000_000,
                current_liabilities=44_200_000_000,
            ),
        ],
        cash_flows=[
            CashFlowSnapshot(
                year=2020,
                operating_cash_flow=23_536_000_000,
                capital_expenditures=3_347_000_000,
                dividends_paid=10_481_000_000,
                interest_expense=1_088_000_000,
                operating_income=21_588_000_000,
                net_income=14_714_000_000,
            ),
            CashFlowSnapshot(
                year=2021,
                operating_cash_flow=23_410_000_000,
                capital_expenditures=3_489_000_000,
                dividends_paid=10_852_000_000,
                interest_expense=1_230_000_000,
                operating_income=24_508_000_000,
                net_income=20_878_000_000,
            ),
            CashFlowSnapshot(
                year=2022,
                operating_cash_flow=21_194_000_000,
                capital_expenditures=4_009_000_000,
                dividends_paid=11_682_000_000,
                interest_expense=1_335_000_000,
                operating_income=24_844_000_000,
                net_income=17_941_000_000,
            ),
            CashFlowSnapshot(
                year=2023,
                operating_cash_flow=22_855_000_000,
                capital_expenditures=4_683_000_000,
                dividends_paid=11_868_000_000,
                interest_expense=1_643_000_000,
                operating_income=21_948_000_000,
                net_income=35_153_000_000,
            ),
            CashFlowSnapshot(
                year=2024,
                operating_cash_flow=23_500_000_000,
                capital_expenditures=4_750_000_000,
                dividends_paid=12_150_000_000,
                interest_expense=1_500_000_000,
                operating_income=24_100_000_000,
                net_income=21_800_000_000,
            ),
        ],
        dividend_history=[
            DividendHistoryPoint(year=2020, dividend_per_share=4.04),
            DividendHistoryPoint(year=2021, dividend_per_share=4.19),
            DividendHistoryPoint(year=2022, dividend_per_share=4.45),
            DividendHistoryPoint(year=2023, dividend_per_share=4.70),
            DividendHistoryPoint(year=2024, dividend_per_share=4.96),
            DividendHistoryPoint(year=2025, dividend_per_share=5.20),
        ],
    ),
}


def get_sample_stock(ticker: str) -> StockProfile:
    symbol = ticker.upper()
    if symbol in _SAMPLE_STOCKS:
        return deepcopy(_SAMPLE_STOCKS[symbol])

    template = deepcopy(_SAMPLE_STOCKS["MSFT"])
    return template.model_copy(
        update={
            "ticker": symbol,
            "company_name": f"{symbol} Sample Dividend Company",
            "sector": "Industrials",
            "industry": "Diversified Operations",
            "price": 84.0,
            "annual_dividend": 2.6,
            "beta": 0.95,
            "description": (
                "Synthetic sample data is shown because no live data provider is "
                "configured for this ticker. Use an Alpha Vantage API key for "
                "live quote and overview enrichment."
            ),
        }
    )


def available_sample_tickers() -> list[str]:
    return sorted(_SAMPLE_STOCKS)
