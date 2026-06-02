import { Navigate, Route, Routes } from 'react-router-dom'

import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import ValuationPage from './pages/ValuationPage'
import DividendSafetyPage from './pages/DividendSafetyPage'

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/ticker" replace />} />
        <Route path="/ticker" element={<HomePage />} />
        <Route path="/valuation" element={<ValuationPage />} />
        <Route path="/dividend-safety" element={<DividendSafetyPage />} />
      </Routes>
    </Layout>
  )
}
