# MASUKA V2 - AI Generation Platform (Single-User)

Ultra-realistic LoRA training and AI generation platform for Flux image models and Hunyuan/Wan video models.

**Single-User Mode:** This is a personal tool designed for individual use without authentication overhead.

## Features

- Ultra-realistic Flux LoRA training for real people (20-30 images)
- Direct image generation with trained LoRAs
- Video LoRA training (Hunyuan Video/Wan models)
- Video generation from trained video LoRAs
- Real-time progress tracking during training
- Model registry and version management
- Cloud storage integration (S3/R2)
- No authentication required - streamlined personal use

## Tech Stack

**Backend:**
- FastAPI - Modern Python web framework
- PostgreSQL - Primary database
- Redis - Caching and job queue
- Celery - Async task processing
- SQLAlchemy - ORM
- SimpleTuner - Flux LoRA training

**Frontend:**
- Vue 3 - Progressive JavaScript framework
- Pinia - State management
- Tailwind CSS - Utility-first CSS
- Axios - HTTP client

**Deployment:**
- Google Colab with A100 GPU (48GB VRAM)
- Docker - Containerization

## Project Structure

```
masuka-v2/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── api/      # API route handlers
│   │   ├── models/   # SQLAlchemy models
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── services/ # Business logic
│   │   ├── tasks/    # Celery tasks
│   │   ├── trainers/ # ML training wrappers
│   │   └── generators/ # ML generation wrappers
│   └── requirements.txt
├── frontend/         # Vue 3 frontend
│   └── src/
│       ├── views/    # Page components
│       ├── components/ # Reusable components
│       ├── stores/   # Pinia stores
│       └── services/ # API communication
└── scripts/          # Utility scripts
```

## Setup Instructions

### Backend Setup

1. Create and activate virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. Access the API documentation:
```
http://localhost:8000/docs
```

### Frontend Setup (Coming in Phase 2)

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### Training (Coming in Phase 2)
- `POST /api/training/flux` - Start Flux LoRA training
- `POST /api/training/video` - Start video LoRA training
- `GET /api/training/{session_id}` - Get training status

### Models (Coming in Phase 2)
- `GET /api/models` - List user models
- `GET /api/models/{model_id}` - Get model details
- `DELETE /api/models/{model_id}` - Delete model

### Generation (Coming in Phase 2)
- `POST /api/generate/image` - Generate image
- `POST /api/generate/video` - Generate video

### Progress (Coming in Phase 2)
- `GET /api/progress/stream/{session_id}` - SSE endpoint for real-time progress

## Development Status

### Phase 1: Core Infrastructure (COMPLETE)
- [x] Project structure
- [x] Database models
- [x] Authentication system
- [x] Configuration management
- [x] API documentation

### Phase 2: Training Pipeline (Next)
- [ ] Celery setup
- [ ] Redis integration
- [ ] Training API endpoints
- [ ] SimpleTuner integration
- [ ] Real-time progress tracking (SSE)

### Phase 3: Generation Pipeline
- [ ] Image generation
- [ ] Video generation
- [ ] Model registry
- [ ] Storage integration

### Phase 4: Frontend
- [ ] Vue 3 application
- [ ] Training interface
- [ ] Generation interface
- [ ] Model management
- [ ] Real-time progress UI

### Phase 5: Colab Deployment
- [ ] Colab notebook
- [ ] Environment setup scripts
- [ ] Model download scripts
- [ ] ngrok integration

## Testing

### Test Authentication Endpoints

1. Health check:
```bash
curl http://localhost:8000/health
```

2. Register a user:
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpassword123"}'
```

3. Login:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpassword123"}'
```

4. Get current user (replace TOKEN):
```bash
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer TOKEN"
```

## Training Best Practices (2025)

### Flux LoRA Training
- **Dataset size:** 20-30 images optimal
- **Captioning:** Florence-2 or JoyCaption
- **Learning rate:** 1e-4
- **Steps:** 2000
- **Network rank:** 32
- **Network alpha:** 16
- **Resolution:** 1024x1024

### Video LoRA Training
- **Note:** Flux LoRAs cannot be used for video
- **Separate training required** for video models
- **Models:** Hunyuan Video or Wan

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.
