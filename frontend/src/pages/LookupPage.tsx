import { useState } from 'react'
import { fetchStock } from '../api/client'
import StockCard from '../components/StockCard'
import TickerForm from '../components/TickerForm'
import type { StockQuote } from '../types'
import './PageShared.css'

export default function LookupPage() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [stock, setStock] = useState<StockQuote | null>(null)

  async function handleLookup(ticker: string) {
    setLoading(true)
    setError(null)
    try {
      const data = await fetchStock(ticker)
      setStock(data)
    } catch (e) {
      setStock(null)
      setError(e instanceof Error ? e.message : 'Failed to fetch stock')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <h1>Stock Lookup</h1>
        <p>Enter a ticker to load dividend-focused fundamentals from Yahoo Finance.</p>
      </header>
      <TickerForm onSubmit={handleLookup} loading={loading} label="Fetch" />
      {error && <p className="error-banner">{error}</p>}
      {stock && <StockCard stock={stock} />}
    </div>
  )
}
