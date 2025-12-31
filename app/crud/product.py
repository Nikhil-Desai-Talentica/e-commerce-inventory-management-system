# app/crud/product.py
from typing import Sequence
from math import ceil

from sqlalchemy import select, func, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.models.category import Category
from app.schemas.product import ProductCreate, ProductUpdate


async def get(db: AsyncSession, product_id: int) -> Product | None:
    result = await db.execute(
        select(Product)
        .where(Product.id == product_id)
        .options()
    )
    return result.scalar_one_or_none()


async def get_multi(
    db: AsyncSession,
    *,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    category_id: int | None = None,
) -> tuple[Sequence[Product], int]:
    """
    Get products with pagination, search, and category filter.
    Returns tuple of (products, total_count).
    """
    query = select(Product)
    count_query = select(func.count()).select_from(Product)

    # Apply filters
    conditions = []
    if search:
        search_pattern = f"%{search.lower()}%"
        conditions.append(func.lower(Product.name).like(search_pattern))
    
    if category_id:
        conditions.append(Product.category_id == category_id)

    if conditions:
        combined_condition = and_(*conditions) if len(conditions) > 1 else conditions[0]
        query = query.where(combined_condition)
        count_query = count_query.where(combined_condition)

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Apply pagination and ordering
    query = query.order_by(Product.name).offset(skip).limit(limit)
    
    result = await db.execute(query)
    products = result.scalars().all()
    
    return products, total


async def create(db: AsyncSession, obj_in: ProductCreate) -> Product:
    # Verify category exists
    category = await db.get(Category, obj_in.category_id)
    if not category:
        raise ValueError(f"Category with id {obj_in.category_id} does not exist")

    db_obj = Product(**obj_in.model_dump())
    db.add(db_obj)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise
    await db.refresh(db_obj)
    return db_obj


async def update(db: AsyncSession, db_obj: Product, obj_in: ProductUpdate) -> Product:
    # If category_id is being updated, verify it exists
    if obj_in.category_id is not None and obj_in.category_id != db_obj.category_id:
        category = await db.get(Category, obj_in.category_id)
        if not category:
            raise ValueError(f"Category with id {obj_in.category_id} does not exist")

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


async def remove(db: AsyncSession, db_obj: Product) -> None:
    await db.delete(db_obj)
    await db.commit()