import './MetricBadge.css'

interface Props {
  label: string
  value: string
  variant?: 'positive' | 'negative' | 'neutral'
}

export default function MetricBadge({ label, value, variant = 'neutral' }: Props) {
  return (
    <div className={`metric-badge ${variant}`}>
      <span className="metric-label">{label}</span>
      <span className="metric-value">{value}</span>
    </div>
  )
}
