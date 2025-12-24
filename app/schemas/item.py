from typing import Optional
from pydantic import BaseModel

class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int

    class Config:
        from_attributes = True

class ItemResponse(BaseModel):
    item_id: int
    q: Optional[str] = None
