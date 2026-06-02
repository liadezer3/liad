import { NavLink, useParams } from "react-router-dom";
import { useTicker } from "../context/TickerContext.jsx";

function Logo() {
  return (
    <svg className="logo" viewBox="0 0 32 32" aria-hidden="true">
      <rect width="32" height="32" rx="7" fill="#0e7c66" />
      <path
        d="M7 21 L13 13 L18 17 L25 8"
        fill="none"
        stroke="#7ef0c8"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle cx="25" cy="8" r="2.4" fill="#7ef0c8" />
    </svg>
  );
}

export default function Navbar() {
  const { symbol } = useTicker();
  const params = useParams();
  const active = params.symbol || symbol;

  return (
    <nav className="navbar">
      <div className="navbar-inner container">
        <NavLink to="/" className="brand">
          <Logo />
          <span>DivGrowth Evaluator</span>
        </NavLink>
        <div className="nav-links">
          <NavLink to="/" className="nav-link" end>
            Search
          </NavLink>
          {active && (
            <>
              <NavLink to={`/overview/${active}`} className="nav-link">
                Overview
              </NavLink>
              <NavLink to={`/valuation/${active}`} className="nav-link">
                Valuation
              </NavLink>
              <NavLink to={`/analysis/${active}`} className="nav-link">
                AI Analysis
              </NavLink>
            </>
          )}
        </div>
        {active && (
          <span className="nav-ticker">
            Active: <strong>{active}</strong>
          </span>
        )}
      </div>
    </nav>
  );
}
