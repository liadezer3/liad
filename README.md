# Dividend Growth Stock Evaluator

AI-powered web app for evaluating dividend growth stocks: live ticker data, DCF/DDM valuation, and balance-sheet-driven dividend safety scoring.

## Project structure

```
├── frontend/                 # React (Vite) UI — components & pages only
│   └── src/
│       ├── components/       # Layout, StockCard, forms
│       ├── pages/            # Home, Lookup, Valuation, Safety
│       └── api/              # HTTP client to backend
└── backend/                  # FastAPI + algorithmic core
    └── app/
        ├── algorithms/       # DCF, DDM (pure valuation math)
        ├── services/         # Market data, AI prompt layer
        └── api/              # REST routes
```

The frontend never embeds valuation logic; the backend keeps algorithms separate from HTTP and data-fetching services.

## Features

| Page | Capability |
|------|------------|
| **Stock Lookup** | Dividend yield, payout ratio, P/E, 52-week range via Yahoo Finance |
| **Valuation** | Discounted Cash Flow (DCF) and Gordon Growth Dividend Discount Model (DDM) |
| **Dividend Safety** | AI analysis of balance sheet trends (OpenAI) or rule-based fallback |
| **Job Scanner Agent** | Location-aware job search organized by salary, title, location, and rating |

## Quick start

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # optional: set OPENAI_API_KEY for AI safety scores
chmod +x run.sh && ./run.sh
```

API: http://127.0.0.1:8000 — docs at http://127.0.0.1:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173 (proxies `/api` to the backend)

### Optional: AI dividend safety

Set `OPENAI_API_KEY` in `backend/.env`. Without it, safety analysis uses a transparent rule-based scorer over payout ratio, leverage, cash, retained earnings, and FCF coverage.

## API endpoints

- `GET /api/stocks/{ticker}` — quote & dividend metrics
- `POST /api/valuation/dcf` — DCF intrinsic value
- `POST /api/valuation/ddm` — DDM fair value
- `POST /api/analysis/dividend-safety` — safety score 0–100
- `POST /api/agents/job-scanner` — organized job listings from configured job sources

## Tests

```bash
cd backend && source .venv/bin/activate && pytest
```

## Disclaimer

For education and research only. Not financial advice. Market data accuracy depends on third-party providers.
