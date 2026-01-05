# app/crud/sku.py
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sku import SKU
from app.models.product import Product
from app.schemas.sku import SKUCreate, SKUUpdate


async def get(db: AsyncSession, sku_id: int) -> SKU | None:
    result = await db.execute(select(SKU).where(SKU.id == sku_id))
    return result.scalar_one_or_none()


async def get_for_product(db: AsyncSession, product_id: int) -> Sequence[SKU]:
    result = await db.execute(
        select(SKU)
        .where(SKU.product_id == product_id)
        .order_by(SKU.name)
    )
    return result.scalars().all()


async def create(db: AsyncSession, product_id: int, obj_in: SKUCreate) -> SKU:
    product = await db.get(Product, product_id)
    if not product:
        raise ValueError(f"Product with id {product_id} does not exist")

    db_obj = SKU(**obj_in.model_dump(), product_id=product_id)
    db.add(db_obj)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise
    await db.refresh(db_obj)
    return db_obj


async def update(db: AsyncSession, db_obj: SKU, obj_in: SKUUpdate) -> SKU:
    if obj_in.product_id is not None and obj_in.product_id != db_obj.product_id:
        product = await db.get(Product, obj_in.product_id)
        if not product:
            raise ValueError(f"Product with id {obj_in.product_id} does not exist")

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


async def remove(db: AsyncSession, db_obj: SKU) -> None:
    await db.delete(db_obj)
    await db.commit()
