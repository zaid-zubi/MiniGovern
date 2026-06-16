from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.auth import get_user_by_id, parse_role_from_token
from core.db.base import UserRole
from core.db.session import get_db
from core.rbac import Permission, role_at_least, role_has_permission
from core.security.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])
        token_role = parse_role_from_token(str(payload["role"]))
    except (KeyError, TypeError, ValueError):
        raise credentials_exception from None

    user = await get_user_by_id(db, user_id)
    if user is None or user.role != token_role:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


def require_roles(*roles: UserRole) -> Callable[..., User]:
    allowed = set(roles)

    async def _check(current_user: Annotated[User, Depends(get_current_active_user)]) -> User:
        if current_user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role",
            )
        return current_user

    return _check


def require_minimum_role(minimum_role: UserRole) -> Callable[..., User]:
    async def _check(current_user: Annotated[User, Depends(get_current_active_user)]) -> User:
        if not role_at_least(current_user.role, minimum_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role",
            )
        return current_user

    return _check


def require_permission(permission: Permission) -> Callable[..., User]:
    async def _check(current_user: Annotated[User, Depends(get_current_active_user)]) -> User:
        if not role_has_permission(current_user.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return _check
