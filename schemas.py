"""Module that defines Pydantic Schemas"""
from pydantic import BaseModel, ConfigDict, Field


class PostBase(BaseModel):
    """Base Schema for Blog Posts"""
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=50)


class PostCreate(PostBase):
    """Schema for creating Blog Posts"""


class PostResponse(PostBase):
    """Schema for API Response for a Blog Post"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    date_posted: str
