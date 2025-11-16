"""
Tests for pytest fixtures to ensure they work correctly.
"""
import pytest
from decimal import Decimal
from datetime import date, time

from app.models import (
    User,
    Brand,
    Category,
    Product,
    ServicePackage,
    TransportLocation,
    Booking,
    PromoCode,
    Order,
    Cart,
    Review,
    Testimonial,
)


@pytest.mark.fixture
@pytest.mark.unit
class TestUserFixtures:
    """Test user-related fixtures."""

    def test_create_user_fixture(self, create_user):
        """Test creating a user with the factory fixture."""
        user = create_user(email="test@example.com")
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.is_admin is False

    def test_user_fixture(self, user):
        """Test the default user fixture."""
        assert user.id is not None
        assert user.email is not None
        assert user.google_id is not None

    def test_admin_user_fixture(self, admin_user):
        """Test the admin user fixture."""
        assert admin_user.id is not None
        assert admin_user.is_admin is True
        assert admin_user.admin_role == "super_admin"

    def test_create_guest_user(self, create_user):
        """Test creating a guest user."""
        guest = create_user(is_guest=True, google_id=None)
        assert guest.google_id is None
        assert guest.email is not None


@pytest.mark.fixture
@pytest.mark.unit
class TestProductFixtures:
    """Test product-related fixtures."""

    def test_create_brand_fixture(self, create_brand):
        """Test creating a brand."""
        brand = create_brand(name="Test Brand")
        assert brand.id is not None
        assert brand.name == "Test Brand"
        assert brand.slug == "test-brand"

    def test_brand_fixture(self, brand):
        """Test the default brand fixture."""
        assert brand.id is not None
        assert brand.name is not None

    def test_create_category_fixture(self, create_category):
        """Test creating a category."""
        category = create_category(name="Skincare")
        assert category.id is not None
        assert category.name == "Skincare"
        assert category.parent_category_id is None

    def test_category_hierarchy(self, create_category):
        """Test creating parent and child categories."""
        parent = create_category(name="Beauty")
        child = create_category(name="Makeup", parent_id=parent.id)
        assert child.parent_category_id == parent.id

    def test_product_fixture(self, product, brand, category):
        """Test the product fixture with brand and category."""
        assert product.id is not None
        assert product.brand_id == brand.id
        assert product.category_id == category.id
        assert isinstance(product.base_price, Decimal)

    def test_create_product_with_custom_price(self, create_product, brand):
        """Test creating a product with custom price."""
        product = create_product(
            brand=brand,
            title="Custom Product",
            base_price="9999.99"
        )
        assert product.base_price == Decimal("9999.99")
        assert product.title == "Custom Product"


@pytest.mark.fixture
@pytest.mark.unit
class TestServiceFixtures:
    """Test service-related fixtures."""

    def test_service_package_fixture(self, service_package):
        """Test the service package fixture."""
        assert service_package.id is not None
        assert service_package.package_type == "regular"
        assert isinstance(service_package.base_bride_price, Decimal)

    def test_create_bridal_package(self, create_service_package):
        """Test creating a bridal service package."""
        package = create_service_package(
            package_type="bridal_large",
            name="Large Bridal Team",
            base_bride_price="3500"
        )
        assert package.package_type == "bridal_large"
        assert package.base_bride_price == Decimal("3500")

    def test_transport_location_fixture(self, transport_location):
        """Test the transport location fixture."""
        assert transport_location.id is not None
        assert transport_location.location_name is not None
        assert isinstance(transport_location.transport_cost, Decimal)

    def test_create_free_location(self, create_transport_location):
        """Test creating a free transport location."""
        location = create_transport_location(
            location_name="Nairobi",
            is_free=True,
            transport_cost="0"
        )
        assert location.is_free is True
        assert location.transport_cost == Decimal("0")


@pytest.mark.fixture
@pytest.mark.unit
class TestBookingFixtures:
    """Test booking-related fixtures."""

    def test_booking_fixture(self, booking, user, service_package, transport_location):
        """Test the booking fixture."""
        assert booking.id is not None
        assert booking.user_id == user.id
        assert booking.package_id == service_package.id
        assert booking.location_id == transport_location.id
        assert booking.booking_number.startswith("BK-2025-")

    def test_booking_deposit_calculation(self, create_booking, user, service_package, transport_location):
        """Test booking deposit is correctly calculated as 50%."""
        booking = create_booking(
            user=user,
            package=service_package,
            location=transport_location,
            total_amount="1000"
        )
        assert booking.deposit_amount == Decimal("500")

    def test_guest_booking(self, create_booking, service_package, transport_location):
        """Test creating a booking for a guest (no user)."""
        booking = create_booking(
            package=service_package,
            location=transport_location,
            guest_email="guest@example.com",
            guest_name="Guest User",
            guest_phone="123456789"
        )
        assert booking.user_id is None
        assert booking.guest_email == "guest@example.com"


@pytest.mark.fixture
@pytest.mark.unit
class TestOrderFixtures:
    """Test order-related fixtures."""

    def test_promo_code_fixture(self, promo_code):
        """Test the promo code fixture."""
        assert promo_code.id is not None
        assert promo_code.code is not None
        assert promo_code.discount_type in ["percentage", "fixed"]

    def test_create_percentage_promo(self, create_promo_code):
        """Test creating a percentage discount promo code."""
        promo = create_promo_code(
            code="SAVE20",
            discount_type="percentage",
            discount_value="20"
        )
        assert promo.code == "SAVE20"
        assert promo.discount_value == Decimal("20")

    def test_order_fixture(self, order, user):
        """Test the order fixture."""
        assert order.id is not None
        assert order.user_id == user.id
        assert order.order_number.startswith("ORD-2025-")
        assert isinstance(order.total_amount, Decimal)

    def test_guest_order(self, create_order):
        """Test creating an order for a guest."""
        order = create_order(
            guest_email="guest@example.com",
            guest_name="Guest User",
            guest_phone="123456789"
        )
        assert order.user_id is None
        assert order.guest_email == "guest@example.com"

    def test_cart_fixture(self, cart, user):
        """Test the cart fixture."""
        assert cart.id is not None
        assert cart.user_id == user.id


@pytest.mark.fixture
@pytest.mark.unit
class TestContentFixtures:
    """Test content-related fixtures."""

    def test_review_fixture(self, review, product, user):
        """Test the review fixture."""
        assert review.id is not None
        assert review.product_id == product.id
        assert review.user_id == user.id
        assert 1 <= review.rating <= 5

    def test_create_review_with_custom_rating(self, create_review, product, user):
        """Test creating a review with custom rating."""
        review = create_review(
            product=product,
            user=user,
            rating=5,
            review_text="Excellent product!"
        )
        assert review.rating == 5
        assert review.review_text == "Excellent product!"

    def test_testimonial_fixture(self, testimonial):
        """Test the testimonial fixture."""
        assert testimonial.id is not None
        assert testimonial.customer_name is not None
        assert testimonial.rating == 5
        assert testimonial.is_approved is True


@pytest.mark.fixture
@pytest.mark.unit
class TestUtilityFixtures:
    """Test utility fixtures."""

    def test_faker_fixture(self, faker):
        """Test the Faker fixture."""
        email = faker.email()
        assert "@" in email

        name = faker.name()
        assert len(name) > 0

    def test_sample_uuid_fixture(self, sample_uuid):
        """Test the sample UUID fixture."""
        assert sample_uuid is not None
        assert len(str(sample_uuid)) == 36

    def test_sample_date_fixture(self, sample_date):
        """Test the sample date fixture."""
        assert isinstance(sample_date, date)

    def test_sample_datetime_fixture(self, sample_datetime):
        """Test the sample datetime fixture."""
        assert sample_datetime is not None
