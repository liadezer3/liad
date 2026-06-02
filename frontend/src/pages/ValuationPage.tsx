import { useState } from 'react'
import { runDCF, runDDM } from '../api/client'
import MetricBadge from '../components/MetricBadge'
import TickerForm from '../components/TickerForm'
import type { DCFResult, DDMResult } from '../types'
import './PageShared.css'
import './ValuationPage.css'

export default function ValuationPage() {
  const [ticker, setTicker] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [dcf, setDcf] = useState<DCFResult | null>(null)
  const [ddm, setDdm] = useState<DDMResult | null>(null)

  const [discountRate, setDiscountRate] = useState(10)
  const [terminalGrowth, setTerminalGrowth] = useState(2.5)
  const [projectionYears, setProjectionYears] = useState(5)
  const [requiredReturn, setRequiredReturn] = useState(9)
  const [divGrowth, setDivGrowth] = useState('')

  async function handleValuate(t: string) {
    setTicker(t)
    setLoading(true)
    setError(null)
    setDcf(null)
    setDdm(null)
    try {
      const [dcfRes, ddmRes] = await Promise.all([
        runDCF({
          ticker: t,
          discount_rate: discountRate / 100,
          terminal_growth_rate: terminalGrowth / 100,
          projection_years: projectionYears,
        }),
        runDDM({
          ticker: t,
          required_return: requiredReturn / 100,
          dividend_growth_rate: divGrowth ? parseFloat(divGrowth) / 100 : undefined,
        }),
      ])
      setDcf(dcfRes)
      setDdm(ddmRes)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Valuation failed')
    } finally {
      setLoading(false)
    }
  }

  function upsideVariant(pct: number | null) {
    if (pct == null) return 'neutral' as const
    return pct >= 0 ? 'positive' : 'negative'
  }

  return (
    <div className="page">
      <header className="page-header">
        <h1>Valuation Models</h1>
        <p>Discounted Cash Flow (DCF) and Gordon Growth Dividend Discount Model (DDM).</p>
      </header>

      <section className="assumptions card">
        <h2>Assumptions</h2>
        <div className="assumption-grid">
          <label>
            Discount rate (%)
            <input
              type="number"
              value={discountRate}
              onChange={(e) => setDiscountRate(Number(e.target.value))}
              min={1}
              max={30}
              step={0.5}
            />
          </label>
          <label>
            Terminal growth (%)
            <input
              type="number"
              value={terminalGrowth}
              onChange={(e) => setTerminalGrowth(Number(e.target.value))}
              min={0}
              max={10}
              step={0.25}
            />
          </label>
          <label>
            Projection years
            <input
              type="number"
              value={projectionYears}
              onChange={(e) => setProjectionYears(Number(e.target.value))}
              min={3}
              max={10}
            />
          </label>
          <label>
            Required return — DDM (%)
            <input
              type="number"
              value={requiredReturn}
              onChange={(e) => setRequiredReturn(Number(e.target.value))}
              min={1}
              max={30}
              step={0.5}
            />
          </label>
          <label>
            Div. growth override (%)
            <input
              type="number"
              placeholder="Auto"
              value={divGrowth}
              onChange={(e) => setDivGrowth(e.target.value)}
              min={0}
              max={20}
              step={0.5}
            />
          </label>
        </div>
      </section>

      <TickerForm onSubmit={handleValuate} loading={loading} label="Run models" />

      {error && <p className="error-banner">{error}</p>}

      {ticker && (dcf || ddm) && (
        <div className="results-grid">
          {dcf && (
            <section className="result-panel card">
              <h2>DCF — {dcf.ticker}</h2>
              <div className="metrics-row">
                <MetricBadge
                  label="Intrinsic value"
                  value={`$${dcf.intrinsic_value_per_share.toFixed(2)}`}
                />
                <MetricBadge
                  label="Upside vs price"
                  value={dcf.upside_pct != null ? `${dcf.upside_pct}%` : '—'}
                  variant={upsideVariant(dcf.upside_pct)}
                />
              </div>
              <h3>Projected FCF</h3>
              <ul className="fcf-list">
                {dcf.projected_fcf.map((v, i) => (
                  <li key={i}>
                    Year {i + 1}: ${(v / 1e6).toFixed(1)}M
                  </li>
                ))}
              </ul>
            </section>
          )}
          {ddm && (
            <section className="result-panel card">
              <h2>DDM — {ddm.ticker}</h2>
              <div className="metrics-row">
                <MetricBadge
                  label="Fair value"
                  value={`$${ddm.fair_value_per_share.toFixed(2)}`}
                />
                <MetricBadge
                  label="Upside vs price"
                  value={ddm.upside_pct != null ? `${ddm.upside_pct}%` : '—'}
                  variant={upsideVariant(ddm.upside_pct)}
                />
              </div>
              <dl className="ddm-details">
                <div>
                  <dt>Annual dividend</dt>
                  <dd>${ddm.annual_dividend.toFixed(2)}</dd>
                </div>
                <div>
                  <dt>Growth rate used</dt>
                  <dd>{(ddm.growth_rate_used * 100).toFixed(2)}%</dd>
                </div>
                <div>
                  <dt>Required return</dt>
                  <dd>{(ddm.required_return * 100).toFixed(2)}%</dd>
                </div>
              </dl>
            </section>
          )}
        </div>
      )}
    </div>
  )
}
