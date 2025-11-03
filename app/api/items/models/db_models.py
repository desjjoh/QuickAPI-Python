"""
api/items/models/db_models.py
-------------------
SQLAlchemy ORM model definitions for the FastAPI application.

This module defines persistent database entities mapped to tables using
SQLAlchemy 2.0’s typed ORM syntax. Each entity inherits from the shared
`Base` declarative class defined in `app.services.db`.

✅ Fully type-annotated using SQLAlchemy’s `Mapped` generics.
✅ Mirrors the Pydantic models (`ItemIn`, `ItemOut`, `Item`) for consistent schema parity.
✅ Minimal column definitions with sensible defaults and indexing for lookups.

"""

from sqlalchemy import Integer, String, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.services.db import Base


class ItemORM(Base):
    """
    ORM model for the `items` table.

    Represents a single item record in the SQLite database. This class
    provides the direct mapping between in-memory Python objects and
    persistent database rows.

    Attributes:
        id (int):
            Primary key for the item record. Auto-incremented by the database.
        name (str):
            Descriptive name of the item. Indexed for quick lookups.
        price (float):
            The item’s price, stored as a floating-point number.

    Example:
        ```python
        new_item = ItemORM(name="Retro Console", price=199.99)
        session.add(new_item)
        await session.commit()
        ```
    """

    __tablename__ = "items"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        doc="Primary key identifier for the item."
    )

    name: Mapped[str] = mapped_column(
        String(120),
        index=True,
        nullable=False,
        doc="Descriptive name of the item (max length 120)."
    )

    price: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        doc="Price of the item stored as a floating-point value."
    )
