# AI Dividend Growth Stock Evaluator

This project contains a multi-page React frontend and a FastAPI backend for evaluating dividend growth stocks.

## Project structure

- `frontend/` - Vite + React client with pages for ticker snapshot, valuation, and dividend safety.
- `backend/` - FastAPI API with ticker retrieval, DCF/DDM valuation models, and AI prompt-based dividend safety scoring.

## Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Optional AI configuration (for live LLM scoring): copy `backend/.env.example` to `backend/.env` and set `OPENAI_API_KEY`.

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Frontend defaults to `http://localhost:5173` and proxies API requests to `http://localhost:8000`.

## API endpoints

- `GET /api/health`
- `GET /api/ticker/{ticker}`
- `POST /api/valuation`
- `POST /api/dividend-safety`

## Notes

- Market data is pulled via `yfinance`.
- The dividend safety service always builds an AI prompt payload; without API credentials it falls back to a deterministic heuristic score.
