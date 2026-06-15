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

router = APIRouter(prefix="/tags", tags=["Tags"])

@router.get("")
async def read_tags(
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

@router.post("/")
async def create_tag(name: str,
                     language: Language = Query(default=Language.EN),
                     db: AsyncSession = Depends(get_db),
                     current_user: Annotated[User, Depends(require_permission(Permission.TAG_CREATE))] = ...
                     ):
    data = await tags.create_tag(db, name, current_user.id)
    return http_response(status=status.HTTP_201_CREATED,
                         message=ResponseMessages.TAGS.CREATED.get(language),
                         data=data)

@router.get("/datasets")
async def get_tag_with_datasets(tag_id: int = None,
                                language: Language = Query(default=Language.EN),
                     db: AsyncSession = Depends(get_db),
                     current_user: Annotated[User, Depends(require_permission(Permission.TAG_CREATE))] = ...):
    data = await tags.get_tag_with_datasets(tag_id, db)
    return http_response(status=status.HTTP_200_OK,
                         message=ResponseMessages.GENERAL.READ.get(language),
                         data=data)
@router.post("/datasets/{dataset_id}/assign")
async def assign_tag(
        dataset_id: int,
        tag_name: str,
        language: Language = Query(default=Language.EN),
        db: AsyncSession = Depends(get_db),
        current_user: Annotated[User, Depends(require_permission(Permission.TAG_ASSIGN))] = ...
):
    data = await tags.assign_tag_to_dataset(db, dataset_id, tag_name, current_user.id)
    return http_response(
        status=status.HTTP_200_OK,
        message=ResponseMessages.TAGS.ASSIGN.get(language),
        data=data
    )


@router.delete("/datasets/{dataset_id}/unassign")
async def unassign_tag(
        dataset_id: int,
        tag_name: str,
        language: Language = Query(default=Language.EN),
        db: AsyncSession = Depends(get_db),
        current_user: Annotated[User, Depends(require_permission(Permission.TAG_DELETE))] = ...
):
    data = await tags.remove_tag_from_dataset(db, dataset_id, tag_name, current_user.id)
    return http_response(status=status.HTTP_200_OK,
                         message=ResponseMessages.TAGS.DELETED.get(language),
                         data=data)


@router.delete("/")
async def delete_tag(tag_id: int,
                     language: Language = Query(default=Language.EN),
                     db: AsyncSession = Depends(get_db),
                     current_user: Annotated[User, Depends(require_permission(Permission.TAG_DELETE))] = ...):
    data = await tags.delete_tag(tag_id, db)
    return http_response(status=status.HTTP_200_OK,
                         message=ResponseMessages.TAGS.DELETED.get(language))
