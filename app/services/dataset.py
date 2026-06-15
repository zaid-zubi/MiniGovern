from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Dataset
from app.services.crud import crud
from core.db.base import WorkflowState


async def get_dataset(
        db: AsyncSession,
        dataset_id: int,
) -> Dataset:
    dataset = await crud.get_one(db, Dataset, id=dataset_id)

    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found",
        )

    return dataset

async def get_dataset_with_tags(
        db: AsyncSession,
        dataset_id: int,
) -> Dataset:
    dataset = await crud.get_one(db, Dataset, selectinload(Dataset.tags), id=dataset_id)

    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found",
        )

    return dataset
async def create_dataset(
        db: AsyncSession,
        table_name: str,
        table_catalog_id: int,
        owner_id: int,
) -> Dataset:
    """
    Create Dataset for scanning job process
    """
    dataset = Dataset(
        name=table_name,
        table_catalog_id=table_catalog_id,
        owner_id=owner_id,
        workflow_state=WorkflowState.DRAFT,
    )

    db.add(dataset)
    await db.flush()

    return dataset


async def get_or_create_dataset(
        db: AsyncSession,
        table_name: str,
        table_catalog_id: int,
        owner_id: int,
) -> Dataset:
    """
    Get or Create dataset through Scan Job process
    """
    existing = await crud.get_one(db, Dataset, table_catalog_id=table_catalog_id)

    if existing:
        return existing

    return await create_dataset(
        db=db,
        table_name=table_name,
        table_catalog_id=table_catalog_id,
        owner_id=owner_id,
    )


async def approve_dataset(
        db: AsyncSession,
        dataset_id: int,
) -> Dataset:
    dataset = await get_dataset(db, dataset_id)

    dataset.workflow_state = WorkflowState.APPROVED

    await crud.update(db, Dataset, dataset_id, dataset)

    return dataset


async def reject_dataset(
        db: AsyncSession,
        dataset_id: int,
        reason: str | None = None,
) -> Dataset:
    dataset = await get_dataset(db, dataset_id)

    dataset.workflow_state = WorkflowState.REJECTED
    dataset.rejection_comment = reason

    await crud.update(db, Dataset, dataset_id, dataset)

    return dataset