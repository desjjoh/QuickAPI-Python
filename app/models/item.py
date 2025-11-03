"""
models/item.py
--------------
Internal representation of an Item entity.

Unlike `ItemOut`, this model is used internally between service layers,
jobs, or background tasks that don’t require HTTP metadata or validation context.

✅ Mirrors ORM attributes for logic-layer use.
✅ ORM-convertible with `.from_orm()`.
✅ Lightweight and serialization-ready.
"""

from pydantic import BaseModel, Field


class Item(BaseModel):
    """
    Lightweight internal Item model.

    Attributes:
        id (int): Unique identifier for the item.
        name (str): Item name.
        price (float): Price value, non-negative.
    """

    id: int = Field(..., description="Unique identifier for the item.")
    name: str = Field(..., description="Item name.")
    price: float = Field(..., ge=0, description="Item price in currency units.")

    class Config:
        """Enable conversion from ORM objects."""
        from_attributes = True
