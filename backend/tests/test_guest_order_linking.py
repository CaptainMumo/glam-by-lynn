"""
Tests for guest order and booking linking functionality
"""
import pytest
from app.models.user import User
from app.models.booking import Booking
from app.models.order import Order, OrderItem
from app.models.service import ServicePackage, TransportLocation
from app.models.product import Product, Brand, Category
from app.services.user_service import link_guest_data_to_user, get_or_create_user_from_oauth
from datetime import date, time
from decimal import Decimal


@pytest.fixture
def service_package(db_session):
    """Create a service package for testing"""
    package = ServicePackage(
        name="Bridal Package",
        package_type="bridal_large",  # Valid type: 'bridal_large', 'bridal_small', 'bride_only', 'regular', 'classes'
        base_bride_price=Decimal("15000.00"),
        is_active=True
    )
    db_session.add(package)
    db_session.commit()
    db_session.refresh(package)
    return package


@pytest.fixture
def transport_location(db_session):
    """Create a transport location for testing"""
    location = TransportLocation(
        location_name="Nairobi CBD",
        county="Nairobi",
        transport_cost=Decimal("1000.00"),
        is_active=True
    )
    db_session.add(location)
    db_session.commit()
    db_session.refresh(location)
    return location


@pytest.fixture
def brand_and_category(db_session):
    """Create brand and category for testing"""
    brand = Brand(
        name="Test Brand",
        slug="test-brand",
        is_active=True
    )
    category = Category(
        name="Makeup",
        slug="makeup",
        is_active=True
    )
    db_session.add(brand)
    db_session.add(category)
    db_session.commit()
    db_session.refresh(brand)
    db_session.refresh(category)
    return brand, category


@pytest.fixture
def product(db_session, brand_and_category):
    """Create a product for testing"""
    brand, category = brand_and_category
    product = Product(
        title="Test Lipstick",  # Product uses 'title', not 'name'
        slug="test-lipstick",
        brand_id=brand.id,
        category_id=category.id,
        base_price=Decimal("500.00"),  # Product uses 'base_price', not 'price'
        inventory_count=100,  # Product uses 'inventory_count', not 'stock_quantity'
        is_active=True
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


def test_link_guest_bookings_to_user(db_session, service_package, transport_location):
    """Test that guest bookings are linked to user account on registration"""
    guest_email = "guest@example.com"

    # Create a guest booking
    booking = Booking(
        booking_number="BK202501180001",
        guest_email=guest_email,
        guest_name="Guest User",
        guest_phone="+254712345678",
        package_id=service_package.id,
        location_id=transport_location.id,
        booking_date=date(2025, 6, 1),
        booking_time=time(10, 0),
        num_brides=1,
        num_maids=2,
        num_mothers=0,
        num_others=0,
        subtotal=Decimal("20000.00"),
        transport_cost=Decimal("1000.00"),
        total_amount=Decimal("21000.00"),
        deposit_amount=Decimal("10500.00"),
        status="pending"
    )
    db_session.add(booking)
    db_session.commit()

    # Create a registered user
    user = User(
        email=guest_email,
        google_id="google123",
        full_name="Registered User",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Link guest data to user
    link_stats = link_guest_data_to_user(db_session, user.id, guest_email)

    # Verify booking was linked
    assert link_stats["bookings_linked"] == 1

    # Refresh booking and check it's now linked to user
    db_session.refresh(booking)
    assert booking.user_id == user.id
    assert booking.guest_email == guest_email  # Guest info preserved


def test_link_guest_orders_to_user(db_session, product):
    """Test that guest orders are linked to user account on registration"""
    guest_email = "guest@example.com"

    # Create a guest order
    order = Order(
        order_number="ORD202501180001",
        guest_email=guest_email,
        guest_name="Guest User",
        guest_phone="+254712345678",
        subtotal=Decimal("500.00"),
        delivery_fee=Decimal("200.00"),
        total_amount=Decimal("700.00"),
        payment_method="mpesa",
        payment_confirmed=False,
        status="pending"
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)

    # Add order item (with product_title as snapshot)
    order_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        product_title=product.title,  # Snapshot of product title at purchase time
        quantity=1,
        unit_price=Decimal("500.00"),
        total_price=Decimal("500.00")
    )
    db_session.add(order_item)
    db_session.commit()

    # Create a registered user
    user = User(
        email=guest_email,
        google_id="google123",
        full_name="Registered User",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Link guest data to user
    link_stats = link_guest_data_to_user(db_session, user.id, guest_email)

    # Verify order was linked
    assert link_stats["orders_linked"] == 1

    # Refresh order and check it's now linked to user
    db_session.refresh(order)
    assert order.user_id == user.id
    assert order.guest_email == guest_email  # Guest info preserved


def test_link_multiple_guest_data(db_session, service_package, transport_location, product):
    """Test linking multiple guest orders and bookings at once"""
    guest_email = "guest@example.com"

    # Create 2 guest bookings
    for i in range(2):
        booking = Booking(
            booking_number=f"BK2025011800{i+1}",
            guest_email=guest_email,
            guest_name="Guest User",
            guest_phone="+254712345678",
            package_id=service_package.id,
            location_id=transport_location.id,
            booking_date=date(2025, 6, i+1),
            booking_time=time(10, 0),
            num_brides=1,
            num_maids=0,
            num_mothers=0,
            num_others=0,
            subtotal=Decimal("15000.00"),
            transport_cost=Decimal("1000.00"),
            total_amount=Decimal("16000.00"),
            deposit_amount=Decimal("8000.00"),
            status="pending"
        )
        db_session.add(booking)

    # Create 3 guest orders
    for i in range(3):
        order = Order(
            order_number=f"ORD2025011800{i+1}",
            guest_email=guest_email,
            guest_name="Guest User",
            guest_phone="+254712345678",
            subtotal=Decimal("500.00"),
            delivery_fee=Decimal("200.00"),
            total_amount=Decimal("700.00"),
            payment_method="mpesa",
            payment_confirmed=False,
            status="pending"
        )
        db_session.add(order)

    db_session.commit()

    # Create a registered user
    user = User(
        email=guest_email,
        google_id="google123",
        full_name="Registered User",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Link all guest data
    link_stats = link_guest_data_to_user(db_session, user.id, guest_email)

    # Verify all were linked
    assert link_stats["orders_linked"] == 3
    assert link_stats["bookings_linked"] == 2


def test_no_linking_for_different_email(db_session, service_package, transport_location):
    """Test that guest data with different email is NOT linked"""
    guest_email = "guest@example.com"
    user_email = "different@example.com"

    # Create guest booking with one email
    booking = Booking(
        booking_number="BK202501180001",
        guest_email=guest_email,
        guest_name="Guest User",
        guest_phone="+254712345678",
        package_id=service_package.id,
        location_id=transport_location.id,
        booking_date=date(2025, 6, 1),
        booking_time=time(10, 0),
        num_brides=1,
        num_maids=0,
        num_mothers=0,
        num_others=0,
        subtotal=Decimal("15000.00"),
        transport_cost=Decimal("1000.00"),
        total_amount=Decimal("16000.00"),
        deposit_amount=Decimal("8000.00"),
        status="pending"
    )
    db_session.add(booking)
    db_session.commit()

    # Create user with different email
    user = User(
        email=user_email,
        google_id="google123",
        full_name="Different User",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Attempt to link (should not link any data)
    link_stats = link_guest_data_to_user(db_session, user.id, user_email)

    # Verify nothing was linked
    assert link_stats["orders_linked"] == 0
    assert link_stats["bookings_linked"] == 0

    # Verify booking is still a guest booking
    db_session.refresh(booking)
    assert booking.user_id is None


def test_oauth_login_triggers_linking(db_session, service_package, transport_location):
    """Test that OAuth login automatically triggers guest data linking"""
    guest_email = "newuser@example.com"

    # Create guest booking BEFORE user registers
    booking = Booking(
        booking_number="BK202501180001",
        guest_email=guest_email,
        guest_name="Future User",
        guest_phone="+254712345678",
        package_id=service_package.id,
        location_id=transport_location.id,
        booking_date=date(2025, 6, 1),
        booking_time=time(10, 0),
        num_brides=1,
        num_maids=0,
        num_mothers=0,
        num_others=0,
        subtotal=Decimal("15000.00"),
        transport_cost=Decimal("1000.00"),
        total_amount=Decimal("16000.00"),
        deposit_amount=Decimal("8000.00"),
        status="pending"
    )
    db_session.add(booking)
    db_session.commit()

    # User signs in with Google OAuth for the first time
    user, created, link_stats = get_or_create_user_from_oauth(
        db=db_session,
        email=guest_email,
        google_id="newgoogle123",
        name="Future User",
        image="https://example.com/photo.jpg"
    )

    # Verify user was created
    assert created is True
    assert user.email == guest_email

    # Verify guest booking was automatically linked
    assert link_stats["bookings_linked"] == 1

    # Verify booking now belongs to user
    db_session.refresh(booking)
    assert booking.user_id == user.id


def test_existing_user_orders_not_affected(db_session, regular_user, product):
    """Test that existing user orders are not affected by linking"""
    guest_email = "other_guest@example.com"

    # Create an order for regular_user
    existing_order = Order(
        order_number="ORD202501180001",
        user_id=regular_user.id,
        subtotal=Decimal("1000.00"),
        delivery_fee=Decimal("200.00"),
        total_amount=Decimal("1200.00"),
        payment_method="mpesa",
        payment_confirmed=True,
        status="shipped"
    )
    db_session.add(existing_order)
    db_session.commit()
    db_session.refresh(existing_order)

    # Try to link guest data (should have no effect)
    link_stats = link_guest_data_to_user(db_session, regular_user.id, guest_email)

    # Verify nothing was linked
    assert link_stats["orders_linked"] == 0

    # Verify existing order unchanged
    db_session.refresh(existing_order)
    assert existing_order.user_id == regular_user.id
    assert existing_order.payment_confirmed == True
