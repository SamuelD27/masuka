from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models import get_db
from app.models.dataset import Dataset
from app.schemas.dataset import DatasetCreate, DatasetResponse
from app.services.storage_service import storage_service
from pathlib import Path
import uuid
import shutil
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Temporary storage for uploaded files (before S3)
TEMP_UPLOAD_DIR = Path("/tmp/masuka/uploads")
TEMP_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def create_dataset(
    request: DatasetCreate,
    db: Session = Depends(get_db)
):
    """Create a new dataset."""
    dataset_id = uuid.uuid4()

    # Create storage path
    storage_path = f"datasets/{dataset_id}"

    # Prepare metadata
    metadata = request.metadata or {}
    if request.trigger_word:
        metadata['trigger_word'] = request.trigger_word

    # Create dataset
    dataset = Dataset(
        id=dataset_id,
        name=request.name,
        storage_path=storage_path,
        dataset_metadata=metadata
    )

    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    logger.info(f"Created dataset {dataset_id}: {request.name}")

    return DatasetResponse(
        id=str(dataset.id),
        name=dataset.name,
        storage_path=dataset.storage_path,
        image_count=dataset.image_count,
        video_count=dataset.video_count,
        is_processed=dataset.is_processed,
        captions_generated=dataset.captions_generated,
        metadata=dataset.dataset_metadata,
        created_at=dataset.created_at
    )

@router.post("/{dataset_id}/upload", status_code=status.HTTP_200_OK)
async def upload_dataset_files(
    dataset_id: str,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Upload images to a dataset."""
    # Get dataset
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Create temporary directory for this dataset
    temp_dir = TEMP_UPLOAD_DIR / str(dataset_id)
    temp_dir.mkdir(parents=True, exist_ok=True)

    uploaded_files = []

    for file in files:
        # Validate file type
        if not file.content_type.startswith('image/'):
            continue

        # Save to temp
        file_path = temp_dir / file.filename
        with open(file_path, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Upload to S3
        storage_path = f"{dataset.storage_path}/{file.filename}"
        success = storage_service.upload_file(
            str(file_path),
            storage_path,
            content_type=file.content_type
        )

        if success:
            uploaded_files.append(file.filename)

    # Update dataset
    dataset.image_count = len(uploaded_files)
    db.commit()

    logger.info(f"Uploaded {len(uploaded_files)} files to dataset {dataset_id}")

    return {
        "dataset_id": str(dataset_id),
        "uploaded_count": len(uploaded_files),
        "files": uploaded_files
    }

@router.get("/", response_model=List[DatasetResponse])
async def list_datasets(
    db: Session = Depends(get_db)
):
    """List all datasets."""
    datasets = db.query(Dataset).order_by(Dataset.created_at.desc()).all()

    return [
        DatasetResponse(
            id=str(d.id),
            name=d.name,
            storage_path=d.storage_path,
            image_count=d.image_count,
            video_count=d.video_count,
            is_processed=d.is_processed,
            captions_generated=d.captions_generated,
            metadata=d.metadata,
            created_at=d.created_at
        )
        for d in datasets
    ]

@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: str,
    db: Session = Depends(get_db)
):
    """Get dataset details."""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    return DatasetResponse(
        id=str(dataset.id),
        name=dataset.name,
        storage_path=dataset.storage_path,
        image_count=dataset.image_count,
        video_count=dataset.video_count,
        is_processed=dataset.is_processed,
        captions_generated=dataset.captions_generated,
        metadata=dataset.dataset_metadata,
        created_at=dataset.created_at
    )

@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset(
    dataset_id: str,
    db: Session = Depends(get_db)
):
    """Delete a dataset."""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Delete from S3
    files = storage_service.list_files(dataset.storage_path)
    for file in files:
        storage_service.delete_file(file)

    # Delete from database
    db.delete(dataset)
    db.commit()

    logger.info(f"Deleted dataset {dataset_id}")

    return None
