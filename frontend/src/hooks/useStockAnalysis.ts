import { useCallback, useEffect, useState } from "react";

import { analyzeStock, fetchStockAnalysis } from "../api";
import type { AnalysisAssumptions, StockAnalysis } from "../types";

const defaultAssumptions: AnalysisAssumptions = {
  dcf_growth_rate: 0.06,
  terminal_growth_rate: 0.025,
  discount_rate: 0.09,
  ddm_growth_rate: 0.045,
  required_return: 0.085,
  projection_years: 5,
};

export type UseStockAnalysisResult = {
  analysis: StockAnalysis | null;
  assumptions: AnalysisAssumptions;
  ticker: string;
  isLoading: boolean;
  error: string | null;
  loadTicker: (nextTicker: string) => Promise<void>;
  updateAssumptions: (nextAssumptions: AnalysisAssumptions) => Promise<void>;
};

export function useStockAnalysis(initialTicker = "MSFT"): UseStockAnalysisResult {
  const [ticker, setTicker] = useState(initialTicker);
  const [analysis, setAnalysis] = useState<StockAnalysis | null>(null);
  const [assumptions, setAssumptions] = useState<AnalysisAssumptions>(defaultAssumptions);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadTicker = useCallback(async (nextTicker: string) => {
    const normalizedTicker = nextTicker.trim().toUpperCase();

    if (!normalizedTicker) {
      setError("Enter a ticker symbol.");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const nextAnalysis = await fetchStockAnalysis(normalizedTicker);
      setTicker(normalizedTicker);
      setAnalysis(nextAnalysis);
      setAssumptions(nextAnalysis.valuation.assumptions);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Unable to load stock analysis.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateAssumptions = useCallback(
    async (nextAssumptions: AnalysisAssumptions) => {
      setIsLoading(true);
      setError(null);

      try {
        const nextAnalysis = await analyzeStock(ticker, nextAssumptions);
        setAnalysis(nextAnalysis);
        setAssumptions(nextAnalysis.valuation.assumptions);
      } catch (caughtError) {
        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "Unable to calculate valuation.",
        );
      } finally {
        setIsLoading(false);
      }
    },
    [ticker],
  );

  useEffect(() => {
    void loadTicker(initialTicker);
  }, [initialTicker, loadTicker]);

  return {
    analysis,
    assumptions,
    ticker,
    isLoading,
    error,
    loadTicker,
    updateAssumptions,
  };
}
