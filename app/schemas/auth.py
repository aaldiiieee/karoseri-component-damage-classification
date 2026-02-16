from typing import Optional
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

# Base schema - shared fields
class AuthBase(BaseModel):
    username: str
    password: str


# Auth login request
class AuthLoginRequest(AuthBase):
    pass


# Auth login response
class AuthLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str
    role: Optional[str] = None