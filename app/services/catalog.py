from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import ColumnCatalog, TableCatalog, Dataset
from app.services.crud import crud
from core.db.base import SensitivityLevel, UserRole
from core.logging import logger
from core.security.masking import mask_value, should_mask
from core.settings.exceptions.catalog import DatasetNotFound


async def get_or_create_table_catalog(
        db: AsyncSession,
        datasource_id: int,
        scan_job_id: int,
        table_name: str,
        row_count: int | None = None,
) -> TableCatalog:
    """
    Get or Create table catalog for scan job process
    """
    logger.info(
        f"Fetching table catalog: datasource_id={datasource_id}, "
        f"scan_job_id={scan_job_id}, table={table_name}"
    )

    existing = await crud.get_one(
        db,
        TableCatalog,
        datasource_id=datasource_id,
        scan_job_id=scan_job_id,
        table_name=table_name
    )

    if existing:
        logger.info(
            f"Table catalog exists: id={existing.id}, table={table_name}"
        )

        if row_count is not None:
            logger.info(
                f"Updating row_count for table {table_name}: {existing.row_count} -> {row_count}"
            )
            existing.row_count = row_count

        return existing

    logger.info(
        f"Creating table catalog: datasource_id={datasource_id}, table={table_name}"
    )

    table_catalog = TableCatalog(
        datasource_id=datasource_id,
        scan_job_id=scan_job_id,
        table_name=table_name,
        row_count=row_count,
    )

    db.add(table_catalog)
    await db.flush()

    logger.info(
        f"Table catalog created: id={table_catalog.id}, table={table_name}"
    )

    return table_catalog


async def upsert_column_catalog(
    db: AsyncSession,
    table_id: int,
    column_name: str,
    declared_type: str,
    profile: dict,
    sensitivity_level: SensitivityLevel = SensitivityLevel.NONE,
    sensitivity_reason: str | None = None,
    semantic_type: str | None = None,
    valid_ratio: float | None = None,
    enrichment_source: str | None = None,
) -> ColumnCatalog:
    """
    Create or update a column catalog entry during scan.
    """

    logger.info(
        f"Fetching column catalog: table_id={table_id}, column={column_name}"
    )

    existing = await crud.get_one(
        db,
        ColumnCatalog,
        table_id=table_id,
        column_name=column_name,
    )

    if existing:
        logger.info(
            f"Updating column catalog: id={existing.id}, column={column_name}"
        )

        existing.declared_type = declared_type
        existing.profile = profile
        existing.sensitivity_level = sensitivity_level
        existing.sensitivity_reason = sensitivity_reason

        # Only overwrite enrichment fields when enrichment succeeded
        if semantic_type is not None:
            existing.semantic_type = semantic_type

        if valid_ratio is not None:
            existing.valid_ratio = valid_ratio

        if enrichment_source is not None:
            existing.enrichment_source = enrichment_source

        await db.flush()

        logger.info(
            f"Column updated: id={existing.id}, "
            f"sensitivity={sensitivity_level.value}, "
            f"semantic_type={existing.semantic_type}"
        )

        return existing

    logger.info(
        f"Creating column catalog: table_id={table_id}, column={column_name}"
    )

    column = ColumnCatalog(
        table_id=table_id,
        column_name=column_name,
        declared_type=declared_type,
        profile=profile,
        sensitivity_level=sensitivity_level,
        sensitivity_reason=sensitivity_reason,
        semantic_type=semantic_type,
        valid_ratio=valid_ratio,
        enrichment_source=enrichment_source,
    )

    db.add(column)
    await db.flush()

    logger.info(
        f"Column catalog created: id={column.id}, column={column_name}"
    )

    return column

async def get_table_catalog(table_id: int, db: AsyncSession, user):
    result = await crud.get_one(
        db,
        Dataset,
        selectinload(Dataset.table_catalog)
        .selectinload(TableCatalog.columns),
        id=table_id,
    )

    if not result:
        raise DatasetNotFound

    role = user.role
    is_admin = role == UserRole.ADMIN

    catalog = result.table_catalog

    for column in catalog.columns:
        sensitivity = column.sensitivity_level

        if should_mask(role, sensitivity):

            if column.profile and "example_values" in column.profile:
                column.profile = mask_profile_examples(
                    column_name=column.column_name,
                    profile=column.profile,
                    sensitivity=sensitivity,
                    role=role,
                )

    return result


def mask_profile_examples(
        column_name: str,
        profile: dict,
        sensitivity: SensitivityLevel,
        role: str | None = None,
):
    if not profile or "example_values" not in profile:
        return profile

    profile = dict(profile)

    profile["example_values"] = [
        mask_value(v, column_name, sensitivity)
        for v in profile["example_values"]
    ]

    return profile
