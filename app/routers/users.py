from typing import List
from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.user import UserCreate, UserUpdate, UserResponse
from ..services.user_service import user_service
from ..configs.db import get_db
import logging

router = APIRouter(
    prefix="/users", 
    tags=["User Management System"],
    responses={
        404: {"description": "User not found"},
        500: {"description": "Internal Server Error"}
    },
)

logger = logging.getLogger("app")

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user."""
    return await user_service.create_user(db, user_in)

@router.get("/", response_model=List[UserResponse])
async def read_users(db: AsyncSession = Depends(get_db)):
    """Read all users."""
    return await user_service.get_users(db)

@router.get("/{user_id}", response_model=UserResponse)
async def read_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """Read a user by ID."""
    user = await user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: UUID, user_in: UserUpdate, db: AsyncSession = Depends(get_db)):
    """Update a user by ID."""
    user = await user_service.update_user(db, user_id, user_in)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a user by ID."""
    success = await user_service.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return None
