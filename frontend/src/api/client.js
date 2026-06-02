// Thin wrapper around the backend REST API.
// All requests go through /api which Vite proxies to FastAPI in dev.

const BASE = import.meta.env.VITE_API_BASE || "";

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      /* ignore JSON parse errors */
    }
    throw new Error(detail);
  }
  return res.json();
}

export const api = {
  health: () => request("/api/health"),
  directory: () => request("/api/stocks/directory"),
  ticker: (symbol) => request(`/api/stocks/${encodeURIComponent(symbol)}`),
  dcf: (body) =>
    request("/api/valuation/dcf", { method: "POST", body: JSON.stringify(body) }),
  ddm: (body) =>
    request("/api/valuation/ddm", { method: "POST", body: JSON.stringify(body) }),
  dividendSafety: (ticker) =>
    request("/api/analysis/dividend-safety", {
      method: "POST",
      body: JSON.stringify({ ticker }),
    }),
};
