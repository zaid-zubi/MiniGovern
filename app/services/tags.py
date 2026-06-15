from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.dataset import Dataset
from app.models.tag import Tag
from app.services.crud import crud
from app.services.dataset import get_dataset_with_tags


async def get_tag_by_name(db: AsyncSession, name: str):
    result = await crud.get_one(db, Tag, name=name)
    if not result:
        raise HTTPException(status_code=404, detail="Tag isn't existed")
    return result


async def get_tag_by_id(db: AsyncSession, id: int, *options):
    result = await crud.get_one(db, Tag, id=id, *options)
    if not result:
        raise HTTPException(status_code=404, detail="Tag isn't existed")
    return result


async def create_tag(db: AsyncSession, name: str, user_id: int, is_system: bool = False) -> Tag:
    tag_existed = await crud.get_one(db, Tag, name=name)
    if tag_existed:
        raise HTTPException(status_code=404, detail="Tag is existed")
    tag = Tag(name=name, owner_id=user_id)
    tag_data = await crud.post(db, Tag, tag)
    return tag_data


async def assign_tag_to_dataset(
        db: AsyncSession,
        dataset_id: int,
        tag_name: str
) -> Dataset:
    dataset, tag = await check_dataset_with_tag(dataset_id, tag_name, db)
    if tag in dataset.tags:
        return dataset

    dataset.tags.append(tag)

    await crud.commit(db, dataset)
    return dataset


async def remove_tag_from_dataset(
        db: AsyncSession,
        dataset_id: int,
        tag_name
) -> Dataset:
    dataset, tag = await check_dataset_with_tag(dataset_id, tag_name, db)

    if tag in dataset.tags:
        dataset.tags.remove(tag)

    await crud.commit(db, dataset)
    return dataset


async def check_dataset_with_tag(dataset_id: int, tag_name: str, db: AsyncSession):
    dataset = await get_dataset_with_tags(db, dataset_id)
    tag = await get_tag_by_name(db, tag_name)
    return dataset, tag


async def delete_tag(tag_id: int, db: AsyncSession):
    tag_data = await get_tag_by_id(db, tag_id)
    await crud.delete(db, Tag, record_ids=tag_id)
    return "deleted"


async def get_tag_with_datasets(tag_id: int, db: AsyncSession):
    tag_with_datasets = await get_tag_by_id(db, tag_id, selectinload(Tag.datasets))
    if not tag_with_datasets:
        raise HTTPException(status_code=404, detail="Tag isn't existed")
    return tag_with_datasets
