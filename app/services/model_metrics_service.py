import logging
from typing import Optional
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.model_metrics import ModelMetrics
from app.services.naive_bayes_service import naive_bayes_service
from app.services.damage_record_service import damage_record_service

logger = logging.getLogger(__name__)


class ModelMetricsService:
    """Service for model training and metrics."""
    
    async def train_model(
        self,
        db: AsyncSession,
        test_size: float = 0.2,
        notes: Optional[str] = None
    ) -> dict:
        """
        Train the Naive Bayes model with current data.
        
        Args:
            db: Database session
            test_size: Proportion of data for testing
            notes: Optional training notes
        
        Returns:
            Training result with metrics
        """
        logger.info("Starting model training")
        
        # Get training data from damage records
        features, labels = await damage_record_service.get_training_data(db)
        
        if len(features) < 10:
            raise ValueError(f"Insufficient training data. Found {len(features)}, minimum 10 required.")
        
        # Train model
        result = naive_bayes_service.train(features, labels, test_size)
        
        # Save metrics to database
        metrics = ModelMetrics(
            training_samples=result["training_samples"],
            accuracy=result["accuracy"],
            precision=result["precision"],
            recall=result["recall"],
            f1_score=result["f1_score"],
            classification_report=result["classification_report"],
            confusion_matrix=result["confusion_matrix"],
            notes=notes
        )
        
        db.add(metrics)
        await db.commit()
        await db.refresh(metrics)
        
        logger.info(f"Model metrics saved: {metrics.id}")
        
        result["metrics_id"] = str(metrics.id)
        return result
    
    async def get_latest(self, db: AsyncSession) -> Optional[ModelMetrics]:
        """Get the latest model metrics."""
        result = await db.execute(
            select(ModelMetrics)
            .order_by(ModelMetrics.created_at.desc())
            .limit(1)
        )
        return result.scalars().first()
    
    async def get_by_id(self, db: AsyncSession, metrics_id: UUID) -> Optional[ModelMetrics]:
        """Get model metrics by ID."""
        result = await db.execute(
            select(ModelMetrics).where(ModelMetrics.id == metrics_id)
        )
        return result.scalars().first()
    
    async def get_all(
        self,
        db: AsyncSession,
        page: int = 1,
        size: int = 10
    ) -> tuple[list[ModelMetrics], int]:
        """Get all model metrics with pagination."""
        logger.debug(f"Getting model metrics: page={page}, size={size}")
        
        # Get total count
        count_result = await db.execute(select(func.count(ModelMetrics.id)))
        total = count_result.scalar() or 0
        
        # Apply pagination
        offset = (page - 1) * size
        result = await db.execute(
            select(ModelMetrics)
            .order_by(ModelMetrics.created_at.desc())
            .offset(offset)
            .limit(size)
        )
        items = result.scalars().all()
        
        return list(items), total
    
    async def get_model_status(self, db: AsyncSession) -> dict:
        """Get current model status with latest metrics."""
        status = naive_bayes_service.get_status()
        
        # Get latest metrics for accuracy
        latest = await self.get_latest(db)
        if latest:
            status["accuracy"] = latest.accuracy
        
        return status
    
    async def delete(self, db: AsyncSession, metrics_id: UUID) -> bool:
        """Delete model metrics."""
        logger.info(f"Deleting model metrics: {metrics_id}")
        
        metrics = await self.get_by_id(db, metrics_id)
        if not metrics:
            return False
        
        await db.delete(metrics)
        await db.commit()
        
        logger.info(f"Model metrics deleted: {metrics_id}")
        return True


model_metrics_service = ModelMetricsService()