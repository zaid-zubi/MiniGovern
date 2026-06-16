from app.services.catalog import (
    get_or_create_table_catalog,
    upsert_column_catalog,
)
from app.services.dataset import get_or_create_dataset
from app.services.datasource import build_mysql_connection_url, _get_datasource
from app.services.enrichment import enrich_column
from app.services.mysql_scanner import (
    get_mysql_engine,
    get_tables,
    get_columns,
    get_sample_rows,
)
from app.services.pii_classifier import classify_column
from app.services.profiler import profile_column
from app.services.scan_job import (
    get_scan_job,
    start_scan_job,
    complete_scan_job,
    fail_scan_job,
)
from core.db.session import AsyncSessionLocal


async def run_scan_job(scan_job_id: int, user_id: int):
    engine = None

    async with AsyncSessionLocal() as db:
        job = None

        try:
            job = await get_scan_job(scan_job_id, db)

            if not job:
                return

            await start_scan_job(job, db)

            datasource = await _get_datasource(
                db,
                job.datasource_id
            )

            connection_url = build_mysql_connection_url(
                datasource
            )

            engine = get_mysql_engine(connection_url)

            tables = await get_tables(engine)

            summary = {
                "tables": 0,
                "datasets": 0,
                "columns": 0,
                "pii_columns": 0,
            }

            for table_name in tables:
                samples = await get_sample_rows(
                    engine,
                    table_name
                )

                table_catalog = await get_or_create_table_catalog(
                    db=db,
                    datasource_id=datasource.id,
                    scan_job_id=job.id,
                    table_name=table_name,
                    row_count=len(samples),
                )

                await get_or_create_dataset(
                    db=db,
                    table_name=table_name,
                    table_catalog_id=table_catalog.id,
                    owner_id=datasource.owner_id,
                )

                columns = await get_columns(
                    engine,
                    table_name
                )

                for col in columns:
                    column_name = col["COLUMN_NAME"]
                    declared_type = col["DATA_TYPE"]

                    profile = profile_column(
                        samples,
                        column_name
                    )

                    sample_values = [
                        row.get(column_name)
                        for row in samples
                    ]

                    level, reason = classify_column(
                        column_name,
                        sample_values,
                    )

                    try:
                        enrichment = await enrich_column(
                            column_name=column_name,
                            values=sample_values,
                        )
                    except Exception:
                        enrichment = {
                            "semantic_type": "unknown",
                            "valid_ratio": None
                        }

                    await upsert_column_catalog(
                        db=db,
                        table_id=table_catalog.id,
                        column_name=column_name,
                        declared_type=declared_type,
                        profile=profile,
                        sensitivity_level=level,
                        sensitivity_reason=reason,
                        semantic_type=enrichment.get(
                            "semantic_type"
                        ),
                        valid_ratio=enrichment.get(
                            "valid_ratio"
                        ),
                        enrichment_source=enrichment.get("enrichment_source")
                    )

                    summary["columns"] += 1

                    if level != level.NONE:
                        summary["pii_columns"] += 1

                summary["tables"] += 1
                summary["datasets"] += 1

            await complete_scan_job(
                job,
                summary,
                db,
                user_id,
            )

        except Exception as e:
            if job:
                await fail_scan_job(
                    job,
                    str(e),
                    db,
                    user_id,
                )

            raise

        finally:
            if engine:
                await engine.dispose()