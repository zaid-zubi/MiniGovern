import pytest
from httpx import AsyncClient

from tests.conftest import get_admin_token


async def create_tag(async_client: AsyncClient, token: str):
    res = await async_client.post(
        "/tags/",
        params={"name": "test-tag"},
        headers={"Authorization": f"Bearer {token}"},
    )
    return res.json()["data"]["id"]


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


@pytest.mark.anyio
async def test_create_tag(async_client: AsyncClient):
    token = await get_admin_token(async_client)

    response = await async_client.post(
        "/tags/",
        params={"name": "test-tag"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code in (200, 201)
    assert "data" in response.json()


@pytest.mark.anyio
async def test_list_tags(async_client: AsyncClient):
    token = await get_admin_token(async_client)

    response = await async_client.get(
        "/tags",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert "data" in response.json()


@pytest.mark.anyio
async def test_get_tag_by_id(async_client: AsyncClient):
    token = await get_admin_token(async_client)

    create = await async_client.post(
        "/tags/",
        params={"name": "test1-tag"},
        headers={"Authorization": f"Bearer {token}"},
    )
    print(create.status_code)
    print(create.text)
    tag_id = create.json()["data"]["id"]

    response = await async_client.get(
        f"/tags/{tag_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["id"] == tag_id


@pytest.mark.anyio
async def test_delete_tag(async_client: AsyncClient):
    token = await get_admin_token(async_client)

    create = await async_client.post(
        "/tags/",
        params={"name": "test2-tag"},
        headers={"Authorization": f"Bearer {token}"},
    )

    tag_id = create.json()["data"]["id"]

    response = await async_client.delete(
        "/tags/",
        params={"tag_id": tag_id},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200


@pytest.mark.anyio
async def test_assign_tag_to_dataset(async_client: AsyncClient):
    token = await get_admin_token(async_client)

    await async_client.post(
        "/tags/",
        params={"name": "assign-tag"},
        headers={"Authorization": f"Bearer {token}"},
    )

    dataset = await create_dataset(async_client, token)

    response = await async_client.post(
        f"/tags/datasets/{dataset}/assign",
        params={"tag_name": "assign-tag"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert "data" in response.json()


@pytest.mark.anyio
async def test_unassign_tag_from_dataset(async_client: AsyncClient):
    token = await get_admin_token(async_client)

    await async_client.post(
        "/tags/",
        params={"name": "unassign-tag"},
        headers={"Authorization": f"Bearer {token}"},
    )

    dataset = await create_dataset(async_client, token)

    await async_client.post(
        f"/tags/datasets/{dataset}/assign",
        params={"tag_name": "unassign-tag"},
        headers={"Authorization": f"Bearer {token}"},
    )

    response = await async_client.delete(
        f"/tags/datasets/{dataset}/unassign",
        params={"tag_name": "unassign-tag"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200


@pytest.mark.anyio
async def test_get_tag_with_datasets(async_client: AsyncClient):
    token = await get_admin_token(async_client)

    tag = await async_client.post(
        "/tags/",
        params={"name": "dataset-tag"},
        headers={"Authorization": f"Bearer {token}"},
    )

    tag_id = tag.json()["data"]["id"]

    response = await async_client.get(
        f"/tags/datasets/{tag_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert "data" in response.json()
