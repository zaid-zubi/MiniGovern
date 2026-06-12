import asyncio
import getpass

from sqlalchemy import select

from app.models.user import User
from core.db.base import UserRole
from core.db.session import AsyncSessionLocal
from core.security import hash_password


async def create_admin():
    print("\n**** Create your default Admin account ****\n")

    email = await asyncio.to_thread(input, "Enter admin email: ")
    email = email.strip()

    password = getpass.getpass("Enter admin password: ").strip()
    confirm_password = getpass.getpass("Confirm admin password: ").strip()

    if password != confirm_password:
        print("❌ Passwords do not match")
        return

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.email == email)
        )
        existing = result.scalar_one_or_none()

        if existing:
            print("⚠️ Admin already exists with this email")
            return

        admin = User(
            email=email,
            hashed_password=hash_password(password),
            role=UserRole.ADMIN,
        )

        db.add(admin)
        await db.commit()

        print("✅ Admin created successfully")


if __name__ == "__main__":
    asyncio.run(create_admin())