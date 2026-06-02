import { Link, useLocation } from "react-router-dom";
import { TrendingUp, BarChart2, Shield, Home, Activity } from "lucide-react";

const links = [
  { to: "/", label: "Search", icon: Home },
  { to: "/overview", label: "Overview", icon: Activity },
  { to: "/dcf", label: "DCF", icon: TrendingUp },
  { to: "/ddm", label: "DDM", icon: BarChart2 },
  { to: "/safety", label: "Safety Score", icon: Shield },
];

export default function Navbar() {
  const location = useLocation();

  return (
    <nav className="sticky top-0 z-50 border-b border-slate-800 bg-slate-950/90 backdrop-blur-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center">
              <TrendingUp className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold text-white text-lg">DividendIQ</span>
          </Link>

          <div className="flex items-center gap-1">
            {links.map(({ to, label, icon: Icon }) => {
              const active = location.pathname === to;
              return (
                <Link
                  key={to}
                  to={to}
                  className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    active
                      ? "bg-brand-600/20 text-brand-400"
                      : "text-slate-400 hover:text-slate-100 hover:bg-slate-800"
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">{label}</span>
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
}
