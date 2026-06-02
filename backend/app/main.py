from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import stock, valuation, analysis

app = FastAPI(
    title="Dividend Growth Stock Evaluator API",
    description="AI-powered API for evaluating dividend growth stocks via DCF, DDM, and AI safety scoring.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stock.router)
app.include_router(valuation.router)
app.include_router(analysis.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}
