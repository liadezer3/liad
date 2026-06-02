import type { AnalysisAssumptions, StockAnalysis } from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
    ...init,
  });

  if (!response.ok) {
    throw new Error(`API request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function fetchStockAnalysis(ticker: string): Promise<StockAnalysis> {
  return request<StockAnalysis>(`/api/stocks/${encodeURIComponent(ticker)}`);
}

export function analyzeStock(
  ticker: string,
  assumptions: AnalysisAssumptions,
): Promise<StockAnalysis> {
  return request<StockAnalysis>(`/api/stocks/${encodeURIComponent(ticker)}/analyze`, {
    method: "POST",
    body: JSON.stringify(assumptions),
  });
}
