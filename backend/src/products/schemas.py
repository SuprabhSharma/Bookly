import uuid
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from pydantic import BaseModel, Field, computed_field, model_validator


def calculate_discount_percent(price: Decimal, mrp: Optional[Decimal]) -> Decimal:
    if mrp is None or mrp <= price or mrp <= 0:
        return Decimal('0.00')
    return ((mrp - price) / mrp * 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def validate_price_pair(price: Decimal, mrp: Optional[Decimal]) -> None:
    if mrp is not None and mrp < price:
        raise ValueError('MRP must be greater than or equal to the selling price')


class ProductImageOut(BaseModel):
    uid: uuid.UUID
    url: str
    position: int

    class Config:
        from_attributes = True


class ProductSummaryOut(BaseModel):
    uid: uuid.UUID
    title: str
    slug: str
    price: Decimal
    mrp: Optional[Decimal] = None
    stock: int
    images: list[ProductImageOut] = []

    @computed_field
    @property
    def discount_percent(self) -> Decimal:
        return calculate_discount_percent(self.price, self.mrp)

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    title: str
    description: str | None = None
    price: Decimal = Field(..., gt=0)
    mrp: Optional[Decimal] = Field(default=None, ge=0)
    stock: int = Field(default=0, ge=0)
    sku: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    attributes: Optional[dict] = None

    @model_validator(mode='after')
    def validate_prices(self):
        validate_price_pair(self.price, self.mrp)
        return self


class ProductCreate(ProductBase):
    slug: str
    image_urls: list[str] = []


class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = Field(default=None, gt=0)
    mrp: Optional[Decimal] = Field(default=None, ge=0)
    stock: Optional[int] = Field(default=None, ge=0)
    sku: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    status: Optional[str] = None
    attributes: Optional[dict] = None
    image_urls: Optional[list[str]] = None

    @model_validator(mode='after')
    def validate_prices(self):
        if self.price is not None and self.mrp is not None:
            validate_price_pair(self.price, self.mrp)
        return self


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
    images: list[ProductImageOut] = []
    created_at: datetime

    @computed_field
    @property
    def discount_percent(self) -> Decimal:
        return calculate_discount_percent(self.price, self.mrp)

    class Config:
        from_attributes = True


class ProductListOut(BaseModel):
    items: list[ProductOut]
    total: int
    page: int
    page_size: int
    pages: int
