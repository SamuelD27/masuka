from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class DatasetCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    trigger_word: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}

class DatasetResponse(BaseModel):
    id: str
    name: str
    storage_path: str
    image_count: int
    video_count: int
    is_processed: bool
    captions_generated: bool
    metadata: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True
