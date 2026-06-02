import { useState, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import TickerInput from "../components/TickerInput";
import MetricCard from "../components/MetricCard";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorAlert from "../components/ErrorAlert";
import ValuationBadge from "../components/ValuationBadge";
import { runDDM } from "../services/api";
import type { DDMResult } from "../services/api";
import { fmtCurrency, fmtPct, fmtNum } from "../utils/format";

const DEFAULT_FORM = {
  required_rate: 10,
  dividend_growth_override: "",
  model_type: "gordon" as "gordon" | "multi_stage",
  high_growth_rate: "",
  high_growth_years: 5,
};

export default function DDMPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [ticker, setTicker] = useState(searchParams.get("ticker") || "");
  const [form, setForm] = useState(DEFAULT_FORM);
  const [result, setResult] = useState<DDMResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runAnalysis = async (t: string) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await runDDM({
        ticker: t,
        required_rate_of_return: form.required_rate / 100,
        dividend_growth_rate: form.dividend_growth_override !== "" ? parseFloat(form.dividend_growth_override) / 100 : null,
        model_type: form.model_type,
        high_growth_rate: form.model_type === "multi_stage" && form.high_growth_rate !== "" ? parseFloat(form.high_growth_rate) / 100 : null,
        high_growth_years: form.model_type === "multi_stage" ? form.high_growth_years : null,
      });
      setResult(data);
      navigate(`/ddm?ticker=${t}`, { replace: true });
    } catch (e: unknown) {
      const msg =
        (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        (e as { message?: string })?.message ||
        "DDM analysis failed.";
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

  const comparisonData = result
    ? [
        { name: "Current Price", value: result.current_price, color: "#64748b" },
        { name: "Intrinsic Value", value: result.intrinsic_value, color: result.intrinsic_value > result.current_price ? "#34d399" : "#f87171" },
      ]
    : [];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white mb-1">Dividend Discount Model</h1>
        <p className="text-slate-400 text-sm">
          Values a stock as the present value of all its future dividend payments.
        </p>
      </div>

      <div className="card space-y-5">
        <div className="max-w-xl">
          <TickerInput onSubmit={handleSubmit} loading={loading} defaultValue={ticker} />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div>
            <label className="label">Required Rate of Return %</label>
            <input
              type="number"
              className="input-field"
              min={1}
              max={50}
              step={0.5}
              value={form.required_rate}
              onChange={(e) => setForm((f) => ({ ...f, required_rate: parseFloat(e.target.value) }))}
            />
            <p className="text-xs text-slate-500 mt-1">Your minimum acceptable return</p>
          </div>
          <div>
            <label className="label">Dividend Growth Override % (optional)</label>
            <input
              type="number"
              className="input-field"
              min={0}
              max={30}
              step={0.5}
              value={form.dividend_growth_override}
              placeholder="Auto-calculated"
              onChange={(e) => setForm((f) => ({ ...f, dividend_growth_override: e.target.value }))}
            />
            <p className="text-xs text-slate-500 mt-1">Leave blank to use 5yr CAGR</p>
          </div>
          <div>
            <label className="label">Model Type</label>
            <select
              className="input-field"
              value={form.model_type}
              onChange={(e) => setForm((f) => ({ ...f, model_type: e.target.value as "gordon" | "multi_stage" }))}
            >
              <option value="gordon">Gordon Growth (single stage)</option>
              <option value="multi_stage">Multi-Stage Growth</option>
            </select>
          </div>

          {form.model_type === "multi_stage" && (
            <>
              <div>
                <label className="label">High Growth Rate % (optional)</label>
                <input
                  type="number"
                  className="input-field"
                  min={0}
                  max={50}
                  step={0.5}
                  value={form.high_growth_rate}
                  placeholder="Auto: 2× long-term rate"
                  onChange={(e) => setForm((f) => ({ ...f, high_growth_rate: e.target.value }))}
                />
              </div>
              <div>
                <label className="label">High Growth Period (years)</label>
                <input
                  type="number"
                  className="input-field"
                  min={1}
                  max={15}
                  step={1}
                  value={form.high_growth_years}
                  onChange={(e) => setForm((f) => ({ ...f, high_growth_years: parseInt(e.target.value) }))}
                />
              </div>
            </>
          )}
        </div>

        {ticker && (
          <button className="btn-primary" onClick={() => runAnalysis(ticker)} disabled={loading}>
            {loading ? "Running…" : "Re-run DDM"}
          </button>
        )}
      </div>

      {loading && <LoadingSpinner label="Running DDM analysis…" />}
      {error && <ErrorAlert message={error} />}

      {result && (
        <>
          <div className="card space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <div>
                <span className="text-xs font-mono font-bold text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded">
                  {result.ticker}
                </span>
                <h2 className="text-xl font-bold text-white mt-1">DDM Valuation Result</h2>
                <p className="text-xs text-slate-500 capitalize mt-0.5">
                  {result.model_type === "gordon" ? "Gordon Growth Model" : "Multi-Stage Growth Model"}
                </p>
              </div>
              <ValuationBadge
                upside={result.upside_downside_pct}
                currentPrice={result.current_price}
                intrinsicValue={result.intrinsic_value}
              />
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <MetricCard label="Current Price" value={fmtCurrency(result.current_price)} />
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

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              <MetricCard label="Last Annual Dividend" value={fmtCurrency(result.last_dividend)} />
              <MetricCard label="Dividend Growth Rate" value={fmtPct(result.dividend_growth_rate)} />
              <MetricCard label="Required Return" value={fmtPct(result.required_rate_of_return)} />
            </div>
          </div>

          {/* Bar chart comparison */}
          <div className="card">
            <h3 className="font-semibold text-white mb-4">Price vs Intrinsic Value</h3>
            <div className="h-52">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={comparisonData} margin={{ top: 5, right: 30, bottom: 5, left: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="name" stroke="#64748b" tick={{ fontSize: 13 }} />
                  <YAxis stroke="#64748b" tick={{ fontSize: 12 }} tickFormatter={(v) => `$${v}`} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155", borderRadius: 8 }}
                    formatter={(v) => [`$${Number(v).toFixed(2)}`]}
                  />
                  <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                    {comparisonData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 text-xs text-slate-500 space-y-1">
            <p className="font-semibold text-slate-400">Methodology</p>
            <p>
              <strong className="text-slate-300">Gordon Growth:</strong> P = D₁ / (r − g) where D₁ is next year's
              expected dividend, r is your required return, and g is the long-term dividend growth rate.
            </p>
            <p className="mt-1">
              <strong className="text-slate-300">Multi-Stage:</strong> Discounts dividends during a high-growth phase
              explicitly, then applies the Gordon model at the end of that phase as a terminal value.
            </p>
          </div>
        </>
      )}
    </div>
  );
}
