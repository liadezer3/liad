import { FormEvent, useEffect, useState } from "react";

import { LoadingState } from "../components/LoadingState";
import { MetricCard } from "../components/MetricCard";
import type { AnalysisAssumptions, StockAnalysis } from "../types";
import { formatCurrency, formatLargeCurrency, formatPercent } from "../utils/format";

type ValuationPageProps = {
  analysis: StockAnalysis | null;
  assumptions: AnalysisAssumptions;
  isLoading: boolean;
  onUpdateAssumptions: (assumptions: AnalysisAssumptions) => Promise<void>;
};

type AssumptionInput = {
  key: keyof AnalysisAssumptions;
  label: string;
  step: number;
  percent?: boolean;
};

const assumptionInputs: AssumptionInput[] = [
  { key: "dcf_growth_rate", label: "DCF FCF growth", step: 0.005, percent: true },
  { key: "terminal_growth_rate", label: "Terminal growth", step: 0.005, percent: true },
  { key: "discount_rate", label: "Discount rate", step: 0.005, percent: true },
  { key: "ddm_growth_rate", label: "DDM dividend growth", step: 0.005, percent: true },
  { key: "required_return", label: "Required return", step: 0.005, percent: true },
  { key: "projection_years", label: "Projection years", step: 1 },
];

export function ValuationPage({
  analysis,
  assumptions,
  isLoading,
  onUpdateAssumptions,
}: ValuationPageProps) {
  const [draft, setDraft] = useState(assumptions);

  useEffect(() => {
    setDraft(assumptions);
  }, [assumptions]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await onUpdateAssumptions(draft);
  }

  if (!analysis) {
    return <LoadingState message="Preparing valuation model..." />;
  }

  const { valuation } = analysis;

  return (
    <section className="stacked-page">
      <div className="section-heading">
        <p className="eyebrow">{analysis.profile.ticker} valuation</p>
        <h2>DCF and dividend discount model</h2>
        <p>
          Adjust assumptions to test sensitivity across free-cash-flow growth,
          terminal value, dividend growth, and required return.
        </p>
      </div>

      <div className="valuation-layout">
        <form className="assumption-panel" onSubmit={handleSubmit}>
          <h3>Model assumptions</h3>
          {assumptionInputs.map((input) => (
            <label key={input.key}>
              <span>{input.label}</span>
              <input
                type="number"
                value={
                  input.percent
                    ? Number((draft[input.key] * 100).toFixed(2))
                    : draft[input.key]
                }
                step={input.percent ? input.step * 100 : input.step}
                onChange={(event) => {
                  const rawValue = Number(event.target.value);
                  setDraft((current) => ({
                    ...current,
                    [input.key]: input.percent ? rawValue / 100 : rawValue,
                  }));
                }}
              />
            </label>
          ))}
          <button type="submit" disabled={isLoading}>
            {isLoading ? "Recalculating..." : "Recalculate valuation"}
          </button>
        </form>

        <div className="valuation-results">
          <div className="metric-grid">
            <MetricCard
              label="DCF fair value"
              value={formatCurrency(valuation.dcf.fair_value_per_share)}
              detail={`${formatPercent(valuation.dcf.margin_of_safety)} margin`}
            />
            <MetricCard
              label="DDM fair value"
              value={formatCurrency(valuation.ddm.fair_value_per_share)}
              detail={`${formatPercent(valuation.ddm.margin_of_safety)} margin`}
            />
            <MetricCard
              label="Blended fair value"
              value={formatCurrency(valuation.blended_fair_value)}
              detail={`${formatPercent(valuation.blended_margin_of_safety)} margin`}
              tone={valuation.blended_margin_of_safety > 0 ? "positive" : "warning"}
            />
          </div>

          <article className="data-card">
            <h3>Projected DCF cash flows</h3>
            <div className="bar-list">
              {valuation.dcf.projected_cash_flows.map((cashFlow, index, cashFlows) => {
                const finalCashFlow = cashFlows[cashFlows.length - 1];

                return (
                  <div key={index} className="bar-row">
                    <span>Year {index + 1}</span>
                    <div>
                      <span
                        style={{
                          width: `${Math.min(100, (cashFlow / finalCashFlow) * 100)}%`,
                        }}
                      />
                    </div>
                    <strong>{formatLargeCurrency(cashFlow)}</strong>
                  </div>
                );
              })}
            </div>
            <p>
              Terminal value: {formatLargeCurrency(valuation.dcf.terminal_value)}.
              Enterprise value: {formatLargeCurrency(valuation.dcf.enterprise_value)}.
            </p>
          </article>
        </div>
      </div>
    </section>
  );
}
