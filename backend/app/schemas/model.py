from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class ModelResponse(BaseModel):
    id: str
    name: str
    version: str
    model_type: str
    trigger_word: Optional[str]
    file_size_mb: Optional[int]
    model_metadata: Optional[Dict[str, Any]]
    created_at: datetime
    download_url: Optional[str] = None

    class Config:
        from_attributes = True
