import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import LookupPage from './pages/LookupPage'
import SafetyPage from './pages/SafetyPage'
import ValuationPage from './pages/ValuationPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="lookup" element={<LookupPage />} />
          <Route path="valuation" element={<ValuationPage />} />
          <Route path="safety" element={<SafetyPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
