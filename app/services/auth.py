from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.auth import UserCreate, UserUpdate, UserRead, TokenResponse
from app.schemas.language import Language
from app.services.audit import log_audit_action
from core.db.base import UserRole
from core.security import hash_password, verify_password, create_access_token
from core.logging import logger
from core.settings.exceptions.auth import UserAlreadyExists, IncorrectEmailOrPassword, InactiveUser, UserNotFound


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    logger.debug(f"Fetching user by email: {email}")
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    logger.debug(f"Fetching user by id: {user_id}")
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    logger.debug(f"Authenticating user: {email}")
    user = await get_user_by_email(db, email)

    if user is None:
        logger.warning(f"Authentication failed: user not found ({email})")
        return None

    if not verify_password(password, user.hashed_password):
        logger.warning(f"Authentication failed: wrong password ({email})")
        return None

    logger.info(f"User authenticated successfully: {email}")
    return user


async def register_and_create_user(body, admin, db):
    logger.info(f"Registering new user with email: {body.email}")

    existing = await get_user_by_email(db, body.email)
    if existing is not None:
        logger.error(f"User already exists: {body.email}")
        raise UserAlreadyExists()

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

    logger.info(f"User created successfully: id={new_user.id}, email={new_user.email}")

    return UserRead.model_validate(new_user)


async def create_user(db: AsyncSession, body: UserCreate) -> UserRead:
    logger.debug(f"Creating user in DB: {body.email}")

    user = User(
        email=body.email,
        hashed_password=hash_password(body.password),
        role=body.role,
        is_active=body.is_active,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    logger.info(f"User persisted in DB: id={user.id}, email={user.email}")

    return UserRead.model_validate(user)


async def update_user(user_id: int, body: UserUpdate, actor_id: int, db: AsyncSession):
    logger.info(f"Updating user: {user_id}")

    user = await get_user_by_id(db, user_id)
    if user is None:
        logger.error(f"User not found: {user_id}")
        raise UserNotFound()

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
                "role": body.role.value if body.role else None,
                "is_active": body.is_active,
            },
        },
    )

    await db.commit()
    await db.refresh(user)

    logger.info(f"User updated successfully: id={user_id}")

    return UserRead.model_validate(user)


def parse_role_from_token(role_value: str) -> UserRole:
    logger.debug(f"Parsing role from token: {role_value}")

    normalized = role_value.lower()
    for role in UserRole:
        if role.value == normalized:
            return role

    logger.error(f"Unknown role received: {role_value}")
    raise ValueError(f"Unknown role: {role_value}")

async def login_user(form_data, db):
    logger.info(f"Login attempt: {form_data.username}")

    user = await authenticate_user(
        db,
        form_data.username,
        form_data.password,
    )

    if user is None:
        logger.warning(f"Login failed: invalid credentials {form_data.username}")
        raise IncorrectEmailOrPassword()

    if not user.is_active:
        logger.warning(f"Login blocked (inactive): {user.email}")
        raise InactiveUser()

    access_token = create_access_token(
        subject=str(user.id),
        role=user.role.value,
        email=user.email,
    )

    logger.info(f"Login successful: {user.email} (id={user.id})")

    await log_audit_action(
        db,
        actor_id=user.id,
        action="login",
        entity_type="auth",
        entity_id=user.id,
        details={"email": user.email},
        can_commit=True
    )

    return TokenResponse(access_token=access_token)