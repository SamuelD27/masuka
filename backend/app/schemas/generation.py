from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class GenerationRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    negative_prompt: Optional[str] = None
    model_id: Optional[str] = None  # LoRA model ID (if using custom LoRA)
    lora_weight: Optional[float] = Field(default=0.8, ge=0.0, le=1.0)

    # Generation parameters
    num_images: int = Field(default=1, ge=1, le=4)
    num_inference_steps: int = Field(default=30, ge=10, le=100)
    guidance_scale: float = Field(default=3.5, ge=1.0, le=20.0)
    width: int = Field(default=1024, ge=512, le=2048)
    height: int = Field(default=1024, ge=512, le=2048)
    seed: Optional[int] = None

    # Additional config
    config: Optional[Dict[str, Any]] = {}

class GenerationResponse(BaseModel):
    job_id: str
    status: str
    task_id: Optional[str] = None

class GenerationJobResponse(BaseModel):
    id: str
    status: str
    prompt: str
    parameters: Dict[str, Any]
    output_paths: Optional[List[str]] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
