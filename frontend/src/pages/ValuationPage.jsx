import { useState } from "react";
import { Link } from "react-router-dom";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import Loader from "../components/Loader.jsx";
import { api } from "../api/client.js";
import { useActiveTicker } from "../hooks/useActiveTicker.js";
import { fmtMoney, fmtPctRaw, verdictClass } from "../utils/format.js";

function RangeField({ label, value, min, max, step, onChange, suffix = "%" }) {
  return (
    <div className="field">
      <label>{label}</label>
      <div className="range-row">
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
        />
        <span className="range-val">
          {value}
          {suffix}
        </span>
      </div>
    </div>
  );
}

function ValuationResult({ result, currency }) {
  const data = result.projections.map((p) => ({
    year: `Y${p.year}`,
    value: p.present_value,
  }));
  return (
    <div>
      <div className="grid cols-3" style={{ marginBottom: "1rem" }}>
        <div className="card metric">
          <span className="label">Fair Value / Share</span>
          <span className="value">{fmtMoney(result.fair_value_per_share, currency)}</span>
        </div>
        <div className="card metric">
          <span className="label">Current Price</span>
          <span className="value">{fmtMoney(result.current_price, currency)}</span>
        </div>
        <div className="card metric">
          <span className="label">Upside / Downside</span>
          <span
            className="value"
            style={{ color: result.upside_pct >= 0 ? "var(--success)" : "var(--danger)" }}
          >
            {result.upside_pct >= 0 ? "+" : ""}
            {fmtPctRaw(result.upside_pct)}
          </span>
          <span className="sub">
            <span className={`badge ${verdictClass(result.verdict)}`}>{result.verdict}</span>
          </span>
        </div>
      </div>

      <div className="card">
        <h3 style={{ fontSize: "1rem" }}>Present value of projected cash flows</h3>
        <ResponsiveContainer width="100%" height={220}>
          <AreaChart data={data} margin={{ top: 8, right: 12, bottom: 0, left: 4 }}>
            <defs>
              <linearGradient id="pvGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#2dd4a7" stopOpacity={0.6} />
                <stop offset="100%" stopColor="#2dd4a7" stopOpacity={0.04} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#25314f" />
            <XAxis dataKey="year" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" width={48} />
            <Tooltip
              contentStyle={{ background: "#0b1120", border: "1px solid #25314f", borderRadius: 10 }}
              formatter={(v) => fmtMoney(v, currency)}
            />
            <Area
              type="monotone"
              dataKey="value"
              stroke="#2dd4a7"
              strokeWidth={2}
              fill="url(#pvGrad)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default function ValuationPage() {
  const { detail, loading, error, symbol } = useActiveTicker();

  // DCF state
  const [dcfInputs, setDcfInputs] = useState({
    discount_rate: 9,
    growth_rate: 8,
    terminal_growth: 2.5,
    projection_years: 10,
  });
  const [dcf, setDcf] = useState(null);
  const [dcfErr, setDcfErr] = useState(null);
  const [dcfBusy, setDcfBusy] = useState(false);

  // DDM state
  const [ddmInputs, setDdmInputs] = useState({
    discount_rate: 9,
    high_growth_rate: 7,
    high_growth_years: 5,
    terminal_growth: 3,
  });
  const [ddm, setDdm] = useState(null);
  const [ddmErr, setDdmErr] = useState(null);
  const [ddmBusy, setDdmBusy] = useState(false);

  const runDcf = async () => {
    setDcfBusy(true);
    setDcfErr(null);
    try {
      const res = await api.dcf({
        ticker: detail.ticker,
        discount_rate: dcfInputs.discount_rate / 100,
        growth_rate: dcfInputs.growth_rate / 100,
        terminal_growth: dcfInputs.terminal_growth / 100,
        projection_years: dcfInputs.projection_years,
      });
      setDcf(res);
    } catch (e) {
      setDcfErr(e.message);
      setDcf(null);
    } finally {
      setDcfBusy(false);
    }
  };

  const runDdm = async () => {
    setDdmBusy(true);
    setDdmErr(null);
    try {
      const res = await api.ddm({
        ticker: detail.ticker,
        discount_rate: ddmInputs.discount_rate / 100,
        high_growth_rate: ddmInputs.high_growth_rate / 100,
        high_growth_years: ddmInputs.high_growth_years,
        terminal_growth: ddmInputs.terminal_growth / 100,
      });
      setDdm(res);
    } catch (e) {
      setDdmErr(e.message);
      setDdm(null);
    } finally {
      setDdmBusy(false);
    }
  };

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

  return (
    <div className="page">
      <div className="page-head">
        <span className="eyebrow">Valuation</span>
        <h1>
          {detail.ticker} fair value
        </h1>
        <p>
          Estimate intrinsic value with two complementary models. Adjust the
          assumptions and re-run to see how sensitive the fair value is.
        </p>
      </div>

      {/* DCF -------------------------------------------------------------- */}
      <div className="section-title">
        <h2>Discounted Cash Flow (DCF)</h2>
      </div>
      <div className="grid cols-2">
        <div className="card">
          <p className="muted" style={{ marginTop: 0, fontSize: "0.85rem" }}>
            Projects free cash flow per share, then discounts each year plus a
            Gordon-growth terminal value back to today.
          </p>
          <RangeField
            label="Discount rate (WACC)"
            value={dcfInputs.discount_rate}
            min={4}
            max={20}
            step={0.5}
            onChange={(v) => setDcfInputs({ ...dcfInputs, discount_rate: v })}
          />
          <RangeField
            label="Stage-1 FCF growth"
            value={dcfInputs.growth_rate}
            min={-5}
            max={25}
            step={0.5}
            onChange={(v) => setDcfInputs({ ...dcfInputs, growth_rate: v })}
          />
          <RangeField
            label="Terminal growth"
            value={dcfInputs.terminal_growth}
            min={0}
            max={5}
            step={0.1}
            onChange={(v) => setDcfInputs({ ...dcfInputs, terminal_growth: v })}
          />
          <RangeField
            label="Projection years"
            value={dcfInputs.projection_years}
            min={3}
            max={20}
            step={1}
            suffix=" yrs"
            onChange={(v) => setDcfInputs({ ...dcfInputs, projection_years: v })}
          />
          <button className="btn" onClick={runDcf} disabled={dcfBusy}>
            {dcfBusy ? "Calculating…" : "Run DCF"}
          </button>
          {dcfErr && <div className="error" style={{ marginTop: "0.8rem" }}>{dcfErr}</div>}
        </div>
        <div>
          {dcf ? (
            <ValuationResult result={dcf} currency={detail.currency} />
          ) : (
            <div className="card" style={{ height: "100%", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <p className="muted">Run the model to see DCF fair value.</p>
            </div>
          )}
        </div>
      </div>

      {/* DDM -------------------------------------------------------------- */}
      <div className="section-title">
        <h2>Dividend Discount Model (DDM)</h2>
      </div>
      <div className="grid cols-2">
        <div className="card">
          <p className="muted" style={{ marginTop: 0, fontSize: "0.85rem" }}>
            A two-stage model: dividends grow at a high rate for a number of
            years, then settle into perpetual terminal growth.
          </p>
          <RangeField
            label="Required return"
            value={ddmInputs.discount_rate}
            min={4}
            max={20}
            step={0.5}
            onChange={(v) => setDdmInputs({ ...ddmInputs, discount_rate: v })}
          />
          <RangeField
            label="High-growth dividend rate"
            value={ddmInputs.high_growth_rate}
            min={-5}
            max={25}
            step={0.5}
            onChange={(v) => setDdmInputs({ ...ddmInputs, high_growth_rate: v })}
          />
          <RangeField
            label="High-growth years"
            value={ddmInputs.high_growth_years}
            min={1}
            max={15}
            step={1}
            suffix=" yrs"
            onChange={(v) => setDdmInputs({ ...ddmInputs, high_growth_years: v })}
          />
          <RangeField
            label="Terminal growth"
            value={ddmInputs.terminal_growth}
            min={0}
            max={5}
            step={0.1}
            onChange={(v) => setDdmInputs({ ...ddmInputs, terminal_growth: v })}
          />
          <button className="btn" onClick={runDdm} disabled={ddmBusy}>
            {ddmBusy ? "Calculating…" : "Run DDM"}
          </button>
          {ddmErr && <div className="error" style={{ marginTop: "0.8rem" }}>{ddmErr}</div>}
        </div>
        <div>
          {ddm ? (
            <ValuationResult result={ddm} currency={detail.currency} />
          ) : (
            <div className="card" style={{ height: "100%", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <p className="muted">
                Run the model to see DDM fair value
                {detail.dividend_per_share > 0 ? "." : " (note: this ticker pays no dividend)."}
              </p>
            </div>
          )}
        </div>
      </div>

      <div className="row" style={{ marginTop: "1.6rem" }}>
        <Link className="btn ghost" to={`/overview/${detail.ticker}`}>← Overview</Link>
        <Link className="btn" to={`/analysis/${detail.ticker}`}>AI Analysis →</Link>
      </div>
    </div>
  );
}
