import { useState } from 'react'

import { runDividendSafety } from '../api/client'

export default function DividendSafetyPage() {
  const [ticker, setTicker] = useState('MSFT')
  const [lookbackYears, setLookbackYears] = useState(5)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [data, setData] = useState(null)

  async function onSubmit(event) {
    event.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await runDividendSafety({
        ticker: ticker.trim().toUpperCase(),
        lookback_years: Number(lookbackYears),
      })
      setData(response)
    } catch (err) {
      setError(err?.response?.data?.detail || 'Dividend safety analysis failed.')
      setData(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section>
      <h2>AI Dividend Safety Score</h2>
      <form className="card form-grid" onSubmit={onSubmit}>
        <label>
          Ticker
          <input value={ticker} onChange={(event) => setTicker(event.target.value)} maxLength={10} />
        </label>

        <label>
          Lookback years
          <input
            type="number"
            min="3"
            max="10"
            value={lookbackYears}
            onChange={(event) => setLookbackYears(event.target.value)}
          />
        </label>

        <button type="submit" disabled={loading}>
          {loading ? 'Analyzing...' : 'Run Safety Analysis'}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {data && (
        <article className="card">
          <h3>{data.ticker}</h3>
          <p>
            <strong>Score:</strong> {data.score}/100 ({data.rating})
          </p>
          <p>
            <strong>Analysis source:</strong> {data.source}
          </p>

          <h4>Reasoning</h4>
          <ul>
            {data.reasoning.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>

          <details>
            <summary>Prompt payload used for AI analysis</summary>
            <pre>{data.prompt}</pre>
          </details>
        </article>
      )}
    </section>
  )
}
