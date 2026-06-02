"""FastAPI application entry point for the Dividend Growth Stock Evaluator."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import analysis, stocks, valuation

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Backend for an AI-powered Dividend Growth Stock Evaluator. Provides "
        "ticker fundamentals, DCF & DDM valuation, and an AI prompt layer that "
        "scores dividend safety from historical balance sheets."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stocks.router)
app.include_router(valuation.router)
app.include_router(analysis.router)


@app.get("/api/health", tags=["meta"])
def health() -> dict:
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        "ai_engine": "llm" if settings.llm_enabled else "heuristic",
    }


@app.get("/", tags=["meta"])
def root() -> dict:
    return {
        "message": "Dividend Growth Stock Evaluator API",
        "docs": "/docs",
        "health": "/api/health",
    }
