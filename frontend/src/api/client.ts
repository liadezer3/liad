import type { DCFResult, DDMResult, DividendSafetyResult, StockQuote } from '../types'

const BASE = import.meta.env.VITE_API_URL ?? ''

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...init?.headers,
    },
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail))
  }
  return res.json()
}

export function fetchStock(ticker: string) {
  return request<StockQuote>(`/api/stocks/${encodeURIComponent(ticker.toUpperCase())}`)
}

export function runDCF(body: {
  ticker: string
  discount_rate: number
  terminal_growth_rate: number
  projection_years: number
}) {
  return request<DCFResult>('/api/valuation/dcf', {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

export function runDDM(body: {
  ticker: string
  required_return: number
  dividend_growth_rate?: number
}) {
  return request<DDMResult>('/api/valuation/ddm', {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

export function analyzeDividendSafety(ticker: string) {
  return request<DividendSafetyResult>('/api/analysis/dividend-safety', {
    method: 'POST',
    body: JSON.stringify({ ticker }),
  })
}
