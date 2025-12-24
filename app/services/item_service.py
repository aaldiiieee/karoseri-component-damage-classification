from typing import Union, Optional
from ..schemas.item import ItemResponse

class ItemService:
    @staticmethod
    def get_root():
        return {"Hello": "World"}

    @staticmethod
    def get_item(item_id: int, q: Optional[str] = None) -> ItemResponse:
        return ItemResponse(item_id=item_id, q=q)

item_service = ItemService()
