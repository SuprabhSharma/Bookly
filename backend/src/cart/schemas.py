import uuid
from decimal import Decimal
from typing import List

from pydantic import BaseModel, Field


class CartItemAdd(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(1, ge=1)


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=1)


class CartItemOut(BaseModel):
    uid: uuid.UUID
    product_id: uuid.UUID
    quantity: int
    unit_price: Decimal
    line_total: Decimal
    product_title: str

    class Config:
        from_attributes = True


class CartOut(BaseModel):
    uid: uuid.UUID
    items: List[CartItemOut]
    subtotal: Decimal
