"""Tests for admin analytics API."""
from decimal import Decimal
from datetime import datetime, timedelta

import pytest
from fastapi import status

from app.models.booking import Booking
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.service import ServicePackage, TransportLocation
from app.models.user import User


@pytest.fixture
def admin_user(db_session):
    """Create an admin user for testing."""
    user = User(
        email="admin@example.com",
        google_id="admin123",
        full_name="Admin User",
        is_admin=True,
        admin_role="super_admin",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_token(admin_user):
    """Create JWT token for admin user."""
    from app.core.security import create_access_token
    return create_access_token(data={"sub": str(admin_user.id), "email": admin_user.email})


@pytest.fixture
def regular_user(db_session):
    """Create a regular (non-admin) user for testing."""
    user = User(
        email="user@example.com",
        google_id="user123",
        full_name="Regular User",
        is_admin=False,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def regular_token(regular_user):
    """Create JWT token for regular user."""
    from app.core.security import create_access_token
    return create_access_token(data={"sub": str(regular_user.id), "email": regular_user.email})


@pytest.fixture
def sample_product(db_session):
    """Create a sample product."""
    product = Product(
        title="Test Lipstick",
        slug="test-lipstick",
        description="Test product",
        base_price=Decimal("1500.00"),
        inventory_count=100,
        is_active=True,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


@pytest.fixture
def sample_service(db_session):
    """Create a sample service package."""
    service = ServicePackage(
        package_type="bridal_large",
        name="Bridal Makeup",
        description="Complete bridal makeup",
        base_bride_price=Decimal("5000.00"),
        base_maid_price=Decimal("3000.00"),
        duration_minutes=120,
        is_active=True,
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)
    return service


@pytest.fixture
def sample_location(db_session):
    """Create a sample transport location."""
    location = TransportLocation(
        location_name="Nairobi CBD",
        transport_cost=Decimal("500.00"),
        is_active=True,
    )
    db_session.add(location)
    db_session.commit()
    db_session.refresh(location)
    return location


@pytest.fixture
def sample_orders(db_session, regular_user, sample_product):
    """Create sample orders for testing."""
    orders = []

    # Create an order from 2 days ago
    order1 = Order(
        order_number="ORD-TEST-001",
        user_id=regular_user.id,
        subtotal=Decimal("3000.00"),
        total_amount=Decimal("3000.00"),
        status="delivered",
        payment_confirmed=True,
        created_at=datetime.utcnow() - timedelta(days=2),
    )
    db_session.add(order1)
    db_session.flush()

    order_item1 = OrderItem(
        order_id=order1.id,
        product_id=sample_product.id,
        product_title=sample_product.title,
        quantity=2,
        unit_price=Decimal("1500.00"),
        total_price=Decimal("3000.00"),
    )
    db_session.add(order_item1)
    orders.append(order1)

    # Create an order from today
    order2 = Order(
        order_number="ORD-TEST-002",
        user_id=regular_user.id,
        subtotal=Decimal("1500.00"),
        total_amount=Decimal("1500.00"),
        status="delivered",
        payment_confirmed=True,
        created_at=datetime.utcnow(),
    )
    db_session.add(order2)
    db_session.flush()

    order_item2 = OrderItem(
        order_id=order2.id,
        product_id=sample_product.id,
        product_title=sample_product.title,
        quantity=1,
        unit_price=Decimal("1500.00"),
        total_price=Decimal("1500.00"),
    )
    db_session.add(order_item2)
    orders.append(order2)

    db_session.commit()
    return orders


@pytest.fixture
def sample_bookings(db_session, regular_user, sample_service, sample_location):
    """Create sample bookings for testing."""
    from datetime import date, time

    bookings = []

    # Create a confirmed booking from 3 days ago
    booking_date1 = date.today() + timedelta(days=7)
    booking1 = Booking(
        booking_number="BK-TEST-001",
        user_id=regular_user.id,
        package_id=sample_service.id,
        booking_date=booking_date1,
        booking_time=time(10, 0),
        location_id=sample_location.id,
        subtotal=Decimal("5000.00"),
        transport_cost=Decimal("500.00"),
        total_amount=Decimal("5500.00"),
        status="confirmed",
        created_at=datetime.utcnow() - timedelta(days=3),
    )
    db_session.add(booking1)
    bookings.append(booking1)

    # Create a pending booking from today
    booking_date2 = date.today() + timedelta(days=10)
    booking2 = Booking(
        booking_number="BK-TEST-002",
        user_id=regular_user.id,
        package_id=sample_service.id,
        booking_date=booking_date2,
        booking_time=time(14, 0),
        location_id=sample_location.id,
        subtotal=Decimal("5000.00"),
        transport_cost=Decimal("500.00"),
        total_amount=Decimal("5500.00"),
        status="pending",
        created_at=datetime.utcnow(),
    )
    db_session.add(booking2)
    bookings.append(booking2)

    db_session.commit()
    return bookings


def test_get_overview_analytics_success(client, admin_token, sample_orders, sample_bookings):
    """Test getting overview analytics with admin token."""
    response = client.get(
        "/api/admin/analytics/overview",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "totalRevenue" in data
    assert "totalOrders" in data
    assert "totalBookings" in data
    assert "totalProducts" in data
    assert "totalCustomers" in data
    assert "pendingOrders" in data
    assert "pendingBookings" in data

    # Check that we have the orders and bookings we created
    assert data["totalOrders"] == 2
    assert data["totalBookings"] == 2


def test_get_overview_analytics_unauthorized(client, regular_token):
    """Test that regular users cannot access analytics."""
    response = client.get(
        "/api/admin/analytics/overview",
        headers={"Authorization": f"Bearer {regular_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_overview_analytics_no_auth(client):
    """Test that unauthenticated requests are rejected."""
    response = client.get("/api/admin/analytics/overview")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_sales_analytics_success(client, admin_token, sample_orders):
    """Test getting sales analytics with admin token."""
    response = client.get(
        "/api/admin/analytics/sales",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "totalRevenue" in data
    assert "totalOrders" in data
    assert "averageOrderValue" in data
    assert "dataPoints" in data
    assert isinstance(data["dataPoints"], list)

    # Check totals
    assert data["totalOrders"] == 2
    assert float(data["totalRevenue"]) == 4500.00


def test_get_sales_analytics_with_date_range(client, admin_token, sample_orders):
    """Test getting sales analytics with custom date range."""
    start_date = (datetime.utcnow() - timedelta(days=1)).isoformat()
    end_date = datetime.utcnow().isoformat()

    response = client.get(
        f"/api/admin/analytics/sales?startDate={start_date}&endDate={end_date}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Should only include order from today
    assert data["totalOrders"] == 1
    assert float(data["totalRevenue"]) == 1500.00


def test_get_product_analytics_success(client, admin_token, sample_orders, sample_product):
    """Test getting product analytics with admin token."""
    response = client.get(
        "/api/admin/analytics/products",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "topProducts" in data
    assert "totalProducts" in data
    assert "lowStockCount" in data
    assert isinstance(data["topProducts"], list)

    # Check that our product appears in top products
    if len(data["topProducts"]) > 0:
        top_product = data["topProducts"][0]
        assert "productId" in top_product
        assert "productName" in top_product
        assert "totalSold" in top_product
        assert "totalRevenue" in top_product
        assert top_product["totalSold"] == 3  # 2 + 1 from sample orders


def test_get_booking_analytics_success(client, admin_token, sample_bookings, sample_service):
    """Test getting booking analytics with admin token."""
    response = client.get(
        "/api/admin/analytics/bookings",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "totalBookings" in data
    assert "totalRevenue" in data
    assert "pendingBookings" in data
    assert "confirmedBookings" in data
    assert "completedBookings" in data
    assert "cancelledBookings" in data
    assert "dataPoints" in data
    assert "topServices" in data

    # Check booking counts
    assert data["totalBookings"] == 2
    assert data["pendingBookings"] == 1
    assert data["confirmedBookings"] == 1

    # Check top services
    if len(data["topServices"]) > 0:
        top_service = data["topServices"][0]
        assert "serviceId" in top_service
        assert "serviceName" in top_service
        assert "totalBookings" in top_service
        assert top_service["totalBookings"] == 2


def test_get_booking_analytics_with_interval(client, admin_token, sample_bookings):
    """Test getting booking analytics with different intervals."""
    response = client.get(
        "/api/admin/analytics/bookings?interval=week",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "dataPoints" in data
    # Week interval not implemented yet, but endpoint should still work
