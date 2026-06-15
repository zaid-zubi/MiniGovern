from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Dataset
from app.services.crud import crud
from core.db.base import WorkflowState
from core.logging import logger


async def get_dataset(
        db: AsyncSession,
        dataset_id: int,
) -> Dataset:
    logger.debug(f"Fetching dataset: id={dataset_id}")

    dataset = await crud.get_one(db, Dataset, id=dataset_id)

    if not dataset:
        logger.warning(f"Dataset not found: id={dataset_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found",
        )

    logger.debug(f"Dataset found: id={dataset_id}, name={dataset.name}")
    return dataset


async def get_dataset_with_tags(
        db: AsyncSession,
        dataset_id: int,
) -> Dataset:
    logger.debug(f"Fetching dataset with tags: id={dataset_id}")

    dataset = await crud.get_one(
        db,
        Dataset,
        selectinload(Dataset.tags),
        id=dataset_id
    )

    if not dataset:
        logger.warning(f"Dataset not found (with tags): id={dataset_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found",
        )

    logger.debug(f"Dataset with tags loaded: id={dataset_id}, tags={len(dataset.tags)}")
    return dataset


from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Dataset
from app.services.crud import crud
from core.logging import logger


async def get_datasets(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 50,
) -> list[Dataset]:
    logger.debug(f"Listing datasets: skip={skip}, limit={limit}")

    datasets = await crud.get_all(
        db,
        Dataset,
        skip=skip,
        limit=limit,
    )
    logger.info(f"Datasets fetched: count={len(datasets)}")
    return datasets


async def create_dataset(
        db: AsyncSession,
        table_name: str,
        table_catalog_id: int,
        owner_id: int,
) -> Dataset:
    """
    Create Dataset for scanning job process
    """
    logger.info(
        f"Creating dataset: table={table_name}, "
        f"table_catalog_id={table_catalog_id}, owner_id={owner_id}"
    )

    dataset = Dataset(
        name=table_name,
        table_catalog_id=table_catalog_id,
        owner_id=owner_id,
        workflow_state=WorkflowState.DRAFT,
    )

    db.add(dataset)
    await db.flush()

    logger.info(f"Dataset created: id={dataset.id}, name={dataset.name}")

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
    logger.debug(
        f"Get or create dataset: table_catalog_id={table_catalog_id}, "
        f"table_name={table_name}"
    )

    existing = await crud.get_one(
        db,
        Dataset,
        table_catalog_id=table_catalog_id,
        owner_id=owner_id
    )
    if existing:
        logger.info(
            f"Dataset already exists: id={existing.id}, table_catalog_id={table_catalog_id}"
        )
        return existing

    logger.info(f"No dataset found, creating new one: table={table_name}")

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
    logger.info(f"Approving dataset: id={dataset_id}")

    dataset = await get_dataset(db, dataset_id)

    dataset.workflow_state = WorkflowState.APPROVED

    await crud.update(db, Dataset, dataset_id, dataset)

    logger.info(f"Dataset approved: id={dataset_id}")

    return dataset


async def reject_dataset(
        db: AsyncSession,
        dataset_id: int,
        reason: str | None = None,
) -> Dataset:
    logger.info(f"Rejecting dataset: id={dataset_id}, reason={reason}")

    dataset = await get_dataset(db, dataset_id)

    dataset.workflow_state = WorkflowState.REJECTED
    dataset.rejection_comment = reason

    await crud.update(db, Dataset, dataset_id, dataset)

    logger.info(f"Dataset rejected: id={dataset_id}")

    return dataset
