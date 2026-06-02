import { useState, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { CheckCircle, AlertTriangle, Shield } from "lucide-react";
import {
  RadialBarChart,
  RadialBar,
  ResponsiveContainer,
  PolarAngleAxis,
} from "recharts";
import TickerInput from "../components/TickerInput";
import MetricCard from "../components/MetricCard";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorAlert from "../components/ErrorAlert";
import { getDividendSafety } from "../services/api";
import type { DividendSafetyResult } from "../services/api";
import { fmtPct, fmtNum } from "../utils/format";

function scoreColor(score: number): string {
  if (score >= 75) return "#34d399";
  if (score >= 55) return "#facc15";
  if (score >= 35) return "#fb923c";
  return "#f87171";
}

function gradeColor(grade: string): string {
  if (grade.startsWith("A")) return "text-emerald-400";
  if (grade.startsWith("B")) return "text-yellow-400";
  if (grade.startsWith("C")) return "text-orange-400";
  return "text-red-400";
}

export default function SafetyPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [ticker, setTicker] = useState(searchParams.get("ticker") || "");
  const [result, setResult] = useState<DividendSafetyResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runAnalysis = async (t: string) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await getDividendSafety(t);
      setResult(data);
      navigate(`/safety?ticker=${t}`, { replace: true });
    } catch (e: unknown) {
      const msg =
        (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        (e as { message?: string })?.message ||
        "Safety analysis failed.";
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

  const gaugeData = result
    ? [{ value: result.safety_score, fill: scoreColor(result.safety_score) }]
    : [];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white mb-1">AI Dividend Safety Score</h1>
        <p className="text-slate-400 text-sm">
          GPT-powered analysis of balance sheet health, coverage ratios, and dividend sustainability.
        </p>
      </div>

      <div className="card">
        <div className="max-w-xl">
          <TickerInput onSubmit={handleSubmit} loading={loading} defaultValue={ticker} />
        </div>
        <p className="text-xs text-slate-500 mt-2">
          Requires an OpenAI API key configured on the backend (OPENAI_API_KEY).
        </p>
      </div>

      {loading && (
        <LoadingSpinner label="Analyzing balance sheet with AI… this may take 10–15 seconds." />
      )}
      {error && <ErrorAlert message={error} />}

      {result && (
        <>
          {/* Score hero */}
          <div className="card">
            <div className="flex flex-col lg:flex-row gap-8 items-center">
              {/* Gauge */}
              <div className="flex flex-col items-center gap-2 flex-shrink-0">
                <div className="relative w-48 h-48">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadialBarChart
                      cx="50%"
                      cy="50%"
                      innerRadius="70%"
                      outerRadius="100%"
                      startAngle={225}
                      endAngle={-45}
                      data={gaugeData}
                    >
                      <PolarAngleAxis
                        type="number"
                        domain={[0, 100]}
                        angleAxisId={0}
                        tick={false}
                      />
                      <RadialBar
                        background={{ fill: "#1e293b" }}
                        dataKey="value"
                        angleAxisId={0}
                        cornerRadius={6}
                      />
                    </RadialBarChart>
                  </ResponsiveContainer>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span
                      className="text-5xl font-extrabold"
                      style={{ color: scoreColor(result.safety_score) }}
                    >
                      {result.safety_score}
                    </span>
                    <span className={`text-2xl font-bold ${gradeColor(result.safety_grade)}`}>
                      {result.safety_grade}
                    </span>
                  </div>
                </div>
                <p className="text-sm text-slate-400 text-center">
                  Dividend Safety Score for{" "}
                  <span className="font-bold text-white">{result.ticker}</span>
                </p>
              </div>

              {/* Summary */}
              <div className="flex-1 space-y-4">
                <div>
                  <h3 className="font-semibold text-white mb-2 flex items-center gap-2">
                    <Shield className="w-4 h-4 text-brand-400" />
                    AI Summary
                  </h3>
                  <p className="text-slate-300 text-sm leading-relaxed">{result.summary}</p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {result.strengths.length > 0 && (
                    <div>
                      <h4 className="text-xs font-semibold text-emerald-400 uppercase tracking-wide mb-2">
                        Strengths
                      </h4>
                      <ul className="space-y-1.5">
                        {result.strengths.map((s, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                            <CheckCircle className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                            {s}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {result.risks.length > 0 && (
                    <div>
                      <h4 className="text-xs font-semibold text-red-400 uppercase tracking-wide mb-2">
                        Risks
                      </h4>
                      <ul className="space-y-1.5">
                        {result.risks.map((r, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                            <AlertTriangle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
                            {r}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Key metrics */}
          <div>
            <h3 className="font-semibold text-white mb-3">Underlying Metrics</h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
              <MetricCard
                label="Payout Ratio"
                value={fmtPct(result.payout_ratio)}
                highlight={
                  result.payout_ratio === null
                    ? "neutral"
                    : result.payout_ratio > 0.9
                    ? "negative"
                    : result.payout_ratio > 0.6
                    ? "neutral"
                    : "positive"
                }
              />
              <MetricCard
                label="FCF Payout Ratio"
                value={fmtPct(result.free_cash_flow_payout)}
                highlight={
                  result.free_cash_flow_payout === null
                    ? "neutral"
                    : result.free_cash_flow_payout > 1
                    ? "negative"
                    : result.free_cash_flow_payout > 0.7
                    ? "neutral"
                    : "positive"
                }
              />
              <MetricCard
                label="Debt / Equity"
                value={result.debt_to_equity !== null ? fmtNum(result.debt_to_equity / 100) : "—"}
                highlight={
                  result.debt_to_equity === null
                    ? "neutral"
                    : result.debt_to_equity > 200
                    ? "negative"
                    : result.debt_to_equity > 100
                    ? "neutral"
                    : "positive"
                }
              />
              <MetricCard
                label="Interest Coverage"
                value={result.interest_coverage !== null ? `${fmtNum(result.interest_coverage)}×` : "—"}
                highlight={
                  result.interest_coverage === null
                    ? "neutral"
                    : result.interest_coverage < 2
                    ? "negative"
                    : result.interest_coverage < 4
                    ? "neutral"
                    : "positive"
                }
              />
              <MetricCard
                label="Dividend CAGR (5yr)"
                value={fmtPct(result.dividend_cagr_5y)}
                highlight={
                  result.dividend_cagr_5y === null
                    ? "neutral"
                    : result.dividend_cagr_5y > 0.05
                    ? "positive"
                    : result.dividend_cagr_5y > 0
                    ? "neutral"
                    : "negative"
                }
              />
              <MetricCard
                label="Years of Div. Growth"
                value={result.years_of_dividend_growth !== null ? `${result.years_of_dividend_growth} yrs` : "—"}
                highlight={
                  result.years_of_dividend_growth === null
                    ? "neutral"
                    : result.years_of_dividend_growth >= 10
                    ? "positive"
                    : result.years_of_dividend_growth >= 5
                    ? "neutral"
                    : "negative"
                }
              />
            </div>
          </div>

          {/* Score legend */}
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4">
            <p className="text-xs font-semibold text-slate-400 mb-3">Scoring Legend</p>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {[
                { range: "85–100", grade: "A+", label: "Very Safe", color: "text-emerald-400" },
                { range: "65–84", grade: "A / B+", label: "Safe", color: "text-green-400" },
                { range: "45–64", grade: "B / C+", label: "Moderate", color: "text-yellow-400" },
                { range: "0–44", grade: "C / D", label: "Risky", color: "text-red-400" },
              ].map(({ range, grade, label, color }) => (
                <div key={range} className="flex flex-col gap-0.5">
                  <span className={`font-bold text-sm ${color}`}>{grade}</span>
                  <span className="text-xs text-slate-300">{label}</span>
                  <span className="text-xs text-slate-500">Score: {range}</span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
