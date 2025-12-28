from sqlalchemy import Column, String, Float, Integer, Text, Enum, ForeignKey, UUID, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.configs.db import Base
from .damage_record import DamageLevel
import uuid

class PredictionHistory(Base):
    """
    Model for storing prediction history.
    Records each prediction made along with its probabilities.
    """
    __tablename__ = "prediction_histories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Foreign key to component
    component_id = Column(UUID(as_uuid=True), ForeignKey("components.id"), nullable=False)

    # Input features used for prediction
    damage_area = Column(Float, nullable=False)
    damage_depth = Column(Float, nullable=False)
    damage_point_count = Column(Integer, nullable=False)
    component_age = Column(Integer, nullable=False)
    usage_frequency = Column(Integer, nullable=False)
    corrosion_level = Column(Integer, nullable=False)
    deformation = Column(Float, nullable=False)

    # Prediction result
    predicted_level = Column(Enum(DamageLevel), nullable=False)
    confidence = Column(Float, nullable=False)  # Confidence score (0-1)

    # Probability per class (for details)
    probabilities = Column(JSONB, nullable=False)
    # Format: {"ringan": 0.7, "sedang": 0.2, "berat": 0.1}

    # Notes
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    component = relationship("Component", back_populates="prediction_histories")

    def __repr__(self):
        return f"<PredictionHistory {self.id}: {self.predicted_level.value} ({self.confidence:.2%})>"