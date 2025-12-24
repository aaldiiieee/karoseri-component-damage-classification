from fastapi import APIRouter
from .items import router as items_router
from .users import router as users_router

router = APIRouter()
router.include_router(items_router)
router.include_router(users_router)
