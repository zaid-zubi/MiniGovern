import pytest
from httpx import AsyncClient

from core.db.base import UserRole
from tests.conftest import (
    get_admin_token,
    generate_random_email,
)


@pytest.mark.anyio
async def test_register_user(async_client: AsyncClient):
    token = await get_admin_token(async_client)

    response = await async_client.post(
        "/auth/users",
        json={
            "email": generate_random_email(),
            "password": "UserPass123!",
            "role": UserRole.EDITOR,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code in (200, 201), response.text

    body = response.json()
    assert "data" in body


@pytest.mark.anyio
async def test_login(async_client: AsyncClient):
    token = await get_admin_token(async_client)

    assert token
    assert isinstance(token, str)


@pytest.mark.anyio
async def test_me(async_client: AsyncClient):
    token = await get_admin_token(async_client)

    response = await async_client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200, response.text

    body = response.json()

    if "data" in body:
        assert body["data"] is not None
    else:
        assert body is not None


@pytest.mark.anyio
async def test_unauthorized_me(async_client: AsyncClient):
    response = await async_client.get("/auth/me")

    assert response.status_code in (401, 403)


@pytest.mark.anyio
async def test_admin_required(async_client: AsyncClient):
    token = await get_admin_token(async_client)

    response = await async_client.get(
        "/auth/users",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200, response.text