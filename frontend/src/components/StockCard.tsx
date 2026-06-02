import type { StockQuote } from '../types'
import './StockCard.css'

function fmt(n: number | null, opts?: Intl.NumberFormatOptions) {
  if (n == null) return '—'
  return n.toLocaleString(undefined, opts)
}

function pct(n: number | null) {
  if (n == null) return '—'
  const v = n < 1 ? n * 100 : n
  return `${v.toFixed(2)}%`
}

interface Props {
  stock: StockQuote
}

export default function StockCard({ stock }: Props) {
  return (
    <div className="stock-card">
      <div className="stock-card-head">
        <h2>{stock.ticker}</h2>
        <p className="stock-name">{stock.name}</p>
        {(stock.sector || stock.industry) && (
          <p className="stock-meta">
            {[stock.sector, stock.industry].filter(Boolean).join(' · ')}
          </p>
        )}
      </div>
      <dl className="stock-grid">
        <div>
          <dt>Price</dt>
          <dd>${fmt(stock.current_price, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</dd>
        </div>
        <div>
          <dt>Div. yield</dt>
          <dd>{pct(stock.dividend_yield)}</dd>
        </div>
        <div>
          <dt>Annual div.</dt>
          <dd>${fmt(stock.dividend_rate, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</dd>
        </div>
        <div>
          <dt>Payout ratio</dt>
          <dd>{pct(stock.payout_ratio)}</dd>
        </div>
        <div>
          <dt>P/E (TTM)</dt>
          <dd>{fmt(stock.trailing_pe, { maximumFractionDigits: 1 })}</dd>
        </div>
        <div>
          <dt>Market cap</dt>
          <dd>{stock.market_cap ? `$${(stock.market_cap / 1e9).toFixed(1)}B` : '—'}</dd>
        </div>
        <div>
          <dt>52W high</dt>
          <dd>${fmt(stock.fifty_two_week_high, { maximumFractionDigits: 2 })}</dd>
        </div>
        <div>
          <dt>52W low</dt>
          <dd>${fmt(stock.fifty_two_week_low, { maximumFractionDigits: 2 })}</dd>
        </div>
      </dl>
    </div>
  )
}
