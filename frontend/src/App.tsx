import { Route, Routes } from "react-router-dom";

import { Layout } from "./components/Layout";
import { useStockAnalysis } from "./hooks/useStockAnalysis";
import { DividendSafetyPage } from "./pages/DividendSafetyPage";
import { MethodologyPage } from "./pages/MethodologyPage";
import { OverviewPage } from "./pages/OverviewPage";
import { ValuationPage } from "./pages/ValuationPage";

export function App() {
  const {
    analysis,
    assumptions,
    ticker,
    isLoading,
    error,
    loadTicker,
    updateAssumptions,
  } = useStockAnalysis();

  return (
    <Routes>
      <Route element={<Layout />}>
        <Route
          index
          element={
            <OverviewPage
              analysis={analysis}
              ticker={ticker}
              isLoading={isLoading}
              error={error}
              onSearch={loadTicker}
            />
          }
        />
        <Route
          path="valuation"
          element={
            <ValuationPage
              analysis={analysis}
              assumptions={assumptions}
              isLoading={isLoading}
              onUpdateAssumptions={updateAssumptions}
            />
          }
        />
        <Route path="safety" element={<DividendSafetyPage analysis={analysis} />} />
        <Route path="methodology" element={<MethodologyPage />} />
      </Route>
    </Routes>
  );
}
