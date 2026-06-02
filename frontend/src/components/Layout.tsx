import { Link, Outlet, useLocation } from 'react-router-dom'
import './Layout.css'

const nav = [
  { to: '/', label: 'Home' },
  { to: '/lookup', label: 'Stock Lookup' },
  { to: '/valuation', label: 'Valuation' },
  { to: '/safety', label: 'Dividend Safety' },
]

export default function Layout() {
  const { pathname } = useLocation()

  return (
    <div className="app-shell">
      <header className="app-header">
        <Link to="/" className="brand">
          <span className="brand-mark">DG</span>
          <span>Dividend Growth Evaluator</span>
        </Link>
        <nav className="app-nav">
          {nav.map(({ to, label }) => (
            <Link
              key={to}
              to={to}
              className={pathname === to ? 'nav-link active' : 'nav-link'}
            >
              {label}
            </Link>
          ))}
        </nav>
      </header>
      <main className="app-main">
        <Outlet />
      </main>
      <footer className="app-footer">
        Educational tool — not investment advice. Data via Yahoo Finance.
      </footer>
    </div>
  )
}
