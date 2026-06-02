import { useState, useEffect } from "react";
import { useSearchParams, useNavigate, Link } from "react-router-dom";
import { ExternalLink, TrendingUp, BarChart2, Shield } from "lucide-react";
import TickerInput from "../components/TickerInput";
import MetricCard from "../components/MetricCard";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorAlert from "../components/ErrorAlert";
import { getStockOverview } from "../services/api";
import type { StockOverview } from "../services/api";
import { fmtCurrency, fmtPct, fmtNum, fmtLargeNum } from "../utils/format";

export default function OverviewPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [ticker, setTicker] = useState(searchParams.get("ticker") || "");
  const [data, setData] = useState<StockOverview | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async (t: string) => {
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const result = await getStockOverview(t);
      setData(result);
      navigate(`/overview?ticker=${t}`, { replace: true });
    } catch (e: unknown) {
      const msg = (e as { response?: { data?: { detail?: string } }; message?: string })
        ?.response?.data?.detail || (e as { message?: string })?.message || "Failed to fetch stock data.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (ticker) fetchData(ticker);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSubmit = (t: string) => {
    setTicker(t);
    fetchData(t);
  };

  const priceRange = data
    ? ((data.current_price - (data.fifty_two_week_low ?? data.current_price)) /
        ((data.fifty_two_week_high ?? data.current_price) - (data.fifty_two_week_low ?? data.current_price))) *
      100
    : 0;

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white mb-1">Stock Overview</h1>
        <p className="text-slate-400 text-sm">Real-time snapshot of key metrics for any publicly traded company.</p>
      </div>

      <div className="max-w-xl">
        <TickerInput onSubmit={handleSubmit} loading={loading} defaultValue={ticker} />
      </div>

      {loading && <LoadingSpinner label="Fetching stock data…" />}
      {error && <ErrorAlert message={error} />}

      {data && (
        <>
          {/* Header card */}
          <div className="card space-y-3">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono font-bold text-brand-400 bg-brand-500/10 px-2 py-0.5 rounded">
                    {data.ticker}
                  </span>
                  <span className="text-xs text-slate-500">{data.sector} · {data.industry}</span>
                </div>
                <h2 className="text-2xl font-bold text-white mt-1">{data.name}</h2>
                {data.website && (
                  <a
                    href={data.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-xs text-brand-400 hover:underline mt-0.5"
                  >
                    {data.website} <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>
              <div className="text-right">
                <div className="text-3xl font-extrabold text-white">{fmtCurrency(data.current_price)}</div>
                {data.fifty_two_week_high && data.fifty_two_week_low && (
                  <div className="text-xs text-slate-500 mt-1">
                    52w: {fmtCurrency(data.fifty_two_week_low)} — {fmtCurrency(data.fifty_two_week_high)}
                  </div>
                )}
              </div>
            </div>

            {/* 52-week range bar */}
            {data.fifty_two_week_high && data.fifty_two_week_low && (
              <div>
                <div className="w-full bg-slate-700 rounded-full h-1.5">
                  <div
                    className="bg-brand-500 h-1.5 rounded-full transition-all"
                    style={{ width: `${Math.min(100, Math.max(0, priceRange))}%` }}
                  />
                </div>
              </div>
            )}
          </div>

          {/* Metrics grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
            <MetricCard label="Market Cap" value={fmtLargeNum(data.market_cap)} />
            <MetricCard label="P/E Ratio" value={fmtNum(data.pe_ratio)} />
            <MetricCard label="Forward P/E" value={fmtNum(data.forward_pe)} />
            <MetricCard label="Beta" value={fmtNum(data.beta, 2)} />
            <MetricCard label="Dividend Yield" value={fmtPct(data.dividend_yield)} highlight={data.dividend_yield && data.dividend_yield > 0.02 ? "positive" : "neutral"} />
            <MetricCard label="Annual Dividend" value={data.annual_dividend ? fmtCurrency(data.annual_dividend) : "—"} />
            <MetricCard label="Payout Ratio" value={fmtPct(data.payout_ratio)} highlight={data.payout_ratio ? (data.payout_ratio > 0.8 ? "negative" : "positive") : "neutral"} />
            <MetricCard label="5yr Avg Yield" value={fmtPct(data.five_year_avg_dividend_yield)} />
            <MetricCard label="Div. Growth (5y)" value={fmtPct(data.dividend_growth_rate_5y)} highlight={data.dividend_growth_rate_5y && data.dividend_growth_rate_5y > 0 ? "positive" : "negative"} />
          </div>

          {/* Description */}
          {data.description && (
            <div className="card">
              <h3 className="font-semibold text-white mb-2">About</h3>
              <p className="text-sm text-slate-400 leading-relaxed line-clamp-5">{data.description}</p>
            </div>
          )}

          {/* Navigation CTAs */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {[
              { to: `/dcf?ticker=${data.ticker}`, icon: TrendingUp, label: "Run DCF Analysis", color: "text-brand-400" },
              { to: `/ddm?ticker=${data.ticker}`, icon: BarChart2, label: "Run DDM Analysis", color: "text-purple-400" },
              { to: `/safety?ticker=${data.ticker}`, icon: Shield, label: "Get Safety Score", color: "text-emerald-400" },
            ].map(({ to, icon: Icon, label, color }) => (
              <Link
                key={to}
                to={to}
                className="card flex items-center gap-3 hover:border-slate-600 transition-colors group"
              >
                <Icon className={`w-5 h-5 ${color}`} />
                <span className="font-medium text-slate-300 group-hover:text-white transition-colors">{label}</span>
              </Link>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
