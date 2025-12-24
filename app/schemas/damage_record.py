from typing import Optional
from uuid import UUID
from pydantic import Field, field_validator, BaseModel 
from .component import ComponentResponse

class DamageFeatures(BaseModel):
    """Schema for 7 Naive Bayes input features."""
    damage_area: float = Field(..., gt=0, description="Damage area in cm²", examples=[5.5])
    damage_depth: float = Field(..., gt=0, description="Damage depth in mm", examples=[1.2])
    damage_point_count: int = Field(..., gt=0, description="Number of damage points", examples=[3])
    component_age: int = Field(..., gt=0, description="Component age in months", examples=[12])
    usage_frequency: int = Field(..., ge=1, le=10, description="Usage frequency (1-10)", examples=[5])
    corrosion_level: int = Field(..., ge=1, le=5, description="Corrosion level (1-5)", examples=[2])
    deformation: float = Field(..., ge=0, description="Deformation in mm", examples=[0.8])


class DamageRecordBase(DamageFeatures):
    """Base schema for DamageRecord."""
    component_id: UUID
    damage_level: str = Field(..., pattern="^(Ringan|Sedang|Berat)$", examples=["Ringan"])
    notes: Optional[str] = None

    @field_validator("damage_level")
    @classmethod
    def validate_damage_level(cls, v: str) -> str:
        allowed = ["Ringan", "Sedang", "Berat"]
        if v not in allowed:
            raise ValueError(f"damage_level must be one of: {allowed}")
        return v


class DamageRecordCreate(DamageRecordBase):
    """Schema for creating a new DamageRecord."""
    pass


class DamageRecordUpdate(BaseModel):
    """Schema for updating DamageRecord."""
    component_id: Optional[UUID] = None
    damage_area: Optional[float] = Field(None, gt=0)
    damage_depth: Optional[float] = Field(None, gt=0)
    damage_point_count: Optional[int] = Field(None, gt=0)
    component_age: Optional[int] = Field(None, gt=0)
    usage_frequency: Optional[int] = Field(None, ge=1, le=10)
    corrosion_level: Optional[int] = Field(None, ge=1, le=5)
    deformation: Optional[float] = Field(None, ge=0)
    damage_level: Optional[str] = Field(None, pattern="^(Ringan|Sedang|Berat)$")
    notes: Optional[str] = None


class DamageRecordResponse(DamageRecordBase):
    """Response schema for DamageRecord."""
    component: Optional[ComponentResponse] = None


class DamageRecordList(BaseModel):
    """Schema for DamageRecord list with pagination."""
    items: list[DamageRecordResponse]
    total: int
    page: int
    size: int
    pages: int


class DamageDistribution(BaseModel):
    """Schema for damage level distribution."""
    ringan: int = 0
    sedang: int = 0
    berat: int = 0
    total: int = 0


class BulkImportResult(BaseModel):
    """Schema for bulk import result."""
    success_count: int
    error_count: int
    errors: list[str] = []