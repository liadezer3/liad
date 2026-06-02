import { useState, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import TickerInput from "../components/TickerInput";
import MetricCard from "../components/MetricCard";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorAlert from "../components/ErrorAlert";
import ValuationBadge from "../components/ValuationBadge";
import { runDCF } from "../services/api";
import type { DCFResult } from "../services/api";
import { fmtCurrency, fmtPct, fmtNum } from "../utils/format";

const DEFAULT_FORM = {
  discount_rate: 10,
  terminal_growth_rate: 3,
  projection_years: 10,
};

export default function DCFPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [ticker, setTicker] = useState(searchParams.get("ticker") || "");
  const [form, setForm] = useState(DEFAULT_FORM);
  const [result, setResult] = useState<DCFResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runAnalysis = async (t: string) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await runDCF({
        ticker: t,
        discount_rate: form.discount_rate / 100,
        terminal_growth_rate: form.terminal_growth_rate / 100,
        projection_years: form.projection_years,
      });
      setResult(data);
      navigate(`/dcf?ticker=${t}`, { replace: true });
    } catch (e: unknown) {
      const msg =
        (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        (e as { message?: string })?.message ||
        "DCF analysis failed.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (t: string) => {
    setTicker(t);
    runAnalysis(t);
  };

  useEffect(() => {
    if (ticker) runAnalysis(ticker);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const chartData = result
    ? result.free_cash_flows.map((fcf, i) => ({
        year: `Y${i + 1}`,
        "FCF/Share": parseFloat(fcf.toFixed(2)),
      }))
    : [];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white mb-1">Discounted Cash Flow Analysis</h1>
        <p className="text-slate-400 text-sm">
          Projects future free cash flows and discounts them back to present value to estimate intrinsic value.
        </p>
      </div>

      {/* Input form */}
      <div className="card space-y-5">
        <div className="max-w-xl">
          <TickerInput onSubmit={handleSubmit} loading={loading} defaultValue={ticker} />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="label">Discount Rate (WACC) %</label>
            <input
              type="number"
              className="input-field"
              min={1}
              max={50}
              step={0.5}
              value={form.discount_rate}
              onChange={(e) => setForm((f) => ({ ...f, discount_rate: parseFloat(e.target.value) }))}
            />
            <p className="text-xs text-slate-500 mt-1">Typical: 8–12%</p>
          </div>
          <div>
            <label className="label">Terminal Growth Rate %</label>
            <input
              type="number"
              className="input-field"
              min={0}
              max={10}
              step={0.5}
              value={form.terminal_growth_rate}
              onChange={(e) => setForm((f) => ({ ...f, terminal_growth_rate: parseFloat(e.target.value) }))}
            />
            <p className="text-xs text-slate-500 mt-1">Typical: 2–4%</p>
          </div>
          <div>
            <label className="label">Projection Years</label>
            <input
              type="number"
              className="input-field"
              min={3}
              max={20}
              step={1}
              value={form.projection_years}
              onChange={(e) => setForm((f) => ({ ...f, projection_years: parseInt(e.target.value) }))}
            />
            <p className="text-xs text-slate-500 mt-1">Typical: 5–10</p>
          </div>
        </div>

        {ticker && (
          <button
            className="btn-primary"
            onClick={() => runAnalysis(ticker)}
            disabled={loading}
          >
            {loading ? "Running…" : "Re-run DCF"}
          </button>
        )}
      </div>

      {loading && <LoadingSpinner label="Running DCF analysis…" />}
      {error && <ErrorAlert message={error} />}

      {result && (
        <>
          {/* Valuation summary */}
          <div className="card space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <div>
                <span className="text-xs font-mono font-bold text-brand-400 bg-brand-500/10 px-2 py-0.5 rounded">
                  {result.ticker}
                </span>
                <h2 className="text-xl font-bold text-white mt-1">DCF Valuation Result</h2>
              </div>
              <ValuationBadge
                upside={result.upside_downside_pct}
                currentPrice={result.current_price}
                intrinsicValue={result.intrinsic_value}
              />
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <MetricCard
                label="Current Price"
                value={fmtCurrency(result.current_price)}
              />
              <MetricCard
                label="Intrinsic Value"
                value={fmtCurrency(result.intrinsic_value)}
                highlight={result.intrinsic_value > result.current_price ? "positive" : "negative"}
              />
              <MetricCard
                label="Margin of Safety"
                value={fmtPct(result.margin_of_safety)}
                highlight={result.margin_of_safety > 0.2 ? "positive" : result.margin_of_safety > 0 ? "neutral" : "negative"}
              />
              <MetricCard
                label="Upside / Downside"
                value={`${result.upside_downside_pct >= 0 ? "+" : ""}${fmtNum(result.upside_downside_pct)}%`}
                highlight={result.upside_downside_pct > 0 ? "positive" : "negative"}
              />
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <MetricCard label="Discount Rate" value={fmtPct(result.discount_rate)} />
              <MetricCard label="Terminal Growth" value={fmtPct(result.terminal_growth_rate)} />
              <MetricCard label="Revenue Growth Est." value={fmtPct(result.revenue_growth_rate)} />
              <MetricCard label="FCF / Share (Base)" value={fmtCurrency(result.fcf_margin)} />
            </div>
          </div>

          {/* FCF projection chart */}
          <div className="card">
            <h3 className="font-semibold text-white mb-4">Projected Free Cash Flow Per Share</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 5, right: 10, bottom: 0, left: 10 }}>
                  <defs>
                    <linearGradient id="fcfGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="year" stroke="#64748b" tick={{ fontSize: 12 }} />
                  <YAxis stroke="#64748b" tick={{ fontSize: 12 }} tickFormatter={(v) => `$${v}`} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155", borderRadius: 8 }}
                    labelStyle={{ color: "#94a3b8" }}
                    formatter={(v) => [`$${Number(v).toFixed(2)}`, "FCF/Share"]}
                  />
                  <ReferenceLine
                    y={result.current_price}
                    stroke="#f59e0b"
                    strokeDasharray="4 2"
                    label={{ value: "Current Price", fill: "#f59e0b", fontSize: 11 }}
                  />
                  <Area
                    type="monotone"
                    dataKey="FCF/Share"
                    stroke="#0ea5e9"
                    strokeWidth={2}
                    fill="url(#fcfGrad)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Methodology note */}
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 text-xs text-slate-500 space-y-1">
            <p className="font-semibold text-slate-400">Methodology</p>
            <p>
              FCF is projected from the latest reported free cash flow using a blended growth rate that decays
              linearly from the estimated historical revenue CAGR toward the terminal growth rate over the
              projection period. Terminal value uses the Gordon Growth Model applied to year-N FCF.
            </p>
          </div>
        </>
      )}
    </div>
  );
}
