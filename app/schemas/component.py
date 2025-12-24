from typing import Optional
from pydantic import Field, BaseModel

class ComponentBase(BaseModel):
    """Base schema for Component."""
    component_code: str = Field(..., min_length=1, max_length=50, examples=["KRS-001"])
    component_name: str = Field(..., min_length=1, max_length=100, examples=["Roof Panel"])
    category: str = Field(..., min_length=1, max_length=50, examples=["Body Panel"])
    description: Optional[str] = Field(None, examples=["Roof section panel of the vehicle"])


class ComponentCreate(ComponentBase):
    """Schema for creating a new Component."""
    pass


class ComponentUpdate(BaseModel):
    """Schema for updating Component (all fields optional)."""
    component_code: Optional[str] = Field(None, min_length=1, max_length=50)
    component_name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ComponentResponse(ComponentBase):
    """Response schema for Component."""
    is_active: bool


class ComponentList(BaseModel):
    """Schema for Component list with pagination."""
    items: list[ComponentResponse]
    total: int
    page: int
    size: int
    pages: int