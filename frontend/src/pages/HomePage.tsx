import { Link } from 'react-router-dom'
import './HomePage.css'

const features = [
  {
    title: 'Stock Lookup',
    desc: 'Fetch live ticker details — yield, payout ratio, sector, and price range.',
    to: '/lookup',
  },
  {
    title: 'DCF & DDM Valuation',
    desc: 'Run Discounted Cash Flow and Gordon Growth Dividend Discount models with adjustable assumptions.',
    to: '/valuation',
  },
  {
    title: 'Dividend Safety',
    desc: 'AI-assisted balance sheet analysis scores dividend sustainability from 0–100.',
    to: '/safety',
  },
  {
    title: 'Job Scanner Agent',
    desc: 'Request location permission and organize nearby jobs by salary, title, location, and rating.',
    to: '/jobs',
  },
  {
    title: 'Music Player',
    desc: 'Stream your SoundCloud playlists in a clean, ad-free interface with full playback controls.',
    to: '/music',
  },
]

export default function HomePage() {
  return (
    <div className="home">
      <section className="hero">
        <p className="eyebrow">AI-Powered Dividend Growth Investing</p>
        <h1>Evaluate dividend stocks with data and discipline</h1>
        <p className="hero-lead">
          Combine fundamental valuation (DCF, DDM) with balance-sheet-driven dividend safety
          scoring — built for long-term dividend growth investors.
        </p>
        <div className="hero-actions">
          <Link to="/lookup" className="btn primary">
            Look up a stock
          </Link>
          <Link to="/valuation" className="btn secondary">
            Run valuation
          </Link>
          <Link to="/jobs" className="btn secondary">
            Scan jobs
          </Link>
        </div>
      </section>
      <section className="feature-grid">
        {features.map((f) => (
          <Link key={f.to} to={f.to} className="feature-card">
            <h3>{f.title}</h3>
            <p>{f.desc}</p>
            <span className="feature-link">Open →</span>
          </Link>
        ))}
      </section>
      <section className="arch-note card">
        <h3>Architecture</h3>
        <p>
          The <strong>frontend</strong> (<code>frontend/src/components</code>) handles UI and routing.
          The <strong>algorithmic backend</strong> (<code>backend/app/algorithms</code>) implements DCF/DDM;
          services layer fetches market data and runs the AI prompt layer for safety analysis.
        </p>
      </section>
    </div>
  )
}
