"""Tests for shopping cart functionality."""
from decimal import Decimal

import pytest
from fastapi import status

from app.models.product import Brand, Category, Product, ProductVariant
from app.models.user import User


@pytest.fixture
def sample_brand(db_session):
    """Create a sample brand."""
    brand = Brand(
        name="Test Brand",
        slug="test-brand",
        description="Test brand for cart tests",
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
        description="Test category for cart tests",
        is_active=True,
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def sample_products(db_session, sample_brand, sample_category):
    """Create sample products for cart testing."""
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
            title="Out of Stock Product",
            slug="out-of-stock",
            description="Product with no stock",
            brand_id=sample_brand.id,
            category_id=sample_category.id,
            base_price=Decimal("1500.00"),
            inventory_count=0,
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
def sample_variants(db_session, sample_products):
    """Create sample product variants."""
    product = sample_products[0]  # Product 1

    variants = [
        ProductVariant(
            product_id=product.id,
            variant_type="Size",
            variant_value="Small",
            price_adjustment=Decimal("0.00"),
            inventory_count=20,
        ),
        ProductVariant(
            product_id=product.id,
            variant_type="Size",
            variant_value="Large",
            price_adjustment=Decimal("200.00"),
            inventory_count=5,
        ),
    ]

    for variant in variants:
        db_session.add(variant)
    db_session.commit()

    return variants


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


def test_get_empty_cart(client, user_token):
    """Test getting empty cart creates one if it doesn't exist."""
    response = client.get(
        "/api/cart",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "id" in data
    assert "items" in data
    assert "totalItems" in data
    assert "totalAmount" in data

    assert len(data["items"]) == 0
    assert data["totalItems"] == 0
    assert float(data["totalAmount"]) == 0.0


def test_get_cart_unauthorized(client):
    """Test that unauthenticated users cannot access cart."""
    response = client.get("/api/cart")

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_add_item_to_cart_success(client, user_token, sample_products):
    """Test successfully adding item to cart."""
    product = sample_products[0]

    response = client.post(
        "/api/cart/items",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"productId": str(product.id), "quantity": 2},
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert data["productId"] == str(product.id)
    assert data["quantity"] == 2
    assert "product" in data
    assert data["product"]["title"] == "Product 1"
    assert "unitPrice" in data
    assert "subtotal" in data
    assert float(data["unitPrice"]) == 1000.00
    assert float(data["subtotal"]) == 2000.00


def test_add_item_with_variant(client, user_token, sample_products, sample_variants):
    """Test adding item with variant to cart."""
    product = sample_products[0]
    variant = sample_variants[1]  # Large variant

    response = client.post(
        "/api/cart/items",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "productId": str(product.id),
            "productVariantId": str(variant.id),
            "quantity": 1,
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert data["productId"] == str(product.id)
    assert data["productVariantId"] == str(variant.id)
    assert data["quantity"] == 1
    assert "productVariant" in data
    assert data["productVariant"]["variantName"] == "Large"  # variant_value is "Large"
    # Unit price should be base price + variant adjustment
    assert float(data["unitPrice"]) == 1200.00


def test_add_item_increases_quantity_if_exists(client, user_token, sample_products):
    """Test adding same item again increases quantity."""
    product = sample_products[0]

    # Add item first time
    response1 = client.post(
        "/api/cart/items",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"productId": str(product.id), "quantity": 2},
    )
    assert response1.status_code == status.HTTP_201_CREATED

    # Add same item again
    response2 = client.post(
        "/api/cart/items",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"productId": str(product.id), "quantity": 3},
    )
    assert response2.status_code == status.HTTP_201_CREATED
    data = response2.json()

    # Quantity should be 2 + 3 = 5
    assert data["quantity"] == 5


def test_add_item_out_of_stock(client, user_token, sample_products):
    """Test adding out of stock item returns error."""
    product = sample_products[2]  # Out of stock product

    response = client.post(
        "/api/cart/items",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"productId": str(product.id), "quantity": 1},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "stock" in response.json()["detail"].lower()


def test_add_item_insufficient_stock(client, user_token, sample_products):
    """Test adding more items than available returns error."""
    product = sample_products[1]  # Product with 10 inventory

    response = client.post(
        "/api/cart/items",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"productId": str(product.id), "quantity": 15},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "insufficient stock" in response.json()["detail"].lower()


def test_add_inactive_product(client, user_token, sample_products):
    """Test adding inactive product returns error."""
    product = sample_products[3]  # Inactive product

    response = client.post(
        "/api/cart/items",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"productId": str(product.id), "quantity": 1},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "not available" in response.json()["detail"].lower()


def test_add_item_unauthorized(client, sample_products):
    """Test adding item without authentication fails."""
    product = sample_products[0]

    response = client.post(
        "/api/cart/items",
        json={"productId": str(product.id), "quantity": 1},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_cart_with_items(client, user_token, sample_products):
    """Test getting cart with items."""
    product1 = sample_products[0]
    product2 = sample_products[1]

    # Add two different items
    client.post(
        "/api/cart/items",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"productId": str(product1.id), "quantity": 2},
    )
    client.post(
        "/api/cart/items",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"productId": str(product2.id), "quantity": 1},
    )

    # Get cart
    response = client.get(
        "/api/cart",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert len(data["items"]) == 2
    assert data["totalItems"] == 3  # 2 + 1
    # Total amount should be (1000 * 2) + (2000 * 1) = 4000
    assert float(data["totalAmount"]) == 4000.00


def test_update_cart_item_quantity(client, user_token, sample_products):
    """Test updating cart item quantity."""
    product = sample_products[0]

    # Add item
    add_response = client.post(
        "/api/cart/items",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"productId": str(product.id), "quantity": 2},
    )
    cart_item_id = add_response.json()["id"]

    # Update quantity
    response = client.put(
        f"/api/cart/items/{cart_item_id}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"quantity": 5},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["quantity"] == 5
    assert float(data["subtotal"]) == 5000.00


def test_update_cart_item_insufficient_stock(client, user_token, sample_products):
    """Test updating quantity to more than available returns error."""
    product = sample_products[1]  # Product with 10 inventory

    # Add item
    add_response = client.post(
        "/api/cart/items",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"productId": str(product.id), "quantity": 2},
    )
    cart_item_id = add_response.json()["id"]

    # Try to update to quantity beyond stock
    response = client.put(
        f"/api/cart/items/{cart_item_id}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"quantity": 15},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "insufficient stock" in response.json()["detail"].lower()


def test_update_cart_item_not_found(client, user_token):
    """Test updating non-existent cart item returns 404."""
    from uuid import uuid4

    fake_id = uuid4()

    response = client.put(
        f"/api/cart/items/{fake_id}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"quantity": 5},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_cart_item_wrong_user(client, user_token, another_user_token, sample_products):
    """Test updating another user's cart item returns 404."""
    product = sample_products[0]

    # User 1 adds item
    add_response = client.post(
        "/api/cart/items",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"productId": str(product.id), "quantity": 2},
    )
    cart_item_id = add_response.json()["id"]

    # User 2 tries to update user 1's cart item
    response = client.put(
        f"/api/cart/items/{cart_item_id}",
        headers={"Authorization": f"Bearer {another_user_token}"},
        json={"quantity": 5},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_remove_cart_item(client, user_token, sample_products):
    """Test removing item from cart."""
    product = sample_products[0]

    # Add item
    add_response = client.post(
        "/api/cart/items",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"productId": str(product.id), "quantity": 2},
    )
    cart_item_id = add_response.json()["id"]

    # Remove item
    response = client.delete(
        f"/api/cart/items/{cart_item_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify cart is now empty
    cart_response = client.get(
        "/api/cart",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert len(cart_response.json()["items"]) == 0


def test_remove_cart_item_not_found(client, user_token):
    """Test removing non-existent cart item returns 404."""
    from uuid import uuid4

    fake_id = uuid4()

    response = client.delete(
        f"/api/cart/items/{fake_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_remove_cart_item_wrong_user(client, user_token, another_user_token, sample_products):
    """Test removing another user's cart item returns 404."""
    product = sample_products[0]

    # User 1 adds item
    add_response = client.post(
        "/api/cart/items",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"productId": str(product.id), "quantity": 2},
    )
    cart_item_id = add_response.json()["id"]

    # User 2 tries to remove user 1's cart item
    response = client.delete(
        f"/api/cart/items/{cart_item_id}",
        headers={"Authorization": f"Bearer {another_user_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_clear_cart(client, user_token, sample_products):
    """Test clearing entire cart."""
    product1 = sample_products[0]
    product2 = sample_products[1]

    # Add multiple items
    client.post(
        "/api/cart/items",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"productId": str(product1.id), "quantity": 2},
    )
    client.post(
        "/api/cart/items",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"productId": str(product2.id), "quantity": 1},
    )

    # Clear cart
    response = client.delete(
        "/api/cart",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify cart is empty
    cart_response = client.get(
        "/api/cart",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    data = cart_response.json()
    assert len(data["items"]) == 0
    assert data["totalItems"] == 0


def test_clear_cart_unauthorized(client):
    """Test clearing cart without authentication fails."""
    response = client.delete("/api/cart")

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_cart_availability_check(client, user_token, sample_products):
    """Test that cart response includes availability status."""
    product = sample_products[0]

    # Add item
    client.post(
        "/api/cart/items",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"productId": str(product.id), "quantity": 2},
    )

    # Get cart
    response = client.get(
        "/api/cart",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    data = response.json()
    assert len(data["items"]) == 1
    assert "isAvailable" in data["items"][0]
    assert data["items"][0]["isAvailable"] is True
    assert "hasUnavailableItems" in data
    assert data["hasUnavailableItems"] is False


def test_cart_computed_fields(client, user_token, sample_products):
    """Test that cart response includes computed fields."""
    product = sample_products[0]

    # Add item
    client.post(
        "/api/cart/items",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"productId": str(product.id), "quantity": 3},
    )

    # Get cart
    response = client.get(
        "/api/cart",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    data = response.json()
    item = data["items"][0]

    # Check item computed fields
    assert "unitPrice" in item
    assert "subtotal" in item
    assert "isAvailable" in item
    assert float(item["unitPrice"]) == 1000.00
    assert float(item["subtotal"]) == 3000.00

    # Check cart computed fields
    assert "totalItems" in data
    assert "totalAmount" in data
    assert "hasUnavailableItems" in data
    assert data["totalItems"] == 3
    assert float(data["totalAmount"]) == 3000.00


def test_variant_stock_validation(client, user_token, sample_products, sample_variants):
    """Test that variant stock is validated correctly."""
    product = sample_products[0]
    variant = sample_variants[1]  # Large variant with 5 stock

    # Try to add more than available variant stock
    response = client.post(
        "/api/cart/items",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "productId": str(product.id),
            "productVariantId": str(variant.id),
            "quantity": 10,
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "insufficient stock" in response.json()["detail"].lower()
    assert "5 available" in response.json()["detail"].lower()


def test_add_zero_quantity(client, user_token, sample_products):
    """Test that adding zero quantity is rejected."""
    product = sample_products[0]

    response = client.post(
        "/api/cart/items",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"productId": str(product.id), "quantity": 0},
    )

    # Should return validation error
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_zero_quantity(client, user_token, sample_products):
    """Test that updating to zero quantity is rejected."""
    product = sample_products[0]

    # Add item
    add_response = client.post(
        "/api/cart/items",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"productId": str(product.id), "quantity": 2},
    )
    cart_item_id = add_response.json()["id"]

    # Try to update to zero
    response = client.put(
        f"/api/cart/items/{cart_item_id}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"quantity": 0},
    )

    # Should return validation error
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
