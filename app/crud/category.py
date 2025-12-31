# app/crud/category.py
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


async def get(db: AsyncSession, category_id: int) -> Category | None:
    result = await db.execute(select(Category).where(Category.id == category_id))
    return result.scalar_one_or_none()


async def get_by_name(db: AsyncSession, name: str) -> Category | None:
    result = await db.execute(select(Category).where(Category.name == name))
    return result.scalar_one_or_none()


async def get_multi(db: AsyncSession) -> Sequence[Category]:
    result = await db.execute(select(Category).order_by(Category.name))
    return result.scalars().all()


async def create(db: AsyncSession, obj_in: CategoryCreate) -> Category:
    db_obj = Category(**obj_in.model_dump())
    db.add(db_obj)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise
    await db.refresh(db_obj)
    return db_obj


async def update(db: AsyncSession, db_obj: Category, obj_in: CategoryUpdate) -> Category:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise
    await db.refresh(db_obj)
    return db_obj


async def remove(db: AsyncSession, db_obj: Category) -> None:
    await db.delete(db_obj)
    await db.commit()