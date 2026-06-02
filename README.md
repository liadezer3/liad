# AI-Powered Dividend Growth Stock Evaluator

A multi-page web application that helps you research dividend-growth stocks. It
fetches ticker fundamentals, runs **Discounted Cash Flow (DCF)** and **Dividend
Discount Model (DDM)** valuations, and uses an **AI prompt layer** to analyze a
company's historical balance sheets and produce a **dividend-safety score**.

> ⚠️ For educational and informational purposes only. This is **not** investment
> advice.

## Architecture

The repository cleanly separates the **frontend UI** from the **algorithmic
backend**:

```
.
├── backend/                # Python · FastAPI (algorithms + AI prompt layer)
│   ├── app/
│   │   ├── main.py         # FastAPI app + CORS + routers
│   │   ├── config.py       # env-driven settings
│   │   ├── models/         # Pydantic request/response schemas
│   │   ├── routers/        # /api/stocks, /api/valuation, /api/analysis
│   │   ├── services/       # market_data · valuation (DCF/DDM) · ai_analysis
│   │   └── data/           # bundled sample fixtures (offline fallback)
│   └── requirements.txt
│
└── frontend/               # JavaScript · React + Vite (presentation)
    ├── src/
    │   ├── pages/          # Home, Overview, Valuation, AI Analysis
    │   ├── components/     # Navbar, search, gauges, metric cards
    │   ├── context/        # shared active-ticker state
    │   ├── hooks/          # deep-link ticker loader
    │   └── api/            # typed REST client
    └── package.json
```

### Backend (FastAPI)

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/api/health` | GET | Service health + active AI engine |
| `/api/stocks/directory` | GET | Bundled sample-ticker directory |
| `/api/stocks/{ticker}` | GET | Ticker profile + multi-year balance sheets |
| `/api/valuation/dcf` | POST | Two-stage Discounted Cash Flow valuation |
| `/api/valuation/ddm` | POST | Two-stage Dividend Discount Model valuation |
| `/api/analysis/dividend-safety` | POST | AI dividend-safety score from balance sheets |

- **Market data** is fetched live via `yfinance`. When the network is
  unavailable or a ticker is incomplete, the API transparently falls back to
  bundled sample fixtures (`JNJ`, `KO`, `PG`, `PEP`, `MSFT`) so the app always
  works.
- **Valuation** implements a two-stage DCF on free cash flow per share and a
  two-stage Gordon-growth DDM, each returning fair value, upside, and a verdict.
- **AI prompt layer** derives financial features (payout ratio, FCF coverage,
  leverage, liquidity, dividend-growth streak) from historical balance sheets
  and either sends them through a structured prompt to an OpenAI-compatible LLM
  (`AI_PROVIDER=llm`) or scores them with a transparent, deterministic heuristic
  engine. Both paths return the same schema, so no API key is required to use
  the app.

### Frontend (React + Vite)

A multi-page SPA (React Router) with a modern dark UI and Recharts
visualizations:

1. **Search** – find a ticker or pick a sample dividend grower.
2. **Overview** – price, yield, payout, dividend-growth streak, balance-sheet
   table, and a FCF-vs-dividends chart.
3. **Valuation** – interactive DCF & DDM with adjustable assumptions.
4. **AI Analysis** – dividend-safety gauge, strengths/risks, and contributing
   factors.

## Getting started

### Prerequisites

- Python 3.10+
- Node.js 18+

### 1. Run the backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate   # optional
pip install -r requirements.txt
cp .env.example .env                                  # optional, for LLM mode
uvicorn app.main:app --reload --port 8000
```

The API is now at `http://127.0.0.1:8000` (interactive docs at `/docs`).

### 2. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The Vite dev server proxies `/api` to the backend,
so no extra CORS configuration is needed in development.

### Enabling the real LLM (optional)

By default the AI analysis uses the offline heuristic engine. To use a real
OpenAI-compatible model, set the following in `backend/.env`:

```env
AI_PROVIDER=llm
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

If the key is missing or the request fails, the service automatically falls back
to the heuristic engine.

## Tech stack

- **Backend:** FastAPI, Pydantic v2, yfinance, httpx, Uvicorn
- **Frontend:** React 18, Vite 5, React Router 6, Recharts
