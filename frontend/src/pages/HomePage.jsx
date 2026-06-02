import TickerSearch from "../components/TickerSearch.jsx";

export default function HomePage() {
  return (
    <div className="page">
      <section className="hero">
        <span className="eyebrow">AI-Powered Equity Income Research</span>
        <h1>
          Evaluate dividend growth stocks with
          <br />
          valuation models + AI safety scoring.
        </h1>
        <p className="lead">
          Pull a company's fundamentals and multi-year balance sheets, run
          Discounted Cash Flow and Dividend Discount Model valuations, and let an
          AI prompt layer grade how safe the dividend really is.
        </p>
      </section>

      <div className="card" style={{ marginTop: "1.4rem" }}>
        <h3>Start with a ticker</h3>
        <p className="muted" style={{ marginTop: 0 }}>
          Live data is fetched when available, with bundled fixtures as an
          offline fallback.
        </p>
        <TickerSearch autoFocus />
      </div>

      <div className="grid cols-3" style={{ marginTop: "1.4rem" }}>
        <div className="card">
          <span className="eyebrow">Step 1 · Overview</span>
          <h3>Company & dividend profile</h3>
          <p className="muted">
            Price, yield, payout ratio, growth streak and a condensed view of the
            historical balance sheet.
          </p>
        </div>
        <div className="card">
          <span className="eyebrow">Step 2 · Valuation</span>
          <h3>DCF & DDM fair value</h3>
          <p className="muted">
            Adjust discount and growth assumptions and instantly see fair value,
            upside, and a verdict for each model.
          </p>
        </div>
        <div className="card">
          <span className="eyebrow">Step 3 · AI Analysis</span>
          <h3>Dividend-safety score</h3>
          <p className="muted">
            An AI prompt layer analyses balance-sheet trends to score dividend
            safety, with transparent contributing factors.
          </p>
        </div>
      </div>
    </div>
  );
}
