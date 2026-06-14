from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ColumnCatalog
from app.models import TableCatalog
from app.services.crud import crud
from core.db.base import SensitivityLevel


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
    existing = await crud.get_one(db, TableCatalog, datasource_id=datasource_id, scan_job_id=scan_job_id,
                                  table_name=table_name)

    if existing:
        if row_count is not None:
            existing.row_count = row_count

        return existing

    table_catalog = TableCatalog(
        datasource_id=datasource_id,
        scan_job_id=scan_job_id,
        table_name=table_name,
        row_count=row_count,
    )

    db.add(table_catalog)
    await db.flush()

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
    existing = await crud.get_one(db, ColumnCatalog, table_id=table_id, column_name=column_name)

    if existing:
        existing.profile = profile
        existing.sensitivity_level = sensitivity_level
        existing.sensitivity_reason = sensitivity_reason
        existing.semantic_type = semantic_type
        existing.valid_ratio = valid_ratio
        existing.enrichment_source = enrichment_source

        await db.flush()
        return existing

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

    return column
