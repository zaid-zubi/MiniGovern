from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine


def get_mysql_engine(connection_url: str) -> AsyncEngine:
    return create_async_engine(
        connection_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_recycle=3600,
    )


async def get_tables(engine: AsyncEngine) -> list[str]:
    query = text("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = DATABASE()
          AND table_type = 'BASE TABLE'
    """)

    async with engine.connect() as conn:
        result = await conn.execute(query)
        return [row[0] for row in result.fetchall()]


async def get_columns(
        engine: AsyncEngine,
        table_name: str,
) -> list[dict]:
    query = text("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = DATABASE()
          AND table_name = :table_name
        ORDER BY ordinal_position
    """)

    async with engine.connect() as conn:
        result = await conn.execute(
            query,
            {"table_name": table_name},
        )

        return result.mappings().all()


async def get_sample_rows(
        engine: AsyncEngine,
        table_name: str,
        limit: int = 100,
) -> list[dict]:
    query = text(f"""
        SELECT *
        FROM `{table_name}`
        LIMIT :limit
    """)

    async with engine.connect() as conn:
        result = await conn.execute(query, {"limit": limit})
        return result.mappings().all()

async def get_sample_rows(
        engine: AsyncEngine,
        table_name: str,
        limit: int = 100,
) -> list[dict]:
    query = text(f"""
        SELECT *
        FROM `{table_name}`
        LIMIT :limit
    """)

    async with engine.connect() as conn:
        result = await conn.execute(query, {"limit": limit})
        return result.mappings().all()
