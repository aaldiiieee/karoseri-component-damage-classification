from sqlalchemy import Column, Float, Integer, Text, UUID
from sqlalchemy.dialects.postgresql import JSONB
from app.configs.db import Base
import uuid


class ModelMetrics(Base):
    """
    Model for storing Naive Bayes training metrics.
    Each training session saves new metrics.
    """
    __tablename__ = "model_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Training data count
    training_samples = Column(Integer, nullable=False)
    
    # Evaluation metrics
    accuracy = Column(Float, nullable=False)
    precision = Column(Float, nullable=False)
    recall = Column(Float, nullable=False)
    f1_score = Column(Float, nullable=False)

    # Detailed metrics per class
    classification_report = Column(JSONB, nullable=False)
    # Format: {
    #   "ringan": {"precision": 0.9, "recall": 0.85, "f1-score": 0.87, "support": 50},
    #   "sedang": {...},
    #   "berat": {...}
    # }

    # Confusion matrix
    confusion_matrix = Column(JSONB, nullable=False)
    # Format: 3x3 matrix for 3 classes

    # Training notes
    notes = Column(Text, nullable=True)

    def __repr__(self):
        return f"<ModelMetrics {self.id}: accuracy={self.accuracy:.2%}>"