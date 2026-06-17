import secrets
import string
import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)

    async with AsyncClient(
            transport=transport,
            base_url="http://test",
    ) as client:
        yield client


async def create_user(async_client: AsyncClient, payload: dict):
    res = await async_client.post("/auth/users", json=payload)
    assert res.status_code in (200, 201), res.text
    return res.json().get("data")


async def login_for_testing(async_client: AsyncClient, email: str, password: str):
    login = await async_client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )

    assert login.status_code == 200, login.text
    return login.json()["access_token"]


async def get_admin_token(async_client: AsyncClient):
    """
    IMPORTANT:
    Admin user must already exist in DB (seeded user).
    """

    login = await async_client.post(
        "/auth/login",
        data={
            "username": "admin@test.com",
            "password": "AdminPass123!",
        },
    )

    assert login.status_code == 200, login.text
    return login.json()["access_token"]


def generate_random_email(domain: str = "test.com") -> str:
    return f"user_{uuid.uuid4().hex[:10]}@{domain}"


def generate_random_password(length: int = 12) -> str:
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(chars) for _ in range(length))
