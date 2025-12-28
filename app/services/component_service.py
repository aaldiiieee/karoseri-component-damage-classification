import logging
from typing import Optional
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.component import Component
from app.schemas.component import ComponentCreate, ComponentUpdate

logger = logging.getLogger("app")


class ComponentService:
    """Service for Component CRUD operations."""
    
    async def create(self, db: AsyncSession, data: ComponentCreate) -> Component:
        """Create a new component."""
        logger.info(f"Creating component: {data.code}")
        
        component = Component(
            code=data.code,
            name=data.name,
            category=data.category,
            description=data.description
        )
        
        db.add(component)
        await db.commit()
        await db.refresh(component)
        
        logger.info(f"Component created: {component.id}")
        return component
    
    async def get_by_id(self, db: AsyncSession, component_id: UUID) -> Optional[Component]:
        """Get component by ID."""
        logger.debug(f"Getting component: {component_id}")
        
        result = await db.execute(
            select(Component).where(Component.id == component_id)
        )
        return result.scalars().first()
    
    async def get_by_code(self, db: AsyncSession, code: str) -> Optional[Component]:
        """Get component by code."""
        result = await db.execute(
            select(Component).where(Component.code == code)
        )
        return result.scalars().first()
    
    async def get_all(
        self,
        db: AsyncSession,
        page: int = 1,
        size: int = 10,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> tuple[list[Component], int]:
        """Get all components with pagination and filters."""
        logger.debug(f"Getting components: page={page}, size={size}")
        
        query = select(Component)
        count_query = select(func.count(Component.id))
        
        # Apply filters
        if category:
            query = query.where(Component.category == category)
            count_query = count_query.where(Component.category == category)
        
        if is_active is not None:
            query = query.where(Component.is_active == is_active)
            count_query = count_query.where(Component.is_active == is_active)
        
        if search:
            search_filter = f"%{search}%"
            query = query.where(
                (Component.code.ilike(search_filter)) |
                (Component.name.ilike(search_filter))
            )
            count_query = count_query.where(
                (Component.code.ilike(search_filter)) |
                (Component.name.ilike(search_filter))
            )
        
        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination
        offset = (page - 1) * size
        query = query.order_by(Component.created_at.desc()).offset(offset).limit(size)
        
        result = await db.execute(query)
        items = result.scalars().all()
        
        return list(items), total
    
    async def update(
        self,
        db: AsyncSession,
        component_id: UUID,
        data: ComponentUpdate
    ) -> Optional[Component]:
        """Update a component."""
        logger.info(f"Updating component: {component_id}")
        
        component = await self.get_by_id(db, component_id)
        if not component:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(component, key, value)
        
        await db.commit()
        await db.refresh(component)
        
        logger.info(f"Component updated: {component_id}")
        return component
    
    async def delete(self, db: AsyncSession, component_id: UUID) -> bool:
        """Delete a component."""
        logger.info(f"Deleting component: {component_id}")
        
        component = await self.get_by_id(db, component_id)
        if not component:
            return False
        
        await db.delete(component)
        await db.commit()
        
        logger.info(f"Component deleted: {component_id}")
        return True
    
    async def get_count(self, db: AsyncSession) -> int:
        """Get total component count."""
        result = await db.execute(select(func.count(Component.id)))
        return result.scalar() or 0
    
    async def get_categories(self, db: AsyncSession) -> list[str]:
        """Get all unique categories."""
        result = await db.execute(
            select(Component.category).distinct()
        )
        return [row[0] for row in result.fetchall()]


component_service = ComponentService()