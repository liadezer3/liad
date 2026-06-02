interface Props {
  label: string;
  value: string | number | null | undefined;
  sub?: string;
  highlight?: "positive" | "negative" | "neutral";
}

export default function MetricCard({ label, value, sub, highlight }: Props) {
  const highlightClass =
    highlight === "positive"
      ? "text-emerald-400"
      : highlight === "negative"
      ? "text-red-400"
      : "text-slate-100";

  return (
    <div className="metric-card">
      <span className="metric-label">{label}</span>
      <span className={`metric-value ${highlightClass}`}>
        {value === null || value === undefined ? "—" : value}
      </span>
      {sub && <span className="text-xs text-slate-500">{sub}</span>}
    </div>
  );
}
