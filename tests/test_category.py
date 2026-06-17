import pytest

from tests.conftest import AsyncClient, get_admin_token


async def create_category(async_client: AsyncClient, token: str):
    res = await async_client.post(
        "/category/",
        json={
            "name": "test3-category",
            "description": "test",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    return res.json()["data"]["id"]


async def create_datasource(async_client: AsyncClient, token: str):
    res = await async_client.post(
        "/datasources",
        json={
            "name": "test app",
            "type": "mysql",
            "host": "localhost",
            "port": 5432,
            "database": "test_app",
            "username": "root",
            "password": "mysql",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    return res.json()["data"]["id"]


@pytest.mark.anyio
async def test_create_category(async_client: AsyncClient):
    token = await get_admin_token(async_client)

    response = await async_client.post(
        "/category/",
        json={
            "name": "test2-category",
            "description": "test",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code in [200, 201]
    assert "data" in response.json()


@pytest.mark.anyio
async def test_read_category(async_client: AsyncClient):
    token = await get_admin_token(async_client)
    category_id = await create_category(async_client, token)

    response = await async_client.get(
        f"/category/{category_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json().get("data")["id"] == category_id


@pytest.mark.anyio
async def test_update_category(async_client: AsyncClient):
    token = await get_admin_token(async_client)
    category_id = await create_category(async_client, token)

    response = await async_client.patch(
        f"/category/{category_id}",
        json={"name": "updated-category"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    assert "data" in response.json()


@pytest.mark.anyio
async def test_delete_category(async_client: AsyncClient):
    token = await get_admin_token(async_client)
    category_id = await create_category(async_client, token)

    response = await async_client.delete(
        f"/category/{category_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert "data" in response.json()


@pytest.mark.anyio
async def test_assign_category_to_datasource(async_client: AsyncClient):
    token = await get_admin_token(async_client)

    category_id = await create_category(async_client, token)
    datasource_id = await create_datasource(async_client, token)

    response = await async_client.post(
        f"/category/{datasource_id}",
        params={"category_id": category_id},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert "data" in response.json()


@pytest.mark.anyio
async def test_unassign_category_from_datasource(async_client: AsyncClient):
    token = await get_admin_token(async_client)

    category_id = await create_category(async_client, token)
    datasource_id = await create_datasource(async_client, token)

    await async_client.post(
        f"/category/{datasource_id}",
        params={"category_id": category_id},
        headers={"Authorization": f"Bearer {token}"},
    )

    response = await async_client.delete(
        f"/category/{datasource_id}/categories/{category_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert "data" in response.json()
