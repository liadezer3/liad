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
cors_kwargs: dict = {
    "allow_origins": origins,
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}
if settings.allow_lan_cors:
    cors_kwargs["allow_origin_regex"] = (
        r"https?://(localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3})(:\d+)?"
    )
app.add_middleware(CORSMiddleware, **cors_kwargs)
app.add_middleware(SessionMiddleware, secret_key=settings.session_secret, https_only=False)

app.include_router(router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
