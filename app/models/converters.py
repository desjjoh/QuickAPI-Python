"""
models/converters.py
-------------------
Utility functions for converting between ORM models and Pydantic schemas.

Provides a consistent interface for transforming database entities into
validated API response objects. This layer enforces strict typing and
ensures data consistency between ORM and schema layers.

✅ Converts SQLAlchemy ORM instances → Pydantic models (ORM mode).
✅ Converts Pydantic input schemas → plain dicts for ORM insertion.
✅ Mirrors how TypeORM entities map to DTOs in your TypeScript projects.

"""

from typing import TypeVar, Type

from app.models.db_models import ItemORM
from app.models.schemas import ItemIn, ItemOut, Item

# Generic type variables for flexibility if you extend this pattern.
TORM = TypeVar("TORM")
TPydantic = TypeVar("TPydantic")


def orm_to_item(orm_obj: ItemORM) -> ItemOut:
    """
    Convert an `ItemORM` instance into an `ItemOut` Pydantic model.

    Args:
        orm_obj (ItemORM):
            A SQLAlchemy ORM object retrieved from the database.

    Returns:
        ItemOut:
            A validated Pydantic model suitable for API responses.

    Example:
        ```python
        db_item = await session.get(ItemORM, 1)
        response = orm_to_item(db_item)
        return response  # ItemOut(id=1, name='Retro Console', price=199.99)
        ```
    """
    return ItemOut.model_validate(orm_obj)


def itemin_to_dict(payload: ItemIn) -> dict:
    """
    Convert an `ItemIn` Pydantic input model into a plain dictionary.

    This function is used when creating ORM objects from API input data.

    Args:
        payload (ItemIn):
            The validated Pydantic input payload from the API layer.

    Returns:
        dict:
            A dictionary ready for unpacking into ORM constructors or
            SQLAlchemy insert statements.

    Example:
        ```python
        data = itemin_to_dict(ItemIn(name='Retro Console', price=199.99))
        new_item = ItemORM(**data)
        session.add(new_item)
        ```
    """
    return payload.model_dump()


def orm_to_item_core(orm_obj: ItemORM) -> Item:
    """
    Convert an `ItemORM` instance into a lightweight internal `Item` model.

    This variant is used internally when you don’t need full API metadata
    or response shape — just an internal, validated object for processing.

    Args:
        orm_obj (ItemORM):
            ORM entity retrieved from the database.

    Returns:
        Item:
            Internal application representation of the item.
    """
    return Item.model_validate(orm_obj)
