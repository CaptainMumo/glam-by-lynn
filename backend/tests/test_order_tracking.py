"""Tests for order tracking API."""
from decimal import Decimal
from datetime import datetime

import pytest
from fastapi import status

from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.user import User


@pytest.fixture
def regular_user(db_session):
    """Create a regular user for testing."""
    user = User(
        email="user@example.com",
        google_id="user123",
        full_name="Test User",
        is_admin=False,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def other_user(db_session):
    """Create another user for testing."""
    user = User(
        email="other@example.com",
        google_id="other123",
        full_name="Other User",
        is_admin=False,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user_token(regular_user):
    """Create JWT token for regular user."""
    from app.core.security import create_access_token

    return create_access_token(data={"sub": str(regular_user.id), "email": regular_user.email})


@pytest.fixture
def other_token(other_user):
    """Create JWT token for other user."""
    from app.core.security import create_access_token

    return create_access_token(data={"sub": str(other_user.id), "email": other_user.email})


@pytest.fixture
def sample_product(db_session):
    """Create a sample product."""
    product = Product(
        title="Test Product",
        slug="test-product",
        description="Test product description",
        base_price=Decimal("1000.00"),
        inventory_count=100,
        is_active=True,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


@pytest.fixture
def user_order(db_session, regular_user, sample_product):
    """Create an order for an authenticated user."""
    order = Order(
        order_number="ORD-20250119-ABC12",
        user_id=regular_user.id,
        delivery_county="Nairobi",
        delivery_town="Nairobi",
        delivery_address="123 Test Street",
        subtotal=Decimal("2000.00"),
        discount_amount=Decimal("0.00"),
        delivery_fee=Decimal("200.00"),
        total_amount=Decimal("2200.00"),
        payment_method="mpesa",
        payment_confirmed=True,
        status="processing",
    )
    db_session.add(order)
    db_session.flush()

    order_item = OrderItem(
        order_id=order.id,
        product_id=sample_product.id,
        product_title=sample_product.title,
        product_sku="TEST-SKU",
        quantity=2,
        unit_price=Decimal("1000.00"),
        discount=Decimal("0.00"),
        total_price=Decimal("2000.00"),
    )
    db_session.add(order_item)
    db_session.commit()
    db_session.refresh(order)
    return order


@pytest.fixture
def guest_order(db_session, sample_product):
    """Create a guest order."""
    order = Order(
        order_number="ORD-20250119-XYZ99",
        guest_email="guest@example.com",
        guest_name="Guest User",
        guest_phone="+254712345678",
        delivery_county="Kitui",
        delivery_town="Kitui Town",
        delivery_address="456 Guest Avenue",
        subtotal=Decimal("1000.00"),
        discount_amount=Decimal("0.00"),
        delivery_fee=Decimal("200.00"),
        total_amount=Decimal("1200.00"),
        payment_method="bank_transfer",
        payment_confirmed=False,
        status="pending",
    )
    db_session.add(order)
    db_session.flush()

    order_item = OrderItem(
        order_id=order.id,
        product_id=sample_product.id,
        product_title=sample_product.title,
        product_sku="TEST-SKU",
        quantity=1,
        unit_price=Decimal("1000.00"),
        discount=Decimal("0.00"),
        total_price=Decimal("1000.00"),
    )
    db_session.add(order_item)
    db_session.commit()
    db_session.refresh(order)
    return order


def test_get_user_orders_success(client, user_token, user_order):
    """Test getting user's orders with authentication."""
    response = client.get(
        "/api/orders",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "orders" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data

    assert data["total"] == 1
    assert len(data["orders"]) == 1
    assert data["orders"][0]["orderNumber"] == user_order.order_number


def test_get_user_orders_unauthorized(client):
    """Test that unauthenticated requests are rejected."""
    response = client.get("/api/orders")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_user_orders_pagination(client, user_token, user_order):
    """Test pagination parameters."""
    response = client.get(
        "/api/orders?skip=0&limit=10",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["skip"] == 0
    assert data["limit"] == 10


def test_get_order_by_id_success(client, user_token, user_order):
    """Test getting specific order by ID."""
    response = client.get(
        f"/api/orders/{user_order.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["id"] == str(user_order.id)
    assert data["orderNumber"] == user_order.order_number
    assert data["status"] == user_order.status
    assert float(data["totalAmount"]) == float(user_order.total_amount)


def test_get_order_by_id_not_found(client, user_token):
    """Test getting non-existent order."""
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    response = client.get(
        f"/api/orders/{fake_uuid}",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_order_by_id_forbidden(client, other_token, user_order):
    """Test that users cannot access other users' orders."""
    response = client.get(
        f"/api/orders/{user_order.id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_track_order_authenticated_user(client, user_token, user_order):
    """Test tracking order by number with authenticated user."""
    response = client.get(
        f"/api/orders/track/{user_order.order_number}",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["orderNumber"] == user_order.order_number
    assert data["status"] == user_order.status


def test_track_order_guest_with_email(client, guest_order):
    """Test tracking guest order with correct email."""
    response = client.get(
        f"/api/orders/track/{guest_order.order_number}?email={guest_order.guest_email}"
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["orderNumber"] == guest_order.order_number
    assert data["guestEmail"] == guest_order.guest_email


def test_track_order_guest_wrong_email(client, guest_order):
    """Test tracking guest order with wrong email."""
    response = client.get(
        f"/api/orders/track/{guest_order.order_number}?email=wrong@example.com"
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_track_order_guest_no_email(client, guest_order):
    """Test tracking guest order without email parameter."""
    response = client.get(f"/api/orders/track/{guest_order.order_number}")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Email required" in response.json()["detail"]


def test_track_order_not_found(client):
    """Test tracking non-existent order."""
    response = client.get("/api/orders/track/ORD-20250119-FAKE1")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_track_order_case_insensitive_email(client, guest_order):
    """Test that email verification is case-insensitive."""
    # Guest order has email "guest@example.com"
    response = client.get(
        f"/api/orders/track/{guest_order.order_number}?email=GUEST@EXAMPLE.COM"
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["orderNumber"] == guest_order.order_number


def test_track_order_authenticated_user_cannot_access_other_user_order(
    client, other_token, user_order
):
    """Test that authenticated users cannot track other users' orders."""
    response = client.get(
        f"/api/orders/track/{user_order.order_number}",
        headers={"Authorization": f"Bearer {other_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
