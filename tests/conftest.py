# tests/conftest.py
import asyncio
from collections.abc import AsyncGenerator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import delete

from app.api.v1.api import api_router
from app.api import deps
from app.db.base import Base
from app.models.category import Category
from app.models.product import Product


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = sessionmaker(
        bind=test_engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    async with async_session() as session:
        yield session
        # Clean up: delete all records in reverse dependency order
        # This ensures each test starts with a clean database
        await session.execute(delete(Product))
        await session.execute(delete(Category))
        await session.commit()
        await session.rollback()


@pytest.fixture(scope="function")
async def app_with_overrides(db_session: AsyncSession) -> FastAPI:
    app = FastAPI()
    app.include_router(api_router, prefix="/api/v1")

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[deps.get_db] = override_get_db
    return app


@pytest.fixture(scope="function")
async def async_client(app_with_overrides: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    from httpx import ASGITransport
    async with AsyncClient(
        transport=ASGITransport(app=app_with_overrides),
        base_url="http://test"
    ) as client:
        yield client