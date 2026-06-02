type MetricCardProps = {
  label: string;
  value: string;
  detail?: string;
  tone?: "neutral" | "positive" | "warning";
};

export function MetricCard({ label, value, detail, tone = "neutral" }: MetricCardProps) {
  return (
    <article className={`metric-card metric-card--${tone}`}>
      <p>{label}</p>
      <strong>{value}</strong>
      {detail ? <span>{detail}</span> : null}
    </article>
  );
}
