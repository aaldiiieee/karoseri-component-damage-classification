from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import Field, BaseModel, ConfigDict
from .damage_record import DamageFeatures
from .component import ComponentResponse

class PredictionRequest(DamageFeatures):
    """Schema for prediction request."""
    component_id: UUID
    notes: Optional[str] = None


class PredictionProbabilities(BaseModel):
    """Schema for probability per class."""
    ringan: float = Field(..., ge=0, le=1)
    sedang: float = Field(..., ge=0, le=1)
    berat: float = Field(..., ge=0, le=1)


class PredictionResult(BaseModel):
    """Schema for prediction result."""
    predicted_level: str  # ringan, sedang, berat
    confidence: float = Field(..., ge=0, le=1)
    probabilities: PredictionProbabilities
    features_used: DamageFeatures


class PredictionResponse(PredictionResult):
    """Response schema for saved prediction."""
    id: UUID
    component_id: UUID
    component: Optional[ComponentResponse] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class PredictionHistoryList(BaseModel):
    """Schema for prediction history list with pagination."""
    items: list[PredictionResponse]
    total: int
    page: int
    size: int
    pages: int


class ModelStatus(BaseModel):
    """Schema for model status."""
    is_trained: bool
    training_samples: Optional[int] = None
    last_trained_at: Optional[str] = None
    accuracy: Optional[float] = None