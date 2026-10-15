import uuid
from datetime import datetime
from typing import List

from pydantic import BaseModel

from src.products.schemas import ProductSummaryOut


class WishlistItemAdd(BaseModel):
    product_id: uuid.UUID


class WishlistItemOut(BaseModel):
    uid: uuid.UUID
    product_id: uuid.UUID
    product_title: str
    product_slug: str
    created_at: datetime
    product: ProductSummaryOut

    class Config:
        from_attributes = True


class WishlistOut(BaseModel):
    items: List[WishlistItemOut]
    total: int
