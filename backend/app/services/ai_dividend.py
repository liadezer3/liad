from __future__ import annotations

import json
import os
from datetime import datetime

import requests

from app.services.market_data import FinancialDataset, MarketDataService


class DividendSafetyAIService:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def _extract_metric(self, dataset: FinancialDataset, metric_name: str, default: float = 0.0) -> list[float]:
        if dataset.balance_sheet.empty or metric_name not in dataset.balance_sheet.index:
            return []

        values: list[float] = []
        for col in dataset.balance_sheet.columns[:5]:
            raw = dataset.balance_sheet.at[metric_name, col]
            try:
                values.append(float(raw))
            except (TypeError, ValueError):
                values.append(default)
        return values

    def _heuristic_assessment(self, dataset: FinancialDataset) -> tuple[int, list[str]]:
        notes: list[str] = []
        score = 50

        total_debt = self._extract_metric(dataset, "Total Debt")
        total_equity = self._extract_metric(dataset, "Stockholders Equity")
        current_assets = self._extract_metric(dataset, "Current Assets")
        current_liabilities = self._extract_metric(dataset, "Current Liabilities")
        cash_and_equiv = self._extract_metric(dataset, "Cash And Cash Equivalents")

        if total_debt and total_equity and total_equity[0] > 0:
            debt_to_equity = total_debt[0] / total_equity[0]
            if debt_to_equity < 0.8:
                score += 15
                notes.append(f"Debt-to-equity is conservative at {debt_to_equity:.2f}.")
            elif debt_to_equity < 1.5:
                score += 5
                notes.append(f"Debt-to-equity is moderate at {debt_to_equity:.2f}.")
            else:
                score -= 15
                notes.append(f"Debt-to-equity is elevated at {debt_to_equity:.2f}.")

        if current_assets and current_liabilities and current_liabilities[0] > 0:
            current_ratio = current_assets[0] / current_liabilities[0]
            if current_ratio >= 1.5:
                score += 10
                notes.append(f"Current ratio of {current_ratio:.2f} supports near-term dividend resiliency.")
            elif current_ratio < 1:
                score -= 10
                notes.append(f"Current ratio of {current_ratio:.2f} suggests tighter liquidity coverage.")

        if cash_and_equiv and total_debt:
            debt_coverage = cash_and_equiv[0] / total_debt[0] if total_debt[0] > 0 else 1.0
            if debt_coverage >= 0.5:
                score += 10
                notes.append("Cash position covers a meaningful portion of debt obligations.")
            else:
                score -= 5
                notes.append("Cash position only covers a limited share of debt obligations.")

        score = max(0, min(100, score))
        return score, notes

    @staticmethod
    def _rating_from_score(score: int) -> str:
        if score >= 80:
            return "Very Safe"
        if score >= 65:
            return "Safe"
        if score >= 50:
            return "Borderline"
        if score >= 35:
            return "At Risk"
        return "Unsafe"

    def build_prompt(self, ticker: str, dataset: FinancialDataset, lookback_years: int) -> str:
        table = MarketDataService.dataframe_to_records(dataset.balance_sheet, max_columns=lookback_years)
        payload = {
            "ticker": ticker,
            "analysis_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "balance_sheet_history": table,
            "current_price": dataset.current_price,
            "dividend_yield": dataset.info.get("dividendYield"),
            "instruction": (
                "Evaluate dividend safety based on leverage trend, liquidity trend, "
                "and capital buffer quality. Return JSON with keys: score (0-100) and reasoning (array)."
            ),
        }
        return json.dumps(payload, indent=2)

    def _call_llm(self, prompt: str, fallback_score: int, fallback_notes: list[str]) -> tuple[int, list[str], str]:
        if not self.api_key:
            return fallback_score, fallback_notes, "heuristic"

        response = requests.post(
            f"{self.base_url.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=20,
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a careful dividend risk analyst."},
                    {"role": "user", "content": prompt},
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.2,
            },
        )
        response.raise_for_status()

        content = response.json()["choices"][0]["message"]["content"]
        parsed = json.loads(content)

        score = int(parsed.get("score", fallback_score))
        reasoning = parsed.get("reasoning", fallback_notes)
        if not isinstance(reasoning, list):
            reasoning = [str(reasoning)]

        score = max(0, min(100, score))
        reasoning = [str(item) for item in reasoning][:5]
        return score, reasoning, "llm"

    def analyze(self, ticker: str, dataset: FinancialDataset, lookback_years: int) -> dict:
        prompt = self.build_prompt(ticker=ticker, dataset=dataset, lookback_years=lookback_years)
        fallback_score, fallback_notes = self._heuristic_assessment(dataset)

        try:
            score, reasoning, source = self._call_llm(prompt, fallback_score, fallback_notes)
        except Exception as exc:
            score = fallback_score
            reasoning = fallback_notes + [f"AI call failed; fallback heuristic used ({exc.__class__.__name__})."]
            source = "heuristic"

        return {
            "ticker": ticker,
            "score": score,
            "rating": self._rating_from_score(score),
            "reasoning": reasoning,
            "prompt": prompt,
            "source": source,
        }
