import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import HomePage from "./pages/HomePage";
import OverviewPage from "./pages/OverviewPage";
import DCFPage from "./pages/DCFPage";
import DDMPage from "./pages/DDMPage";
import SafetyPage from "./pages/SafetyPage";

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/overview" element={<OverviewPage />} />
            <Route path="/dcf" element={<DCFPage />} />
            <Route path="/ddm" element={<DDMPage />} />
            <Route path="/safety" element={<SafetyPage />} />
          </Routes>
        </main>
        <footer className="border-t border-slate-800 py-4 text-center text-xs text-slate-600">
          DividendIQ — For educational purposes only. Not financial advice.
        </footer>
      </div>
    </BrowserRouter>
  );
}
