from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router


def create_app() -> FastAPI:
    load_dotenv()

    app = FastAPI(
        title="AI Dividend Growth Stock Evaluator",
        description=(
            "FastAPI backend that retrieves ticker data, computes valuation metrics, "
            "and performs AI-assisted dividend safety analysis."
        ),
        version="0.1.0",
    )

    allowed_origins = [
        origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router, prefix="/api")
    return app


app = create_app()
