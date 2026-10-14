import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


class CheckoutRequest(BaseModel):
    address_id: uuid.UUID
    payment_method: str = "cod"  # cod | online_mock


class OrderItemOut(BaseModel):
    uid: uuid.UUID
    product_id: uuid.UUID
    title_snapshot: str
    price_snapshot: Decimal
    quantity: int
    line_total: Decimal

    class Config:
        from_attributes = True


class SubOrderOut(BaseModel):
    uid: uuid.UUID
    vendor_id: uuid.UUID
    subtotal: Decimal
    status: str
    items: List[OrderItemOut]

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    uid: uuid.UUID
    total: Decimal
    payment_method: str
    payment_status: str
    status: str
    address_snapshot: dict
    sub_orders: List[SubOrderOut]
    created_at: datetime

    class Config:
        from_attributes = True


class SubOrderStatusUpdate(BaseModel):
    status: str  # confirmed | shipped | delivered | cancelled
