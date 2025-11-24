from collections.abc import Sequence
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.entities.item_orm import ItemORM
from app.models.item_model import ItemBase
from app.models.parameters_model import HexId


class ItemRepository:
    async def get_all(self, session: AsyncSession) -> Sequence[ItemORM]:
        result = await session.execute(select(ItemORM))

        return result.scalars().all()

    async def get_by_id(self, session: AsyncSession, id: HexId) -> ItemORM | None:
        result = await session.execute(select(ItemORM).where(ItemORM.id == id))

        return result.scalar_one_or_none()

    async def create(self, session: AsyncSession, *, item_in: ItemBase) -> ItemORM:
        item = ItemORM(**item_in.model_dump())
        session.add(item)

        await session.commit()
        await session.refresh(item)

        return item

    async def update(
        self,
        session: AsyncSession,
        obj: ItemORM,
        new_data: dict[str, Any],
    ) -> ItemORM:
        for field, value in new_data.items():
            setattr(obj, field, value)

        await session.commit()
        await session.refresh(obj)

        return obj

    async def delete(
        self,
        session: AsyncSession,
        obj: ItemORM,
    ) -> ItemORM:
        await session.delete(obj)
        await session.commit()

        return obj


repo = ItemRepository()
