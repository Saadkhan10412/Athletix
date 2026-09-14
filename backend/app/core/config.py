"""
ATHLETIX — Application Configuration
app/core/config.py

This module manages centralized environment variables and configuration settings for the
ATHLETIX FastAPI backend using Pydantic Settings.

Configuration Sections:
- Supabase Settings: Project connection URL and high-privilege Service Role Key for server operations.
- Cloudinary Settings: Credentials for video upload, cloud processing, and CDN distribution.
- App Runtime Settings: Environment mode ('development' vs 'production') and cryptographic SECRET_KEY.
- CORS & Frontend Origins: Permitted origins for web clients, Expo development servers, and production web apps.
"""

# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded automatically from the environment or .env file.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ─── Supabase Configuration ───────────────────────────────────────────────
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str

    # ─── Cloudinary Video Storage ─────────────────────────────────────────────
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    # ─── Application Runtime Settings ─────────────────────────────────────────
    APP_ENV: str = "development"
    SECRET_KEY: str

    # Base frontend URL used for auth redirects and email link generation
    FRONTEND_URL: str = "http://localhost:8081"

    # AI Real-time Gym Coach Live URL (Set via LIVE_COACH_URL environment variable in production)
    LIVE_COACH_URL: str = ""

    # ─── Allowed CORS Origins ─────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:8081",
        "http://localhost:19006",
        "http://localhost:3000",
        "http://localhost:5173",
        "https://athletix.app",
    ]


# Singleton instance of application configuration
settings = Settings()