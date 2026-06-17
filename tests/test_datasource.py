import pytest

from tests.conftest import AsyncClient, get_admin_token


async def create_datasource(async_client: AsyncClient, token: str):
    response = await async_client.post(
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
    return response


@pytest.mark.anyio
async def test_create_datasource(async_client: AsyncClient):
    token = await get_admin_token(async_client)
    response = await create_datasource(async_client, token)
    assert response.status_code in 201
    assert "data" in response.json()


@pytest.mark.anyio
async def test_list_datasources(async_client: AsyncClient):
    token = await get_admin_token(async_client)

    response = await async_client.get(
        "/datasources",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert "data" in response.json()


@pytest.mark.anyio
async def test_get_datasource(async_client: AsyncClient):
    token = await get_admin_token(async_client)

    res = await create_datasource(async_client, token)
    datasource_id = res.json()["data"]["id"]

    response = await async_client.get(
        f"/datasources/{datasource_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["id"] == datasource_id


@pytest.mark.anyio
async def test_update_datasource(async_client: AsyncClient):
    token = await get_admin_token(async_client)

    res = await create_datasource(async_client, token)

    datasource_id = res.json()["data"]["id"]

    response = await async_client.patch(
        f"/datasources/{datasource_id}",
        json={"name": "updated-db"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200


@pytest.mark.anyio
async def test_delete_datasource(async_client: AsyncClient):
    token = await get_admin_token(async_client)

    res = await create_datasource(async_client, token)

    datasource_id = res.json()["data"]["id"]

    response = await async_client.delete(
        f"/datasources/{datasource_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200


@pytest.mark.anyio
async def test_datasource_catalog(async_client: AsyncClient):
    token = await get_admin_token(async_client)
    res = await create_datasource(async_client, token)
    datasource_id = res.json()["data"]["id"]
    response = await async_client.get(
        f"/datasources/{datasource_id}/catalog",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert "data" in response.json()


@pytest.mark.anyio
async def test_test_connection(async_client: AsyncClient):
    token = await get_admin_token(async_client)
    create = await create_datasource(async_client, token)
    datasource_id = create.json()["data"]["id"]

    response = await async_client.get(
        f"/datasources/test_connection/?datasource_id={datasource_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
