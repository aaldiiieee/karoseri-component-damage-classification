from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.configs.security import get_current_user
from ..schemas.auth import AuthLoginRequest, AuthLoginResponse
from ..services.auth_service import auth_service
from ..configs.db import get_db
import logging

router = APIRouter(
    prefix="/auth", 
    tags=["Authentication"],
    responses={
        404: {"description": "Authentication failed"},
        500: {"description": "Internal Server Error"}
    },
)


logger = logging.getLogger("app")


@router.post("/login", response_model=AuthLoginResponse, status_code=status.HTTP_200_OK)
async def login(auth_data: AuthLoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate a user and return authentication response."""
    auth_response = await auth_service.login(db, auth_data)
    if not auth_response:
        raise HTTPException(status_code=404, detail="Authentication failed")
    return auth_response


@router.get("/protected", status_code=status.HTTP_200_OK)
async def protected_route(username: str = Depends(get_current_user)):
    """A protected route that requires authentication."""
    return {"message": f"Hello, {username}. You have accessed a protected route."}