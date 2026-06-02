import { useEffect } from "react";
import { useParams } from "react-router-dom";
import { useTicker } from "../context/TickerContext.jsx";

// Ensures the ticker referenced in the URL is loaded into shared context,
// e.g. on a hard refresh or when navigating straight to a deep link.
export function useActiveTicker() {
  const { symbol: urlSymbol } = useParams();
  const { detail, symbol, loading, error, loadTicker } = useTicker();

  useEffect(() => {
    if (urlSymbol && urlSymbol.toUpperCase() !== symbol) {
      loadTicker(urlSymbol);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [urlSymbol]);

  const ready = detail && detail.ticker?.toUpperCase() === urlSymbol?.toUpperCase();
  return { detail: ready ? detail : null, loading, error, symbol: urlSymbol };
}
