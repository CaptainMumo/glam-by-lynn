"""Tests for testimonials API endpoints."""
import pytest
from fastapi import status

from app.models.content import Testimonial
from app.models.service import ServicePackage, TransportLocation
from app.models.product import Product, Brand, Category


@pytest.fixture
def service_package(db_session):
    """Create a test service package."""
    package = ServicePackage(
        package_type="bridal_large",
        name="Test Bridal Package",
        description="Test package",
        base_bride_price=10000.00,
        is_active=True,
        display_order=1,
    )
    db_session.add(package)
    db_session.commit()
    db_session.refresh(package)
    return package


@pytest.fixture
def product(db_session):
    """Create a test product."""
    # Create brand
    brand = Brand(
        name="Test Brand",
        slug="test-brand",
        is_active=True,
    )
    db_session.add(brand)

    # Create category
    category = Category(
        name="Test Category",
        slug="test-category",
        display_order=1,
        is_active=True,
    )
    db_session.add(category)
    db_session.commit()

    # Create product
    product = Product(
        title="Test Product",
        slug="test-product",
        brand_id=brand.id,
        category_id=category.id,
        base_price=100.00,
        inventory_count=50,
        low_stock_threshold=10,
        is_active=True,
        is_featured=False,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


@pytest.fixture
def sample_testimonials(db_session, service_package, product):
    """Create sample testimonials for testing."""
    testimonials = [
        # Approved, featured testimonial
        Testimonial(
            customer_name="John Doe",
            customer_photo_url="https://example.com/john.jpg",
            location="Nairobi",
            rating=5,
            testimonial_text="Amazing service! The makeup was flawless.",
            related_service_id=service_package.id,
            is_featured=True,
            is_approved=True,
            display_order=1,
        ),
        # Approved, not featured testimonial
        Testimonial(
            customer_name="Jane Smith",
            location="Kitui",
            rating=5,
            testimonial_text="Highly recommended! Professional and talented.",
            is_featured=False,
            is_approved=True,
            display_order=2,
        ),
        # Approved testimonial for product
        Testimonial(
            customer_name="Alice Johnson",
            customer_photo_url="https://example.com/alice.jpg",
            rating=4,
            testimonial_text="Great product, fast delivery!",
            related_product_id=product.id,
            is_featured=False,
            is_approved=True,
            display_order=3,
        ),
        # NOT approved testimonial (should not appear in results)
        Testimonial(
            customer_name="Bob Wilson",
            rating=5,
            testimonial_text="This should not appear - not approved yet.",
            is_featured=False,
            is_approved=False,
            display_order=4,
        ),
        # Approved, featured testimonial without related entities
        Testimonial(
            customer_name="Carol Brown",
            location="Mombasa",
            rating=5,
            testimonial_text="Absolutely wonderful experience!",
            is_featured=True,
            is_approved=True,
            display_order=0,  # Should appear first
        ),
    ]

    for testimonial in testimonials:
        db_session.add(testimonial)
    db_session.commit()

    # Refresh all testimonials
    for testimonial in testimonials:
        db_session.refresh(testimonial)

    return testimonials


def test_list_testimonials_default(client, sample_testimonials):
    """Test listing all approved testimonials."""
    response = client.get("/api/testimonials")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "items" in data
    assert "total" in data

    # Should return 4 approved testimonials (excluding the unapproved one)
    assert data["total"] == 4
    assert len(data["items"]) == 4

    # Verify ordering: featured first, then by display_order
    items = data["items"]
    assert items[0]["isFeatured"] is True
    assert items[0]["displayOrder"] == 0

    assert items[1]["isFeatured"] is True
    assert items[1]["displayOrder"] == 1

    # Verify none of the items are unapproved
    for item in items:
        assert item["customerName"] != "Bob Wilson"


def test_list_featured_testimonials(client, sample_testimonials):
    """Test listing only featured testimonials."""
    response = client.get("/api/testimonials/featured")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2

    # All returned items should be featured
    for item in data["items"]:
        assert item["isFeatured"] is True

    # Verify ordering by display_order
    items = data["items"]
    assert items[0]["displayOrder"] == 0
    assert items[1]["displayOrder"] == 1


def test_filter_testimonials_by_service(client, sample_testimonials, service_package):
    """Test filtering testimonials by service package."""
    response = client.get(f"/api/testimonials?related_service_id={service_package.id}")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    # Should only return the one testimonial related to the service
    assert data["total"] == 1
    assert len(data["items"]) == 1

    item = data["items"][0]
    assert item["relatedServiceId"] == str(service_package.id)
    assert item["customerName"] == "John Doe"


def test_filter_testimonials_by_product(client, sample_testimonials, product):
    """Test filtering testimonials by product."""
    response = client.get(f"/api/testimonials?related_product_id={product.id}")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    # Should only return the one testimonial related to the product
    assert data["total"] == 1
    assert len(data["items"]) == 1

    item = data["items"][0]
    assert item["relatedProductId"] == str(product.id)
    assert item["customerName"] == "Alice Johnson"


def test_testimonials_exclude_unapproved(client, sample_testimonials):
    """Test that unapproved testimonials are excluded from results."""
    response = client.get("/api/testimonials")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    items = data["items"]

    # Verify no unapproved testimonials in results
    customer_names = [item["customerName"] for item in items]
    assert "Bob Wilson" not in customer_names


def test_testimonials_empty_results(client, db_session):
    """Test listing testimonials when none exist."""
    response = client.get("/api/testimonials")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["total"] == 0
    assert len(data["items"]) == 0


def test_featured_testimonials_empty_results(client, sample_testimonials):
    """Test featured testimonials when all are set to not featured."""
    # Update all testimonials to not featured
    for testimonial in sample_testimonials:
        testimonial.is_featured = False

    # Get the database session from fixtures
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        for testimonial in sample_testimonials:
            db.merge(testimonial)
        db.commit()
    finally:
        db.close()

    response = client.get("/api/testimonials/featured")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["total"] == 0
    assert len(data["items"]) == 0


def test_testimonial_response_schema(client, sample_testimonials):
    """Test that testimonial response has all required fields."""
    response = client.get("/api/testimonials")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data["items"]) > 0

    # Check first item has all required fields
    item = data["items"][0]
    assert "id" in item
    assert "customerName" in item
    assert "customerPhotoUrl" in item
    assert "location" in item
    assert "rating" in item
    assert "testimonialText" in item
    assert "relatedServiceId" in item
    assert "relatedProductId" in item
    assert "isFeatured" in item
    assert "displayOrder" in item
    assert "createdAt" in item

    # Verify data types
    assert isinstance(item["customerName"], str)
    assert isinstance(item["rating"], int)
    assert isinstance(item["testimonialText"], str)
    assert isinstance(item["isFeatured"], bool)
    assert isinstance(item["displayOrder"], int)

    # Verify rating is within valid range (1-5)
    assert 1 <= item["rating"] <= 5


def test_testimonials_ordering(client, db_session):
    """Test that testimonials are ordered correctly."""
    # Create testimonials with specific ordering attributes
    testimonials = [
        Testimonial(
            customer_name="User A",
            rating=5,
            testimonial_text="Not featured, order 2",
            is_featured=False,
            is_approved=True,
            display_order=2,
        ),
        Testimonial(
            customer_name="User B",
            rating=5,
            testimonial_text="Featured, order 1",
            is_featured=True,
            is_approved=True,
            display_order=1,
        ),
        Testimonial(
            customer_name="User C",
            rating=5,
            testimonial_text="Not featured, order 1",
            is_featured=False,
            is_approved=True,
            display_order=1,
        ),
        Testimonial(
            customer_name="User D",
            rating=5,
            testimonial_text="Featured, order 0",
            is_featured=True,
            is_approved=True,
            display_order=0,
        ),
    ]

    for testimonial in testimonials:
        db_session.add(testimonial)
    db_session.commit()

    response = client.get("/api/testimonials")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    items = data["items"]

    # Order should be:
    # 1. Featured first (is_featured=True)
    # 2. Then by display_order (ascending)
    # 3. Then by created_at (descending)

    # First item should be featured with display_order=0
    assert items[0]["isFeatured"] is True
    assert items[0]["displayOrder"] == 0
    assert items[0]["customerName"] == "User D"

    # Second item should be featured with display_order=1
    assert items[1]["isFeatured"] is True
    assert items[1]["displayOrder"] == 1
    assert items[1]["customerName"] == "User B"

    # Third item should have display_order=1 and not featured
    assert items[2]["isFeatured"] is False
    assert items[2]["displayOrder"] == 1
    assert items[2]["customerName"] == "User C"

    # Fourth item should have display_order=2
    assert items[3]["displayOrder"] == 2
    assert items[3]["customerName"] == "User A"


def test_invalid_service_id_filter(client):
    """Test filtering with invalid service ID."""
    response = client.get("/api/testimonials?related_service_id=invalid-uuid")

    # Should return 422 validation error
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_invalid_product_id_filter(client):
    """Test filtering with invalid product ID."""
    response = client.get("/api/testimonials?related_product_id=invalid-uuid")

    # Should return 422 validation error
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
