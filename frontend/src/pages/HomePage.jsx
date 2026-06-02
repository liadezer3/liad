import { useState } from 'react'

import { fetchTicker } from '../api/client'

export default function HomePage() {
  const [ticker, setTicker] = useState('MSFT')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [data, setData] = useState(null)

  async function onSubmit(event) {
    event.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await fetchTicker(ticker.trim().toUpperCase())
      setData(response)
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to fetch ticker details.')
      setData(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section>
      <h2>Ticker Snapshot</h2>
      <form className="card form-grid" onSubmit={onSubmit}>
        <label>
          Stock ticker
          <input value={ticker} onChange={(event) => setTicker(event.target.value)} maxLength={10} />
        </label>
        <button type="submit" disabled={loading}>
          {loading ? 'Loading...' : 'Fetch Details'}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {data && (
        <article className="card metrics-grid">
          <Metric label="Company" value={data.company_name || 'n/a'} />
          <Metric label="Sector" value={data.sector || 'n/a'} />
          <Metric label="Industry" value={data.industry || 'n/a'} />
          <Metric label="Price" value={formatCurrency(data.current_price, data.currency)} />
          <Metric label="Market Cap" value={formatNumber(data.market_cap)} />
          <Metric label="P/E" value={formatDecimal(data.pe_ratio)} />
          <Metric label="Dividend Yield" value={formatPercent(data.dividend_yield)} />
          <Metric label="52 Week High" value={formatCurrency(data.fifty_two_week_high, data.currency)} />
          <Metric label="52 Week Low" value={formatCurrency(data.fifty_two_week_low, data.currency)} />
        </article>
      )}
    </section>
  )
}

function Metric({ label, value }) {
  return (
    <div>
      <p className="metric-label">{label}</p>
      <p className="metric-value">{value}</p>
    </div>
  )
}

function formatCurrency(value, currency = 'USD') {
  if (typeof value !== 'number') return 'n/a'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    maximumFractionDigits: 2,
  }).format(value)
}

function formatNumber(value) {
  if (typeof value !== 'number') return 'n/a'
  return new Intl.NumberFormat('en-US', { notation: 'compact' }).format(value)
}

function formatDecimal(value) {
  return typeof value === 'number' ? value.toFixed(2) : 'n/a'
}

function formatPercent(value) {
  return typeof value === 'number' ? `${(value * 100).toFixed(2)}%` : 'n/a'
}
