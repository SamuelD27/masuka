from sqlalchemy import Column, String, Integer, Float, Text, DateTime, JSON
from datetime import datetime
import uuid
from app.models import Base, UUID

class TrainingSession(Base):
    __tablename__ = "training_sessions"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    model_type = Column(String(50), nullable=False)  # 'flux_image', 'hunyuan_video', 'wan_video'
    status = Column(String(20), nullable=False, default='pending')  # pending, training, completed, failed, cancelled

    # Training configuration
    config = Column(JSON, nullable=False)

    # Progress tracking
    progress = Column(JSON, nullable=True)  # {step: int, total_steps: int, loss: float, epoch: int}
    current_step = Column(Integer, default=0)
    total_steps = Column(Integer, nullable=True)
    current_loss = Column(Float, nullable=True)

    # Error handling
    error_message = Column(Text, nullable=True)

    # Task management
    celery_task_id = Column(String(255), nullable=True)

    # Timestamps
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<TrainingSession {self.name} ({self.status})>"
