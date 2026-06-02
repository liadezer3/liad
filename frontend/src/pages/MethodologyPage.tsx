export function MethodologyPage() {
  return (
    <section className="stacked-page">
      <div className="section-heading">
        <p className="eyebrow">How the evaluator works</p>
        <h2>Transparent assumptions for dividend growth research</h2>
        <p>
          The application separates presentation from financial algorithms so
          analysts can review, test, and evolve the models independently.
        </p>
      </div>

      <div className="methodology-grid">
        <article className="data-card">
          <span className="step-number">01</span>
          <h3>Ticker details</h3>
          <p>
            The backend loads a stock profile, current price, dividend, share
            count, and historical financial snapshots. Sample data is available
            offline, and Alpha Vantage can enrich quote and overview fields when
            an API key is configured.
          </p>
        </article>

        <article className="data-card">
          <span className="step-number">02</span>
          <h3>Discounted Cash Flow</h3>
          <p>
            Latest free cash flow is projected for the selected period, discounted
            at the required rate, and combined with a terminal value. Net debt is
            subtracted before dividing by shares outstanding.
          </p>
        </article>

        <article className="data-card">
          <span className="step-number">03</span>
          <h3>Dividend Discount Model</h3>
          <p>
            The DDM estimates value from next year's dividend divided by the
            spread between required return and perpetual dividend growth. It is
            most useful for mature dividend payers with stable payout policies.
          </p>
        </article>

        <article className="data-card">
          <span className="step-number">04</span>
          <h3>AI prompt safety layer</h3>
          <p>
            A generated prompt frames the company like an equity research task.
            The service then applies deterministic scoring to the same prompt
            inputs: cash-flow coverage, payout ratio, leverage, liquidity,
            interest coverage, and dividend growth consistency.
          </p>
        </article>
      </div>

      <article className="data-card">
        <h3>Important limitation</h3>
        <p>
          Outputs are educational research aids, not investment advice. Always
          verify filings, capital allocation plans, debt maturities, and
          management guidance before relying on any valuation or dividend safety
          conclusion.
        </p>
      </article>
    </section>
  );
}
