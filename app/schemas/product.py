# app/schemas/product.py
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from app.schemas.category import Category


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category_id: int = Field(..., gt=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category_id: Optional[int] = Field(None, gt=0)


class ProductInDBBase(ProductBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class Product(ProductInDBBase):
    category: Category


class ProductListResponse(BaseModel):
    items: list[Product]
    total: int
    page: int
    page_size: int
    total_pages: int

    model_config = ConfigDict(from_attributes=True)