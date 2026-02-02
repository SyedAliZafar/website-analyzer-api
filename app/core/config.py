"""
Central application configuration using Pydantic Settings.
Loads environment variables from .env and system environment.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    # Application
    app_name: str = "Website Analyzer API"
    environment: str = Field(default="development")

    # API Keys (will auto-match GEMINI_API_KEY and PAGESPEED_API_KEY from .env)
    gemini_api_key: Optional[str] = Field(default=None)
    pagespeed_api_key: Optional[str] = Field(default=None)

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # HTTP
    request_timeout: float = 30.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,  # This allows GEMINI_API_KEY to match gemini_api_key
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings instance (singleton-style).
    Safe to import anywhere in the app.
    """
    return Settings()