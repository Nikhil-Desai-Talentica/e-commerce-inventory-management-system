# tests/test_products.py
import pytest
from httpx import AsyncClient


@pytest.fixture
async def sample_category(async_client: AsyncClient):
    """Helper fixture to create a sample category for product tests."""
    resp = await async_client.post(
        "/api/v1/categories",
        json={"name": "Electronics", "description": "Electronic devices"},
    )
    assert resp.status_code == 201
    return resp.json()


@pytest.fixture
async def sample_category_2(async_client: AsyncClient):
    """Helper fixture to create a second sample category."""
    resp = await async_client.post(
        "/api/v1/categories",
        json={"name": "Apparel", "description": "Clothing items"},
    )
    assert resp.status_code == 201
    return resp.json()


@pytest.mark.asyncio
async def test_create_product(async_client: AsyncClient, sample_category):
    """Test creating a product successfully."""
    resp = await async_client.post(
        "/api/v1/products",
        json={
            "name": "iPhone 15",
            "description": "Latest iPhone model",
            "category_id": sample_category["id"],
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] > 0
    assert data["name"] == "iPhone 15"
    assert data["description"] == "Latest iPhone model"
    assert data["category_id"] == sample_category["id"]
    assert "category" in data
    assert data["category"]["id"] == sample_category["id"]
    assert data["category"]["name"] == sample_category["name"]


@pytest.mark.asyncio
async def test_create_product_with_invalid_category(async_client: AsyncClient):
    """Test creating a product with non-existent category should fail."""
    resp = await async_client.post(
        "/api/v1/products",
        json={
            "name": "Test Product",
            "description": "Test description",
            "category_id": 99999,
        },
    )
    assert resp.status_code == 400
    assert "does not exist" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_create_duplicate_product(async_client: AsyncClient, sample_category):
    """Test creating a duplicate product name should fail."""
    await async_client.post(
        "/api/v1/products",
        json={
            "name": "iPhone 15",
            "description": "First product",
            "category_id": sample_category["id"],
        },
    )
    
    resp = await async_client.post(
        "/api/v1/products",
        json={
            "name": "iPhone 15",
            "description": "Duplicate product",
            "category_id": sample_category["id"],
        },
    )
    assert resp.status_code == 400
    assert "already exists" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_get_product(async_client: AsyncClient, sample_category):
    """Test getting a product by ID."""
    create_resp = await async_client.post(
        "/api/v1/products",
        json={
            "name": "Samsung Galaxy S24",
            "description": "Android smartphone",
            "category_id": sample_category["id"],
        },
    )
    product_id = create_resp.json()["id"]
    
    resp = await async_client.get(f"/api/v1/products/{product_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == product_id
    assert data["name"] == "Samsung Galaxy S24"
    assert data["category_id"] == sample_category["id"]


@pytest.mark.asyncio
async def test_get_product_not_found(async_client: AsyncClient):
    """Test getting a non-existent product should return 404."""
    resp = await async_client.get("/api/v1/products/99999")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_list_products_basic(async_client: AsyncClient, sample_category):
    """Test listing products without filters."""
    # Create multiple products
    await async_client.post(
        "/api/v1/products",
        json={
            "name": "Product A",
            "description": "First product",
            "category_id": sample_category["id"],
        },
    )
    await async_client.post(
        "/api/v1/products",
        json={
            "name": "Product B",
            "description": "Second product",
            "category_id": sample_category["id"],
        },
    )
    
    resp = await async_client.get("/api/v1/products")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data
    assert len(data["items"]) >= 2
    assert data["total"] >= 2
    assert data["page"] == 1
    assert data["page_size"] == 10


@pytest.mark.asyncio
async def test_list_products_with_pagination(async_client: AsyncClient, sample_category):
    """Test listing products with pagination."""
    # Create 5 products
    for i in range(5):
        await async_client.post(
            "/api/v1/products",
            json={
                "name": f"Product {i}",
                "description": f"Product number {i}",
                "category_id": sample_category["id"],
            },
        )
    
    # Test first page
    resp = await async_client.get("/api/v1/products?page=1&page_size=2")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["total"] >= 5
    
    # Test second page
    resp = await async_client.get("/api/v1/products?page=2&page_size=2")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 2
    assert data["page"] == 2


@pytest.mark.asyncio
async def test_list_products_with_search(async_client: AsyncClient, sample_category):
    """Test listing products with name search."""
    await async_client.post(
        "/api/v1/products",
        json={
            "name": "iPhone 15 Pro",
            "description": "Pro model",
            "category_id": sample_category["id"],
        },
    )
    await async_client.post(
        "/api/v1/products",
        json={
            "name": "Samsung Galaxy",
            "description": "Android phone",
            "category_id": sample_category["id"],
        },
    )
    await async_client.post(
        "/api/v1/products",
        json={
            "name": "iPad Pro",
            "description": "Tablet device",
            "category_id": sample_category["id"],
        },
    )
    
    # Search for "iPhone"
    resp = await async_client.get("/api/v1/products?search=iPhone")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert all("iPhone" in product["name"] for product in data["items"])
    
    # Search for "Pro" (should match both iPhone 15 Pro and iPad Pro)
    resp = await async_client.get("/api/v1/products?search=Pro")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 2
    assert all("Pro" in product["name"] for product in data["items"])


@pytest.mark.asyncio
async def test_list_products_with_category_filter(
    async_client: AsyncClient, sample_category, sample_category_2
):
    """Test listing products filtered by category."""
    # Create products in different categories
    await async_client.post(
        "/api/v1/products",
        json={
            "name": "Electronics Product",
            "description": "In electronics category",
            "category_id": sample_category["id"],
        },
    )
    await async_client.post(
        "/api/v1/products",
        json={
            "name": "Apparel Product",
            "description": "In apparel category",
            "category_id": sample_category_2["id"],
        },
    )
    
    # Filter by electronics category
    resp = await async_client.get(f"/api/v1/products?category_id={sample_category['id']}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert all(
        product["category_id"] == sample_category["id"] for product in data["items"]
    )
    
    # Filter by apparel category
    resp = await async_client.get(f"/api/v1/products?category_id={sample_category_2['id']}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert all(
        product["category_id"] == sample_category_2["id"] for product in data["items"]
    )


@pytest.mark.asyncio
async def test_list_products_with_search_and_category_filter(
    async_client: AsyncClient, sample_category, sample_category_2
):
    """Test listing products with both search and category filter (AND logic)."""
    # Create products in electronics category
    await async_client.post(
        "/api/v1/products",
        json={
            "name": "iPhone 15",
            "description": "Apple phone",
            "category_id": sample_category["id"],
        },
    )
    await async_client.post(
        "/api/v1/products",
        json={
            "name": "Samsung Galaxy",
            "description": "Samsung phone",
            "category_id": sample_category["id"],
        },
    )
    
    # Create product with similar name in different category
    await async_client.post(
        "/api/v1/products",
        json={
            "name": "iPhone Case",
            "description": "Phone accessory",
            "category_id": sample_category_2["id"],
        },
    )
    
    # Search for "iPhone" in electronics category (should only return iPhone 15)
    resp = await async_client.get(
        f"/api/v1/products?search=iPhone&category_id={sample_category['id']}"
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "iPhone 15"
    assert data["items"][0]["category_id"] == sample_category["id"]
    
    # Search for "iPhone" in apparel category (should return iPhone Case)
    resp = await async_client.get(
        f"/api/v1/products?search=iPhone&category_id={sample_category_2['id']}"
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "iPhone Case"
    assert data["items"][0]["category_id"] == sample_category_2["id"]


@pytest.mark.asyncio
async def test_list_products_search_case_insensitive(
    async_client: AsyncClient, sample_category
):
    """Test that product search is case-insensitive."""
    await async_client.post(
        "/api/v1/products",
        json={
            "name": "iPhone 15 Pro Max",
            "description": "Large iPhone",
            "category_id": sample_category["id"],
        },
    )
    
    # Search with lowercase
    resp = await async_client.get("/api/v1/products?search=iphone")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    
    # Search with uppercase
    resp = await async_client.get("/api/v1/products?search=IPHONE")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_update_product(async_client: AsyncClient, sample_category):
    """Test updating a product."""
    create_resp = await async_client.post(
        "/api/v1/products",
        json={
            "name": "Old Product Name",
            "description": "Old description",
            "category_id": sample_category["id"],
        },
    )
    product_id = create_resp.json()["id"]
    
    update_resp = await async_client.put(
        f"/api/v1/products/{product_id}",
        json={
            "name": "New Product Name",
            "description": "New description",
        },
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["name"] == "New Product Name"
    assert data["description"] == "New description"
    assert data["id"] == product_id


@pytest.mark.asyncio
async def test_update_product_partial(async_client: AsyncClient, sample_category):
    """Test partial update of a product."""
    create_resp = await async_client.post(
        "/api/v1/products",
        json={
            "name": "Original Name",
            "description": "Original description",
            "category_id": sample_category["id"],
        },
    )
    product_id = create_resp.json()["id"]
    
    # Update only name
    update_resp = await async_client.put(
        f"/api/v1/products/{product_id}",
        json={"name": "Updated Name"},
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["name"] == "Updated Name"
    assert data["description"] == "Original description"  # Should remain unchanged


@pytest.mark.asyncio
async def test_update_product_change_category(
    async_client: AsyncClient, sample_category, sample_category_2
):
    """Test updating a product's category."""
    create_resp = await async_client.post(
        "/api/v1/products",
        json={
            "name": "Movable Product",
            "description": "Product to move",
            "category_id": sample_category["id"],
        },
    )
    product_id = create_resp.json()["id"]
    
    update_resp = await async_client.put(
        f"/api/v1/products/{product_id}",
        json={"category_id": sample_category_2["id"]},
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["category_id"] == sample_category_2["id"]
    assert data["category"]["id"] == sample_category_2["id"]


@pytest.mark.asyncio
async def test_update_product_invalid_category(async_client: AsyncClient, sample_category):
    """Test updating a product with invalid category should fail."""
    create_resp = await async_client.post(
        "/api/v1/products",
        json={
            "name": "Test Product",
            "description": "Test",
            "category_id": sample_category["id"],
        },
    )
    product_id = create_resp.json()["id"]
    
    update_resp = await async_client.put(
        f"/api/v1/products/{product_id}",
        json={"category_id": 99999},
    )
    assert update_resp.status_code == 400
    assert "does not exist" in update_resp.json()["detail"]


@pytest.mark.asyncio
async def test_update_product_duplicate_name(
    async_client: AsyncClient, sample_category
):
    """Test updating a product to duplicate name should fail."""
    await async_client.post(
        "/api/v1/products",
        json={
            "name": "Existing Product",
            "description": "First product",
            "category_id": sample_category["id"],
        },
    )
    
    create_resp = await async_client.post(
        "/api/v1/products",
        json={
            "name": "Another Product",
            "description": "Second product",
            "category_id": sample_category["id"],
        },
    )
    product_id = create_resp.json()["id"]
    
    # Try to update second product to have same name as first
    update_resp = await async_client.put(
        f"/api/v1/products/{product_id}",
        json={"name": "Existing Product"},
    )
    assert update_resp.status_code == 400
    assert "Error updating product" in update_resp.json()["detail"]


@pytest.mark.asyncio
async def test_update_product_not_found(async_client: AsyncClient):
    """Test updating a non-existent product should return 404."""
    resp = await async_client.put(
        "/api/v1/products/99999",
        json={"name": "New Name"},
    )
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_delete_product(async_client: AsyncClient, sample_category):
    """Test deleting a product."""
    create_resp = await async_client.post(
        "/api/v1/products",
        json={
            "name": "Product To Delete",
            "description": "Will be deleted",
            "category_id": sample_category["id"],
        },
    )
    product_id = create_resp.json()["id"]
    
    del_resp = await async_client.delete(f"/api/v1/products/{product_id}")
    assert del_resp.status_code == 204
    
    get_resp = await async_client.get(f"/api/v1/products/{product_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_product_not_found(async_client: AsyncClient):
    """Test deleting a non-existent product should return 404."""
    resp = await async_client.delete("/api/v1/products/99999")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_list_products_empty_result(async_client: AsyncClient):
    """Test listing products with filter that matches nothing."""
    resp = await async_client.get("/api/v1/products?search=NonexistentProduct")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert len(data["items"]) == 0
    assert data["page"] == 1
    assert data["total_pages"] == 0


@pytest.mark.asyncio
async def test_list_products_pagination_edge_cases(
    async_client: AsyncClient, sample_category
):
    """Test pagination edge cases."""
    # Create 3 products
    for i in range(3):
        await async_client.post(
            "/api/v1/products",
            json={
                "name": f"Product {i}",
                "description": f"Product {i}",
                "category_id": sample_category["id"],
            },
        )
    
    # Request page beyond available data
    resp = await async_client.get("/api/v1/products?page=10&page_size=10")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 0
    assert data["page"] == 10
    assert data["total"] >= 3