from fastapi import APIRouter
from .users import router as users_router
from .component import router as component_router
from .damage_record import router as damage_record_router
from .dashboard import router as dashboard_router
from .auth import router as auth_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(component_router)
router.include_router(damage_record_router)
router.include_router(dashboard_router)
