# tests/test_categories.py
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_category(async_client: AsyncClient):
    resp = await async_client.post(
        "/api/v1/categories",
        json={"name": "Electronics", "description": "Gadgets and devices"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] > 0
    assert data["name"] == "Electronics"


@pytest.mark.asyncio
async def test_create_duplicate_category(async_client: AsyncClient):
    await async_client.post(
        "/api/v1/categories",
        json={"name": "Apparel", "description": "Clothing"},
    )
    resp = await async_client.post(
        "/api/v1/categories",
        json={"name": "Apparel", "description": "Duplicate"},
    )
    assert resp.status_code == 400
    assert "already exists" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_list_categories(async_client: AsyncClient):
    await async_client.post(
        "/api/v1/categories",
        json={"name": "Books", "description": "Reading material"},
    )
    resp = await async_client.get("/api/v1/categories")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert any(cat["name"] == "Books" for cat in data)


@pytest.mark.asyncio
async def test_get_category_not_found(async_client: AsyncClient):
    resp = await async_client.get("/api/v1/categories/999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_category(async_client: AsyncClient):
    create_resp = await async_client.post(
        "/api/v1/categories",
        json={"name": "OldName", "description": "Old desc"},
    )
    cat_id = create_resp.json()["id"]

    update_resp = await async_client.put(
        f"/api/v1/categories/{cat_id}",
        json={"name": "NewName", "description": "New desc"},
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["name"] == "NewName"
    assert data["description"] == "New desc"


@pytest.mark.asyncio
async def test_delete_category(async_client: AsyncClient):
    create_resp = await async_client.post(
        "/api/v1/categories",
        json={"name": "ToDelete", "description": "To be deleted"},
    )
    cat_id = create_resp.json()["id"]

    del_resp = await async_client.delete(f"/api/v1/categories/{cat_id}")
    assert del_resp.status_code == 204

    get_resp = await async_client.get(f"/api/v1/categories/{cat_id}")
    assert get_resp.status_code == 404