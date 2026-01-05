# app/schemas/sku.py
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SKUBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    price: Decimal = Field(..., ge=0)
    quantity: int = Field(..., ge=0)


class SKUCreate(SKUBase):
    pass


class SKUUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)
    quantity: Optional[int] = Field(None, ge=0)
    product_id: Optional[int] = Field(None, gt=0)


class SKUInDBBase(SKUBase):
    id: int
    product_id: int

    model_config = ConfigDict(from_attributes=True)


class SKU(SKUInDBBase):
    pass


class SKUListResponse(BaseModel):
    items: list[SKU]
    total: int

    model_config = ConfigDict(from_attributes=True)
