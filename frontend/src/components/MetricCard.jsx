export default function MetricCard({ label, value, sub }) {
  return (
    <div className="card metric">
      <span className="label">{label}</span>
      <span className="value">{value}</span>
      {sub && <span className="sub">{sub}</span>}
    </div>
  );
}
