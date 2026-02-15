import asyncio
import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.configs.db import AsyncSessionLocal
from app.services.user_service import user_service
from app.schemas.user import UserCreate

async def seed():
    async with AsyncSessionLocal() as db:
        username = "admin"
        
        user = await user_service.get_by_username(db, username)
        if user:
            print(f"User '{username}' already exists.")
            return

        print(f"Creating user '{username}'...")
        try:
            user_in = UserCreate(
                username=username,
                password="password123",
                role="admin",
                is_active=True
            )
            created_user = await user_service.create_user(db, user_in)
            print(f"User '{created_user.username}' created successfully!")
        except Exception as e:
            print(f"Error creating user: {e}")

if __name__ == "__main__":
    asyncio.run(seed())
