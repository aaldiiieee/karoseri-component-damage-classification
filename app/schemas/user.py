from typing import Optional
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

# Base schema - shared fields
class UserBase(BaseModel):
    username: str
    role: Optional[str] = "user"
    is_active: Optional[bool] = True


# Create request
class UserCreate(UserBase):
    password: str


# Update request - all fields optional
class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


# Response - exclude password
class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Full model (internal use)
class User(UserResponse):
    password: str