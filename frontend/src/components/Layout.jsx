import { NavLink } from 'react-router-dom'

const links = [
  { to: '/ticker', label: 'Ticker Snapshot' },
  { to: '/valuation', label: 'Valuation (DCF + DDM)' },
  { to: '/dividend-safety', label: 'Dividend Safety AI' },
]

export default function Layout({ children }) {
  return (
    <div className="app-shell">
      <header>
        <h1>AI Dividend Growth Stock Evaluator</h1>
        <p>Analyze dividend stocks with valuation math and AI-assisted balance-sheet safety scoring.</p>
        <nav>
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) => (isActive ? 'active-link' : '')}
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </header>

      <main>{children}</main>
    </div>
  )
}
