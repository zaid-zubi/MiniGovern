from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.auth import require_permission
from app.models import User
from app.schemas.language import Language
from app.services.catalog import get_table_catalog as read_table_catalog
from core.db.session import get_db
from core.rbac import Permission
from core.settings.constants import ResponseMessages
from core.settings.response import http_response

router = APIRouter(prefix="/catalog", tags=["Catalogs"])


@router.get("/")
async def get_table_catalog(
    table_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission(Permission.CATALOG_READ))],
    language: Annotated[Language, Query()] = Language.EN,
):
    data = await read_table_catalog(table_id, db, _)
    return http_response(
        status=status.HTTP_200_OK, message=ResponseMessages.TAGS.READ.get(language), data=data
    )
