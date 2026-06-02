import { useState } from 'react'

import { runValuation } from '../api/client'

const defaultState = {
  ticker: 'MSFT',
  forecast_years: 5,
  fcf_growth_rate: 0.06,
  discount_rate: 0.1,
  terminal_growth_rate: 0.03,
  required_return: 0.09,
  dividend_growth_rate: 0.05,
}

export default function ValuationPage() {
  const [formState, setFormState] = useState(defaultState)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [data, setData] = useState(null)

  function onChange(event) {
    const { name, value } = event.target
    setFormState((prev) => ({ ...prev, [name]: name === 'ticker' ? value : Number(value) }))
  }

  async function onSubmit(event) {
    event.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await runValuation({
        ...formState,
        ticker: formState.ticker.trim().toUpperCase(),
      })
      setData(response)
    } catch (err) {
      setError(err?.response?.data?.detail || 'Valuation analysis failed.')
      setData(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section>
      <h2>Valuation Models</h2>
      <form className="card form-grid" onSubmit={onSubmit}>
        <label>
          Ticker
          <input name="ticker" maxLength={10} value={formState.ticker} onChange={onChange} />
        </label>

        <label>
          Forecast years
          <input type="number" name="forecast_years" min="3" max="10" value={formState.forecast_years} onChange={onChange} />
        </label>

        <label>
          FCF growth rate
          <input type="number" step="0.005" name="fcf_growth_rate" value={formState.fcf_growth_rate} onChange={onChange} />
        </label>

        <label>
          Discount rate
          <input type="number" step="0.005" name="discount_rate" value={formState.discount_rate} onChange={onChange} />
        </label>

        <label>
          Terminal growth rate
          <input type="number" step="0.005" name="terminal_growth_rate" value={formState.terminal_growth_rate} onChange={onChange} />
        </label>

        <label>
          Required return (DDM)
          <input type="number" step="0.005" name="required_return" value={formState.required_return} onChange={onChange} />
        </label>

        <label>
          Dividend growth rate
          <input type="number" step="0.005" name="dividend_growth_rate" value={formState.dividend_growth_rate} onChange={onChange} />
        </label>

        <button type="submit" disabled={loading}>
          {loading ? 'Calculating...' : 'Run Valuation'}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {data && (
        <div className="results-stack">
          <ModelCard title="Discounted Cash Flow" metric={data.dcf} />
          <ModelCard title="Dividend Discount Model" metric={data.ddm} />
        </div>
      )}
    </section>
  )
}

function ModelCard({ title, metric }) {
  return (
    <article className="card">
      <h3>{title}</h3>
      <p><strong>Intrinsic Value / Share:</strong> {formatCurrency(metric.intrinsic_value_per_share)}</p>
      <p><strong>Current Price:</strong> {formatCurrency(metric.current_price)}</p>
      <p><strong>Margin of Safety:</strong> {formatPercent(metric.margin_of_safety)}</p>
      <h4>Assumptions</h4>
      <ul>
        {Object.entries(metric.assumptions).map(([key, value]) => (
          <li key={key}>{key}: {typeof value === 'number' ? value.toFixed(4) : String(value)}</li>
        ))}
      </ul>
      {metric.notes.length > 0 && (
        <>
          <h4>Notes</h4>
          <ul>
            {metric.notes.map((note) => (
              <li key={note}>{note}</li>
            ))}
          </ul>
        </>
      )}
    </article>
  )
}

function formatCurrency(value) {
  if (typeof value !== 'number') return 'n/a'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 2,
  }).format(value)
}

function formatPercent(value) {
  if (typeof value !== 'number') return 'n/a'
  return `${(value * 100).toFixed(2)}%`
}
