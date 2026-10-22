from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Kiswahili Grammar Tutor CBot"
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api/v1"
    
    # Local SQLite fallback for zero-dependency local dev / offline edge deployment
    DATABASE_URL: str = "sqlite+aiosqlite:///./tutor_storage.db"
    gemini_api_key: str | None = None
    class Config:
        env_file = ".env",
        extra="ignore"

settings = Settings()