from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.auth import get_current_active_user, require_roles
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserCreate, UserRead, UserUpdate
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
        form_data.username,   # email here
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
    _admin: Annotated[User, Depends(require_roles(UserRole.ADMIN))] = ...,
) -> User:
    existing = await get_user_by_email(db, body.email)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    return await create_user(db, body)


@router.patch("/users/{user_id}", response_model=UserRead)
async def patch_user(
    user_id: int,
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: Annotated[User, Depends(require_roles(UserRole.ADMIN))] = ...,
) -> User:
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return await update_user(db, user, body)
