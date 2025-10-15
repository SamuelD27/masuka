from celery import Task
from app.tasks.celery_app import celery_app
from app.services.model_service import model_service
from app.services.storage_service import storage_service
from app.models import SessionLocal
from app.models.asset import GeneratedAsset
from app.models.model import Model
from datetime import datetime
from pathlib import Path
import logging
import traceback
import uuid

logger = logging.getLogger(__name__)

class DatabaseTask(Task):
    """Base task with database session management."""
    _db = None

    @property
    def db(self):
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None

@celery_app.task(bind=True, base=DatabaseTask, name='app.tasks.generation_tasks.generate_image')
def generate_image(self, job_id: str, config: dict):
    """
    Generate images using Flux with optional LoRA.

    Args:
        job_id: Generation job UUID
        config: Generation configuration dict
    """
    logger.info(f"Starting image generation for job {job_id}")

    try:
        # Get job from database
        asset = self.db.query(GeneratedAsset).filter(
            GeneratedAsset.id == job_id
        ).first()

        if not asset:
            raise ValueError(f"Generation job {job_id} not found")

        # Extract parameters
        prompt = config['prompt']
        model_id = config.get('model_id')
        lora_weight = config.get('lora_weight', 0.8)
        num_images = config.get('num_images', 1)
        num_inference_steps = config.get('num_inference_steps', 30)
        guidance_scale = config.get('guidance_scale', 3.5)
        width = config.get('width', 1024)
        height = config.get('height', 1024)
        seed = config.get('seed')

        logger.info(f"Prompt: {prompt}")
        logger.info(f"Parameters: images={num_images}, steps={num_inference_steps}, guidance={guidance_scale}")

        # Get generator
        generator = model_service.get_generator('flux')

        # Load LoRA if specified
        if model_id:
            logger.info(f"Loading LoRA model {model_id}")
            model = self.db.query(Model).filter(Model.id == model_id).first()

            if not model:
                raise ValueError(f"Model {model_id} not found")

            generator = model_service.load_lora_for_generation(
                model_id=str(model.id),
                storage_path=model.storage_path,
                weight=lora_weight
            )

            logger.info(f"LoRA loaded: {model.name}")

        # Create output directory
        output_dir = Path(f"/tmp/masuka/generated/{job_id}")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate images
        logger.info("Starting generation...")
        output_paths = generator.generate(
            prompt=prompt,
            negative_prompt=config.get('negative_prompt'),
            num_images=num_images,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            width=width,
            height=height,
            seed=seed,
            output_dir=str(output_dir)
        )

        logger.info(f"Generated {len(output_paths)} images")

        # Upload to storage
        storage_paths = []
        for i, local_path in enumerate(output_paths):
            storage_path = f"generated/{job_id}/image_{i+1}.png"
            success = storage_service.upload_file(
                local_path,
                storage_path,
                content_type='image/png'
            )

            if success:
                storage_paths.append(storage_path)
                logger.info(f"Uploaded to {storage_path}")

        # Update asset
        asset.storage_path = storage_paths[0] if storage_paths else ""
        asset.parameters['output_paths'] = storage_paths
        asset.completed_at = datetime.utcnow()
        self.db.commit()

        logger.info(f"Generation job {job_id} completed successfully")

        return {
            'job_id': job_id,
            'status': 'completed',
            'output_paths': storage_paths
        }

    except Exception as e:
        logger.error(f"Generation failed: {str(e)}")
        logger.error(traceback.format_exc())

        # Update asset with error
        asset = self.db.query(GeneratedAsset).filter(
            GeneratedAsset.id == job_id
        ).first()

        if asset:
            asset.parameters['error'] = str(e)
            asset.completed_at = datetime.utcnow()
            self.db.commit()

        raise
