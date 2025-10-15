from celery import Celery
from app.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    'masuka',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        'app.tasks.training_tasks',
        'app.tasks.generation_tasks'
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=14400,  # 4 hours max
    task_soft_time_limit=14400,
    worker_prefetch_multiplier=1,  # Process one task at a time
    worker_max_tasks_per_child=1,  # Restart worker after each task (GPU memory)
    broker_connection_retry_on_startup=True,
)

# Task routes
celery_app.conf.task_routes = {
    'app.tasks.training_tasks.*': {'queue': 'training'},
    'app.tasks.generation_tasks.*': {'queue': 'generation'},
}

logger.info("Celery app initialized")
