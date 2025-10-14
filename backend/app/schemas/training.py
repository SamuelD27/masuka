from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class TrainingRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    model_type: str = Field(..., pattern="^(flux_image|hunyuan_video|wan_video)$")
    dataset_id: str

    # Training parameters
    learning_rate: Optional[float] = 1e-4
    steps: Optional[int] = 2000
    network_dim: Optional[int] = 32
    network_alpha: Optional[int] = 16
    resolution: Optional[int] = 1024
    trigger_word: Optional[str] = None

    # Additional config
    config: Optional[Dict[str, Any]] = {}

class TrainingResponse(BaseModel):
    session_id: str
    status: str
    task_id: Optional[str] = None

class TrainingStatusResponse(BaseModel):
    session_id: str
    name: str
    model_type: str
    status: str
    progress: Optional[Dict[str, Any]] = None
    current_step: Optional[int] = None
    total_steps: Optional[int] = None
    current_loss: Optional[float] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
