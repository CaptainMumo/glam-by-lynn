"""
Pytest configuration and fixtures
"""
import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.models.user import User
# Import all models to ensure they're registered with SQLAlchemy
from app.models.product import Brand, Category, Product, ProductImage, ProductVideo, ProductVariant
from app.models.service import ServicePackage, TransportLocation, CalendarAvailability
from app.models.booking import Booking
from app.models.order import Order, OrderItem, Cart, CartItem, Wishlist, PromoCode
from app.models.content import Review, GalleryPost, Testimonial


# Use test database URL or fall back to main database
# For local development, this will use the configured database
from app.core.config import settings

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", settings.DATABASE_URL)

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with overridden database dependency"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db_session):
    """Create an admin user for testing"""
    user = User(
        email="admin@test.com",
        full_name="Admin User",
        google_id="admin123",
        is_active=True,
        is_admin=True,
        admin_role="super_admin"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def regular_user(db_session):
    """Create a regular user for testing"""
    user = User(
        email="user@test.com",
        full_name="Regular User",
        google_id="user123",
        is_active=True,
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_token(admin_user):
    """Create a mock admin token"""
    from app.core.security import create_access_token
    return create_access_token(data={"sub": str(admin_user.id)})


@pytest.fixture
def user_token(regular_user):
    """Create a mock regular user token"""
    from app.core.security import create_access_token
    return create_access_token(data={"sub": str(regular_user.id)})


@pytest.fixture
def admin_headers(admin_token):
    """Create authorization headers for admin user"""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def user_headers(user_token):
    """Create authorization headers for regular user"""
    return {"Authorization": f"Bearer {user_token}"}
