import { LoadingState } from "../components/LoadingState";
import { MetricCard } from "../components/MetricCard";
import type { StockAnalysis } from "../types";
import { formatLargeCurrency, formatMultiple, formatPercent } from "../utils/format";

type DividendSafetyPageProps = {
  analysis: StockAnalysis | null;
};

export function DividendSafetyPage({ analysis }: DividendSafetyPageProps) {
  if (!analysis) {
    return <LoadingState message="Preparing dividend safety analysis..." />;
  }

  const { profile, dividend_safety: safety } = analysis;

  return (
    <section className="stacked-page">
      <div className="section-heading">
        <p className="eyebrow">{profile.ticker} dividend safety</p>
        <h2>AI prompt-driven balance sheet review</h2>
        <p>
          The backend builds a financial analyst prompt and scores dividend
          durability using historical leverage, liquidity, payout, and cash-flow
          coverage signals.
        </p>
      </div>

      <div className="metric-grid">
        <MetricCard
          label="Safety score"
          value={`${safety.score}/100`}
          detail={safety.rating}
          tone={safety.score >= 70 ? "positive" : "warning"}
        />
        <MetricCard
          label="FCF coverage"
          value={formatMultiple(safety.metrics.latest_fcf_dividend_coverage)}
          detail="latest fiscal year"
        />
        <MetricCard
          label="Payout ratio"
          value={formatPercent(safety.metrics.latest_payout_ratio)}
          detail="latest fiscal year"
        />
        <MetricCard
          label="Debt to equity"
          value={formatMultiple(safety.metrics.latest_debt_to_equity)}
          detail="latest fiscal year"
        />
      </div>

      <div className="two-column">
        <article className="data-card">
          <h3>Strengths</h3>
          <ul className="insight-list positive-list">
            {safety.strengths.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
        <article className="data-card">
          <h3>Risks to monitor</h3>
          <ul className="insight-list warning-list">
            {safety.risks.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
      </div>

      <article className="data-card">
        <h3>AI rationale</h3>
        <ol className="rationale-list">
          {safety.rationale.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ol>
      </article>

      <article className="data-card table-card">
        <h3>Historical balance sheet trend</h3>
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Year</th>
                <th>Total assets</th>
                <th>Total debt</th>
                <th>Cash</th>
                <th>Debt/equity</th>
                <th>Current ratio</th>
              </tr>
            </thead>
            <tbody>
              {profile.balance_sheets.map((sheet) => (
                <tr key={sheet.year}>
                  <td>{sheet.year}</td>
                  <td>{formatLargeCurrency(sheet.total_assets)}</td>
                  <td>{formatLargeCurrency(sheet.total_debt)}</td>
                  <td>{formatLargeCurrency(sheet.cash_and_equivalents)}</td>
                  <td>{formatMultiple(sheet.debt_to_equity)}</td>
                  <td>{formatMultiple(sheet.current_ratio)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </article>

      <article className="prompt-card">
        <div>
          <p className="eyebrow">Prompt layer</p>
          <h3>Generated analyst prompt</h3>
        </div>
        <pre>{safety.prompt}</pre>
      </article>
    </section>
  );
}
