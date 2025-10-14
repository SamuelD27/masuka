from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, JSON
from datetime import datetime
import uuid
from app.models import Base, UUID

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    storage_path = Column(Text, nullable=False)

    # Dataset info
    image_count = Column(Integer, default=0)
    video_count = Column(Integer, default=0)

    # Processing status
    is_processed = Column(Boolean, default=False)
    captions_generated = Column(Boolean, default=False)

    # Metadata
    dataset_metadata = Column(JSON, nullable=True)  # {trigger_word, caption_style, preprocessing_params}

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Dataset {self.name}>"
