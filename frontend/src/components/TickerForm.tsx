import { useState, type FormEvent } from 'react'
import './TickerForm.css'

interface Props {
  onSubmit: (ticker: string) => void
  loading?: boolean
  label?: string
  defaultTicker?: string
}

export default function TickerForm({
  onSubmit,
  loading,
  label = 'Analyze',
  defaultTicker = '',
}: Props) {
  const [ticker, setTicker] = useState(defaultTicker)

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const t = ticker.trim().toUpperCase()
    if (t) onSubmit(t)
  }

  return (
    <form className="ticker-form" onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="e.g. JNJ, KO, PG"
        value={ticker}
        onChange={(e) => setTicker(e.target.value.toUpperCase())}
        maxLength={10}
        aria-label="Stock ticker"
      />
      <button type="submit" disabled={loading || !ticker.trim()}>
        {loading ? 'Loading…' : label}
      </button>
    </form>
  )
}
