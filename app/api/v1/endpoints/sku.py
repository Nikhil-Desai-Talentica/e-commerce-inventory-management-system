# app/api/v1/endpoints/sku.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.api.deps import get_db

router = APIRouter(tags=["skus"])


@router.post(
    "/products/{product_id}/skus",
    response_model=schemas.SKU,
    status_code=status.HTTP_201_CREATED,
)
async def create_sku_for_product(
    product_id: int,
    sku_in: schemas.SKUCreate,
    db: AsyncSession = Depends(get_db),
):
    product = await crud.product.get(db, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )
    try:
        return await crud.sku.create(db, product_id=product_id, obj_in=sku_in)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SKU with this name already exists for this product.",
        )


@router.get(
    "/products/{product_id}/skus",
    response_model=schemas.SKUListResponse,
)
async def list_skus_for_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    product = await crud.product.get(db, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )
    skus = await crud.sku.get_for_product(db, product_id=product_id)
    return schemas.SKUListResponse(items=list(skus), total=len(skus))


@router.get("/skus/{sku_id}", response_model=schemas.SKU)
async def read_sku(
    sku_id: int,
    db: AsyncSession = Depends(get_db),
):
    sku = await crud.sku.get(db, sku_id=sku_id)
    if not sku:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SKU not found.",
        )
    return sku


@router.put("/skus/{sku_id}", response_model=schemas.SKU)
async def update_sku(
    sku_id: int,
    sku_in: schemas.SKUUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await crud.sku.get(db, sku_id=sku_id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SKU not found.",
        )

    try:
        return await crud.sku.update(db, db_obj=db_obj, obj_in=sku_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SKU with this name already exists for this product.",
        )


@router.delete(
    "/skus/{sku_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_sku(
    sku_id: int,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await crud.sku.get(db, sku_id=sku_id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SKU not found.",
        )
    await crud.sku.remove(db, db_obj=db_obj)
