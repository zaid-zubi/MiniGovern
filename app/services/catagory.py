from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category
from app.schemas.category import CategoryIn, CategoryUpdate
from app.schemas.datasource import ListDataSourceWithCategories
from app.services.audit import log_audit_action
from app.services.crud import crud
from app.services.datasource import get_datasource_with_categories


async def create_category(category: CategoryIn, db: AsyncSession, actor_id: int):
    existing = await crud.get_one(db, Category, name=category.name)
    if existing:
        raise HTTPException(detail="Category is existed", status_code=400)

    category_body = category.model_dump()
    category = Category(**category_body)

    result = await crud.post(db, Category, category)

    await log_audit_action(
        db,
        actor_id=actor_id,
        action="create_category",
        entity_type="category",
        entity_id=result.id,
        details={
            "name": result.name,
        },
        can_commit=True
    )

    return result


async def update_category(
        category: CategoryUpdate,
        category_id: int,
        db: AsyncSession,
        actor_id: int,
):
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

    return updated_category


async def get_category(category_id, db):
    category = await crud.get_one(db, Category, id=category_id)
    if not category:
        raise HTTPException(detail="Category isn't existed", status_code=404)
    return category


async def delete_category(category_id: int, db: AsyncSession, actor_id: int):
    existing = await crud.get_one(db, Category, id=category_id)
    if not existing:
        raise HTTPException(detail="Category isn't existed", status_code=404)
    await log_audit_action(
        db,
        actor_id=actor_id,
        action="delete_category",
        entity_type="category",
        entity_id=category_id,
        details={
            "name": existing.name,
        },
    )
    await crud.delete(db, Category, record_ids=category_id)

    return "deleted"


async def assign_datasource_with_category(
        category_id,
        datasource_id,
        db,
        actor_id: int,
):
    datasource = await get_datasource_with_categories(db, datasource_id)
    category = await get_category(category_id, db)

    if any(c.id == category.id for c in datasource.categories):
        raise HTTPException(
            status_code=409,
            detail="Category already assigned",
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

    return ListDataSourceWithCategories.model_validate(datasource)


async def unassign_datasource_with_category(
        datasource_id: int,
        category_id: int,
        db: AsyncSession,
        actor_id: int,
):
    datasource = await get_datasource_with_categories(db, datasource_id)
    category = await get_category(category_id, db)

    if not any(c.id == category.id for c in datasource.categories):
        raise HTTPException(status_code=404, detail="Not assigned")

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

    return ListDataSourceWithCategories.model_validate(datasource)
