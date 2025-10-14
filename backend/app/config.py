from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "MASUKA V2"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://masuka:password@localhost:5432/masuka"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Storage (S3/R2)
    S3_BUCKET: str = "masuka-models"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    S3_ENDPOINT_URL: Optional[str] = None  # For Cloudflare R2
    S3_REGION: str = "us-east-1"

    # Paths (for Colab)
    SIMPLETUNER_PATH: str = "/content/SimpleTuner"
    DIFFUSION_PIPE_PATH: str = "/content/diffusion-pipe"
    MODELS_PATH: str = "/content/models"
    TEMP_PATH: str = "/tmp/masuka"

    # CORS (will be split from comma-separated string in .env)
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:8000"

    # Training defaults
    DEFAULT_FLUX_LEARNING_RATE: float = 1e-4
    DEFAULT_FLUX_STEPS: int = 2000
    DEFAULT_FLUX_RANK: int = 32
    DEFAULT_FLUX_ALPHA: int = 16
    DEFAULT_RESOLUTION: int = 1024

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Hugging Face
    HF_TOKEN: Optional[str] = None

    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS_ORIGINS string to list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
