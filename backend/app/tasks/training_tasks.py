from celery import Task
from app.tasks.celery_app import celery_app
from app.trainers.flux_trainer import FluxTrainer
from app.models import SessionLocal
from app.models.training import TrainingSession
from app.models.model import Model
from app.services.storage_service import storage_service
from app.utils.progress import progress_manager
from datetime import datetime
from pathlib import Path
import logging
import traceback

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

@celery_app.task(bind=True, base=DatabaseTask, name='app.tasks.training_tasks.train_flux_lora')
def train_flux_lora(self, session_id: str, config: dict):
    """
    Train a Flux LoRA model.

    Args:
        session_id: Training session UUID
        config: Training configuration dict
    """
    logger.info(f"Starting Flux LoRA training for session {session_id}")

    try:
        # Get training session
        session = self.db.query(TrainingSession).filter(
            TrainingSession.id == session_id
        ).first()

        if not session:
            raise ValueError(f"Training session {session_id} not found")

        # Update session status
        session.status = 'training'
        session.started_at = datetime.utcnow()
        session.celery_task_id = self.request.id
        self.db.commit()

        # Update progress in Redis
        progress_manager.set_progress(session_id, {
            'status': 'training',
            'progress': 0,
            'message': 'Initializing training...'
        })

        # Progress callback
        def progress_callback(step: int, total_steps: int, loss: float = None):
            # Update database
            session.current_step = step
            session.total_steps = total_steps
            session.current_loss = loss
            self.db.commit()

            # Update Redis for real-time tracking
            progress_manager.update_step(session_id, step, total_steps, loss)

        # Initialize trainer
        logger.info("Initializing FluxTrainer")
        trainer = FluxTrainer(config)

        # Train
        logger.info("Starting training process")
        result = trainer.train(progress_callback=progress_callback)

        logger.info(f"Training completed: {result}")

        # Upload model to storage
        logger.info("Uploading model to storage")
        model_filename = f"{session_id}/flux_lora.safetensors"

        # Get the final checkpoint
        if result['checkpoints']:
            final_checkpoint = result['checkpoints'][-1]
            storage_path = f"models/{session_id}/{model_filename}"

            success = storage_service.upload_file(
                final_checkpoint,
                storage_path,
                content_type='application/octet-stream'
            )

            if not success:
                raise Exception("Failed to upload model to storage")

            # Get file size
            file_size_mb = Path(final_checkpoint).stat().st_size / (1024 * 1024)

            # Create model entry
            model = Model(
                training_session_id=session_id,
                name=session.name,
                version='v1',
                model_type='flux_image',
                storage_path=storage_path,
                file_size_mb=int(file_size_mb),
                trigger_word=config.get('trigger_word'),
                metadata={
                    'training_params': {
                        'learning_rate': config.get('learning_rate'),
                        'steps': result['final_step'],
                        'network_dim': config.get('network_dim'),
                        'resolution': config.get('resolution'),
                    },
                    'final_loss': result.get('final_loss')
                }
            )
            self.db.add(model)

        # Update session
        session.status = 'completed'
        session.completed_at = datetime.utcnow()
        self.db.commit()

        # Update progress
        progress_manager.set_progress(session_id, {
            'status': 'completed',
            'progress': 100,
            'message': 'Training completed successfully!'
        })

        logger.info(f"Training session {session_id} completed successfully")

        return {
            'session_id': session_id,
            'status': 'completed',
            'model_id': str(model.id) if result['checkpoints'] else None
        }

    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        logger.error(traceback.format_exc())

        # Update session
        session = self.db.query(TrainingSession).filter(
            TrainingSession.id == session_id
        ).first()

        if session:
            session.status = 'failed'
            session.error_message = str(e)
            session.completed_at = datetime.utcnow()
            self.db.commit()

        # Update progress
        progress_manager.set_progress(session_id, {
            'status': 'failed',
            'error': str(e)
        })

        raise

@celery_app.task(bind=True, base=DatabaseTask, name='app.tasks.training_tasks.cancel_training')
def cancel_training(self, session_id: str):
    """Cancel a training session."""
    logger.info(f"Cancelling training session {session_id}")

    try:
        session = self.db.query(TrainingSession).filter(
            TrainingSession.id == session_id
        ).first()

        if not session:
            raise ValueError(f"Training session {session_id} not found")

        # Revoke Celery task
        if session.celery_task_id:
            celery_app.control.revoke(session.celery_task_id, terminate=True)

        # Update session
        session.status = 'cancelled'
        session.completed_at = datetime.utcnow()
        self.db.commit()

        # Update progress
        progress_manager.set_progress(session_id, {
            'status': 'cancelled',
            'message': 'Training cancelled by user'
        })

        logger.info(f"Training session {session_id} cancelled")

    except Exception as e:
        logger.error(f"Failed to cancel training: {str(e)}")
        raise
