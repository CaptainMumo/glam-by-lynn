"""Tests for wishlist functionality."""
from decimal import Decimal

import pytest
from fastapi import status

from app.models.product import Brand, Category, Product
from app.models.user import User


@pytest.fixture
def sample_brand(db_session):
    """Create a sample brand."""
    brand = Brand(
        name="Test Brand",
        slug="test-brand",
        description="Test brand for wishlist tests",
        is_active=True,
    )
    db_session.add(brand)
    db_session.commit()
    db_session.refresh(brand)
    return brand


@pytest.fixture
def sample_category(db_session):
    """Create a sample category."""
    category = Category(
        name="Test Category",
        slug="test-category",
        description="Test category for wishlist tests",
        is_active=True,
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def sample_products(db_session, sample_brand, sample_category):
    """Create sample products for wishlist testing."""
    products = [
        Product(
            title="Product 1",
            slug="product-1",
            description="First test product",
            brand_id=sample_brand.id,
            category_id=sample_category.id,
            base_price=Decimal("1000.00"),
            inventory_count=50,
            is_active=True,
        ),
        Product(
            title="Product 2",
            slug="product-2",
            description="Second test product",
            brand_id=sample_brand.id,
            category_id=sample_category.id,
            base_price=Decimal("2000.00"),
            inventory_count=10,
            is_active=True,
        ),
        Product(
            title="Inactive Product",
            slug="inactive-product",
            description="Product that is not active",
            brand_id=sample_brand.id,
            category_id=sample_category.id,
            base_price=Decimal("3000.00"),
            inventory_count=100,
            is_active=False,
        ),
    ]

    for product in products:
        db_session.add(product)
    db_session.commit()

    return products


@pytest.fixture
def authenticated_user(db_session):
    """Create authenticated user for testing."""
    user = User(
        email="testuser@example.com",
        google_id="test123",
        full_name="Test User",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def another_user(db_session):
    """Create another user for authorization testing."""
    user = User(
        email="anotheruser@example.com",
        google_id="test456",
        full_name="Another User",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user_token(authenticated_user):
    """Create JWT token for authenticated user."""
    from app.core.security import create_access_token

    return create_access_token(
        data={"sub": str(authenticated_user.id), "email": authenticated_user.email}
    )


@pytest.fixture
def another_user_token(another_user):
    """Create JWT token for another user."""
    from app.core.security import create_access_token

    return create_access_token(data={"sub": str(another_user.id), "email": another_user.email})


def test_get_empty_wishlist(client, user_token):
    """Test getting empty wishlist."""
    response = client.get(
        "/api/wishlist",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "items" in data
    assert "total" in data
    assert len(data["items"]) == 0
    assert data["total"] == 0


def test_get_wishlist_unauthorized(client):
    """Test that unauthenticated users cannot access wishlist."""
    response = client.get("/api/wishlist")

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_add_product_to_wishlist(client, user_token, sample_products):
    """Test successfully adding product to wishlist."""
    product = sample_products[0]

    response = client.post(
        "/api/wishlist",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"productId": str(product.id)},
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert data["productId"] == str(product.id)
    assert "product" in data
    assert data["product"]["title"] == "Product 1"
    assert float(data["product"]["basePrice"]) == 1000.00
    assert "createdAt" in data


def test_add_multiple_products_to_wishlist(client, user_token, sample_products):
    """Test adding multiple products to wishlist."""
    product1 = sample_products[0]
    product2 = sample_products[1]

    # Add first product
    response1 = client.post(
        "/api/wishlist",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"productId": str(product1.id)},
    )
    assert response1.status_code == status.HTTP_201_CREATED

    # Add second product
    response2 = client.post(
        "/api/wishlist",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"productId": str(product2.id)},
    )
    assert response2.status_code == status.HTTP_201_CREATED

    # Get wishlist
    response = client.get(
        "/api/wishlist",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert len(data["items"]) == 2
    assert data["total"] == 2


def test_add_duplicate_product_fails(client, user_token, sample_products):
    """Test that adding duplicate product to wishlist fails."""
    product = sample_products[0]

    # Add product first time
    response1 = client.post(
        "/api/wishlist",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"productId": str(product.id)},
    )
    assert response1.status_code == status.HTTP_201_CREATED

    # Try to add same product again
    response2 = client.post(
        "/api/wishlist",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"productId": str(product.id)},
    )

    assert response2.status_code == status.HTTP_400_BAD_REQUEST
    assert "already in" in response2.json()["detail"].lower() and "wishlist" in response2.json()["detail"].lower()


def test_add_inactive_product_fails(client, user_token, sample_products):
    """Test that adding inactive product to wishlist fails."""
    product = sample_products[2]  # Inactive product

    response = client.post(
        "/api/wishlist",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"productId": str(product.id)},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "not available" in response.json()["detail"].lower()


def test_add_nonexistent_product_fails(client, user_token):
    """Test that adding nonexistent product fails."""
    from uuid import uuid4

    fake_id = uuid4()

    response = client.post(
        "/api/wishlist",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"productId": str(fake_id)},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "not found" in response.json()["detail"].lower()


def test_add_to_wishlist_unauthorized(client, sample_products):
    """Test that adding to wishlist requires authentication."""
    product = sample_products[0]

    response = client.post(
        "/api/wishlist",
        json={"productId": str(product.id)},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_remove_from_wishlist(client, user_token, sample_products):
    """Test removing product from wishlist."""
    product = sample_products[0]

    # Add product
    client.post(
        "/api/wishlist",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"productId": str(product.id)},
    )

    # Remove product
    response = client.delete(
        f"/api/wishlist/{product.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify wishlist is empty
    wishlist_response = client.get(
        "/api/wishlist",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert len(wishlist_response.json()["items"]) == 0


def test_remove_nonexistent_product_fails(client, user_token, sample_products):
    """Test that removing product not in wishlist fails."""
    product = sample_products[0]

    response = client.delete(
        f"/api/wishlist/{product.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_remove_from_wishlist_unauthorized(client, sample_products):
    """Test that removing from wishlist requires authentication."""
    product = sample_products[0]

    response = client.delete(f"/api/wishlist/{product.id}")

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_check_product_in_wishlist(client, user_token, sample_products):
    """Test checking if product is in wishlist."""
    product = sample_products[0]

    # Initially not in wishlist
    response = client.get(
        f"/api/wishlist/check/{product.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["inWishlist"] is False

    # Add product
    client.post(
        "/api/wishlist",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"productId": str(product.id)},
    )

    # Now should be in wishlist
    response = client.get(
        f"/api/wishlist/check/{product.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["inWishlist"] is True


def test_check_wishlist_unauthorized(client, sample_products):
    """Test that checking wishlist requires authentication."""
    product = sample_products[0]

    response = client.get(f"/api/wishlist/check/{product.id}")

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_wishlist_items_newest_first(client, user_token, sample_products):
    """Test that wishlist items are returned newest first."""
    product1 = sample_products[0]
    product2 = sample_products[1]

    # Add product1 first
    client.post(
        "/api/wishlist",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"productId": str(product1.id)},
    )

    # Add product2 second
    client.post(
        "/api/wishlist",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"productId": str(product2.id)},
    )

    # Get wishlist
    response = client.get(
        "/api/wishlist",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    data = response.json()
    assert len(data["items"]) == 2

    # Product2 (added second) should be first (newest first)
    assert data["items"][0]["productId"] == str(product2.id)
    assert data["items"][1]["productId"] == str(product1.id)


def test_wishlist_isolation_between_users(client, user_token, another_user_token, sample_products):
    """Test that wishlists are isolated between users."""
    product = sample_products[0]

    # User 1 adds product
    client.post(
        "/api/wishlist",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"productId": str(product.id)},
    )

    # User 2's wishlist should be empty
    response = client.get(
        "/api/wishlist",
        headers={"Authorization": f"Bearer {another_user_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 0


def test_wishlist_includes_product_details(client, user_token, sample_products):
    """Test that wishlist response includes product details."""
    product = sample_products[0]

    # Add product
    client.post(
        "/api/wishlist",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"productId": str(product.id)},
    )

    # Get wishlist
    response = client.get(
        "/api/wishlist",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    data = response.json()
    assert len(data["items"]) == 1

    item = data["items"][0]
    assert "product" in item
    assert item["product"]["id"] == str(product.id)
    assert item["product"]["title"] == "Product 1"
    assert item["product"]["slug"] == "product-1"
    assert float(item["product"]["basePrice"]) == 1000.00
    assert item["product"]["inventoryCount"] == 50
    assert item["product"]["isActive"] is True
