import { useNavigate } from "react-router-dom";
import { TrendingUp, BarChart2, Shield, Zap } from "lucide-react";
import TickerInput from "../components/TickerInput";

const features = [
  {
    icon: TrendingUp,
    title: "DCF Valuation",
    desc: "Discounted Cash Flow analysis projecting future free cash flows to determine intrinsic value.",
    color: "text-brand-400",
    bg: "bg-brand-500/10",
  },
  {
    icon: BarChart2,
    title: "Dividend Discount Model",
    desc: "Gordon Growth and Multi-Stage DDM to price stocks based on expected dividend streams.",
    color: "text-purple-400",
    bg: "bg-purple-500/10",
  },
  {
    icon: Shield,
    title: "AI Safety Score",
    desc: "GPT-powered analysis of balance sheet health, payout coverage, and dividend growth streak.",
    color: "text-emerald-400",
    bg: "bg-emerald-500/10",
  },
  {
    icon: Zap,
    title: "Real-Time Data",
    desc: "Live market data via Yahoo Finance — always current prices, dividends, and financials.",
    color: "text-amber-400",
    bg: "bg-amber-500/10",
  },
];

const exampleTickers = ["AAPL", "JNJ", "KO", "MSFT", "PG", "ABBV", "O", "VZ"];

export default function HomePage() {
  const navigate = useNavigate();

  const handleSearch = (ticker: string) => {
    navigate(`/overview?ticker=${ticker}`);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-16 flex flex-col items-center gap-12">
      {/* Hero */}
      <div className="text-center space-y-4">
        <div className="inline-flex items-center gap-2 text-brand-400 bg-brand-500/10 border border-brand-500/20 text-sm font-medium px-4 py-1.5 rounded-full mb-2">
          <Zap className="w-3.5 h-3.5" />
          AI-Powered Dividend Analysis
        </div>
        <h1 className="text-4xl sm:text-5xl font-extrabold text-white tracking-tight leading-tight">
          Evaluate Dividend Growth
          <span className="text-brand-400 block">Stocks with Confidence</span>
        </h1>
        <p className="text-slate-400 text-lg max-w-2xl mx-auto">
          Enter any stock ticker to get a full valuation suite — DCF, DDM, and an AI-powered
          dividend safety score backed by real financial data.
        </p>
      </div>

      {/* Search */}
      <div className="w-full max-w-xl">
        <TickerInput onSubmit={handleSearch} placeholder="Enter ticker (e.g. KO, JNJ, AAPL)…" />
        <div className="flex flex-wrap gap-2 mt-3">
          {exampleTickers.map((t) => (
            <button
              key={t}
              onClick={() => handleSearch(t)}
              className="px-3 py-1 text-xs font-semibold text-slate-400 bg-slate-800 hover:bg-slate-700 hover:text-slate-100 rounded-full transition-colors"
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {/* Feature cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full">
        {features.map(({ icon: Icon, title, desc, color, bg }) => (
          <div key={title} className="card flex gap-4">
            <div className={`w-10 h-10 rounded-lg ${bg} flex items-center justify-center flex-shrink-0`}>
              <Icon className={`w-5 h-5 ${color}`} />
            </div>
            <div>
              <h3 className="font-semibold text-white mb-1">{title}</h3>
              <p className="text-sm text-slate-400">{desc}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
