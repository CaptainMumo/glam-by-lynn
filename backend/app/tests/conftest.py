"""
Pytest configuration and comprehensive fixtures for all models
"""
import pytest
from datetime import datetime, date, time, timedelta
from decimal import Decimal
from typing import Generator
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from faker import Faker

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings
from app.models import (
    User,
    Brand,
    Category,
    Product,
    ProductImage,
    ProductVideo,
    ProductVariant,
    ServicePackage,
    TransportLocation,
    CalendarAvailability,
    Booking,
    PromoCode,
    Order,
    OrderItem,
    Cart,
    CartItem,
    Wishlist,
    Review,
    GalleryPost,
    Testimonial,
    VisionRegistration,
    AdminActivityLog,
)

# Test database URL
# Note: Use PostgreSQL for full feature compatibility (ARRAY, JSONB, UUID)
# SQLite does not support ARRAY, JSONB columns used in the schema
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create test session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize Faker
fake = Faker()


# ============================================================================
# Base Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """
    Create a fresh database for each test.

    Note: This uses SQLite by default for speed. For full feature testing
    with ARRAY, JSONB, and UUID columns, configure PostgreSQL test database.
    """
    Base.metadata.create_all(bind=engine)
    db_session = TestingSessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """
    Create a test client with database dependency override.
    """
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def faker() -> Faker:
    """
    Provide Faker instance for generating test data.
    """
    return fake


# ============================================================================
# User Fixtures
# ============================================================================

@pytest.fixture
def create_user(db: Session, faker: Faker):
    """Factory fixture to create users."""
    def _create_user(
        email: str = None,
        google_id: str = None,
        is_admin: bool = False,
        admin_role: str = None,
        **kwargs
    ) -> User:
        user = User(
            email=email or faker.email(),
            full_name=kwargs.get("full_name", faker.name()),
            phone_number=kwargs.get("phone_number", faker.phone_number()),
            google_id=google_id or (faker.uuid4() if not kwargs.get("is_guest") else None),
            is_admin=is_admin,
            admin_role=admin_role if is_admin else None,
            is_active=kwargs.get("is_active", True),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    return _create_user


@pytest.fixture
def user(create_user) -> User:
    """Create a regular user."""
    return create_user()


@pytest.fixture
def admin_user(create_user) -> User:
    """Create an admin user."""
    return create_user(
        email="admin@glamlynn.com",
        is_admin=True,
        admin_role="super_admin"
    )


# ============================================================================
# Product Fixtures
# ============================================================================

@pytest.fixture
def create_brand(db: Session, faker: Faker):
    """Factory fixture to create brands."""
    def _create_brand(name: str = None, **kwargs) -> Brand:
        brand_name = name or faker.company()
        brand = Brand(
            name=brand_name,
            slug=kwargs.get("slug", brand_name.lower().replace(" ", "-")),
            description=kwargs.get("description", faker.text()),
            logo_url=kwargs.get("logo_url", faker.image_url()),
            is_active=kwargs.get("is_active", True),
        )
        db.add(brand)
        db.commit()
        db.refresh(brand)
        return brand
    return _create_brand


@pytest.fixture
def brand(create_brand) -> Brand:
    """Create a brand."""
    return create_brand()


@pytest.fixture
def create_category(db: Session, faker: Faker):
    """Factory fixture to create categories."""
    def _create_category(name: str = None, parent_id=None, **kwargs) -> Category:
        cat_name = name or faker.word().capitalize()
        category = Category(
            name=cat_name,
            slug=kwargs.get("slug", cat_name.lower()),
            parent_category_id=parent_id,
            description=kwargs.get("description", faker.sentence()),
            display_order=kwargs.get("display_order", 0),
            is_active=kwargs.get("is_active", True),
        )
        db.add(category)
        db.commit()
        db.refresh(category)
        return category
    return _create_category


@pytest.fixture
def category(create_category) -> Category:
    """Create a category."""
    return create_category()


@pytest.fixture
def create_product(db: Session, faker: Faker):
    """Factory fixture to create products."""
    def _create_product(brand: Brand = None, category: Category = None, **kwargs) -> Product:
        title = kwargs.get("title", faker.catch_phrase())
        product = Product(
            title=title,
            slug=kwargs.get("slug", title.lower().replace(" ", "-")),
            description=kwargs.get("description", faker.text()),
            brand_id=brand.id if brand else None,
            category_id=category.id if category else None,
            base_price=Decimal(kwargs.get("base_price", str(faker.random_int(100, 10000)))),
            sku=kwargs.get("sku", faker.ean13()),
            inventory_count=kwargs.get("inventory_count", faker.random_int(0, 100)),
            low_stock_threshold=kwargs.get("low_stock_threshold", 10),
            is_active=kwargs.get("is_active", True),
            is_featured=kwargs.get("is_featured", False),
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
    return _create_product


@pytest.fixture
def product(create_product, brand, category) -> Product:
    """Create a product with brand and category."""
    return create_product(brand=brand, category=category)


# ============================================================================
# Service Fixtures
# ============================================================================

@pytest.fixture
def create_service_package(db: Session, faker: Faker):
    """Factory fixture to create service packages."""
    def _create_service_package(package_type: str = "regular", **kwargs) -> ServicePackage:
        package = ServicePackage(
            package_type=package_type,
            name=kwargs.get("name", f"{package_type.replace('_', ' ').title()} Package"),
            description=kwargs.get("description", faker.text()),
            base_bride_price=Decimal(kwargs.get("base_bride_price", "2500")),
            base_maid_price=Decimal(kwargs.get("base_maid_price", "1000")),
            base_mother_price=Decimal(kwargs.get("base_mother_price", "1200")),
            base_other_price=Decimal(kwargs.get("base_other_price", "1000")),
            duration_minutes=kwargs.get("duration_minutes", 120),
            is_active=kwargs.get("is_active", True),
        )
        db.add(package)
        db.commit()
        db.refresh(package)
        return package
    return _create_service_package


@pytest.fixture
def service_package(create_service_package) -> ServicePackage:
    """Create a service package."""
    return create_service_package()


@pytest.fixture
def create_transport_location(db: Session, faker: Faker):
    """Factory fixture to create transport locations."""
    def _create_transport_location(location_name: str = None, **kwargs) -> TransportLocation:
        location = TransportLocation(
            location_name=location_name or faker.city(),
            county=kwargs.get("county", faker.state()),
            transport_cost=Decimal(kwargs.get("transport_cost", "1000")),
            is_free=kwargs.get("is_free", False),
            is_active=kwargs.get("is_active", True),
        )
        db.add(location)
        db.commit()
        db.refresh(location)
        return location
    return _create_transport_location


@pytest.fixture
def transport_location(create_transport_location) -> TransportLocation:
    """Create a transport location."""
    return create_transport_location()


# ============================================================================
# Booking Fixtures
# ============================================================================

@pytest.fixture
def create_booking(db: Session, faker: Faker):
    """Factory fixture to create bookings."""
    def _create_booking(
        user: User = None,
        package: ServicePackage = None,
        location: TransportLocation = None,
        **kwargs
    ) -> Booking:
        total = Decimal(kwargs.get("total_amount", "5000"))
        booking = Booking(
            booking_number=kwargs.get("booking_number", f"BK-2025-{faker.random_int(1000, 9999):06d}"),
            user_id=user.id if user else None,
            guest_email=kwargs.get("guest_email", faker.email() if not user else None),
            guest_name=kwargs.get("guest_name", faker.name() if not user else None),
            guest_phone=kwargs.get("guest_phone", faker.phone_number() if not user else None),
            package_id=package.id if package else None,
            booking_date=kwargs.get("booking_date", date.today() + timedelta(days=30)),
            booking_time=kwargs.get("booking_time", time(10, 0)),
            location_id=location.id if location else None,
            subtotal=Decimal(kwargs.get("subtotal", "4000")),
            transport_cost=Decimal(kwargs.get("transport_cost", "1000")),
            total_amount=total,
            deposit_amount=round(total * Decimal("0.5"), 2),
            status=kwargs.get("status", "pending"),
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)
        return booking
    return _create_booking


@pytest.fixture
def booking(create_booking, user, service_package, transport_location) -> Booking:
    """Create a booking."""
    return create_booking(user=user, package=service_package, location=transport_location)


# ============================================================================
# Order Fixtures
# ============================================================================

@pytest.fixture
def create_promo_code(db: Session, faker: Faker):
    """Factory fixture to create promo codes."""
    def _create_promo_code(code: str = None, **kwargs) -> PromoCode:
        promo = PromoCode(
            code=code or faker.bothify("PROMO####"),
            description=kwargs.get("description", "Test promo code"),
            discount_type=kwargs.get("discount_type", "percentage"),
            discount_value=Decimal(kwargs.get("discount_value", "10")),
            is_active=kwargs.get("is_active", True),
        )
        db.add(promo)
        db.commit()
        db.refresh(promo)
        return promo
    return _create_promo_code


@pytest.fixture
def promo_code(create_promo_code) -> PromoCode:
    """Create a promo code."""
    return create_promo_code()


@pytest.fixture
def create_order(db: Session, faker: Faker):
    """Factory fixture to create orders."""
    def _create_order(user: User = None, promo_code: PromoCode = None, **kwargs) -> Order:
        order = Order(
            order_number=kwargs.get("order_number", f"ORD-2025-{faker.random_int(1000, 9999):06d}"),
            user_id=user.id if user else None,
            guest_email=kwargs.get("guest_email", faker.email() if not user else None),
            guest_name=kwargs.get("guest_name", faker.name() if not user else None),
            guest_phone=kwargs.get("guest_phone", faker.phone_number() if not user else None),
            delivery_county=kwargs.get("delivery_county", faker.state()),
            delivery_town=kwargs.get("delivery_town", faker.city()),
            delivery_address=kwargs.get("delivery_address", faker.address()),
            subtotal=Decimal(kwargs.get("subtotal", "5000")),
            discount_amount=Decimal(kwargs.get("discount_amount", "0")),
            promo_code_id=promo_code.id if promo_code else None,
            delivery_fee=Decimal(kwargs.get("delivery_fee", "500")),
            total_amount=Decimal(kwargs.get("total_amount", "5500")),
            status=kwargs.get("status", "pending"),
        )
        db.add(order)
        db.commit()
        db.refresh(order)
        return order
    return _create_order


@pytest.fixture
def order(create_order, user) -> Order:
    """Create an order."""
    return create_order(user=user)


@pytest.fixture
def create_cart(db: Session):
    """Factory fixture to create carts."""
    def _create_cart(user: User) -> Cart:
        cart = Cart(user_id=user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
        return cart
    return _create_cart


@pytest.fixture
def cart(create_cart, user) -> Cart:
    """Create a cart for a user."""
    return create_cart(user)


# ============================================================================
# Review & Content Fixtures
# ============================================================================

@pytest.fixture
def create_review(db: Session, faker: Faker):
    """Factory fixture to create reviews."""
    def _create_review(product: Product, user: User, **kwargs) -> Review:
        review = Review(
            product_id=product.id,
            user_id=user.id,
            rating=kwargs.get("rating", faker.random_int(1, 5)),
            review_text=kwargs.get("review_text", faker.paragraph()),
            is_verified_purchase=kwargs.get("is_verified_purchase", True),
            is_approved=kwargs.get("is_approved", True),
        )
        db.add(review)
        db.commit()
        db.refresh(review)
        return review
    return _create_review


@pytest.fixture
def review(create_review, product, user) -> Review:
    """Create a review."""
    return create_review(product, user)


@pytest.fixture
def create_testimonial(db: Session, faker: Faker):
    """Factory fixture to create testimonials."""
    def _create_testimonial(**kwargs) -> Testimonial:
        testimonial = Testimonial(
            customer_name=kwargs.get("customer_name", faker.name()),
            location=kwargs.get("location", faker.city()),
            rating=kwargs.get("rating", 5),
            testimonial_text=kwargs.get("testimonial_text", faker.paragraph()),
            is_approved=kwargs.get("is_approved", True),
        )
        db.add(testimonial)
        db.commit()
        db.refresh(testimonial)
        return testimonial
    return _create_testimonial


@pytest.fixture
def testimonial(create_testimonial) -> Testimonial:
    """Create a testimonial."""
    return create_testimonial()


# ============================================================================
# Utility Fixtures
# ============================================================================

@pytest.fixture
def sample_uuid():
    """Generate a sample UUID."""
    return uuid4()


@pytest.fixture
def sample_date():
    """Generate a sample date."""
    return date.today()


@pytest.fixture
def sample_datetime():
    """Generate a sample datetime."""
    return datetime.utcnow()
