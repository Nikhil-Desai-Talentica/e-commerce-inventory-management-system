# tests/test_skus.py
import pytest
from httpx import AsyncClient


@pytest.fixture
async def sample_category(async_client: AsyncClient):
    resp = await async_client.post(
        "/api/v1/categories",
        json={"name": "Electronics", "description": "Electronic devices"},
    )
    assert resp.status_code == 201
    return resp.json()


@pytest.fixture
async def sample_product(async_client: AsyncClient, sample_category):
    resp = await async_client.post(
        "/api/v1/products",
        json={
            "name": "iPhone 15",
            "description": "Latest iPhone model",
            "category_id": sample_category["id"],
        },
    )
    assert resp.status_code == 201
    return resp.json()


@pytest.fixture
async def second_product(async_client: AsyncClient, sample_category):
    resp = await async_client.post(
        "/api/v1/products",
        json={
            "name": "MacBook Pro",
            "description": "Laptop",
            "category_id": sample_category["id"],
        },
    )
    assert resp.status_code == 201
    return resp.json()


@pytest.mark.asyncio
async def test_create_sku_for_product(async_client: AsyncClient, sample_product):
    resp = await async_client.post(
        f"/api/v1/products/{sample_product['id']}/skus",
        json={
            "name": "iPhone 15 - 128GB - Black",
            "description": "Black variant",
            "price": "999.99",
            "quantity": 10,
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] > 0
    assert data["product_id"] == sample_product["id"]
    assert data["name"] == "iPhone 15 - 128GB - Black"
    assert float(data["price"]) == 999.99
    assert data["quantity"] == 10


@pytest.mark.asyncio
async def test_create_sku_invalid_product(async_client: AsyncClient):
    resp = await async_client.post(
        "/api/v1/products/99999/skus",
        json={
            "name": "Invalid SKU",
            "price": "10.00",
            "quantity": 1,
        },
    )
    assert resp.status_code == 404
    assert "Product not found" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_list_skus_for_product(async_client: AsyncClient, sample_product):
    for name in ["Variant A", "Variant B"]:
        create_resp = await async_client.post(
            f"/api/v1/products/{sample_product['id']}/skus",
            json={
                "name": name,
                "description": f"{name} description",
                "price": "50.00",
                "quantity": 5,
            },
        )
        assert create_resp.status_code == 201

    list_resp = await async_client.get(
        f"/api/v1/products/{sample_product['id']}/skus"
    )
    assert list_resp.status_code == 200
    data = list_resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert {sku["name"] for sku in data["items"]} == {"Variant A", "Variant B"}


@pytest.mark.asyncio
async def test_update_sku(async_client: AsyncClient, sample_product):
    create_resp = await async_client.post(
        f"/api/v1/products/{sample_product['id']}/skus",
        json={
            "name": "Variant C",
            "description": "Initial description",
            "price": "75.00",
            "quantity": 3,
        },
    )
    sku_id = create_resp.json()["id"]

    update_resp = await async_client.put(
        f"/api/v1/skus/{sku_id}",
        json={"name": "Variant C Updated", "quantity": 7},
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["id"] == sku_id
    assert data["name"] == "Variant C Updated"
    assert data["quantity"] == 7


@pytest.mark.asyncio
async def test_update_sku_invalid_product(
    async_client: AsyncClient, sample_product
):
    create_resp = await async_client.post(
        f"/api/v1/products/{sample_product['id']}/skus",
        json={
            "name": "Variant D",
            "price": "120.00",
            "quantity": 2,
        },
    )
    sku_id = create_resp.json()["id"]

    update_resp = await async_client.put(
        f"/api/v1/skus/{sku_id}",
        json={"product_id": 99999},
    )
    assert update_resp.status_code == 400
    assert "does not exist" in update_resp.json()["detail"]


@pytest.mark.asyncio
async def test_delete_sku(async_client: AsyncClient, sample_product):
    create_resp = await async_client.post(
        f"/api/v1/products/{sample_product['id']}/skus",
        json={
            "name": "Variant E",
            "price": "30.00",
            "quantity": 8,
        },
    )
    sku_id = create_resp.json()["id"]

    delete_resp = await async_client.delete(f"/api/v1/skus/{sku_id}")
    assert delete_resp.status_code == 204

    get_resp = await async_client.get(f"/api/v1/skus/{sku_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_duplicate_sku_name_per_product(
    async_client: AsyncClient, sample_product
):
    first_resp = await async_client.post(
        f"/api/v1/products/{sample_product['id']}/skus",
        json={
            "name": "Variant F",
            "price": "40.00",
            "quantity": 1,
        },
    )
    assert first_resp.status_code == 201

    duplicate_resp = await async_client.post(
        f"/api/v1/products/{sample_product['id']}/skus",
        json={
            "name": "Variant F",
            "price": "45.00",
            "quantity": 2,
        },
    )
    assert duplicate_resp.status_code == 400
    assert "already exists" in duplicate_resp.json()["detail"]


@pytest.mark.asyncio
async def test_same_sku_name_allowed_across_products(
    async_client: AsyncClient, sample_product, second_product
):
    resp_one = await async_client.post(
        f"/api/v1/products/{sample_product['id']}/skus",
        json={
            "name": "Shared Name",
            "price": "10.00",
            "quantity": 1,
        },
    )
    resp_two = await async_client.post(
        f"/api/v1/products/{second_product['id']}/skus",
        json={
            "name": "Shared Name",
            "price": "20.00",
            "quantity": 2,
        },
    )
    assert resp_one.status_code == 201
    assert resp_two.status_code == 201
    assert resp_one.json()["product_id"] != resp_two.json()["product_id"]
