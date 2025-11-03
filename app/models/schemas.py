"""
models/schemas.py
-----------------
Pydantic models defining API input and output schemas for the Item resource.

These models are used to validate request bodies and serialize responses.
They mirror the SQLAlchemy ORM structure but remain independent of it,
allowing strict validation and transformation control.

✅ Supports `.from_orm()` conversion for ORM objects.
✅ Enforces type validation and length constraints.
✅ Used in route handlers and OpenAPI schema generation.
"""

from pydantic import BaseModel, Field


class ItemIn(BaseModel):
    """
    Schema for creating a new item.

    Attributes:
        name (str): The name of the item (1–120 characters).
        price (float): The item’s price, must be non-negative.
    """

    name: str = Field(..., min_length=1, max_length=120, description="Name of the item.")
    price: float = Field(..., ge=0, description="Item price in currency units.")

    class Config:
        """Enable ORM compatibility for nested validation."""
        from_attributes = True  # replaces `orm_mode = True` in Pydantic v2


class ItemOut(BaseModel):
    """
    Schema for API responses containing item data.

    Attributes:
        id (int): The database-generated unique identifier.
        name (str): The item’s display name.
        price (float): The item’s price in standard currency units.
    """

    id: int = Field(..., description="Unique identifier for the item.")
    name: str = Field(..., description="Name of the item.")
    price: float = Field(..., ge=0, description="Item price in currency units.")

    class Config:
        """Allow ORM object conversion for seamless serialization."""
        from_attributes = True
