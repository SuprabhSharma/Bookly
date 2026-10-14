from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel, Field


class ReviewModel(BaseModel):
    uid: uuid.UUID
    rating: int = Field(ge=1, le=5)
    review_text: str
    user_id: uuid.UUID
    book_id: Optional[uuid.UUID] = None
    created_at: datetime


class ReviewCreateModel(BaseModel):
    rating: int = Field(ge=1, le=5)
    review_text: str


class ReviewOut(BaseModel):
    uid: uuid.UUID
    rating: int
    review_text: str
    user_id: Optional[uuid.UUID] = None
    product_id: Optional[uuid.UUID] = None
    book_id: Optional[uuid.UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True