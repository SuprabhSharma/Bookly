from pydantic import BaseModel , Field
from datetime import datetime
from typing  import Optional
import uuid



class ReviewModel(BaseModel):
    uid: uuid.UUID 
    rating: int = Field(le=5)
    review_test : str 
    user_id: uuid.UUID  
    book_id: uuid.UUID 
    created_at: datetime 
    


class ReviewCreateModel(BaseModel):
    rating: int = Field(le=5)
    review_test : str