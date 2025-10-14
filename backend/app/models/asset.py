from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.models import Base, UUID

class GeneratedAsset(Base):
    __tablename__ = "generated_assets"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    model_id = Column(UUID, ForeignKey("models.id"), nullable=True)

    asset_type = Column(String(20), nullable=False)  # 'image', 'video'
    storage_path = Column(Text, nullable=False)

    # Generation parameters
    prompt = Column(Text, nullable=True)
    negative_prompt = Column(Text, nullable=True)
    parameters = Column(JSON, nullable=True)  # {steps, cfg_scale, seed, etc}

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    model = relationship("Model", backref="generated_assets")

    def __repr__(self):
        return f"<GeneratedAsset {self.asset_type} - {self.id}>"
