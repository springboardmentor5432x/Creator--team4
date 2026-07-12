"""
config.py - Application Configuration

Loads environment variables and defines global settings used across the app.
Uses Pydantic's BaseSettings for validation and type safety.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv

# Explicitly load .env file
load_dotenv()


class Settings(BaseSettings):
    """
    Central configuration class.
    Values are read from environment variables or a .env file.
    """

    # --- Application ---
    APP_NAME: str = "FastAPI Auth Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # --- JWT Settings ---
    # Secret key used to sign JWT tokens. MUST be changed in production.
    # Generate a strong key with: openssl rand -hex 32
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    # Access token expiry in minutes
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- Database Settings ---
    DATABASE_URL: str

    # --- MongoDB Settings ---
    MONGODB_URL: str
    MONGODB_DB_NAME: str = "creatoriq"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.
    Using lru_cache ensures the .env file is read only once.
    """
    return Settings()


# Convenience instance for direct imports
settings = get_settings()
