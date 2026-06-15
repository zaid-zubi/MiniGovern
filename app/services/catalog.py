from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ColumnCatalog, TableCatalog
from app.services.crud import crud
from core.db.base import SensitivityLevel
from core.logging import logger


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
    logger.debug(
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
            logger.debug(
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
    Get or Create column catalog for scan job process
    """
    logger.debug(
        f"Fetching column catalog: table_id={table_id}, column={column_name}"
    )

    existing = await crud.get_one(
        db,
        ColumnCatalog,
        table_id=table_id,
        column_name=column_name
    )

    if existing:
        logger.info(
            f"Updating column catalog: id={existing.id}, column={column_name}"
        )

        existing.profile = profile
        existing.sensitivity_level = sensitivity_level
        existing.sensitivity_reason = sensitivity_reason
        existing.semantic_type = semantic_type
        existing.valid_ratio = valid_ratio
        existing.enrichment_source = enrichment_source

        await db.flush()

        logger.debug(
            f"Column updated: id={existing.id}, sensitivity={sensitivity_level.value}"
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