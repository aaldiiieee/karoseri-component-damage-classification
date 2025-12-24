from typing import Optional
from fastapi import APIRouter
from ..services.item_service import item_service
from ..schemas.item import ItemResponse

router = APIRouter()

@router.get("/")
def read_root():
    return item_service.get_root()

@router.get("/items/{item_id}", response_model=ItemResponse)
def read_item(item_id: int, q: Optional[str] = None):
    return item_service.get_item(item_id, q)
