"""Application configuration loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the backend service."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Dividend Growth Stock Evaluator API"
    app_version: str = "1.0.0"

    # CORS
    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # AI prompt layer
    ai_provider: str = "heuristic"  # "llm" | "heuristic"
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"

    # Market data
    enable_sample_fallback: bool = True

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def llm_enabled(self) -> bool:
        """True only when the LLM mode is requested *and* a key is present."""
        return self.ai_provider.lower() == "llm" and bool(self.openai_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
