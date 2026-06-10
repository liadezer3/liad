# AGENTS.md

## Cursor Cloud specific instructions

### Architecture

Full-stack **Dividend Growth Stock Evaluator**: React (Vite) frontend + FastAPI backend. No database or Docker Compose. Live market data comes from Yahoo Finance via `yfinance` (outbound internet required).

### Services (both required for UI E2E)

| Service | Port | Start command |
|---------|------|---------------|
| Backend API | 8000 | `cd backend && source .venv/bin/activate && ./run.sh` |
| Frontend dev server | 5173 | `cd frontend && npm run dev` |

Use **tmux** for long-running dev servers. The backend binds to `0.0.0.0:8000`; Vite serves on `http://localhost:5173` and proxies `/api` and `/health` to the backend (see `frontend/vite.config.ts`).

### System dependency (one-time on fresh Ubuntu)

`python3 -m venv` requires the `python3.12-venv` apt package if venv creation fails with "ensurepip is not available".

### Optional configuration

Copy `backend/.env.example` to `backend/.env` and set `OPENAI_API_KEY` for AI-powered dividend safety scores. Without it, safety analysis uses a rule-based fallback.

### Lint / test / build

See `README.md` for canonical commands:

- **Backend tests:** `cd backend && source .venv/bin/activate && pytest`
- **Frontend lint:** `cd frontend && npm run lint`
- **Frontend build:** `cd frontend && npm run build`

Backend tests cover DCF/DDM math only (no live network). Stock lookup, valuation, and safety endpoints need the backend running plus Yahoo Finance access.

### Gotchas

- Vite may respond on `http://localhost:5173` but not `http://127.0.0.1:5173` in this environment; use `localhost` for browser and curl checks against the frontend.
- Reinstalling Python deps while uvicorn `--reload` is running usually picks up changes; if imports fail after a major dependency change, restart the backend tmux session.
