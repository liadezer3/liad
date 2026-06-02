import { createContext, useCallback, useContext, useMemo, useState } from "react";
import { api } from "../api/client.js";

// Shared state for the currently-selected ticker so the Overview, Valuation
// and Analysis pages all operate on the same company without re-fetching.
const TickerContext = createContext(null);

export function TickerProvider({ children }) {
  const [symbol, setSymbol] = useState("");
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadTicker = async (raw) => {
    const sym = (raw || "").trim().toUpperCase();
    if (!sym) return null;
    setLoading(true);
    setError(null);
    setSymbol(sym);
    try {
      const data = await api.ticker(sym);
      setDetail(data);
      return data;
    } catch (err) {
      setError(err.message);
      setDetail(null);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const value = useMemo(
    () => ({ symbol, detail, loading, error, loadTicker }),
    [symbol, detail, loading, error]
  );

  return <TickerContext.Provider value={value}>{children}</TickerContext.Provider>;
}

export function useTicker() {
  const ctx = useContext(TickerContext);
  if (!ctx) throw new Error("useTicker must be used within a TickerProvider");
  return ctx;
}
