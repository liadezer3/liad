import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface Props {
  upside: number;
  currentPrice: number;
  intrinsicValue: number;
}

export default function ValuationBadge({ upside, currentPrice, intrinsicValue }: Props) {
  const isUndervalued = intrinsicValue > currentPrice;
  const pct = Math.abs(upside).toFixed(1);

  if (isUndervalued) {
    return (
      <div className="inline-flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 px-4 py-2 rounded-full font-semibold text-sm">
        <TrendingUp className="w-4 h-4" />
        Undervalued — {pct}% Upside
      </div>
    );
  } else if (upside < -5) {
    return (
      <div className="inline-flex items-center gap-2 bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-2 rounded-full font-semibold text-sm">
        <TrendingDown className="w-4 h-4" />
        Overvalued — {pct}% Downside
      </div>
    );
  } else {
    return (
      <div className="inline-flex items-center gap-2 bg-yellow-500/10 border border-yellow-500/30 text-yellow-400 px-4 py-2 rounded-full font-semibold text-sm">
        <Minus className="w-4 h-4" />
        Fairly Valued
      </div>
    );
  }
}
