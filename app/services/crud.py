from typing import Any, TypeVar

from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class CRUD:
    @staticmethod
    def _to_dict(data: dict[str, Any] | BaseModel) -> dict[str, Any]:
        if isinstance(data, BaseModel):
            return data.model_dump(exclude_unset=True)
        return data

    @staticmethod
    async def post(
        db: AsyncSession,
        table: type[ModelType],
        body: dict[str, Any] | BaseModel,
    ) -> ModelType:
        instance = table(**CRUD._to_dict(body))
        db.add(instance)
        await db.commit()
        await db.refresh(instance)
        return instance

    @staticmethod
    async def get_one(
        db: AsyncSession,
        table: type[ModelType],
        record_id: int,
    ) -> ModelType | None:
        result = await db.execute(select(table).where(table.id == record_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
        db: AsyncSession,
        table: type[ModelType],
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ModelType]:
        result = await db.execute(select(table).offset(skip).limit(limit))
        return list(result.scalars().all())

    @staticmethod
    async def update(
        db: AsyncSession,
        table: type[ModelType],
        record_id: int,
        body: dict[str, Any] | BaseModel,
    ) -> ModelType | None:
        instance = await CRUD.get_one(db, table, record_id)
        if instance is None:
            return None

        for key, value in CRUD._to_dict(body).items():
            setattr(instance, key, value)

        await db.commit()
        await db.refresh(instance)
        return instance

    @staticmethod
    async def delete(
        db: AsyncSession,
        table: type[ModelType],
        record_ids: int | list[int],
    ) -> int:
        ids = [record_ids] if isinstance(record_ids, int) else record_ids
        result = await db.execute(delete(table).where(table.id.in_(ids)))
        await db.commit()
        return result.rowcount or 0


crud = CRUD()