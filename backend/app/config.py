from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    soundcloud_client_id: str = ""
    soundcloud_client_secret: str = ""
    soundcloud_redirect_uri: str = "http://127.0.0.1:8000/api/auth/callback"
    session_secret: str = "change-me-in-production"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    frontend_url: str = "http://localhost:5173"


settings = Settings()
