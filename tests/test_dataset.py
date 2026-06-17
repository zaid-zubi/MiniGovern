import pytest

from tests.conftest import AsyncClient, get_admin_token


async def get_list_datasets(async_client: AsyncClient, token: str):
    response = await async_client.get(
        "/dataset/",
        headers={"Authorization": f"Bearer {token}"},
    )
    return response.json()['data']


async def create_dataset(async_client: AsyncClient, token: str):
    res = await async_client.post(
        "/dataset/",
        json={
            "name": "tag-dataset",
            "description": "test",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    return res.json()["data"]["id"]


async def get_draft_datasets(async_client: AsyncClient, token: str):
    datasets = await get_list_datasets(async_client, token)
    draft_datasets = [
        d for d in datasets
        if d.get("workflow_state") == "draft"
    ]
    return draft_datasets


async def get_submitted_datasets(async_client: AsyncClient, token: str):
    datasets = await get_list_datasets(async_client, token)
    submitted_datasets = [
        d for d in datasets
        if d.get("workflow_state") == "submitted"
    ]
    return submitted_datasets


@pytest.mark.anyio
async def test_list_datasets(async_client: AsyncClient):
    token = await get_admin_token(async_client)

    response = await async_client.get(
        "/dataset/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert "data" in response.json()


@pytest.mark.anyio
async def test_read_dataset(async_client: AsyncClient):
    token = await get_admin_token(async_client)
    datasets = await get_list_datasets(async_client, token)
    dataset_id = datasets[0].get("id")
    response = await async_client.get(
        f"/dataset/{dataset_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["data"]["id"] == dataset_id


@pytest.mark.anyio
async def test_submit_dataset(async_client: AsyncClient):
    token = await get_admin_token(async_client)
    draft_datasets = await get_draft_datasets(async_client, token)
    dataset_id = draft_datasets[0].get("id")

    response = await async_client.post(
        f"/dataset/{dataset_id}/submit",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert "data" in response.json()


@pytest.mark.anyio
async def test_approve_dataset(async_client: AsyncClient):
    token = await get_admin_token(async_client)
    submitted_datasets = await get_submitted_datasets(async_client, token)
    dataset_id = submitted_datasets[0].get("id")

    response = await async_client.post(
        f"/dataset/{dataset_id}/approve",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert "data" in response.json()


@pytest.mark.anyio
async def test_reject_dataset(async_client: AsyncClient):
    token = await get_admin_token(async_client)
    submitted_datasets = await get_submitted_datasets(async_client, token)
    dataset_id = submitted_datasets[0].get("id")

    response = await async_client.post(
        f"/dataset/{dataset_id}/reject",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert "data" in response.json()


@pytest.mark.anyio
async def test_dataset_audit_logs(async_client: AsyncClient):
    token = await get_admin_token(async_client)
    dataset_id = await create_dataset(async_client, token)

    response = await async_client.get(
        f"/dataset/{dataset_id}/audit-logs",
        headers={"Authorization": f"/Bearer {token}"},
    )

    assert response.status_code == 200
    assert "data" in response.json()
