from typing import Annotated

from fastapi import APIRouter, Depends, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.auth import get_current_active_user, require_roles
from app.models.user import User
from app.schemas.auth import TokenResponse, UserCreate, UserRead, UserUpdate
from app.schemas.language import Language
from app.services.auth import (
    update_user, register_and_create_user, login_user,
)
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
    return http_response(status=status.HTTP_201_CREATED,
                         message=ResponseMessages.GENERAL.CREATE.get(language),
                         data=new_user)


@router.patch("/users/{user_id}")
async def patch_user(
        user_id: int,
        body: UserUpdate,
        db: AsyncSession = Depends(get_db),
        admin: Annotated[User, Depends(require_roles(UserRole.ADMIN))] = ...,
        language: Annotated[Language, Query()] = Language.EN,

):
    data = await update_user(user_id, body, admin.id, db)
    return http_response(status=status.HTTP_201_CREATED,
                         message=ResponseMessages.GENERAL.UPDATE.get(language),
                         data=data)
