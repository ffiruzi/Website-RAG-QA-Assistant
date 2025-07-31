import os
from typing import Optional, List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Website RAG Q&A System"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database settings
    DATABASE_URL: str = "sqlite:///./app.db"

    # OpenAI API settings
    OPENAI_API_KEY: Optional[str] = None

    # Security
    SECRET_KEY: str = "your-secret-key-here"  # In production, use a secure random key
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080", "http://localhost:5173"]

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "pretty"  # "json" or "pretty"
    LOG_FILE: Optional[str] = "logs/app.log"

    # Cache settings
    CACHE_ENABLED: bool = True
    CACHE_TTL_SECONDS: int = 60 * 5  # 5 minutes

    # API settings
    API_V1_PREFIX: str = "/api/v1"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()