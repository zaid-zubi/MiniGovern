from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.dataset import Dataset
from app.models.tag import Tag
from app.services.crud import crud
from app.services.dataset import get_dataset_with_tags
from app.services.audit import log_audit_action
from core.logging import logger

from core.settings.exceptions.tag import (
    TagNotFound,
    TagAlreadyExists,
    TagAlreadyAssigned,
    TagNotAssigned,
)


async def get_list_tags(db: AsyncSession, skip: int = 0, limit: int = 100):
    logger.info(f"Fetching tags list: skip={skip}, limit={limit}")

    result = await crud.get_all(db, Tag, skip=skip, limit=limit)

    logger.info(f"Tags fetched: count={len(result)}")

    return result


async def get_tag_by_name(db: AsyncSession, name: str):
    logger.info(f"Fetching tag by name: {name}")

    result = await crud.get_one(db, Tag, name=name)

    if not result:
        logger.warning(f"Tag not found by name: {name}")
        raise TagNotFound(f"Tag '{name}' not found")

    return result


async def get_tag_by_id(db: AsyncSession, id: int, *options):
    logger.info(f"Fetching tag by id: {id}")

    result = await crud.get_one(db, Tag, id=id, *options)

    if not result:
        logger.warning(f"Tag not found by id: {id}")
        raise TagNotFound(f"Tag {id} not found")

    return result


async def create_tag(
        db: AsyncSession,
        name: str,
        user_id: int,
        is_system: bool = False,
):
    logger.info(f"Creating tag: name={name}, user_id={user_id}")

    tag_existed = await crud.get_one(db, Tag, name=name)
    if tag_existed:
        logger.warning(f"Tag already exists: name={name}")
        raise TagAlreadyExists(f"Tag '{name}' already exists")

    tag = Tag(name=name, owner_id=user_id)
    tag_data = await crud.post(db, Tag, tag)

    logger.info(f"Tag created: id={tag_data.id}, name={tag_data.name}")

    await log_audit_action(
        db,
        actor_id=user_id,
        action="create_tag",
        entity_type="tag",
        entity_id=tag_data.id,
        details={
            "tag_name": tag_data.name,
            "is_system": is_system,
        },
    )

    await db.commit()

    return tag_data


async def assign_tag_to_dataset(
        db: AsyncSession,
        dataset_id: int,
        tag_name: str,
        actor_id: int,
) -> Dataset:
    logger.info(
        f"Assigning tag: dataset_id={dataset_id}, tag={tag_name}, actor_id={actor_id}"
    )

    dataset, tag = await check_dataset_with_tag(dataset_id, tag_name, db)

    if tag in dataset.tags:
        logger.warning(
            f"Tag already assigned: dataset_id={dataset_id}, tag={tag_name}"
        )
        raise TagAlreadyAssigned(f"Tag '{tag_name}' already assigned")

    dataset.tags.append(tag)

    await log_audit_action(
        db,
        actor_id=actor_id,
        action="assign_tag",
        entity_type="dataset",
        entity_id=dataset.id,
        dataset_id=dataset.id,
        details={
            "tag_id": tag.id,
            "tag_name": tag.name,
        },
    )

    await crud.commit(db, dataset)

    logger.info(
        f"Tag assigned successfully: dataset_id={dataset_id}, tag={tag_name}"
    )

    return dataset


async def remove_tag_from_dataset(
        db: AsyncSession,
        dataset_id: int,
        tag_name: str,
        actor_id: int,
):
    logger.info(
        f"Removing tag: dataset_id={dataset_id}, tag={tag_name}, actor_id={actor_id}"
    )

    dataset, tag = await check_dataset_with_tag(dataset_id, tag_name, db)

    if tag not in dataset.tags:
        logger.warning(
            f"Tag not assigned: dataset_id={dataset_id}, tag={tag_name}"
        )
        raise TagNotAssigned(f"Tag '{tag_name}' is not assigned")

    dataset.tags.remove(tag)

    await log_audit_action(
        db,
        actor_id=actor_id,
        action="remove_tag",
        entity_type="dataset",
        entity_id=dataset.id,
        dataset_id=dataset.id,
        details={
            "tag_id": tag.id,
            "tag_name": tag.name,
        },
    )

    await crud.commit(db, dataset)

    logger.info(
        f"Tag removed successfully: dataset_id={dataset_id}, tag={tag_name}"
    )

    return dataset


async def check_dataset_with_tag(dataset_id: int, tag_name: str, db: AsyncSession):
    logger.info(f"Checking relation: dataset_id={dataset_id}, tag={tag_name}")

    dataset = await get_dataset_with_tags(db, dataset_id)
    tag = await get_tag_by_name(db, tag_name)

    return dataset, tag


async def delete_tag(
        tag_id: int,
        db: AsyncSession,
        actor_id: int,
):
    logger.info(f"Deleting tag: id={tag_id}, actor_id={actor_id}")

    tag_data = await get_tag_by_id(db, tag_id)
    if not tag_data:
        raise TagNotFound

    await log_audit_action(
        db,
        actor_id=actor_id,
        action="delete_tag",
        entity_type="tag",
        entity_id=tag_data.id,
        details={"tag_name": tag_data.name},
    )

    await crud.delete(db, Tag, record_ids=tag_id)

    logger.info(f"Tag deleted: id={tag_id}, name={tag_data.name}")

    return "deleted"


async def get_tag_with_datasets(tag_id: int, db: AsyncSession):
    logger.info(f"Fetching tag with datasets: id={tag_id}")

    tag = await get_tag_by_id(db, tag_id, selectinload(Tag.datasets))

    logger.info(
        f"Tag loaded: id={tag_id}, datasets={len(tag.datasets)}"
    )

    return tag