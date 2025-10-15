# Placeholder for Phase 3
from app.tasks.celery_app import celery_app

@celery_app.task(name='app.tasks.generation_tasks.generate_image')
def generate_image(job_id: str, config: dict):
    """Placeholder for image generation - will be implemented in Phase 3."""
    pass
