import logging
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..configs.db import get_db
from ..schemas import (
    PredictionRequest,
    PredictionResult,
    PredictionResponse,
    PredictionHistoryList,
    ModelStatus,
    TrainingRequest,
    TrainingResult,
    ModelMetricsResponse,
    ModelMetricsList
)
from ..services import (
    prediction_service,
    component_service,
    model_metrics_service,
    naive_bayes_service
)

logger = logging.getLogger("app")

router = APIRouter(prefix="/predictions", tags=["Predictions"])


@router.post("/predict", response_model=PredictionResult)
async def predict_damage_level(
    data: PredictionRequest,
    save_history: bool = Query(True, description="Save prediction to history"),
    db: AsyncSession = Depends(get_db)
):
    """
    Predict damage level for given features.
    
    Input features:
    - damage_area: Damage area in cm²
    - damage_depth: Damage depth in mm
    - damage_point_count: Number of damage points
    - component_age: Component age in months
    - usage_frequency: Usage frequency (1-10)
    - corrosion_level: Corrosion level (1-5)
    - deformation: Deformation in mm
    
    Output: Predicted damage level (Ringan/Sedang/Berat) with probabilities
    """
    # Check if model is trained
    if not naive_bayes_service.is_trained:
        raise HTTPException(
            status_code=400,
            detail="Model is not trained yet. Please train the model first."
        )
    
    # Verify component exists
    component = await component_service.get_by_id(db, data.component_id)
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    
    try:
        result = await prediction_service.predict(db, data, save_history=save_history)
        return result
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=PredictionHistoryList)
async def get_prediction_history(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    component_id: Optional[UUID] = Query(None, description="Filter by component"),
    predicted_level: Optional[str] = Query(None, description="Filter by predicted level"),
    db: AsyncSession = Depends(get_db)
):
    """Get prediction history with pagination and filters."""
    # Validate predicted_level
    if predicted_level:
        predicted_level = predicted_level.lower()
        if predicted_level not in ["ringan", "sedang", "berat"]:
            raise HTTPException(
                status_code=400,
                detail="predicted_level must be one of: ringan, sedang, berat"
            )
    
    items, total = await prediction_service.get_history(
        db, page=page, size=size, component_id=component_id, predicted_level=predicted_level
    )
    
    pages = (total + size - 1) // size
    
    return PredictionHistoryList(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/history/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(
    prediction_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a prediction by ID."""
    prediction = await prediction_service.get_by_id(db, prediction_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return prediction


@router.delete("/history/{prediction_id}", status_code=204)
async def delete_prediction(
    prediction_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete a prediction from history."""
    deleted = await prediction_service.delete(db, prediction_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return None


@router.get("/model-status", response_model=ModelStatus)
async def get_model_status(db: AsyncSession = Depends(get_db)):
    """Get current model status."""
    return await model_metrics_service.get_model_status(db)


@router.post("/train", response_model=TrainingResult)
async def train_model(
    data: TrainingRequest = TrainingRequest(),
    db: AsyncSession = Depends(get_db)
):
    """
    Train the Naive Bayes model with current damage records.
    
    Requires minimum 10 damage records for training.
    """
    try:
        result = await model_metrics_service.train_model(
            db, test_size=data.test_size, notes=data.notes
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Training error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics", response_model=ModelMetricsList)
async def get_model_metrics(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db)
):
    """Get all model training metrics history."""
    items, total = await model_metrics_service.get_all(db, page=page, size=size)
    
    return ModelMetricsList(
        items=items,
        total=total
    )


@router.get("/metrics/latest", response_model=ModelMetricsResponse)
async def get_latest_metrics(db: AsyncSession = Depends(get_db)):
    """Get the latest model metrics."""
    metrics = await model_metrics_service.get_latest(db)
    if not metrics:
        raise HTTPException(status_code=404, detail="No training metrics found")
    return metrics


@router.get("/model-info")
async def get_model_info():
    """
    Get detailed model information including parameters.
    
    Returns Naive Bayes model parameters:
    - class_prior: Prior probability of each class
    - theta: Mean of each feature per class
    - var: Variance of each feature per class
    """
    if not naive_bayes_service.is_trained:
        raise HTTPException(
            status_code=400,
            detail="Model is not trained yet"
        )
    
    return naive_bayes_service.get_model_info()