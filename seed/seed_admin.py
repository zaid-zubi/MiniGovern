import asyncio
import getpass
import re

from sqlalchemy import select

from app.models.user import User
from core.db.base import UserRole
from core.db.session import AsyncSessionLocal
from core.security.security import hash_password

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"


def validate_email(email: str) -> bool:
    return re.match(EMAIL_REGEX, email) is not None


def validate_password(password: str) -> tuple[bool, str]:
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if len(password) > 128:
        return False, "Password must be less than 128 characters"
    return True, ""


async def create_admin():
    print("\n**** Create your default Admin account ****\n")

    email = await asyncio.to_thread(input, "Enter admin emails: ")
    email = email.strip()

    if not validate_email(email):
        print("❌ Invalid emails format")
        return

    password = getpass.getpass("Enter admin password: ").strip()
    confirm_password = getpass.getpass("Confirm admin password: ").strip()

    if password != confirm_password:
        print("❌ Passwords do not match")
        return

    is_valid, msg = validate_password(password)
    if not is_valid:
        print(f"❌ {msg}")
        return

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == email))
        existing = result.scalar_one_or_none()

        if existing:
            print("⚠️ Admin already exists with this emails")
            return

        admin = User(
            email=email,
            hashed_password=hash_password(password),
            role=UserRole.ADMIN,
            is_active=True,
        )

        db.add(admin)
        await db.commit()

        print("✅ Admin created successfully")


if __name__ == "__main__":
    asyncio.run(create_admin())
