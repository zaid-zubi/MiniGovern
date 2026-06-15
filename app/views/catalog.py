from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.auth import require_permission
from app.models import User
from app.schemas.language import Language
from app.services import tags
from app.services.tags import get_list_tags
from core.db.session import get_db
from core.rbac import Permission
from core.settings.constants import ResponseMessages
from core.settings.response import http_response

router = APIRouter(prefix="/catalog", tags=["Catalogs"])

@router.get("")
async def get_table_catalog(
        db: Annotated[AsyncSession, Depends(get_db)],
        _: Annotated[User, Depends(require_permission(Permission.TAG_READ))],
        language: Annotated[Language, Query()] = Language.EN,
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=100, ge=1, le=200),
):
    data = await get_list_tags(db, skip=skip, limit=limit)
    return http_response(status=status.HTTP_200_OK,
                         message=ResponseMessages.TAGS.READ.get(language),
                         data=data)