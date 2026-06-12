from app.models.datasource import DataSource
from app.models.user import User
from app.schemas.datasource import DataSourceCreate, DataSourceUpdate
from app.services.crud import crud
from core.encryption import encrypt_value
from sqlalchemy.ext.asyncio import AsyncSession


async def create_datasource(
    db: AsyncSession,
    body: DataSourceCreate,
    owner: User,
) -> DataSource:
    payload = {
        "name": body.name,
        "host": body.host,
        "port": body.port,
        "database": body.database,
        "username": body.username,
        "encrypted_password": encrypt_value(body.password),
        "owner_id": owner.id,
    }
    return await crud.post(db, DataSource, payload)


async def get_datasource(db: AsyncSession, datasource_id: int) -> DataSource | None:
    return await crud.get_one(db, DataSource, datasource_id)


async def list_datasources(
    db: AsyncSession,
    *,
    skip: int = 0,
    limit: int = 100,
) -> list[DataSource]:
    return await crud.get_all(db, DataSource, skip=skip, limit=limit)


async def update_datasource(
    db: AsyncSession,
    datasource: DataSource,
    body: DataSourceUpdate,
) -> DataSource:
    updates = body.model_dump(exclude_unset=True)
    if "password" in updates:
        updates["encrypted_password"] = encrypt_value(updates.pop("password"))

    updated = await crud.update(db, DataSource, datasource.id, updates)
    if updated is None:
        raise ValueError("Datasource not found")
    return updated


async def delete_datasource(db: AsyncSession, datasource_id: int) -> int:
    return await crud.delete(db, DataSource, datasource_id)
