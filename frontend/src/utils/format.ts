export function formatCurrency(value: number, maximumFractionDigits = 2): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits,
  }).format(value);
}

export function formatLargeCurrency(value: number): string {
  const absValue = Math.abs(value);

  if (absValue >= 1_000_000_000_000) {
    return `${formatCurrency(value / 1_000_000_000_000, 2)}T`;
  }

  if (absValue >= 1_000_000_000) {
    return `${formatCurrency(value / 1_000_000_000, 2)}B`;
  }

  if (absValue >= 1_000_000) {
    return `${formatCurrency(value / 1_000_000, 2)}M`;
  }

  return formatCurrency(value, 0);
}

export function formatPercent(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "percent",
    maximumFractionDigits: 1,
  }).format(value);
}

export function formatMultiple(value: number): string {
  return `${value.toFixed(2)}x`;
}
