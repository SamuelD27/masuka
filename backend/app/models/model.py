from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.models import Base, UUID

class Model(Base):
    __tablename__ = "models"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    training_session_id = Column(UUID, ForeignKey("training_sessions.id"), nullable=False)

    name = Column(String(255), nullable=False)
    version = Column(String(50), nullable=False)
    model_type = Column(String(50), nullable=False)  # 'flux_image', 'hunyuan_video', 'wan_video'

    # Storage
    storage_path = Column(Text, nullable=False)  # S3/R2 path
    file_size_mb = Column(Integer, nullable=True)

    # Model metadata
    trigger_word = Column(String(100), nullable=True)
    model_metadata = Column(JSON, nullable=True)  # {training_params, dataset_info, etc}

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    training_session = relationship("TrainingSession", backref="models")

    def __repr__(self):
        return f"<Model {self.name} v{self.version}>"
