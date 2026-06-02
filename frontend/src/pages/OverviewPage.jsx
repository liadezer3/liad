import { Link } from "react-router-dom";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from "recharts";
import Loader from "../components/Loader.jsx";
import MetricCard from "../components/MetricCard.jsx";
import { useActiveTicker } from "../hooks/useActiveTicker.js";
import { fmtMoney, fmtPct, fmtCompact, fmtNumber } from "../utils/format.js";

const chartTheme = {
  grid: "#25314f",
  axis: "#94a3b8",
};

export default function OverviewPage() {
  const { detail, loading, error, symbol } = useActiveTicker();

  if (loading) return <div className="page"><Loader label={`Loading ${symbol}…`} /></div>;
  if (error)
    return (
      <div className="page">
        <div className="error">{error}</div>
        <p style={{ marginTop: "1rem" }}>
          <Link className="btn ghost" to="/">← Back to search</Link>
        </p>
      </div>
    );
  if (!detail) return <div className="page"><Loader /></div>;

  const sheets = detail.balance_sheets || [];
  const cashflowData = sheets.map((s) => ({
    year: s.year,
    "Free Cash Flow": Math.round(s.free_cash_flow),
    "Dividends Paid": Math.round(s.dividends_paid),
  }));

  return (
    <div className="page">
      <div className="page-head">
        <span className="eyebrow">Overview</span>
        <div className="row space-between" style={{ alignItems: "flex-start" }}>
          <div>
            <h1 style={{ marginBottom: "0.2rem" }}>
              {detail.name}{" "}
              <span className="muted" style={{ fontSize: "1rem" }}>
                ({detail.ticker})
              </span>
            </h1>
            <p className="muted" style={{ margin: 0 }}>
              {[detail.sector, detail.industry, detail.exchange]
                .filter(Boolean)
                .join(" · ")}
            </p>
          </div>
          {detail.is_sample && (
            <span className="pill-sample">sample data</span>
          )}
        </div>
      </div>

      <div className="grid cols-4">
        <MetricCard label="Price" value={fmtMoney(detail.price, detail.currency)} />
        <MetricCard
          label="Dividend Yield"
          value={fmtPct(detail.dividend_yield)}
          sub={`${fmtMoney(detail.dividend_per_share, detail.currency)} / share`}
        />
        <MetricCard
          label="Payout Ratio"
          value={detail.payout_ratio != null ? fmtPct(detail.payout_ratio) : "—"}
        />
        <MetricCard
          label="Growth Streak"
          value={detail.years_of_growth != null ? `${detail.years_of_growth} yrs` : "—"}
          sub="consecutive increases"
        />
      </div>

      <div className="grid cols-4" style={{ marginTop: "1.1rem" }}>
        <MetricCard label="Market Cap" value={fmtCompact(detail.market_cap)} />
        <MetricCard label="EPS (TTM)" value={detail.eps != null ? fmtMoney(detail.eps) : "—"} />
        <MetricCard
          label="FCF / Share"
          value={detail.free_cash_flow_per_share != null ? fmtMoney(detail.free_cash_flow_per_share) : "—"}
        />
        <MetricCard label="Beta" value={fmtNumber(detail.beta)} />
      </div>

      {detail.summary && (
        <div className="card" style={{ marginTop: "1.1rem" }}>
          <h3>About</h3>
          <p className="muted" style={{ marginBottom: 0 }}>{detail.summary}</p>
        </div>
      )}

      {cashflowData.length > 0 && (
        <>
          <div className="section-title">
            <h2>Free Cash Flow vs. Dividends Paid</h2>
          </div>
          <div className="card">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={cashflowData} margin={{ top: 8, right: 12, bottom: 0, left: 8 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={chartTheme.grid} />
                <XAxis dataKey="year" stroke={chartTheme.axis} />
                <YAxis
                  stroke={chartTheme.axis}
                  tickFormatter={(v) => fmtCompact(v)}
                  width={56}
                />
                <Tooltip
                  contentStyle={{
                    background: "#0b1120",
                    border: "1px solid #25314f",
                    borderRadius: 10,
                  }}
                  formatter={(v) => fmtCompact(v)}
                />
                <Legend />
                <Bar dataKey="Free Cash Flow" fill="#2dd4a7" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Dividends Paid" fill="#6ea8fe" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
            <p className="muted" style={{ fontSize: "0.78rem", marginBottom: 0 }}>
              Figures in reporting currency ({detail.currency}). FCF comfortably
              above dividends paid indicates a well-covered payout.
            </p>
          </div>

          <div className="section-title">
            <h2>Historical Balance Sheet</h2>
          </div>
          <div className="card" style={{ overflowX: "auto" }}>
            <table>
              <thead>
                <tr>
                  <th>Year</th>
                  <th>Total Assets</th>
                  <th>Total Liab.</th>
                  <th>Equity</th>
                  <th>Cash</th>
                  <th>Total Debt</th>
                  <th>Net Income</th>
                  <th>FCF</th>
                  <th>Dividends</th>
                </tr>
              </thead>
              <tbody>
                {sheets.map((s) => (
                  <tr key={s.year}>
                    <td>{s.year}</td>
                    <td>{fmtCompact(s.total_assets)}</td>
                    <td>{fmtCompact(s.total_liabilities)}</td>
                    <td>{fmtCompact(s.total_equity)}</td>
                    <td>{fmtCompact(s.cash_and_equivalents)}</td>
                    <td>{fmtCompact(s.total_debt)}</td>
                    <td>{fmtCompact(s.net_income)}</td>
                    <td>{fmtCompact(s.free_cash_flow)}</td>
                    <td>{fmtCompact(s.dividends_paid)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      <div className="row" style={{ marginTop: "1.6rem", gap: "0.8rem" }}>
        <Link className="btn" to={`/valuation/${detail.ticker}`}>
          Run Valuation →
        </Link>
        <Link className="btn ghost" to={`/analysis/${detail.ticker}`}>
          AI Dividend-Safety Analysis →
        </Link>
      </div>
    </div>
  );
}
