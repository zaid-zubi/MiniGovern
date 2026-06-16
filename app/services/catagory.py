from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category
from app.schemas.category import CategoryIn, CategoryUpdate
from app.schemas.datasource import ListDataSourceWithCategories
from app.services.audit import log_audit_action
from app.services.crud import crud
from app.services.datasource import get_datasource_with_categories
from core.logging import logger

from core.settings.exceptions.dataset import (
    CategoryNotFound,
    CategoryAlreadyExists,
    CategoryAlreadyAssigned,
    CategoryNotAssigned,
)


async def create_category(category: CategoryIn, db: AsyncSession, actor_id: int):
    logger.info(f"Creating category: {category.name}")

    existing = await crud.get_one(db, Category, name=category.name)
    if existing:
        logger.warning(f"Category already exists: {category.name}")
        raise CategoryAlreadyExists(f"Category '{category.name}' already exists")

    category_body = category.model_dump()
    category_obj = Category(**category_body)

    result = await crud.post(db, Category, category_obj)

    logger.info(f"Category created: id={result.id}, name={result.name}")

    await log_audit_action(
        db,
        actor_id=actor_id,
        action="create_category",
        entity_type="category",
        entity_id=result.id,
        details={"name": result.name},
        can_commit=True
    )

    return result


async def update_category(
        category: CategoryUpdate,
        category_id: int,
        db: AsyncSession,
        actor_id: int,
):
    existing = await crud.get_one(db, Category, id=category_id)
    if not existing:
        raise CategoryNotFound
    logger.info(f"Updating category: id={category_id}")

    await log_audit_action(
        db,
        actor_id=actor_id,
        action="update_category",
        entity_type="category",
        entity_id=category_id,
        details=category.model_dump(exclude_unset=True),
    )

    updated_category = await crud.update(
        db,
        Category,
        record_id=category_id,
        body=category,
    )

    logger.info(f"Category updated successfully: id={category_id}")

    return updated_category


async def get_category(category_id: int, db: AsyncSession):
    logger.info(f"Fetching category: id={category_id}")

    category = await crud.get_one(db, Category, id=category_id)
    if not category:
        logger.warning(f"Category not found: id={category_id}")
        raise CategoryNotFound(f"Category {category_id} not found")

    return category


async def delete_category(category_id: int, db: AsyncSession, actor_id: int):
    logger.info(f"Deleting category: id={category_id}")

    existing = await crud.get_one(db, Category, id=category_id)
    if not existing:
        logger.warning(f"Delete failed - category not found: id={category_id}")
        raise CategoryNotFound(f"Category {category_id} not found")

    await log_audit_action(
        db,
        actor_id=actor_id,
        action="delete_category",
        entity_type="category",
        entity_id=category_id,
        details={"name": existing.name},
    )

    await crud.delete(db, Category, record_ids=category_id)

    logger.info(f"Category deleted: id={category_id}, name={existing.name}")

    return "deleted"


async def assign_datasource_with_category(
        category_id: int,
        datasource_id: int,
        db: AsyncSession,
        actor_id: int,
):
    logger.info(f"Assign category {category_id} -> datasource {datasource_id}")

    datasource = await get_datasource_with_categories(db, datasource_id)
    category = await get_category(category_id, db)

    if any(c.id == category.id for c in datasource.categories):
        logger.warning(
            f"Category already assigned: category_id={category_id}, datasource_id={datasource_id}"
        )
        raise CategoryAlreadyAssigned(
            f"Category {category_id} already assigned to datasource {datasource_id}"
        )

    datasource.categories.append(category)

    await log_audit_action(
        db,
        actor_id=actor_id,
        action="assign_category_to_datasource",
        entity_type="datasource",
        entity_id=datasource_id,
        dataset_id=None,
        details={
            "category_id": category.id,
            "category_name": category.name,
        },
    )

    await crud.commit(db, datasource)

    logger.info(
        f"Category assigned successfully: category_id={category_id}, datasource_id={datasource_id}"
    )

    return ListDataSourceWithCategories.model_validate(datasource)


async def unassign_datasource_with_category(
        datasource_id: int,
        category_id: int,
        db: AsyncSession,
        actor_id: int,
):
    logger.info(f"Unassign category {category_id} from datasource {datasource_id}")

    datasource = await get_datasource_with_categories(db, datasource_id)
    category = await get_category(category_id, db)

    if not any(c.id == category.id for c in datasource.categories):
        logger.warning(
            f"Unassign failed - not assigned: category_id={category_id}, datasource_id={datasource_id}"
        )
        raise CategoryNotAssigned(
            f"Category {category_id} is not assigned to datasource {datasource_id}"
        )

    datasource.categories.remove(category)

    await log_audit_action(
        db,
        actor_id=actor_id,
        action="unassign_category_from_datasource",
        entity_type="datasource",
        entity_id=datasource_id,
        dataset_id=None,
        details={
            "category_id": category.id,
            "category_name": category.name,
        },
    )

    await crud.commit(db, datasource)

    logger.info(
        f"Category unassigned successfully: category_id={category_id}, datasource_id={datasource_id}"
    )

    return ListDataSourceWithCategories.model_validate(datasource)