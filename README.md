# AI-Powered Dividend Growth Stock Evaluator

A multi-page web application for researching dividend growth stocks. The project
is intentionally split into a React/Vite frontend and an algorithmic FastAPI
backend.

## Project structure

```text
.
├── backend/          # FastAPI API, market data adapters, valuation algorithms
└── frontend/         # Vite + React application and routed UI pages
```

## Features

- Fetch stock ticker details through the backend API.
- Calculate Discounted Cash Flow (DCF) and Dividend Discount Model (DDM)
  valuation estimates.
- Analyze historical balance sheets and cash-flow coverage with an AI prompt
  layer that produces dividend safety scores.
- Multi-page React UI for overview, valuation, dividend safety, and
  methodology.
- Works out of the box with sample ticker data; optionally integrates with
  Alpha Vantage for live quote/company overview data.

## Backend setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Optional environment variables:

```bash
export ALPHA_VANTAGE_API_KEY=your_key
export FRONTEND_ORIGIN=http://localhost:5173
```

The API runs at `http://localhost:8000`.

Useful endpoints:

- `GET /api/health`
- `GET /api/stocks/{ticker}`
- `POST /api/stocks/{ticker}/analyze`

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173` and expects the API at
`http://localhost:8000`. Override this with:

```bash
VITE_API_BASE_URL=http://localhost:8000 npm run dev
```

## Notes

This project is a research aid and does not provide financial advice. The sample
data and valuation outputs are illustrative and should be verified against
primary filings before making investment decisions.
