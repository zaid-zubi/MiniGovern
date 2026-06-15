from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.auth import get_current_active_user, require_roles
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserCreate, UserRead, UserUpdate
from app.services.audit import log_audit_action
from app.services.auth import (
    authenticate_user,
    create_user,
    get_user_by_email,
    get_user_by_id,
    update_user,
)
from core.db.base import UserRole
from core.db.session import get_db
from core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])



@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(
        db,
        form_data.username,
        form_data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")

    access_token = create_access_token(
        subject=str(user.id),
        role=user.role.value,
        email=user.email,
    )

    await log_audit_action(
        db,
        actor_id=user.id,
        action="login",
        entity_type="auth",
        entity_id=user.id,
        details={
            "email": user.email,
        },
    )

    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserRead)
async def read_current_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    return current_user


@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    body: UserCreate,
    db: AsyncSession = Depends(get_db),
    admin: Annotated[User, Depends(require_roles(UserRole.ADMIN))] = ...,
) -> User:
    existing = await get_user_by_email(db, body.email)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    new_user = await create_user(db, body)

    await log_audit_action(
        db,
        actor_id=admin.id,
        action="create",
        entity_type="user",
        entity_id=new_user.id,
        details={
            "email": new_user.email,
            "role": new_user.role.value,
        },
    )

    return new_user


@router.patch("/users/{user_id}", response_model=UserRead)
async def patch_user(
    user_id: int,
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    admin: Annotated[User, Depends(require_roles(UserRole.ADMIN))] = ...,
) -> User:
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    old_data = {
        "email": user.email,
        "role": user.role.value,
        "is_active": user.is_active,
    }

    updated_user = await update_user(db, user, body)

    await log_audit_action(
        db,
        actor_id=admin.id,
        action="update",
        entity_type="user",
        entity_id=updated_user.id,
        details={
            "before": old_data,
            "after": {
                "email": updated_user.email,
                "role": updated_user.role.value,
                "is_active": updated_user.is_active,
            },
        },
    )

    return updated_user