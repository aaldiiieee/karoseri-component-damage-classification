from typing import Optional
from pydantic import BaseModel

# Base schema - shared fields
class UserBase(BaseModel):
    username: str

# Create request
class UserCreate(UserBase):
    password: str

# Update request - all fields optional
class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None

# Response - exclude password
class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True

# Full model (internal use)
class User(UserResponse):
    password: str