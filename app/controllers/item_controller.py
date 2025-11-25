from collections.abc import Sequence
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_session
from app.database.entities.item_orm import ItemORM
from app.database.repositories.item_repo import repo
from app.models.error_model import ErrorResponse
from app.models.item_model import (
    ItemBase,
    ItemResponse,
    UpdateItemRequest,
)
from app.models.parameters_model import HexId

router: APIRouter = APIRouter()


## POST /
@router.post(
    "/",
    summary="Create a new item",
    description="Creates a new item using validated input. Returns the fully normalized item resource after persistence.",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create(
    payload: ItemBase, db: AsyncSession = Depends(get_session)
) -> ItemResponse:
    created: ItemORM = await repo.create(db, item_in=payload)

    return ItemResponse.model_validate(created)


## GET /
@router.get(
    "/",
    summary="Get a list of items",
    description="Retrieves a paginated list of items. Supports page, limit, sorting, and optional filtering.",
    response_model=list[ItemResponse],
    status_code=status.HTTP_200_OK,
)
async def get_all(db: AsyncSession = Depends(get_session)) -> list[ItemResponse]:
    items: Sequence[ItemORM] = await repo.get_all(db)

    return [ItemResponse.model_validate(item) for item in items]


## GET /:id
@router.get(
    "/{id}",
    summary="Get a single item by ID",
    description="Fetches a single item by its unique identifier. Returns 404 if the item does not exist.",
    response_model=ItemResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "No item exists with the provided identifier.",
            "model": ErrorResponse,
        }
    },
)
async def get(id: HexId, db: AsyncSession = Depends(get_session)) -> ItemResponse:
    found: ItemORM | None = await repo.get_by_id(db, id)

    if not found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource with ID '{id}' not found",
        )

    return ItemResponse.model_validate(found)


## PATCH /:id
@router.patch(
    "/{id}",
    summary="Update an item by ID",
    description="Applies a partial update to an existing item. Only provided fields are modified. Returns the updated resource.",
    response_model=ItemResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "No item exists with the provided identifier.",
            "model": ErrorResponse,
        },
    },
)
async def update(
    id: HexId, payload: UpdateItemRequest, db: AsyncSession = Depends(get_session)
) -> ItemResponse:
    update_data: dict[str, Any] = payload.model_dump(exclude_unset=True)

    obj: ItemORM | None = await repo.get_by_id(db, id)

    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource with ID '{id}' not found.",
        )

    updated: ItemORM = await repo.update(db, obj, update_data)

    return ItemResponse.model_validate(updated)


## PUT /:id
@router.put(
    "/{id}",
    summary="Replace an item by ID",
    description="Replaces an existing item with the provided data. All fields must be supplied. Returns the updated resource.",
    response_model=ItemResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "No item exists with the provided identifier.",
            "model": ErrorResponse,
        },
    },
)
async def replace(
    id: HexId, payload: ItemBase, db: AsyncSession = Depends(get_session)
) -> ItemResponse:
    update_data: dict[str, Any] = payload.model_dump(exclude_unset=False)

    obj: ItemORM | None = await repo.get_by_id(db, id)

    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource with ID '{id}' not found.",
        )

    updated: ItemORM = await repo.update(db, obj, update_data)

    return ItemResponse.model_validate(updated)


## DELETE /:id
@router.delete(
    "/{id}",
    summary="Delete an item by ID",
    description="Removes an item by its ID. Returns the deleted resource for confirmation. Returns 404 if the item is not found.",
    response_model=ItemResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "No item exists with the provided identifier.",
            "model": ErrorResponse,
        },
    },
)
async def delete(id: HexId, db: AsyncSession = Depends(get_session)) -> ItemResponse:
    obj: ItemORM | None = await repo.get_by_id(db, id)

    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource with ID '{id}' not found.",
        )

    removed: ItemORM = await repo.delete(db, obj)

    return ItemResponse.model_validate(removed)
