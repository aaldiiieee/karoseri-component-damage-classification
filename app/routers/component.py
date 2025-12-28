import logging
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.configs.db import get_db
from ..schemas import (
    ComponentCreate,
    ComponentUpdate,
    ComponentResponse,
    ComponentList
)
from app.services import component_service

logger = logging.getLogger("app")

router = APIRouter(prefix="/components", tags=["Components"])

@router.post("/", response_model=ComponentResponse, status_code=201)
async def create_component(
    data: ComponentCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new component."""
    # Check if component code already exists
    existing = await component_service.get_by_code(db, data.code)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Component with code '{data.code}' already exists"
        )
    
    component = await component_service.create(db, data)
    return component


@router.get("/", response_model=ComponentList)
async def get_components(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search by code or name"),
    db: AsyncSession = Depends(get_db)
):
    """Get all components with pagination and filters."""
    items, total = await component_service.get_all(
        db, page=page, size=size, category=category, is_active=is_active, search=search
    )
    
    pages = (total + size - 1) // size  # Ceiling division
    
    return ComponentList(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/categories", response_model=list[str])
async def get_categories(db: AsyncSession = Depends(get_db)):
    """Get all unique component categories."""
    return await component_service.get_categories(db)


@router.get("/{component_id}", response_model=ComponentResponse)
async def get_component(
    component_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a component by ID."""
    component = await component_service.get_by_id(db, component_id)
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    return component


@router.put("/{component_id}", response_model=ComponentResponse)
async def update_component(
    component_id: UUID,
    data: ComponentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a component."""
    # Check if new code already exists (if updating code)
    if data.code:
        existing = await component_service.get_by_code(db, data.code)
        if existing and existing.id != component_id:
            raise HTTPException(
                status_code=400,
                detail=f"Component with code '{data.code}' already exists"
            )
    
    component = await component_service.update(db, component_id, data)
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    return component


@router.delete("/{component_id}", status_code=204)
async def delete_component(
    component_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete a component."""
    deleted = await component_service.delete(db, component_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Component not found")
    return None