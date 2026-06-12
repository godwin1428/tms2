"""
TMS — Application Configuration
Loads settings from .env via pydantic-settings.
"""
from pydantic_settings import BaseSettings
from pathlib import Path
import os
import secrets

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_hex(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'telemedicine.db'}"

    # Uploads
    UPLOAD_DIR: str = str(BASE_DIR / "uploads")

    # CORS
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")

    # Gemini AI
    GEMINI_API_KEY: str = ""

    model_config = {
        "env_file": str(BASE_DIR / ".env"),
        "extra": "ignore",
    }

    @property
    def upload_path(self) -> Path:
        p = Path(self.UPLOAD_DIR)
        p.mkdir(parents=True, exist_ok=True)
        return p


settings = Settings()
