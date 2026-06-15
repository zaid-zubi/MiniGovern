from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.auth import require_permission
from app.models.user import User
from app.schemas.category import CategoryIn, CategoryUpdate
from app.schemas.datasource import DataSourceRead
from app.schemas.language import Language
from app.services.catagory import create_category, update_category as update_category_service, get_category, \
    delete_category, assign_datasource_with_category, unassign_datasource_with_category
from core.db.session import get_db
from core.rbac import Permission
from core.settings.constants import ResponseMessages
from core.settings.response import http_response

router = APIRouter(prefix="/category", tags=["categories"])


@router.post("/")
async def add_category(category: CategoryIn,
                       db: AsyncSession = Depends(get_db),
                       current_user: Annotated[User, Depends(require_permission(Permission.CATEGORY_WRITE))] = ...,
                       language: Annotated[Language, Query()] = Language.EN
                       ):
    data = await create_category(category, db, current_user.id)
    return http_response(status=status.HTTP_201_CREATED,
                         message=ResponseMessages.CATEGORY.CREATED.get(language),
                         data=data)


@router.patch("/{category_id}")
async def update_category(
        category_id: int,
        category: CategoryUpdate,
        db: Annotated[AsyncSession, Depends(get_db)],
        current_user: Annotated[User, Depends(require_permission(Permission.CATEGORY_UPDATE))],
        language: Annotated[Language, Query()] = Language.EN,
):
    data = await update_category_service(category, category_id, db, current_user.id)
    return http_response(status=status.HTTP_201_CREATED, message=ResponseMessages.CATEGORY.UPDATED.get(language),
                         data=data)


@router.get("/{category_id}")
async def read_category(
        category_id: int,
        db: Annotated[AsyncSession, Depends(get_db)],
        _: Annotated[User, Depends(require_permission(Permission.CATEGORY_READ))] = ...,
        language: Annotated[Language, Query()] = Language.EN
):
    data = await get_category(category_id, db)
    return http_response(status=status.HTTP_200_OK, message=ResponseMessages.GENERAL.READ.get(language), data=data)


@router.delete("/{category_id}")
async def remove_category(category_id: int,
                          db: Annotated[AsyncSession, Depends(get_db)],
                          current_user: Annotated[User, Depends(require_permission(Permission.CATEGORY_DELETE))] = ...,
                          language: Annotated[Language, Query()] = Language.EN
                          ):
    data = await delete_category(category_id, db, current_user.id)
    return http_response(status=status.HTTP_200_OK, message=ResponseMessages.CATEGORY.DELETED.get(language), data=data)


@router.post("/{datasource_id}")
async def assign_datasource_to_category(datasource_id: int,
                                        category_id: int,
                                        db: Annotated[AsyncSession, Depends(get_db)],
                                        current_user: Annotated[
                                            User, Depends(require_permission(Permission.CATEGORY_WRITE))] = ...,
                                        language: Annotated[Language, Query()] = Language.EN
                                        ):
    data = await assign_datasource_with_category(category_id, datasource_id, db, current_user.id)
    return http_response(status=status.HTTP_200_OK, message=ResponseMessages.CATEGORY.ASSIGN.get(language), data=data)


@router.delete("/{datasource_id}/categories/{category_id}")
async def unassign_category_from_datasource(
        datasource_id: int,
        category_id: int,
        db: Annotated[AsyncSession, Depends(get_db)],
        current_user: Annotated[User, Depends(require_permission(Permission.CATEGORY_WRITE))] = ...,
        language: Annotated[Language, Query()] = Language.EN,
):
    data = await unassign_datasource_with_category(datasource_id, category_id, db, current_user.id)
    return http_response(status=status.HTTP_200_OK, message=ResponseMessages.CATEGORY.UNASSIGN.get(language), data=data)
