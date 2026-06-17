from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.auth import require_permission
from app.models.user import User
from app.schemas.datasource import DataSourceCreate, DataSourceUpdate
from app.schemas.language import Language
from app.services.datasource import (
    create_datasource,
    delete_datasource,
    get_datasource,
    get_datasource_catalog,
    list_datasources,
    test_connection,
    update_datasource,
)
from core.db.session import get_db
from core.rbac import Permission
from core.settings.constants import ResponseMessages
from core.settings.response import http_response

router = APIRouter(prefix="/datasources", tags=["datasources"])


@router.get("")
async def read_datasources(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission(Permission.DATASOURCE_READ))],
    language: Annotated[Language, Query()] = Language.EN,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
):
    data = await list_datasources(db, skip=skip, limit=limit)
    return http_response(
        status=status.HTTP_200_OK, message=ResponseMessages.DATASOURCE.READ.get(language), data=data
    )


@router.get("/{datasource_id}")
async def read_datasource(
    datasource_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission(Permission.DATASOURCE_READ))],
    language: Annotated[Language, Query()] = Language.EN,
):
    data = await get_datasource(db, datasource_id)
    return http_response(
        status=status.HTTP_200_OK, message=ResponseMessages.DATASOURCE.READ.get(language), data=data
    )


@router.post("")
async def add_datasource(
    body: DataSourceCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission(Permission.DATASOURCE_WRITE))],
    language: Annotated[Language, Query()] = Language.EN,
):
    data = await create_datasource(db, body, current_user)
    return http_response(
        status=status.HTTP_201_CREATED,
        message=ResponseMessages.DATASOURCE.CREATE.get(language),
        data=data,
    )


@router.patch("/{datasource_id}")
async def patch_datasource(
    datasource_id: int,
    body: DataSourceUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission(Permission.DATASOURCE_WRITE))],
    language: Annotated[Language, Query()] = Language.EN,
):
    data = await update_datasource(db, datasource_id, body, current_user)
    return http_response(
        status=status.HTTP_201_CREATED,
        message=ResponseMessages.DATASOURCE.UPDATE.get(language),
        data=data,
    )


@router.delete("/{datasource_id}")
async def remove_datasource(
    datasource_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission(Permission.DATASOURCE_WRITE))],
    language: Annotated[Language, Query()] = Language.EN,
):
    data = await delete_datasource(db, datasource_id, current_user)
    return http_response(
        status=status.HTTP_201_CREATED,
        message=ResponseMessages.DATASOURCE.DELETE.get(language),
        data=data,
    )


@router.get("/test_connection/")
async def test_connection_datasource(datasource_id: int, db: AsyncSession = Depends(get_db)):
    test_conn = await test_connection(datasource_id, db)
    return test_conn


@router.get("/{datasource_id}/catalog")
async def read_datasource_catalog(
    datasource_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission(Permission.DATASOURCE_READ))],
    language: Annotated[Language, Query()] = Language.EN,
):
    data = await get_datasource_catalog(db, datasource_id)
    return http_response(
        status=status.HTTP_200_OK, message=ResponseMessages.GENERAL.READ.get(language), data=data
    )
