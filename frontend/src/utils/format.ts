export function fmtCurrency(value: number | null | undefined, decimals = 2): string {
  if (value === null || value === undefined) return "—";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}

export function fmtPct(value: number | null | undefined, decimals = 1): string {
  if (value === null || value === undefined) return "—";
  return `${(value * 100).toFixed(decimals)}%`;
}

export function fmtNum(value: number | null | undefined, decimals = 2): string {
  if (value === null || value === undefined) return "—";
  return value.toFixed(decimals);
}

export function fmtLargeNum(value: number | null | undefined): string {
  if (value === null || value === undefined) return "—";
  if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
  if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
  if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
  return `$${value.toLocaleString()}`;
}
