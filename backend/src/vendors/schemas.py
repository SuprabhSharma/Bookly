import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class VendorApply(BaseModel):
    store_name: str
    slug: str
    description: Optional[str] = None
    logo_url: Optional[str] = None


class VendorUpdate(BaseModel):
    store_name: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None


class VendorOut(BaseModel):
    uid: uuid.UUID
    store_name: str
    slug: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
