import { scoreColor } from "../utils/format.js";

// Circular SVG gauge for the dividend-safety score (0-100).
export default function ScoreGauge({ score, size = 180 }) {
  const stroke = 14;
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const pct = Math.max(0, Math.min(100, score)) / 100;
  const dash = c * pct;
  const color = scoreColor(score);

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      <circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        fill="none"
        stroke="var(--surface-2)"
        strokeWidth={stroke}
      />
      <circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        fill="none"
        stroke={color}
        strokeWidth={stroke}
        strokeLinecap="round"
        strokeDasharray={`${dash} ${c - dash}`}
        transform={`rotate(-90 ${size / 2} ${size / 2})`}
        style={{ transition: "stroke-dasharray 0.6s ease" }}
      />
      <text
        x="50%"
        y="47%"
        textAnchor="middle"
        fontSize={size * 0.26}
        fontWeight="800"
        fill={color}
      >
        {Math.round(score)}
      </text>
      <text
        x="50%"
        y="64%"
        textAnchor="middle"
        fontSize={size * 0.085}
        fill="var(--muted)"
        letterSpacing="1"
      >
        / 100
      </text>
    </svg>
  );
}
