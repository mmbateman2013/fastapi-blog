"""Module that defines Pydantic Schemas"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


#region User Schema
class UserBase(BaseModel):
    """Base Schema for Users"""
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)


class UserCreate(UserBase):
    """Schema for creating Users"""


class UserResponse(UserBase):
    """Schema for API Response for a User"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    image_file: str | None
    image_path: str


class UserUpdate(BaseModel):
    """Base Schema for Users"""
    username: str | None = Field(min_length=1, max_length=50, default=None)
    email: EmailStr | None = Field(max_length=120, default=None)
    image_file: str | None = Field(min_length=1, max_length=200, default=None)

#endregion


#region Post Schema
class PostBase(BaseModel):
    """Base Schema for Blog Posts"""
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)


class PostCreate(PostBase):
    """Schema for creating Blog Posts"""
    user_id: int #TODO: REMOVE THIS LATER


class PostUpdate(PostBase):
    """Schema for updating Blog Posts"""
    title: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None = Field(default=None, min_length=1)


class PostResponse(PostBase):
    """Schema for API Response for a Blog Post"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    date_posted: datetime
    author: UserResponse
#endregion
