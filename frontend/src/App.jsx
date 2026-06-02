import { Routes, Route, Navigate } from "react-router-dom";
import Navbar from "./components/Navbar.jsx";
import HomePage from "./pages/HomePage.jsx";
import OverviewPage from "./pages/OverviewPage.jsx";
import ValuationPage from "./pages/ValuationPage.jsx";
import AnalysisPage from "./pages/AnalysisPage.jsx";

export default function App() {
  return (
    <>
      <Navbar />
      <main className="container">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/overview/:symbol" element={<OverviewPage />} />
          <Route path="/valuation/:symbol" element={<ValuationPage />} />
          <Route path="/analysis/:symbol" element={<AnalysisPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      <footer className="footer container">
        Dividend Growth Stock Evaluator · For educational and informational use
        only — not investment advice.
      </footer>
    </>
  );
}
