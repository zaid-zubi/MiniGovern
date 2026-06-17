import pytest

from tests.conftest import (
    AsyncClient,
    generate_random_email,
    generate_random_password,
    login_for_testing,
)


async def create_datasource(client: AsyncClient, token: str):
    res = await client.post(
        "/datasources",
        json={
            "name": "test-db",
            "type": "postgres",
            "host": "localhost",
            "port": 5432,
            "database": "test",
            "username": "user",
            "password": "pass",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code in (200, 201), res.text
    return res.json()["data"]["id"]


@pytest.mark.anyio
async def test_get_table_catalog(async_client):
    email = generate_random_email(domain="gmail.com")
    password = generate_random_password()
    token = await login_for_testing(async_client, email, password)
    table_id = await create_datasource(async_client, token)

    response = await async_client.get(
        "/catalog/",
        params={"table_id": table_id},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200, response.text

    body = response.json()
    assert "data" in body
    assert "message" in body
