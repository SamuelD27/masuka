from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models import get_db
from app.models.training import TrainingSession
from app.schemas.training import TrainingRequest, TrainingResponse, TrainingStatusResponse
from app.tasks.training_tasks import train_flux_lora, cancel_training
from pathlib import Path
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/flux", response_model=TrainingResponse, status_code=status.HTTP_201_CREATED)
async def start_flux_training(
    request: TrainingRequest,
    db: Session = Depends(get_db)
):
    """Start Flux LoRA training."""
    # Validate dataset exists
    from app.models.dataset import Dataset
    dataset = db.query(Dataset).filter(Dataset.id == request.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Create training session
    session = TrainingSession(
        name=request.name,
        model_type='flux_image',
        status='pending',
        config={
            'dataset_id': request.dataset_id,
            'learning_rate': request.learning_rate,
            'steps': request.steps,
            'network_dim': request.network_dim,
            'network_alpha': request.network_alpha,
            'resolution': request.resolution,
            'trigger_word': request.trigger_word,
            **request.config
        },
        total_steps=request.steps
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    # Prepare training config
    output_dir = Path(f"/tmp/masuka/training/{session.id}")
    output_dir.mkdir(parents=True, exist_ok=True)

    # TODO: Download dataset from S3 to local path
    # For now, assume dataset is in temp directory
    dataset_path = f"/tmp/masuka/uploads/{request.dataset_id}"

    training_config = {
        'dataset_path': dataset_path,
        'output_path': str(output_dir),
        'learning_rate': request.learning_rate,
        'steps': request.steps,
        'network_dim': request.network_dim,
        'network_alpha': request.network_alpha,
        'resolution': request.resolution,
        'trigger_word': request.trigger_word or '',
    }

    # Queue training task
    task = train_flux_lora.delay(str(session.id), training_config)

    # Update session with task ID
    session.celery_task_id = task.id
    db.commit()

    logger.info(f"Started Flux training session {session.id}, task {task.id}")

    return TrainingResponse(
        session_id=str(session.id),
        status='pending',
        task_id=task.id
    )

@router.post("/{session_id}/cancel", status_code=status.HTTP_200_OK)
async def cancel_training_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Cancel a training session."""
    session = db.query(TrainingSession).filter(TrainingSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Training session not found")

    if session.status not in ['pending', 'training']:
        raise HTTPException(status_code=400, detail="Training session cannot be cancelled")

    # Queue cancellation task
    cancel_training.delay(session_id)

    return {"message": "Training cancellation requested"}

@router.get("/{session_id}", response_model=TrainingStatusResponse)
async def get_training_status(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get training session status."""
    session = db.query(TrainingSession).filter(TrainingSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Training session not found")

    return TrainingStatusResponse(
        session_id=str(session.id),
        name=session.name,
        model_type=session.model_type,
        status=session.status,
        progress=session.progress,
        current_step=session.current_step,
        total_steps=session.total_steps,
        current_loss=session.current_loss,
        error_message=session.error_message,
        started_at=session.started_at,
        completed_at=session.completed_at,
        created_at=session.created_at
    )

@router.get("/", response_model=List[TrainingStatusResponse])
async def list_training_sessions(
    db: Session = Depends(get_db)
):
    """List all training sessions."""
    sessions = db.query(TrainingSession).order_by(TrainingSession.created_at.desc()).all()

    return [
        TrainingStatusResponse(
            session_id=str(s.id),
            name=s.name,
            model_type=s.model_type,
            status=s.status,
            progress=s.progress,
            current_step=s.current_step,
            total_steps=s.total_steps,
            current_loss=s.current_loss,
            error_message=s.error_message,
            started_at=s.started_at,
            completed_at=s.completed_at,
            created_at=s.created_at
        )
        for s in sessions
    ]
