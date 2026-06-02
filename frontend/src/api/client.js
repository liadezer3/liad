import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 30000,
})

export async function fetchTicker(ticker) {
  const { data } = await api.get(`/api/ticker/${ticker}`)
  return data
}

export async function runValuation(payload) {
  const { data } = await api.post('/api/valuation', payload)
  return data
}

export async function runDividendSafety(payload) {
  const { data } = await api.post('/api/dividend-safety', payload)
  return data
}
