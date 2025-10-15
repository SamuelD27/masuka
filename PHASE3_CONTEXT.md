# MASUKA V2 - Phase 3 Context

## Project Overview

**MASUKA V2** is a single-user AI generation platform for training and generating ultra-realistic LoRA models. The platform supports:
- **Flux LoRA training** for ultra-realistic image generation (20-30 images)
- **Image generation** with trained Flux LoRAs
- **Video LoRA training** (Hunyuan Video/Wan models) - planned
- **Video generation** with trained video LoRAs - planned

**Architecture:** Single-user mode (no authentication) for personal use in Google Colab with GPU acceleration.

## Current Status

### ✅ Phase 1: Core Infrastructure (COMPLETE)
- FastAPI backend with async support
- PostgreSQL database with SQLAlchemy ORM
- Single-user architecture (no user_id fields)
- Configuration management with Pydantic Settings
- CORS middleware and API documentation
- Database models: TrainingSession, Model, Dataset, GeneratedAsset

### ✅ Phase 2: Training Pipeline (COMPLETE)
- Celery + Redis async job queue
- SimpleTuner integration for Flux LoRA training
- S3/R2 storage integration for datasets and models
- Real-time progress tracking via Server-Sent Events (SSE)
- Dataset upload API with image validation
- Training API with progress callbacks
- Model upload to S3 after training
- Google Colab notebook for end-to-end training workflow

**Colab Workflow:**
1. Cell 1: Start backend (FastAPI + Celery + Redis + ngrok tunnel)
2. Cell 2: Upload images → Start training → Monitor progress (single cell)
3. Cell 4: Debug helper for troubleshooting

### 🎯 Phase 3: Generation Pipeline (NEXT)

**Goal:** Implement image generation API that uses trained Flux LoRA models to generate images.

**Requirements:**
1. Image generation API endpoint
2. Download trained models from S3
3. Load Flux base model + LoRA weights
4. Generate images with ComfyUI or diffusers
5. Upload generated images to S3
6. Track generation history in database
7. Real-time generation progress tracking
8. Colab integration for testing

## Tech Stack

**Backend:**
- FastAPI 0.115.0+ (async web framework)
- SQLAlchemy 2.0.25 (ORM)
- PostgreSQL (database)
- Redis 5.0.1 (message broker + cache)
- Celery 5.3.6 (async task queue)
- boto3 1.34.34 (S3 client)
- Pydantic 2.11.0+ (validation with strict mode)
- pyngrok (Colab tunnel for API access)

**Training:**
- SimpleTuner (Flux LoRA training framework)
- Train script: `SimpleTuner/simpletuner/train.py`

**Generation (to implement):**
- Option 1: ComfyUI (node-based workflow)
- Option 2: diffusers library (Hugging Face)

**Deployment:**
- Google Colab (T4/A100 GPU, 48GB VRAM)
- ngrok for public API access

## Project Structure

```
masuka-v2/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── datasets.py       # Dataset upload + management
│   │   │   ├── training.py       # Training API (start/cancel/status)
│   │   │   └── progress.py       # SSE progress streaming
│   │   ├── models/
│   │   │   ├── training.py       # TrainingSession model
│   │   │   ├── model.py          # Model registry
│   │   │   ├── dataset.py        # Dataset model
│   │   │   └── asset.py          # GeneratedAsset model (for Phase 3)
│   │   ├── schemas/
│   │   │   ├── training.py       # Training request/response schemas
│   │   │   └── dataset.py        # Dataset schemas
│   │   ├── tasks/
│   │   │   ├── training_tasks.py # Celery training tasks
│   │   │   └── generation_tasks.py # Celery generation tasks (for Phase 3)
│   │   ├── trainers/
│   │   │   ├── base_trainer.py   # Base trainer class
│   │   │   └── flux_trainer.py   # SimpleTuner wrapper
│   │   ├── generators/
│   │   │   └── __init__.py       # For Phase 3
│   │   ├── services/
│   │   │   └── storage_service.py # S3 upload/download
│   │   ├── utils/
│   │   │   └── progress.py       # Redis progress manager
│   │   ├── config.py             # Settings with Pydantic
│   │   └── main.py               # FastAPI app
│   └── requirements.txt
├── MASUKA_V2_Colab_SingleCell.ipynb  # Colab notebook
└── README.md
```

## Database Models

### TrainingSession
```python
class TrainingSession(Base):
    __tablename__ = "training_sessions"

    id: UUID (primary key)
    name: str
    model_type: str  # 'flux_image', 'hunyuan_video', 'wan_video'
    status: str  # 'pending', 'training', 'completed', 'failed', 'cancelled'

    # Training config
    config: JSON  # {dataset_id, learning_rate, steps, network_dim, etc}

    # Progress tracking
    progress: JSON  # {step, total_steps, loss, epoch}
    current_step: int
    total_steps: int
    current_loss: float

    # Task management
    celery_task_id: str
    error_message: str

    # Timestamps
    started_at: datetime
    completed_at: datetime
    created_at: datetime
    updated_at: datetime
```

### Model
```python
class Model(Base):
    __tablename__ = "models"

    id: UUID (primary key)
    training_session_id: UUID (foreign key)

    name: str
    version: str
    model_type: str  # 'flux_image', 'hunyuan_video', 'wan_video'

    # Storage
    storage_path: str  # S3/R2 path
    file_size_mb: int

    # Model metadata
    trigger_word: str
    model_metadata: JSON  # {training_params, dataset_info, etc}

    # Timestamps
    created_at: datetime
```

### Dataset
```python
class Dataset(Base):
    __tablename__ = "datasets"

    id: UUID (primary key)
    name: str
    storage_path: str  # S3/R2 path

    # Dataset info
    image_count: int
    video_count: int

    # Processing status
    is_processed: bool
    captions_generated: bool

    # Metadata
    dataset_metadata: JSON  # {trigger_word, caption_style, preprocessing_params}

    # Timestamps
    created_at: datetime
    updated_at: datetime
```

### GeneratedAsset (for Phase 3)
```python
# TODO: Implement in Phase 3
class GeneratedAsset(Base):
    __tablename__ = "generated_assets"

    id: UUID (primary key)
    model_id: UUID (foreign key)

    asset_type: str  # 'image', 'video'
    storage_path: str  # S3/R2 path

    # Generation config
    prompt: str
    negative_prompt: str
    generation_config: JSON  # {steps, cfg_scale, seed, etc}

    # Metadata
    file_size_mb: int

    # Timestamps
    created_at: datetime
```

## API Endpoints (Current)

### Datasets
- `POST /api/datasets/` - Upload dataset (images + metadata)
- `GET /api/datasets/{dataset_id}` - Get dataset info

### Training
- `POST /api/training/flux` - Start Flux LoRA training (returns 201)
- `GET /api/training/{session_id}` - Get training status
- `GET /api/training/` - List all training sessions
- `POST /api/training/{session_id}/cancel` - Cancel training

### Progress
- `GET /api/progress/stream/{session_id}` - SSE endpoint for real-time progress

### Health
- `GET /health` - Health check
- `GET /` - API root

## Key Implementation Details

### Single-User Mode
**IMPORTANT:** The platform is single-user, so all models are designed WITHOUT `user_id` fields.

**Removed from all code:**
- No `user_id` columns in database models
- No `user_id` parameters in API endpoints
- No `user_id` in Celery tasks

### S3 Configuration
**AWS S3:**
- Do NOT specify `endpoint_url` (let boto3 auto-detect regional endpoint)
- Use virtual-hosted-style addressing
- Requires IAM permissions: `s3:PutObject`, `s3:GetObject`, `s3:DeleteObject`

**Cloudflare R2 or custom S3:**
- Specify `endpoint_url` in settings
- Use path-style addressing

**Storage Service** (`backend/app/services/storage_service.py`):
```python
# Only add endpoint_url for non-AWS S3
if settings.S3_ENDPOINT_URL and 'amazonaws.com' not in settings.S3_ENDPOINT_URL:
    client_kwargs['endpoint_url'] = settings.S3_ENDPOINT_URL
    # Use path-style for custom endpoints
    boto_config = Config(signature_version='s3v4', s3={'addressing_style': 'path'})
```

### SimpleTuner Integration
**Train script path:** `SimpleTuner/simpletuner/train.py`

**Configuration format:**
```yaml
model:
  name_or_path: 'black-forest-labs/FLUX.1-dev'
  is_flux: true
  quantize: true
  quantize_dtype: 'fp8'

train:
  learning_rate: 1e-4
  lr_scheduler: 'constant_with_warmup'
  lr_warmup_steps: 100
  optimizer: 'adamw8bit'
  max_train_steps: 2000
  save_steps: 250
  mixed_precision: 'bf16'
  gradient_checkpointing: true

network:
  type: 'lora'
  rank: 32
  alpha: 16
  dropout: 0.0
  target_modules: ['to_q', 'to_k', 'to_v', 'to_out.0']

data:
  dataset_path: '/path/to/images'
  resolution: 1024
  caption_ext: 'txt'
  cache_latents: true
  batch_size: 1

output:
  output_dir: '/path/to/output'
  save_precision: 'bf16'
  logging_dir: '/path/to/output/logs'
```

### Celery Task Pattern
```python
from celery import Task
from app.tasks.celery_app import celery_app
from app.models import SessionLocal

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
    session = self.db.query(TrainingSession).filter(
        TrainingSession.id == session_id
    ).first()

    # Update progress in Redis
    progress_manager.set_progress(session_id, {'status': 'training', 'progress': 0})

    # ... training logic ...

    self.db.commit()
```

### Progress Tracking
**Redis-based real-time progress:**
```python
from app.utils.progress import progress_manager

# Update progress
progress_manager.set_progress(session_id, {
    'status': 'training',
    'progress': 50,
    'message': 'Processing step 500/1000'
})

progress_manager.update_step(session_id, step=500, total_steps=1000, loss=0.123)
```

**SSE endpoint** (`backend/app/api/progress.py`):
```python
@router.get("/stream/{session_id}")
async def stream_progress(session_id: str):
    async def event_generator():
        while True:
            progress = progress_manager.get_progress(session_id)
            if progress:
                yield f"data: {json.dumps(progress)}\n\n"
            await asyncio.sleep(1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

## Environment Variables

**Required:**
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string (for Celery + progress)
- `AWS_ACCESS_KEY_ID` - S3 credentials
- `AWS_SECRET_ACCESS_KEY` - S3 credentials
- `S3_BUCKET_NAME` - S3 bucket name
- `S3_REGION` - S3 region (e.g., 'us-east-1')

**Optional:**
- `S3_ENDPOINT_URL` - Only for non-AWS S3 (e.g., Cloudflare R2)
- `HF_TOKEN` - Hugging Face token for model downloads
- `NGROK_AUTH_TOKEN` - For Colab tunnel (only in Colab)
- `SIMPLETUNER_PATH` - Path to SimpleTuner installation (default: `/content/SimpleTuner`)

**Defaults:**
- `DEFAULT_FLUX_LEARNING_RATE=1e-4`
- `DEFAULT_FLUX_STEPS=2000`
- `DEFAULT_FLUX_RANK=32`
- `DEFAULT_FLUX_ALPHA=16`
- `DEFAULT_RESOLUTION=1024`

## Colab Notebook Structure

**MASUKA_V2_Colab_SingleCell.ipynb:**

**Cell 1: Start Backend**
- Clone repository (or pull if exists)
- Install dependencies
- Start PostgreSQL, Redis, Celery worker
- Start FastAPI with uvicorn
- Create ngrok tunnel
- Store `API_URL` in Colab environment

**Cell 2: Upload + Train + Monitor**
- Upload images to create dataset
- Start training session
- Monitor progress via SSE in real-time
- Accepts status codes 200 and 201

**Cell 4: Debug Helper**
- Check API_URL
- Test health endpoint
- List training sessions

## Phase 2 Issues Resolved

### 1. Pydantic Settings Validation
**Issue:** Routes not loading due to `NGROK_AUTH_TOKEN` in .env but not in Settings class
**Fix:** Added `NGROK_AUTH_TOKEN: Optional[str] = None` and `extra = "ignore"` to Config

### 2. user_id References
**Issue:** Single-user mode doesn't need user_id fields
**Fix:** Removed all user_id references from:
- `backend/app/api/datasets.py`
- `backend/app/api/training.py`
- `backend/app/tasks/training_tasks.py`

### 3. S3 PermanentRedirect
**Issue:** Specifying endpoint_url for AWS S3 causes wrong endpoint
**Fix:** Skip endpoint_url if it contains 'amazonaws.com', let boto3 auto-detect

### 4. SimpleTuner Path
**Issue:** Train script not found at `SimpleTuner/train.py`
**Fix:** Corrected path to `SimpleTuner/simpletuner/train.py` with fallback

### 5. Status Code Validation
**Issue:** POST /api/training/flux returns 201, notebook checked for 200
**Fix:** Accept both 200 and 201 status codes

### 6. Dataset Metadata Field
**Issue:** Using `metadata` instead of `dataset_metadata`
**Fix:** Updated all references to use correct field name

## Phase 3 Requirements

### Image Generation API

**Endpoint:** `POST /api/generate/image`

**Request:**
```json
{
  "model_id": "uuid",
  "prompt": "photo of ohwx person standing in a field",
  "negative_prompt": "blurry, low quality",
  "num_inference_steps": 28,
  "guidance_scale": 3.5,
  "width": 1024,
  "height": 1024,
  "seed": null,
  "lora_scale": 1.0
}
```

**Response:**
```json
{
  "asset_id": "uuid",
  "status": "pending",
  "task_id": "celery_task_id"
}
```

### Generation Task Flow

1. Validate model exists in database
2. Download model from S3 to local cache
3. Load Flux base model (FLUX.1-dev)
4. Load LoRA weights from trained model
5. Generate image with specified parameters
6. Upload generated image to S3
7. Create GeneratedAsset entry in database
8. Update progress in Redis for SSE streaming

### Technology Options

**Option 1: ComfyUI (Recommended)**
- Node-based workflow engine
- Built-in Flux + LoRA support
- Can run headless via API
- Used in production by many tools

**Option 2: diffusers**
- Hugging Face library
- Simpler API, more control
- Direct Python integration
- May require custom LoRA loading code

### File Structure for Phase 3

**New files to create:**
```
backend/app/
├── api/
│   └── generation.py          # Generation API endpoints
├── generators/
│   ├── base_generator.py      # Base generator class
│   └── flux_generator.py      # Flux image generator
├── schemas/
│   └── generation.py          # Generation request/response schemas
└── tasks/
    └── generation_tasks.py    # Celery generation tasks (UPDATE)
```

**Files to update:**
```
backend/app/
├── models/
│   └── asset.py               # Add GeneratedAsset model
├── main.py                    # Register generation router
└── config.py                  # Add generation settings
```

**Colab notebook:**
- Add Cell 3: Image Generation interface
- Test model download, image generation, S3 upload

### Success Criteria for Phase 3

- [ ] GeneratedAsset model created
- [ ] Generation API endpoint working
- [ ] Model download from S3 implemented
- [ ] Flux base model loading working
- [ ] LoRA weight loading working
- [ ] Image generation producing correct output
- [ ] Generated images uploaded to S3
- [ ] Progress tracking via SSE
- [ ] Colab cell for testing generation
- [ ] Error handling for missing models, OOM, etc.

## Best Practices

### Training Parameters (2025)
- **Dataset size:** 20-30 images optimal for person LoRAs
- **Captioning:** Florence-2 or JoyCaption recommended
- **Learning rate:** 1e-4 (default)
- **Steps:** 2000 (default)
- **Network rank:** 32 (default)
- **Network alpha:** 16 (default)
- **Resolution:** 1024x1024

### Code Quality
- Use type hints everywhere
- Log important operations
- Handle errors gracefully
- Use Pydantic for validation
- Follow FastAPI best practices
- Use async where beneficial
- Close database sessions properly

### Git Workflow
- Commit after each fix/feature
- Use descriptive commit messages
- Include co-author attribution:
  ```
  🤖 Generated with [Claude Code](https://claude.com/claude-code)

  Co-Authored-By: Claude <noreply@anthropic.com>
  ```

## Testing Checklist for Phase 3

### Generation API
- [ ] POST /api/generate/image with valid model_id
- [ ] Error handling for missing model_id
- [ ] Error handling for invalid parameters
- [ ] Generation progress tracking via SSE
- [ ] Generated asset saved to database
- [ ] Image uploaded to S3

### Model Management
- [ ] Download model from S3
- [ ] Cache model locally
- [ ] Load Flux base model
- [ ] Load LoRA weights
- [ ] Cleanup temp files after generation

### Colab Integration
- [ ] Cell for image generation
- [ ] Display generated image in notebook
- [ ] Download generated image
- [ ] List all generated assets
- [ ] Delete generated assets

## Resources

**Repository:** https://github.com/SamuelD27/masuka.git
**Branch:** main

**SimpleTuner:**
- Installation: `git clone https://github.com/bghira/SimpleTuner.git`
- Train script: `SimpleTuner/simpletuner/train.py`
- Documentation: Check SimpleTuner repository

**Flux Models:**
- Base model: `black-forest-labs/FLUX.1-dev`
- Requires Hugging Face token (HF_TOKEN)

**ComfyUI (if chosen):**
- Installation: `git clone https://github.com/comfyanonymous/ComfyUI.git`
- API docs: Check ComfyUI repository

**diffusers (if chosen):**
- Install: `pip install diffusers transformers accelerate`
- Flux pipeline: `FluxPipeline.from_pretrained()`

## Next Steps for Phase 3

1. **Create GeneratedAsset model** in `backend/app/models/asset.py`
2. **Create generation schemas** in `backend/app/schemas/generation.py`
3. **Implement FluxGenerator** in `backend/app/generators/flux_generator.py`
4. **Create generation API** in `backend/app/api/generation.py`
5. **Implement generation Celery task** in `backend/app/tasks/generation_tasks.py`
6. **Add model download logic** to storage_service.py
7. **Test end-to-end** in Colab notebook
8. **Add Colab cell** for image generation

**Priority:** Choose between ComfyUI vs diffusers first, then implement generator class.
