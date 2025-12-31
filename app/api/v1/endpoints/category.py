# app/api/v1/endpoints/category.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app import crud, schemas

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post(
    "",
    response_model=schemas.Category,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    category_in: schemas.CategoryCreate,
    db: AsyncSession = Depends(get_db),
):
    existing = await crud.category.get_by_name(db, name=category_in.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists.",
        )
    try:
        return await crud.category.create(db, obj_in=category_in)
    except IntegrityError:
        # Extra safety for race conditions
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists.",
        )


@router.get("/{category_id}", response_model=schemas.Category)
async def read_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
):
    category = await crud.category.get(db, category_id=category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found.",
        )
    return category


@router.get("", response_model=list[schemas.Category])
async def list_categories(
    db: AsyncSession = Depends(get_db),
):
    return await crud.category.get_multi(db)


@router.put("/{category_id}", response_model=schemas.Category)
async def update_category(
    category_id: int,
    category_in: schemas.CategoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await crud.category.get(db, category_id=category_id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found.",
        )

    if category_in.name:
        existing = await crud.category.get_by_name(db, name=category_in.name)
        if existing and existing.id != category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another category with this name already exists.",
            )

    try:
        return await crud.category.update(db, db_obj=db_obj, obj_in=category_in)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Another category with this name already exists.",
        )


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await crud.category.get(db, category_id=category_id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found.",
        )
    await crud.category.remove(db, db_obj=db_obj)