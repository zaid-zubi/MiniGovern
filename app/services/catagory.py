from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category
from app.schemas.category import CategoryIn, CategoryUpdate
from app.schemas.datasource import ListDataSourceWithCategories
from app.services.crud import crud
from app.services.datasource import get_datasource_with_categories


async def create_category(category: CategoryIn, db: AsyncSession):
    existing = await crud.get_one(db, Category, name=category.name)
    if existing:
        raise HTTPException(detail="Category is existed", status_code=400)
    category_body = category.model_dump()
    category = Category(**category_body)
    result = await crud.post(db, Category, category)
    return result


async def update_category(category: CategoryUpdate, category_id: int, db: AsyncSession):
    updated_category = await crud.update(db, Category, record_id=category_id, body=category)
    return updated_category


async def get_category(category_id, db):
    category = await crud.get_one(db, Category, id=category_id)
    if not category:
        raise HTTPException(detail="Category isn't existed", status_code=404)
    return category


async def delete_category(category_id: int, db: AsyncSession):
    existing = await crud.get_one(db, Category, id=category_id)
    if not existing:
        raise HTTPException(detail="Category isn't existed", status_code=404)
    result = await crud.delete(db, Category, record_ids=category_id)
    return result


async def assign_datasource_with_category(category_id, datasource_id, db):
    datasource = await get_datasource_with_categories(db, datasource_id)
    category = await get_category(category_id, db)

    if any(c.id == category.id for c in datasource.categories):
        raise HTTPException(
            status_code=409,
            detail="Category already assigned"
        )

    datasource.categories.append(category)

    await crud.commit(db, datasource)
    return ListDataSourceWithCategories.model_validate(datasource)


async def unassign_datasource_with_category(datasource_id: int, category_id: int, db: AsyncSession):
    datasource = await get_datasource_with_categories(db, datasource_id)
    category = await get_category(category_id, db)

    if not any(c.id == category.id for c in datasource.categories):
        raise HTTPException(status_code=404, detail="Not assigned")

    datasource.categories.remove(category)

    await crud.commit(db, datasource)
    return ListDataSourceWithCategories.model_validate(datasource)