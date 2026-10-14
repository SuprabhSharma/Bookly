import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class ServiceCreate(BaseModel):
    title: str
    slug: str
    description: Optional[str] = None
    price: Decimal = Field(..., ge=0)
    duration_minutes: int = Field(default=60, ge=1)
    image_urls: List[str] = []


class ServiceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = Field(default=None, ge=0)
    duration_minutes: Optional[int] = Field(default=None, ge=1)
    status: Optional[str] = None
    image_urls: Optional[List[str]] = None


class ServiceImageOut(BaseModel):
    uid: uuid.UUID
    url: str
    position: int

    class Config:
        from_attributes = True


class ServiceVendorOut(BaseModel):
    uid: uuid.UUID
    store_name: str
    slug: str

    class Config:
        from_attributes = True


class ServiceOut(BaseModel):
    uid: uuid.UUID
    title: str
    slug: str
    description: Optional[str] = None
    price: Decimal
    duration_minutes: int
    status: str
    vendor: Optional[ServiceVendorOut] = None
    images: List[ServiceImageOut] = []
    created_at: datetime

    class Config:
        from_attributes = True


class ServiceListOut(BaseModel):
    items: List[ServiceOut]
    total: int
    page: int
    page_size: int
    pages: int
