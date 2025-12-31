# app/api/v1/api.py
from fastapi import APIRouter

from app.api.v1.endpoints import category

api_router = APIRouter()
api_router.include_router(category.router)