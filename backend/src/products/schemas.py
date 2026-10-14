import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class ProductImageOut(BaseModel):
    uid: uuid.UUID
    url: str
    position: int

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: Decimal = Field(..., ge=0)
    mrp: Optional[Decimal] = Field(default=None, ge=0)
    stock: int = Field(default=0, ge=0)
    sku: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    attributes: Optional[dict] = None


class ProductCreate(ProductBase):
    slug: str
    image_urls: List[str] = []


class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = Field(default=None, ge=0)
    mrp: Optional[Decimal] = Field(default=None, ge=0)
    stock: Optional[int] = Field(default=None, ge=0)
    sku: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    status: Optional[str] = None
    attributes: Optional[dict] = None
    image_urls: Optional[List[str]] = None


class VendorMiniOut(BaseModel):
    uid: uuid.UUID
    store_name: str
    slug: str

    class Config:
        from_attributes = True


class CategoryMiniOut(BaseModel):
    uid: uuid.UUID
    name: str
    slug: str

    class Config:
        from_attributes = True


class ProductOut(BaseModel):
    uid: uuid.UUID
    title: str
    slug: str
    description: Optional[str] = None
    price: Decimal
    mrp: Optional[Decimal] = None
    stock: int
    sku: Optional[str] = None
    status: str
    rating_avg: Decimal
    rating_count: int
    attributes: Optional[dict] = None
    vendor: Optional[VendorMiniOut] = None
    category: Optional[CategoryMiniOut] = None
    images: List[ProductImageOut] = []
    created_at: datetime

    class Config:
        from_attributes = True


class ProductListOut(BaseModel):
    items: List[ProductOut]
    total: int
    page: int
    page_size: int
    pages: int
