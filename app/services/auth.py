from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.auth import UserCreate, UserUpdate, UserRead, TokenResponse
from app.services.audit import log_audit_action
from core.db.base import UserRole
from core.security import hash_password, verify_password, create_access_token


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    user = await get_user_by_email(db, email)
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user


async def register_and_create_user(body, admin, db):
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
        can_commit=True
    )
    return UserRead.model_validate(new_user)


async def create_user(db: AsyncSession, body: UserCreate) -> User:
    user = User(
        email=body.email,
        hashed_password=hash_password(body.password),
        role=body.role,
        is_active=body.is_active,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user(user_id: int, body: UserUpdate, actor_id: int, db: AsyncSession):
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    old_data = {
        "email": user.email,
        "role": user.role.value,
        "is_active": user.is_active,
    }
    if body.role is not None:
        user.role = body.role
    if body.is_active is not None:
        user.is_active = body.is_active
    if body.password is not None:
        user.hashed_password = hash_password(body.password)
    await log_audit_action(
        db,
        actor_id=actor_id,
        action="update",
        entity_type="user",
        entity_id=user_id,
        details={
            "before": old_data,
            "after": {
                "email": body.email,
                "role": body.role.value,
                "is_active": body.is_active,
            },
        },
    )
    await db.commit()
    await db.refresh(user)
    return UserRead.model_validate(user)


def parse_role_from_token(role_value: str) -> UserRole:
    normalized = role_value.lower()
    for role in UserRole:
        if role.value == normalized:
            return role
    raise ValueError(f"Unknown role: {role_value}")


async def login_user(form_data, db):
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
    print("access token: ", access_token)

    await log_audit_action(
        db,
        actor_id=user.id,
        action="login",
        entity_type="auth",
        entity_id=user.id,
        details={
            "email": user.email,
        },
        can_commit=True
    )

    return TokenResponse(access_token=access_token)
