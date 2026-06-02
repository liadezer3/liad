import { MetricCard } from "../components/MetricCard";
import { TickerSearch } from "../components/TickerSearch";
import type { StockAnalysis } from "../types";
import { formatCurrency, formatPercent } from "../utils/format";

type OverviewPageProps = {
  analysis: StockAnalysis | null;
  ticker: string;
  isLoading: boolean;
  error: string | null;
  onSearch: (ticker: string) => Promise<void>;
};

export function OverviewPage({
  analysis,
  ticker,
  isLoading,
  error,
  onSearch,
}: OverviewPageProps) {
  const profile = analysis?.profile;

  return (
    <section className="page-grid">
      <div className="hero-card">
        <p className="eyebrow">Fundamentals + valuation + AI prompt layer</p>
        <h2>Find dividend growers with durable cash-flow coverage.</h2>
        <p>
          Enter a ticker to fetch profile data, calculate intrinsic value ranges,
          and evaluate historical balance sheets for dividend safety.
        </p>
        <TickerSearch ticker={ticker} isLoading={isLoading} onSearch={onSearch} />
        {error ? <p className="error-message">{error}</p> : null}
      </div>

      {profile && analysis ? (
        <>
          <article className="company-card">
            <div>
              <p className="eyebrow">{profile.ticker}</p>
              <h3>{profile.company_name}</h3>
              <p>{profile.description}</p>
            </div>
            <div className="tag-row">
              <span>{profile.sector}</span>
              <span>{profile.industry}</span>
              <span>Beta {profile.beta.toFixed(2)}</span>
            </div>
          </article>

          <div className="metric-grid">
            <MetricCard label="Price" value={formatCurrency(profile.price)} />
            <MetricCard
              label="Dividend yield"
              value={formatPercent(profile.dividend_yield)}
              detail={`${formatCurrency(profile.annual_dividend)} annual dividend`}
              tone="positive"
            />
            <MetricCard
              label="Blended fair value"
              value={formatCurrency(analysis.valuation.blended_fair_value)}
              detail={`${formatPercent(
                analysis.valuation.blended_margin_of_safety,
              )} margin of safety`}
              tone={
                analysis.valuation.blended_margin_of_safety > 0 ? "positive" : "warning"
              }
            />
            <MetricCard
              label="Dividend safety"
              value={`${analysis.dividend_safety.score}/100`}
              detail={analysis.dividend_safety.rating}
              tone={analysis.dividend_safety.score >= 70 ? "positive" : "warning"}
            />
          </div>
        </>
      ) : null}
    </section>
  );
}
