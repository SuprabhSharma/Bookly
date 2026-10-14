import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str
    slug: str
    parent_id: Optional[uuid.UUID] = None
    image_url: Optional[str] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None
    image_url: Optional[str] = None


class CategoryOut(BaseModel):
    uid: uuid.UUID
    name: str
    slug: str
    parent_id: Optional[uuid.UUID] = None
    image_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
