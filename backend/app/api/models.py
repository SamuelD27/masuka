from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import get_db
from app.models.model import Model
from app.schemas.model import ModelResponse
from app.services.storage_service import storage_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[ModelResponse])
async def list_models(
    model_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all trained models."""
    query = db.query(Model)

    if model_type:
        query = query.filter(Model.model_type == model_type)

    models = query.order_by(Model.created_at.desc()).all()

    results = []
    for model in models:
        # Generate download URL
        download_url = storage_service.get_presigned_url(
            model.storage_path,
            expiration=3600
        )

        results.append(ModelResponse(
            id=str(model.id),
            name=model.name,
            version=model.version,
            model_type=model.model_type,
            trigger_word=model.trigger_word,
            file_size_mb=model.file_size_mb,
            model_metadata=model.model_metadata,
            created_at=model.created_at,
            download_url=download_url
        ))

    return results

@router.get("/{model_id}", response_model=ModelResponse)
async def get_model(
    model_id: str,
    db: Session = Depends(get_db)
):
    """Get model details."""
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    # Generate download URL
    download_url = storage_service.get_presigned_url(
        model.storage_path,
        expiration=3600
    )

    return ModelResponse(
        id=str(model.id),
        name=model.name,
        version=model.version,
        model_type=model.model_type,
        trigger_word=model.trigger_word,
        file_size_mb=model.file_size_mb,
        model_metadata=model.model_metadata,
        created_at=model.created_at,
        download_url=download_url
    )

@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(
    model_id: str,
    db: Session = Depends(get_db)
):
    """Delete a model."""
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    # Delete from storage
    storage_service.delete_file(model.storage_path)

    # Delete from database
    db.delete(model)
    db.commit()

    logger.info(f"Deleted model {model_id}")

    return None
