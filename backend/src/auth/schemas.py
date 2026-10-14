import uuid
from datetime import datetime

from pydantic import BaseModel, Field
from src.books.schemas import Book
from src.reviews.schemas import ReviewModel


class UserCreateModel(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    email: str = Field(max_length=40)
    first_name: str
    last_name: str
    password: str = Field(min_length=6, max_length=72)


class UserModel(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    role: str
    is_verified: bool = Field(default=False)
    password_hash: str = Field(exclude=True)
    created_at: datetime
    updated_at: datetime
    
    
class UserBooksModel(UserModel):
    books : list[Book]
    reviews : list[ReviewModel]
    
    



class UserLoginModel(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=6, max_length=72)
    
    
    
class EmailModel(BaseModel):
    addresses: list[str]
    
    
    
class PasswordResetRequestModel(BaseModel):
    email: str


class PasswordResetConfirmModel(BaseModel):
    new_password: str
    confirm_new_password: str