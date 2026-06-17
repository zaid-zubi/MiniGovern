import uuid

import pytest

from tests.conftest import AsyncClient, get_admin_token


async def create_datasource(async_client: AsyncClient, token: str):
    res = await async_client.post(
        "/datasources",
        json={
            "name": "scan-db",
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
async def test_create_scan_job(async_client: AsyncClient):
    token = await get_admin_token(async_client)
    datasource_id = await create_datasource(async_client, token)

    response = await async_client.post(
        "/scan-jobs",
        json={"datasource_id": datasource_id},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201, response.text
    assert "data" in response.json()


@pytest.mark.anyio
async def test_get_scan_job_status(async_client: AsyncClient):
    token = await get_admin_token(async_client)
    datasource_id = await create_datasource(async_client, token)

    create = await async_client.post(
        "/scan-jobs",
        json={"datasource_id": datasource_id},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert create.status_code in (200, 201), create.text
    job_id = create.json()["data"]["id"]

    response = await async_client.get(
        f"/scan-jobs/{job_id}/status",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200, response.text
    assert "data" in response.json()


@pytest.mark.anyio
async def test_get_scan_job_query_param(async_client: AsyncClient):
    token = await get_admin_token(async_client)
    datasource_id = await create_datasource(async_client, token)

    create = await async_client.post(
        "/scan-jobs",
        json={"datasource_id": datasource_id},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert create.status_code in (200, 201), create.text
    job_id = create.json()["data"]["id"]

    response = await async_client.get(
        f"/scan-jobs/?scan_job_id={job_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200, response.text
    assert "data" in response.json()