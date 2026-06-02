# DividendIQ — AI-Powered Dividend Growth Stock Evaluator

A full-stack web application that fetches stock data, computes financial valuations (DCF & DDM), and uses an AI prompt layer to generate dividend safety scores.

## Project Structure

```
/
├── backend/                  # FastAPI Python backend
│   ├── app/
│   │   ├── main.py           # App entry point, CORS, router registration
│   │   ├── config.py         # Pydantic Settings (env vars)
│   │   ├── models/
│   │   │   └── stock.py      # Pydantic request/response schemas
│   │   ├── routers/
│   │   │   ├── stock.py      # GET /api/stock/{ticker}
│   │   │   ├── valuation.py  # POST /api/valuation/dcf  +  /ddm
│   │   │   └── analysis.py   # POST /api/analysis/dividend-safety
│   │   └── services/
│   │       ├── stock_service.py   # yfinance data fetching, DCF, DDM math
│   │       └── ai_service.py      # OpenAI prompt layer for safety score
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/                 # React + Vite TypeScript frontend
    ├── src/
    │   ├── components/       # Reusable UI components
    │   │   ├── Navbar.tsx
    │   │   ├── TickerInput.tsx
    │   │   ├── MetricCard.tsx
    │   │   ├── ValuationBadge.tsx
    │   │   ├── ErrorAlert.tsx
    │   │   └── LoadingSpinner.tsx
    │   ├── pages/            # Route-level page components
    │   │   ├── HomePage.tsx        # Search / landing page
    │   │   ├── OverviewPage.tsx    # Stock overview + key metrics
    │   │   ├── DCFPage.tsx         # DCF analysis with chart
    │   │   ├── DDMPage.tsx         # DDM analysis with comparison chart
    │   │   └── SafetyPage.tsx      # AI dividend safety score + gauge
    │   ├── services/
    │   │   └── api.ts        # Axios API service layer
    │   └── utils/
    │       └── format.ts     # Currency / percentage formatters
    ├── tailwind.config.js
    ├── vite.config.ts
    └── .env.example
```

## Features

| Feature | Description |
|---|---|
| Stock Overview | Live price, P/E, dividend yield, 52-week range, sector, description |
| DCF Analysis | Multi-year FCF projection with customizable WACC and terminal growth rate |
| DDM Analysis | Gordon Growth and Multi-Stage Dividend Discount models |
| AI Safety Score | GPT-powered 0–100 score with grade, summary, strengths & risks |

## Prerequisites

- Python 3.11+
- Node.js 20+
- OpenAI API key (for the AI Safety Score feature)

## Backend Setup

```bash
cd backend
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API will be live at `http://localhost:8000`. Interactive docs: `http://localhost:8000/docs`.

## Frontend Setup

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

The app will open at `http://localhost:5173`.

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/stock/{ticker}` | Fetch stock overview |
| POST | `/api/valuation/dcf` | Run DCF analysis |
| POST | `/api/valuation/ddm` | Run DDM analysis |
| POST | `/api/analysis/dividend-safety` | AI dividend safety score |
| GET | `/api/health` | Health check |

## Environment Variables

### Backend (`backend/.env`)

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | Required for AI safety score |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model to use |
| `ALLOWED_ORIGINS` | `http://localhost:5173` | CORS allowed origins |

### Frontend (`frontend/.env`)

| Variable | Default | Description |
|---|---|---|
| `VITE_API_URL` | `http://localhost:8000` | Backend base URL |

## Disclaimer

This application is for educational purposes only and does not constitute financial advice. Always do your own research before making investment decisions.
