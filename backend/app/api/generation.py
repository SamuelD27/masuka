from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import get_db
from app.models.asset import GeneratedAsset
from app.schemas.generation import GenerationRequest, GenerationResponse, GenerationJobResponse
from app.tasks.generation_tasks import generate_image
from app.services.storage_service import storage_service
import uuid
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/image", response_model=GenerationResponse, status_code=status.HTTP_201_CREATED)
async def create_image_generation(
    request: GenerationRequest,
    db: Session = Depends(get_db)
):
    """Start image generation job."""
    # Create asset record
    job_id = uuid.uuid4()

    asset = GeneratedAsset(
        id=job_id,
        model_id=request.model_id if request.model_id else None,
        asset_type='image',
        storage_path='',  # Will be updated after generation
        prompt=request.prompt,
        negative_prompt=request.negative_prompt,
        parameters={
            'num_images': request.num_images,
            'num_inference_steps': request.num_inference_steps,
            'guidance_scale': request.guidance_scale,
            'width': request.width,
            'height': request.height,
            'seed': request.seed,
            'lora_weight': request.lora_weight,
            'config': request.config
        }
    )

    db.add(asset)
    db.commit()
    db.refresh(asset)

    # Prepare generation config
    generation_config = {
        'prompt': request.prompt,
        'negative_prompt': request.negative_prompt,
        'model_id': request.model_id,
        'lora_weight': request.lora_weight,
        'num_images': request.num_images,
        'num_inference_steps': request.num_inference_steps,
        'guidance_scale': request.guidance_scale,
        'width': request.width,
        'height': request.height,
        'seed': request.seed,
    }

    # Queue generation task
    task = generate_image.delay(str(job_id), generation_config)

    logger.info(f"Started image generation job {job_id}, task {task.id}")

    return GenerationResponse(
        job_id=str(job_id),
        status='pending',
        task_id=task.id
    )

@router.get("/{job_id}", response_model=GenerationJobResponse)
async def get_generation_job(
    job_id: str,
    db: Session = Depends(get_db)
):
    """Get generation job status."""
    asset = db.query(GeneratedAsset).filter(GeneratedAsset.id == job_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Generation job not found")

    # Get output paths
    output_paths = asset.parameters.get('output_paths', []) if asset.parameters else []

    # Generate presigned URLs for images
    if output_paths:
        presigned_urls = []
        for path in output_paths:
            url = storage_service.get_presigned_url(path, expiration=3600)
            if url:
                presigned_urls.append(url)
        output_paths = presigned_urls

    # Determine status
    error = asset.parameters.get('error') if asset.parameters else None
    if error:
        status_value = 'failed'
    elif output_paths:
        status_value = 'completed'
    else:
        status_value = 'processing'

    return GenerationJobResponse(
        id=str(asset.id),
        status=status_value,
        prompt=asset.prompt or '',
        parameters=asset.parameters or {},
        output_paths=output_paths,
        error_message=error,
        created_at=asset.created_at,
        completed_at=asset.completed_at
    )

@router.get("/", response_model=List[GenerationJobResponse])
async def list_generation_jobs(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """List recent generation jobs."""
    assets = db.query(GeneratedAsset).filter(
        GeneratedAsset.asset_type == 'image'
    ).order_by(GeneratedAsset.created_at.desc()).limit(limit).all()

    results = []
    for asset in assets:
        output_paths = asset.parameters.get('output_paths', []) if asset.parameters else []

        # Generate presigned URLs
        if output_paths:
            presigned_urls = []
            for path in output_paths:
                url = storage_service.get_presigned_url(path, expiration=3600)
                if url:
                    presigned_urls.append(url)
            output_paths = presigned_urls

        # Determine status
        error = asset.parameters.get('error') if asset.parameters else None
        if error:
            status_value = 'failed'
        elif output_paths:
            status_value = 'completed'
        else:
            status_value = 'processing'

        results.append(GenerationJobResponse(
            id=str(asset.id),
            status=status_value,
            prompt=asset.prompt or '',
            parameters=asset.parameters or {},
            output_paths=output_paths,
            error_message=error,
            created_at=asset.created_at,
            completed_at=asset.completed_at
        ))

    return results

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_generation_job(
    job_id: str,
    db: Session = Depends(get_db)
):
    """Delete a generation job and its images."""
    asset = db.query(GeneratedAsset).filter(GeneratedAsset.id == job_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Generation job not found")

    # Delete images from storage
    output_paths = asset.parameters.get('output_paths', []) if asset.parameters else []
    for path in output_paths:
        storage_service.delete_file(path)

    # Delete from database
    db.delete(asset)
    db.commit()

    logger.info(f"Deleted generation job {job_id}")

    return None
