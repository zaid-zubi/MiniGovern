from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import selectinload

from app.models.datasource import DataSource
from app.models.user import User
from app.schemas.datasource import DataSourceCreate, DataSourceUpdate, ListDataSourceWithCategories, DataSourceRead
from app.services.crud import crud
from core.encryption import encrypt_value, decrypt_value


from app.services.audit import log_audit_action

async def create_datasource(
    db: AsyncSession,
    body: DataSourceCreate,
    owner: User,
) -> DataSource:
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

    return DataSourceRead.model_validate(datasource)


async def get_datasource(
        db: AsyncSession,
        datasource_id: int,
):
    datasource = await crud.get_one(
        db,
        DataSource,
        id=datasource_id,
    )

    if not datasource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Datasource not found",
        )

    return DataSourceRead.model_validate(datasource)

async def get_datasource_with_categories(
    db: AsyncSession,
    datasource_id: int,
) -> ListDataSourceWithCategories:

    datasource = await crud.get_one(
        db,
        DataSource,
        selectinload(DataSource.categories),
        id=datasource_id,
    )

    if not datasource:
        raise HTTPException(status_code=404, detail="Datasource not found")

    return datasource

async def list_datasources(
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
) -> list[DataSourceRead]:
    datasources = await crud.get_all(
        db,
        DataSource,
        skip=skip,
        limit=limit,
    )
    datasources_list = [DataSourceRead.model_validate(datasource) for datasource in datasources]
    return datasources_list


async def update_datasource(
    db: AsyncSession,
    datasource_id: int,
    body: DataSourceUpdate,
    actor: User,
):
    datasource = await crud.get_one(
        db,
        DataSource,
        id=datasource_id,
    )

    if not datasource:
        raise HTTPException(
            status_code=404,
            detail="Datasource not found",
        )

    before = {
        "name": datasource.name,
        "host": datasource.host,
        "port": datasource.port,
        "database": datasource.database,
        "username": datasource.username,
    }

    updates = body.model_dump(exclude_unset=True)

    if "password" in updates:
        updates["encrypted_password"] = encrypt_value(
            updates.pop("password")
        )

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
        details={
            "before": before,
            "after": after,
        },
    )

    await db.commit()
    await db.refresh(datasource)

    return DataSourceRead.model_validate(datasource)


async def delete_datasource(
    db: AsyncSession,
    datasource_id: int,
    actor: User,
) -> int:
    datasource = await crud.get_one(
        db,
        DataSource,
        id=datasource_id,
    )

    if not datasource:
        raise HTTPException(
            status_code=404,
            detail="Datasource not found",
        )

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

    await crud.delete(
        db,
        DataSource,
        datasource_id,
    )

    return datasource_id


def build_mysql_connection_url(
        datasource: DataSource,
) -> str:
    password = decrypt_value(datasource.encrypted_password)
    return (
        f"mysql+aiomysql://"
        f"{datasource.username}:{password}"
        f"@{datasource.host}:{datasource.port}"
        f"/{datasource.database}"
    )


async def create_mysql_engine(datasource: DataSource):
    url = build_mysql_connection_url(datasource)
    return create_async_engine(
        url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )


async def test_connection(datasource_id: int, db: AsyncSession) -> bool:
    datasource = await crud.get_one(db, DataSource, id=datasource_id)
    engine = await create_mysql_engine(datasource)
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True

    except Exception as e:
        raise e
    finally:
        await engine.dispose()
