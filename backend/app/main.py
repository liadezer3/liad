from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router
from app.settings import get_settings


settings = get_settings()

app = FastAPI(
    title="AI-Powered Dividend Growth Stock Evaluator",
    description=(
        "Stock profile retrieval, DCF/DDM valuation, and AI-prompted dividend "
        "safety analysis."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
