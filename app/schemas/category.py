# app/schemas/category.py
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)


class CategoryInDBBase(CategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class Category(CategoryInDBBase):
    pass