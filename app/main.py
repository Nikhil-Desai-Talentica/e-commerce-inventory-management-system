# app/main.py
import asyncio

from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import settings
from app.api.v1.api import api_router
from app.db.base import Base
from app.db.session import engine


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
)


@app.on_event("startup")
async def on_startup() -> None:
    # Simple auto-create of tables; for real prod use Alembic migrations
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Optional: simple health check
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))


app.include_router(api_router, prefix=settings.API_V1_STR)