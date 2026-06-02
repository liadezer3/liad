export const fmtPct = (v, digits = 2) =>
  v === null || v === undefined ? "—" : `${(v * 100).toFixed(digits)}%`;

export const fmtPctRaw = (v, digits = 2) =>
  v === null || v === undefined ? "—" : `${v.toFixed(digits)}%`;

export const fmtMoney = (v, currency = "USD") => {
  if (v === null || v === undefined) return "—";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format(v);
};

export const fmtNumber = (v, digits = 2) =>
  v === null || v === undefined ? "—" : Number(v).toFixed(digits);

export const fmtCompact = (v) => {
  if (v === null || v === undefined) return "—";
  return new Intl.NumberFormat("en-US", {
    notation: "compact",
    maximumFractionDigits: 2,
  }).format(v);
};

export const verdictClass = (verdict) => {
  if (verdict === "Undervalued") return "good";
  if (verdict === "Overvalued") return "bad";
  return "neutral";
};

export const ratingClass = (rating) => {
  if (rating === "Very Safe" || rating === "Safe") return "good";
  if (rating === "Borderline") return "warn";
  return "bad";
};

export const scoreColor = (score) => {
  if (score >= 85) return "#34d399";
  if (score >= 70) return "#2dd4a7";
  if (score >= 50) return "#fbbf24";
  if (score >= 30) return "#fb923c";
  return "#f87171";
};
