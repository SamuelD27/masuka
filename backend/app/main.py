from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.models import Base, engine

# Import all models to ensure they're registered with SQLAlchemy
from app.models.training import TrainingSession
from app.models.model import Model
from app.models.asset import GeneratedAsset
from app.models.dataset import Dataset

# Create all tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Ultra-realistic LoRA training and AI generation platform (Single-User)",
    version="2.0.0",
    debug=settings.DEBUG
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "2.0.0",
        "mode": "single-user"
    }

@app.get("/")
async def root():
    return {
        "message": "MASUKA V2 API - Single User Mode",
        "docs": "/docs",
        "health": "/health"
    }

# Import and include routers
from app.api import datasets, training, progress, generation, models

app.include_router(datasets.router, prefix="/api/datasets", tags=["datasets"])
app.include_router(training.router, prefix="/api/training", tags=["training"])
app.include_router(progress.router, prefix="/api/progress", tags=["progress"])
app.include_router(generation.router, prefix="/api/generate", tags=["generation"])
app.include_router(models.router, prefix="/api/models", tags=["models"])
