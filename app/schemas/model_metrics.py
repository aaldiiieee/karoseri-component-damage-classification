from typing import Optional
from pydantic import Field, BaseModel 

class ClassMetrics(BaseModel):
    """Schema for metrics per class."""
    precision: float = Field(..., ge=0, le=1)
    recall: float = Field(..., ge=0, le=1)
    f1_score: float = Field(..., ge=0, le=1, alias="f1-score")
    support: int


class ClassificationReport(BaseModel):
    """Schema for classification report."""
    ringan: ClassMetrics = Field(..., alias="Ringan")
    sedang: ClassMetrics = Field(..., alias="Sedang")
    berat: ClassMetrics = Field(..., alias="Berat")


class TrainingRequest(BaseModel):
    """Schema for model training request."""
    test_size: float = Field(0.2, gt=0, lt=1, description="Proportion of data for testing")
    notes: Optional[str] = None


class TrainingResult(BaseModel):
    """Schema for training result."""
    success: bool
    message: str
    training_samples: int
    test_samples: int
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    classification_report: dict
    confusion_matrix: list[list[int]]


class ModelMetricsResponse(BaseModel):
    """Response schema for ModelMetrics."""
    training_samples: int
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    classification_report: dict
    confusion_matrix: list[list[int]]
    notes: Optional[str] = None


class ModelMetricsList(BaseModel):
    """Schema for ModelMetrics list."""
    items: list[ModelMetricsResponse]
    total: int