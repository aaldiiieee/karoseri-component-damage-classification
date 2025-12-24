from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from ..schemas.users import UserCreate, UserUpdate, UserResponse
from ..services.user_service import user_service

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate):
    return user_service.create_user(user_in)

@router.get("/", response_model=List[UserResponse])
def read_users():
    return user_service.get_users()

@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int):
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_in: UserUpdate):
    user = user_service.update_user(user_id, user_in)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    success = user_service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return None
