from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.soundcloud_routes import router
from app.config import settings

app = FastAPI(
    title="Wavebox — SoundCloud Playlist Player",
    description="Ad-free SoundCloud playlist player powered by the SoundCloud API",
    version="1.0.0",
)

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=settings.session_secret, https_only=False)

app.include_router(router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
