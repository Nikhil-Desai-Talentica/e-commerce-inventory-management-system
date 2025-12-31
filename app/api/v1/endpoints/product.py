# app/api/v1/endpoints/product.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app import crud, schemas

from math import ceil

router = APIRouter(prefix="/products", tags=["products"])


@router.post(
    "",
    response_model=schemas.Product,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    product_in: schemas.ProductCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await crud.product.create(db, obj_in=product_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this name already exists.",
        )


@router.get("/{product_id}", response_model=schemas.Product)
async def read_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    product = await crud.product.get(db, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )
    return product


@router.get("", response_model=schemas.ProductListResponse)
async def list_products(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    search: str | None = Query(None, description="Search by product name"),
    category_id: int | None = Query(None, gt=0, description="Filter by category ID"),
):
    skip = (page - 1) * page_size
    products, total = await crud.product.get_multi(
        db,
        skip=skip,
        limit=page_size,
        search=search,
        category_id=category_id,
    )

    total_pages = ceil(total / page_size) if total > 0 else 0

    return schemas.ProductListResponse(
        items=list(products),
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.put("/{product_id}", response_model=schemas.Product)
async def update_product(
    product_id: int,
    product_in: schemas.ProductUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await crud.product.get(db, product_id=product_id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )

    try:
        return await crud.product.update(db, db_obj=db_obj, obj_in=product_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error updating product.",
        )


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await crud.product.get(db, product_id=product_id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )
    await crud.product.remove(db, db_obj=db_obj)