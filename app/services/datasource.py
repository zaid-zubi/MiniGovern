from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import selectinload

from app.models.datasource import DataSource
from app.models.user import User
from app.schemas.datasource import (
    DataSourceCreate,
    DataSourceUpdate,
    ListDataSourceWithCategories,
    DataSourceRead,
)
from app.services.audit import log_audit_action
from app.services.crud import crud
from core.encryption import encrypt_value, decrypt_value
from core.logging import logger

from core.settings.exceptions.datasource import (
    DatasourceNotFound,
    DatasourceConnectionFailed,
)


async def create_datasource(
        db: AsyncSession,
        body: DataSourceCreate,
        owner: User,
):
    logger.info(f"Creating datasource: name={body.name}, owner_id={owner.id}")

    datasource = DataSource(
        name=body.name,
        host=body.host,
        port=body.port,
        database=body.database,
        username=body.username,
        encrypted_password=encrypt_value(body.password),
        owner_id=owner.id,
    )

    await crud.post(db, DataSource, datasource)

    logger.info(
        f"Datasource created: id={datasource.id}, name={datasource.name}, host={datasource.host}"
    )

    await log_audit_action(
        db,
        actor_id=owner.id,
        action="create",
        entity_type="datasource",
        entity_id=datasource.id,
        details={
            "name": datasource.name,
            "host": datasource.host,
            "database": datasource.database,
        },
    )

    await db.commit()

    logger.info(f"Datasource committed to DB: id={datasource.id}")

    return DataSourceRead.model_validate(datasource)


async def _get_datasource(db: AsyncSession, datasource_id: int):
    logger.debug(f"Fetching datasource: id={datasource_id}")

    datasource = await crud.get_one(db, DataSource, id=datasource_id)

    if not datasource:
        logger.warning(f"Datasource not found: id={datasource_id}")
        raise DatasourceNotFound(f"Datasource {datasource_id} not found")

    logger.debug(f"Datasource found: id={datasource_id}, name={datasource.name}")
    return datasource


async def get_datasource(db: AsyncSession, datasource_id: int):
    datasource = await _get_datasource(db, datasource_id)
    return DataSourceRead.model_validate(datasource)


async def get_datasource_with_categories(
        db: AsyncSession,
        datasource_id: int,
):
    logger.debug(f"Fetching datasource with categories: id={datasource_id}")

    datasource = await crud.get_one(
        db,
        DataSource,
        selectinload(DataSource.categories),
        id=datasource_id,
    )

    if not datasource:
        logger.warning(f"Datasource not found (with categories): id={datasource_id}")
        raise DatasourceNotFound(f"Datasource {datasource_id} not found")

    logger.debug(
        f"Datasource loaded with categories: id={datasource_id}, "
        f"categories={len(datasource.categories)}"
    )

    return datasource


async def list_datasources(db: AsyncSession, *, skip: int = 0, limit: int = 100):
    logger.debug(f"Listing datasources: skip={skip}, limit={limit}")

    datasources = await crud.get_all(
        db,
        DataSource,
        skip=skip,
        limit=limit,
    )

    logger.info(f"Datasources fetched: count={len(datasources)}")

    return [
        DataSourceRead.model_validate(ds)
        for ds in datasources
    ]


async def update_datasource(
        db: AsyncSession,
        datasource_id: int,
        body: DataSourceUpdate,
        actor: User,
):
    logger.info(f"Updating datasource: id={datasource_id}, actor_id={actor.id}")

    datasource = await crud.get_one(db, DataSource, id=datasource_id)

    if not datasource:
        logger.warning(f"Update failed - datasource not found: id={datasource_id}")
        raise DatasourceNotFound(f"Datasource {datasource_id} not found")

    before = {
        "name": datasource.name,
        "host": datasource.host,
        "port": datasource.port,
        "database": datasource.database,
        "username": datasource.username,
    }

    updates = body.model_dump(exclude_unset=True)

    if "password" in updates:
        logger.debug("Encrypting updated password for datasource")
        updates["encrypted_password"] = encrypt_value(updates.pop("password"))

    logger.debug(f"Applying updates: {list(updates.keys())}")

    for key, value in updates.items():
        setattr(datasource, key, value)

    await db.flush()

    after = {
        "name": datasource.name,
        "host": datasource.host,
        "port": datasource.port,
        "database": datasource.database,
        "username": datasource.username,
    }

    await log_audit_action(
        db,
        actor_id=actor.id,
        action="update",
        entity_type="datasource",
        entity_id=datasource.id,
        details={"before": before, "after": after},
    )

    await db.commit()
    await db.refresh(datasource)

    logger.info(f"Datasource updated successfully: id={datasource.id}")

    return DataSourceRead.model_validate(datasource)


async def delete_datasource(db: AsyncSession, datasource_id: int, actor: User):
    logger.info(f"Deleting datasource: id={datasource_id}, actor_id={actor.id}")

    datasource = await crud.get_one(db, DataSource, id=datasource_id)

    if not datasource:
        logger.warning(f"Delete failed - datasource not found: id={datasource_id}")
        raise DatasourceNotFound(f"Datasource {datasource_id} not found")

    await log_audit_action(
        db,
        actor_id=actor.id,
        action="delete",
        entity_type="datasource",
        entity_id=datasource.id,
        details={
            "name": datasource.name,
            "host": datasource.host,
            "database": datasource.database,
        },
    )

    await crud.delete(db, DataSource, datasource_id)

    logger.info(f"Datasource deleted: id={datasource_id}")

    return datasource_id


def build_mysql_connection_url(datasource: DataSource):
    logger.debug(f"Building MySQL connection URL: id={datasource.id}")

    password = decrypt_value(datasource.encrypted_password)

    return (
        f"mysql+aiomysql://"
        f"{datasource.username}:{password}"
        f"@{datasource.host}:{datasource.port}"
        f"/{datasource.database}"
    )


async def create_mysql_engine(datasource: DataSource):
    logger.info(f"Creating MySQL engine: id={datasource.id}")

    url = build_mysql_connection_url(datasource)

    return create_async_engine(
        url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )


async def test_connection(datasource_id: int, db: AsyncSession):
    logger.info(f"Testing DB connection: datasource_id={datasource_id}")

    datasource = await crud.get_one(db, DataSource, id=datasource_id)

    if not datasource:
        logger.warning(f"Connection test failed - datasource not found: id={datasource_id}")
        raise DatasourceNotFound(f"Datasource {datasource_id} not found")

    engine = await create_mysql_engine(datasource)

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

        logger.info(f"Connection successful: datasource_id={datasource_id}")
        return True

    except Exception as e:
        logger.error(
            f"Connection failed: datasource_id={datasource_id}, error={str(e)}"
        )
        raise DatasourceConnectionFailed(str(e))

    finally:
        await engine.dispose()
        logger.debug(f"Engine disposed: datasource_id={datasource_id}")