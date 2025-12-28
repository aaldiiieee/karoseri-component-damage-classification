import logging
from typing import Optional
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.damage_record import DamageRecord, DamageLevel
from app.schemas.damage_record import DamageRecordCreate, DamageRecordUpdate, DamageDistribution

logger = logging.getLogger(__name__)


class DamageRecordService:
    """Service for DamageRecord CRUD operations."""
    
    async def create(self, db: AsyncSession, data: DamageRecordCreate) -> DamageRecord:
        """Create a new damage record."""
        logger.info(f"Creating damage record for component: {data.component_id}")
        
        record = DamageRecord(
            component_id=data.component_id,
            damage_area=data.damage_area,
            damage_depth=data.damage_depth,
            damage_point_count=data.damage_point_count,
            component_age=data.component_age,
            usage_frequency=data.usage_frequency,
            corrosion_level=data.corrosion_level,
            deformation=data.deformation,
            damage_level=DamageLevel(data.damage_level),
            notes=data.notes
        )
        
        db.add(record)
        await db.commit()
        await db.refresh(record)
        
        logger.info(f"Damage record created: {record.id}")
        return record
    
    async def get_by_id(self, db: AsyncSession, record_id: UUID) -> Optional[DamageRecord]:
        """Get damage record by ID with component."""
        logger.debug(f"Getting damage record: {record_id}")
        
        result = await db.execute(
            select(DamageRecord)
            .options(selectinload(DamageRecord.component))
            .where(DamageRecord.id == record_id)
        )
        return result.scalars().first()
    
    async def get_all(
        self,
        db: AsyncSession,
        page: int = 1,
        size: int = 10,
        component_id: Optional[UUID] = None,
        damage_level: Optional[str] = None
    ) -> tuple[list[DamageRecord], int]:
        """Get all damage records with pagination and filters."""
        logger.debug(f"Getting damage records: page={page}, size={size}")
        
        query = select(DamageRecord).options(selectinload(DamageRecord.component))
        count_query = select(func.count(DamageRecord.id))
        
        # Apply filters
        if component_id:
            query = query.where(DamageRecord.component_id == component_id)
            count_query = count_query.where(DamageRecord.component_id == component_id)
        
        if damage_level:
            level = DamageLevel(damage_level)
            query = query.where(DamageRecord.damage_level == level)
            count_query = count_query.where(DamageRecord.damage_level == level)
        
        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination
        offset = (page - 1) * size
        query = query.order_by(DamageRecord.created_at.desc()).offset(offset).limit(size)
        
        result = await db.execute(query)
        items = result.scalars().all()
        
        return list(items), total
    
    async def update(
        self,
        db: AsyncSession,
        record_id: UUID,
        data: DamageRecordUpdate
    ) -> Optional[DamageRecord]:
        """Update a damage record."""
        logger.info(f"Updating damage record: {record_id}")
        
        record = await self.get_by_id(db, record_id)
        if not record:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        
        # Handle damage_level enum conversion
        if "damage_level" in update_data:
            update_data["damage_level"] = DamageLevel(update_data["damage_level"])
        
        for key, value in update_data.items():
            setattr(record, key, value)
        
        await db.commit()
        await db.refresh(record)
        
        logger.info(f"Damage record updated: {record_id}")
        return record
    
    async def delete(self, db: AsyncSession, record_id: UUID) -> bool:
        """Delete a damage record."""
        logger.info(f"Deleting damage record: {record_id}")
        
        record = await self.get_by_id(db, record_id)
        if not record:
            return False
        
        await db.delete(record)
        await db.commit()
        
        logger.info(f"Damage record deleted: {record_id}")
        return True
    
    async def get_count(self, db: AsyncSession) -> int:
        """Get total damage record count."""
        result = await db.execute(select(func.count(DamageRecord.id)))
        return result.scalar() or 0
    
    async def get_distribution(self, db: AsyncSession) -> DamageDistribution:
        """Get damage level distribution."""
        logger.debug("Getting damage distribution")
        
        result = await db.execute(
            select(DamageRecord.damage_level, func.count(DamageRecord.id))
            .group_by(DamageRecord.damage_level)
        )
        
        distribution = {"ringan": 0, "sedang": 0, "berat": 0, "total": 0}
        
        for level, count in result.fetchall():
            if level == DamageLevel.ringan:
                distribution["ringan"] = count
            elif level == DamageLevel.sedang:
                distribution["sedang"] = count
            elif level == DamageLevel.berat:
                distribution["berat"] = count
            distribution["total"] += count
        
        return DamageDistribution(**distribution)
    
    async def get_training_data(self, db: AsyncSession) -> tuple[list[list[float]], list[str]]:
        """Get all damage records as training data."""
        logger.info("Getting training data")
        
        result = await db.execute(select(DamageRecord))
        records = result.scalars().all()
        
        features = []
        labels = []
        
        for record in records:
            features.append(record.get_features())
            labels.append(record.damage_level.value)
        
        logger.info(f"Training data retrieved: {len(features)} samples")
        return features, labels
    
    async def bulk_create(
        self,
        db: AsyncSession,
        records: list[DamageRecordCreate]
    ) -> tuple[int, int, list[str]]:
        """Bulk create damage records."""
        logger.info(f"Bulk creating {len(records)} damage records")
        
        success_count = 0
        error_count = 0
        errors = []
        
        for i, data in enumerate(records):
            try:
                record = DamageRecord(
                    component_id=data.component_id,
                    damage_area=data.damage_area,
                    damage_depth=data.damage_depth,
                    damage_point_count=data.damage_point_count,
                    component_age=data.component_age,
                    usage_frequency=data.usage_frequency,
                    corrosion_level=data.corrosion_level,
                    deformation=data.deformation,
                    damage_level=DamageLevel(data.damage_level),
                    notes=data.notes
                )
                db.add(record)
                success_count += 1
            except Exception as e:
                error_count += 1
                errors.append(f"Row {i + 1}: {str(e)}")
        
        if success_count > 0:
            await db.commit()
        
        logger.info(f"Bulk create completed: {success_count} success, {error_count} errors")
        return success_count, error_count, errors


damage_record_service = DamageRecordService()