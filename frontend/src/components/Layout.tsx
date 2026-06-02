import { NavLink, Outlet } from "react-router-dom";

export function Layout() {
  return (
    <div className="app-shell">
      <header className="site-header">
        <div>
          <p className="eyebrow">AI dividend research</p>
          <h1>Dividend Growth Stock Evaluator</h1>
        </div>
        <nav className="site-nav" aria-label="Primary navigation">
          <NavLink to="/">Overview</NavLink>
          <NavLink to="/valuation">Valuation</NavLink>
          <NavLink to="/safety">Dividend Safety</NavLink>
          <NavLink to="/methodology">Methodology</NavLink>
        </nav>
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  );
}
