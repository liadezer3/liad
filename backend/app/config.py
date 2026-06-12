from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    soundcloud_client_id: str = ""
    soundcloud_client_secret: str = ""
    soundcloud_redirect_uri: str = "http://127.0.0.1:5173/api/auth/callback"
    soundcloud_redirect_uris: str = ""
    session_secret: str = "change-me-in-production"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    allow_lan_cors: bool = True
    frontend_url: str = "http://localhost:5173"


settings = Settings()
