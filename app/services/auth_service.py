from fastapi import HTTPException, status
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.configs.security import verify_password, create_access_token, create_refresh_token, get_password_hash

from app.models.users import User
from app.schemas.auth import AuthLoginResponse, AuthLoginRequest

import logging

logger = logging.getLogger("app")


class AuthService:
    """Service for user authentication and management."""
    
    async def login(self, db: AsyncSession, data: AuthLoginRequest) -> Optional[User]:
        """
        Authenticate user by username and password.
        
        Args:
            db: Database session
            data: AuthLoginRequest object containing username and password

        Returns:
            Authenticated User object or None
        """

        logger.info(f"Attempting login for user: {data.username}")

        result = await db.execute(select(User).where(User.username == data.username))

        user = result.scalars().first()
        if not user:
            logger.warning(f"Login failed: User {data.username} not found")
            return None
        
        if not verify_password(data.password, user.password):
            logger.warning(f"Login failed: Incorrect password for user {data.username}")
            return None
        
        token = create_access_token(
            data = {
                "user_id": str(user.id),
                "username": str(user.username),
            }
        )

        logger.info(f"User {data.username} authenticated successfully")

        response = AuthLoginResponse(
            access_token=token,
            token_type="bearer"
        )

        return response
    
auth_service = AuthService()