import logging
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
import csv
import io

from ..configs.db import get_db
from ..schemas import (
    DamageRecordCreate,
    DamageRecordUpdate,
    DamageRecordResponse,
    DamageRecordList,
    DamageDistribution,
    BulkImportResult
)
from ..services import damage_record_service, component_service

logger = logging.getLogger("app")

router = APIRouter(prefix="/damage-records", tags=["Damage Records"])


@router.post("/", response_model=DamageRecordResponse, status_code=201)
async def create_damage_record(
    data: DamageRecordCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new damage record (training data)."""
    # Verify component exists
    component = await component_service.get_by_id(db, data.component_id)
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    
    record = await damage_record_service.create(db, data)
    return record


@router.get("/", response_model=DamageRecordList)
async def get_damage_records(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    component_id: Optional[UUID] = Query(None, description="Filter by component"),
    damage_level: Optional[str] = Query(None, description="Filter by damage level (ringan/sedang/berat)"),
    db: AsyncSession = Depends(get_db)
):
    """Get all damage records with pagination and filters."""
    # Validate damage_level
    if damage_level:
        damage_level = damage_level.lower()
        if damage_level not in ["ringan", "sedang", "berat"]:
            raise HTTPException(
                status_code=400,
                detail="damage_level must be one of: ringan, sedang, berat"
            )
    
    items, total = await damage_record_service.get_all(
        db, page=page, size=size, component_id=component_id, damage_level=damage_level
    )
    
    pages = (total + size - 1) // size
    
    return DamageRecordList(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/distribution", response_model=DamageDistribution)
async def get_damage_distribution(db: AsyncSession = Depends(get_db)):
    """Get damage level distribution statistics."""
    return await damage_record_service.get_distribution(db)


@router.get("/{record_id}", response_model=DamageRecordResponse)
async def get_damage_record(
    record_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a damage record by ID."""
    record = await damage_record_service.get_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Damage record not found")
    return record


@router.put("/{record_id}", response_model=DamageRecordResponse)
async def update_damage_record(
    record_id: UUID,
    data: DamageRecordUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a damage record."""
    # Verify component exists if updating component_id
    if data.component_id:
        component = await component_service.get_by_id(db, data.component_id)
        if not component:
            raise HTTPException(status_code=404, detail="Component not found")
    
    record = await damage_record_service.update(db, record_id, data)
    if not record:
        raise HTTPException(status_code=404, detail="Damage record not found")
    return record


@router.delete("/{record_id}", status_code=204)
async def delete_damage_record(
    record_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete a damage record."""
    deleted = await damage_record_service.delete(db, record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Damage record not found")
    return None


@router.post("/bulk-import", response_model=BulkImportResult)
async def bulk_import_damage_records(
    file: UploadFile = File(..., description="CSV file with damage records"),
    db: AsyncSession = Depends(get_db)
):
    """
    Bulk import damage records from CSV file.
    
    CSV format:
    component_code,damage_area,damage_depth,damage_point_count,component_age,usage_frequency,corrosion_level,deformation,damage_level,notes
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    content = await file.read()
    decoded = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(decoded))
    
    records = []
    errors = []
    
    for i, row in enumerate(reader, start=2):  # Start at 2 (1 for header)
        try:
            # Get component by code
            component_code = row.get("component_code", "").strip()
            component = await component_service.get_by_code(db, component_code)
            
            if not component:
                errors.append(f"Row {i}: Component '{component_code}' not found")
                continue
            
            record_data = DamageRecordCreate(
                component_id=component.id,
                damage_area=float(row["damage_area"]),
                damage_depth=float(row["damage_depth"]),
                damage_point_count=int(row["damage_point_count"]),
                component_age=int(row["component_age"]),
                usage_frequency=int(row["usage_frequency"]),
                corrosion_level=int(row["corrosion_level"]),
                deformation=float(row["deformation"]),
                damage_level=row["damage_level"].strip(),
                notes=row.get("notes", "").strip() or None
            )
            records.append(record_data)
        except Exception as e:
            errors.append(f"Row {i}: {str(e)}")
    
    # Bulk create valid records
    if records:
        success, error_count, bulk_errors = await damage_record_service.bulk_create(db, records)
        errors.extend(bulk_errors)
    else:
        success = 0
    
    return BulkImportResult(
        success_count=success,
        error_count=len(errors),
        errors=errors[:20]  # Limit to first 20 errors
    )