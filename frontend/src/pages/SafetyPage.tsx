import { useState } from 'react'
import { analyzeDividendSafety } from '../api/client'
import TickerForm from '../components/TickerForm'
import type { DividendSafetyResult } from '../types'
import './PageShared.css'
import './SafetyPage.css'

function scoreColor(score: number) {
  if (score >= 85) return 'excellent'
  if (score >= 70) return 'good'
  if (score >= 55) return 'fair'
  if (score >= 40) return 'weak'
  return 'risk'
}

export default function SafetyPage() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<DividendSafetyResult | null>(null)

  async function handleAnalyze(ticker: string) {
    setLoading(true)
    setError(null)
    try {
      const data = await analyzeDividendSafety(ticker)
      setResult(data)
    } catch (e) {
      setResult(null)
      setError(e instanceof Error ? e.message : 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <h1>Dividend Safety Analysis</h1>
        <p>
          Balance sheet trends are analyzed via an AI prompt layer (OpenAI) when configured,
          or a rule-based scorer otherwise.
        </p>
      </header>

      <TickerForm onSubmit={handleAnalyze} loading={loading} label="Analyze safety" />

      {error && <p className="error-banner">{error}</p>}

      {result && (
        <div className="safety-results">
          <div className={`score-ring ${scoreColor(result.safety_score)}`}>
            <span className="score-value">{result.safety_score}</span>
            <span className="score-label">Safety score</span>
          </div>

          <div className="safety-main card">
            <div className="safety-head">
              <h2>
                {result.ticker} — {result.rating}
              </h2>
              <span className={`badge ${result.ai_powered ? 'ai' : 'rules'}`}>
                {result.ai_powered ? 'AI-powered' : 'Rule-based'}
              </span>
            </div>
            <p className="summary">{result.summary}</p>

            {result.factors.length > 0 && (
              <>
                <h3>Key factors</h3>
                <ul className="factor-list">
                  {result.factors.map((f, i) => (
                    <li key={i} className={`impact-${f.impact}`}>
                      <strong>{f.name}</strong>
                      <span>{f.detail}</span>
                    </li>
                  ))}
                </ul>
              </>
            )}

            {Object.keys(result.balance_sheet_highlights).length > 0 && (
              <>
                <h3>Balance sheet highlights</h3>
                <table className="bs-table">
                  <thead>
                    <tr>
                      <th>Line item</th>
                      <th>Prior period</th>
                      <th>Latest</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(result.balance_sheet_highlights).map(([key, vals]) => (
                      <tr key={key}>
                        <td>{key}</td>
                        <td>{vals[0] != null ? vals[0].toLocaleString() : '—'}</td>
                        <td>{vals[1] != null ? vals[1].toLocaleString() : vals[0]?.toLocaleString() ?? '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
