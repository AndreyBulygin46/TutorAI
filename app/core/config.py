import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://user:password@localhost:5432/ai_tutor_local"
    )
    
    # App
    PROJECT_NAME: str = "AI Tutor"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

settings = Settings()