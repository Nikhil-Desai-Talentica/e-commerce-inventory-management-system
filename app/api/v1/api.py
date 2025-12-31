# app/api/v1/api.py
from fastapi import APIRouter

from app.api.v1.endpoints import category, product

api_router = APIRouter()
api_router.include_router(category.router)
api_router.include_router(product.router)