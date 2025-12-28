import logging
from typing import Optional
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.prediction_history import PredictionHistory
from app.models.damage_record import DamageLevel
from app.schemas.prediction import PredictionRequest
from app.services.naive_bayes_service import naive_bayes_service

logger = logging.getLogger(__name__)


class PredictionService:
    """Service for predictions and prediction history."""
    
    async def predict(
        self,
        db: AsyncSession,
        data: PredictionRequest,
        save_history: bool = True
    ) -> dict:
        """
        Make a prediction and optionally save to history.
        
        Args:
            db: Database session
            data: Prediction request with features
            save_history: Whether to save prediction to history
        
        Returns:
            Prediction result with probabilities
        """
        logger.info(f"Making prediction for component: {data.component_id}")
        
        # Prepare features
        features = [
            data.damage_area,
            data.damage_depth,
            data.damage_point_count,
            data.component_age,
            data.usage_frequency,
            data.corrosion_level,
            data.deformation
        ]
        
        # Get prediction from model
        result = naive_bayes_service.predict(features)
        
        # Save to history if requested
        if save_history:
            history = PredictionHistory(
                component_id=data.component_id,
                damage_area=data.damage_area,
                damage_depth=data.damage_depth,
                damage_point_count=data.damage_point_count,
                component_age=data.component_age,
                usage_frequency=data.usage_frequency,
                corrosion_level=data.corrosion_level,
                deformation=data.deformation,
                predicted_level=DamageLevel(result["predicted_level"]),
                confidence=result["confidence"],
                probabilities=result["probabilities"],
                notes=data.notes
            )
            
            db.add(history)
            await db.commit()
            await db.refresh(history)
            
            logger.info(f"Prediction saved: {history.id}")
            result["id"] = str(history.id)
        
        # Add features used to result
        result["features_used"] = {
            "damage_area": data.damage_area,
            "damage_depth": data.damage_depth,
            "damage_point_count": data.damage_point_count,
            "component_age": data.component_age,
            "usage_frequency": data.usage_frequency,
            "corrosion_level": data.corrosion_level,
            "deformation": data.deformation
        }
        
        return result
    
    async def get_history(
        self,
        db: AsyncSession,
        page: int = 1,
        size: int = 10,
        component_id: Optional[UUID] = None,
        predicted_level: Optional[str] = None
    ) -> tuple[list[PredictionHistory], int]:
        """Get prediction history with pagination and filters."""
        logger.debug(f"Getting prediction history: page={page}, size={size}")
        
        query = select(PredictionHistory).options(selectinload(PredictionHistory.component))
        count_query = select(func.count(PredictionHistory.id))
        
        # Apply filters
        if component_id:
            query = query.where(PredictionHistory.component_id == component_id)
            count_query = count_query.where(PredictionHistory.component_id == component_id)
        
        if predicted_level:
            level = DamageLevel(predicted_level)
            query = query.where(PredictionHistory.predicted_level == level)
            count_query = count_query.where(PredictionHistory.predicted_level == level)
        
        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination
        offset = (page - 1) * size
        query = query.order_by(PredictionHistory.created_at.desc()).offset(offset).limit(size)
        
        result = await db.execute(query)
        items = result.scalars().all()
        
        return list(items), total
    
    async def get_by_id(
        self,
        db: AsyncSession,
        prediction_id: UUID
    ) -> Optional[PredictionHistory]:
        """Get prediction by ID."""
        result = await db.execute(
            select(PredictionHistory)
            .options(selectinload(PredictionHistory.component))
            .where(PredictionHistory.id == prediction_id)
        )
        return result.scalars().first()
    
    async def get_recent(
        self,
        db: AsyncSession,
        limit: int = 5
    ) -> list[PredictionHistory]:
        """Get recent predictions."""
        result = await db.execute(
            select(PredictionHistory)
            .options(selectinload(PredictionHistory.component))
            .order_by(PredictionHistory.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_count(self, db: AsyncSession) -> int:
        """Get total prediction count."""
        result = await db.execute(select(func.count(PredictionHistory.id)))
        return result.scalar() or 0
    
    async def delete(self, db: AsyncSession, prediction_id: UUID) -> bool:
        """Delete a prediction from history."""
        logger.info(f"Deleting prediction: {prediction_id}")
        
        prediction = await self.get_by_id(db, prediction_id)
        if not prediction:
            return False
        
        await db.delete(prediction)
        await db.commit()
        
        logger.info(f"Prediction deleted: {prediction_id}")
        return True


prediction_service = PredictionService()