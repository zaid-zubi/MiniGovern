from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from core.logging import logger


def get_mysql_engine(connection_url: str) -> AsyncEngine:
    logger.info("Creating MySQL async engine")

    engine = create_async_engine(
        connection_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_recycle=3600,
    )

    logger.info("MySQL engine created successfully")
    return engine


async def get_tables(engine: AsyncEngine) -> list[str]:
    logger.info("Fetching tables from database")

    query = text("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = DATABASE()
          AND table_type = 'BASE TABLE'
    """)

    async with engine.connect() as conn:
        result = await conn.execute(query)
        tables = [row[0] for row in result.fetchall()]

    logger.info(f"Tables fetched: count={len(tables)}")

    return tables


async def get_columns(
    engine: AsyncEngine,
    table_name: str,
) -> list[dict]:
    logger.info(f"Fetching columns for table: {table_name}")

    query = text("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = DATABASE()
          AND table_name = :table_name
        ORDER BY ordinal_position
    """)

    async with engine.connect() as conn:
        result = await conn.execute(query, {"table_name": table_name})
        columns = result.mappings().all()

    logger.info(f"Columns fetched: table={table_name}, count={len(columns)}")

    return columns


async def get_sample_rows(
    engine: AsyncEngine,
    table_name: str,
    limit: int = 100,
) -> list[dict]:
    logger.info(f"Fetching sample rows: table={table_name}, limit={limit}")

    query = text(f"""
        SELECT *
        FROM `{table_name}`
        LIMIT :limit
    """)

    async with engine.connect() as conn:
        result = await conn.execute(query, {"limit": limit})
        rows = result.mappings().all()

    logger.info(f"Sample rows fetched: table={table_name}, count={len(rows)}")

    return rows
