from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.auth import get_current_active_user, require_permission
from app.models.user import User
from app.schemas.datasource import DataSourceCreate, DataSourceRead, DataSourceUpdate
from app.services.datasource import (
    create_datasource,
    delete_datasource,
    get_datasource,
    list_datasources,
    update_datasource, test_connection,
)
from core.db.session import get_db
from core.rbac import Permission

router = APIRouter(prefix="/datasources", tags=["datasources"])


@router.get("", response_model=list[DataSourceRead])
async def read_datasources(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission(Permission.DATASOURCE_READ))],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
) -> list[DataSourceRead]:
    return await list_datasources(db, skip=skip, limit=limit)


@router.get("/{datasource_id}", response_model=DataSourceRead)
async def read_datasource(
    datasource_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission(Permission.DATASOURCE_READ))],
) -> DataSourceRead:
    datasource = await get_datasource(db, datasource_id)
    if datasource is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Datasource not found")
    return datasource


@router.post("", response_model=DataSourceRead, status_code=status.HTTP_201_CREATED)
async def add_datasource(
    body: DataSourceCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission(Permission.DATASOURCE_WRITE))],
) -> DataSourceRead:
    return await create_datasource(db, body, current_user)


@router.patch("/{datasource_id}", response_model=DataSourceRead)
async def patch_datasource(
    datasource_id: int,
    body: DataSourceUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission(Permission.DATASOURCE_WRITE))],
) -> DataSourceRead:
    return await update_datasource(db, datasource_id, body)


@router.delete("/{datasource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_datasource(
    datasource_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission(Permission.DATASOURCE_WRITE))],
) -> None:
    deleted = await delete_datasource(db, datasource_id)
    if deleted == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Datasource not found")


@router.get("/test_connection/")
async def test_connection_datasource(datasource_id: int, db: AsyncSession=Depends(get_db)):
    test_conn = await test_connection(datasource_id, db)
    return test_conn