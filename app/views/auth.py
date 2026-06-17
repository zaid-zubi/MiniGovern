from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.auth import get_current_active_user, require_roles
from app.models.user import User
from app.schemas.auth import UserCreate, UserRead, UserUpdate
from app.schemas.language import Language
from app.services.auth import (
    delete_user,
    get_users,
    login_user,
    register_and_create_user,
    update_user,
)
from app.services.auth import get_user as read_user
from core.db.base import UserRole
from core.db.session import get_db
from core.settings.constants import ResponseMessages
from core.settings.response import http_response

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
    language: Annotated[Language, Query()] = Language.EN,
):
    data = await login_user(form_data, db)
    return data


@router.get("/me", response_model=UserRead)
async def read_current_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    return current_user


@router.post("/users")
async def register_user(
    body: UserCreate,
    db: AsyncSession = Depends(get_db),
    admin: Annotated[User, Depends(require_roles(UserRole.ADMIN))] = ...,
    language: Annotated[Language, Query()] = Language.EN,
):
    new_user = await register_and_create_user(body, admin, db)
    return http_response(
        status=status.HTTP_201_CREATED,
        message=ResponseMessages.GENERAL.CREATE.get(language),
        data=new_user,
    )


@router.patch("/users/{user_id}")
async def patch_user(
    user_id: int,
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    admin: Annotated[User, Depends(require_roles(UserRole.ADMIN))] = ...,
    language: Annotated[Language, Query()] = Language.EN,
):
    data = await update_user(user_id, body, admin.id, db)
    return http_response(
        status=status.HTTP_201_CREATED,
        message=ResponseMessages.GENERAL.UPDATE.get(language),
        data=data,
    )


@router.get("/users")
async def list_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
    language: Annotated[Language, Query()] = Language.EN,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
):
    data = await get_users(db, skip=skip, limit=limit)

    return http_response(
        status=status.HTTP_200_OK,
        message=ResponseMessages.GENERAL.READ.get(language),
        data=data,
    )


@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
    language: Annotated[Language, Query()] = Language.EN,
):
    data = await read_user(db, user_id)

    return http_response(
        status=status.HTTP_200_OK,
        message=ResponseMessages.GENERAL.READ.get(language),
        data=data,
    )


@router.delete("/users/{user_id}")
async def remove_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
    language: Annotated[Language, Query()] = Language.EN,
):
    data = await delete_user(db, user_id, admin.id)

    return http_response(
        status=status.HTTP_200_OK,
        message=ResponseMessages.GENERAL.DELETE.get(language),
        data=data,
    )
