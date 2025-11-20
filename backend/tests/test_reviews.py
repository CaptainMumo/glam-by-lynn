"""Tests for product review API endpoints."""
import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.product import Product, Brand, Category
from app.models.order import Order, OrderItem
from app.models.content import Review


@pytest.fixture
def test_user(db_session: Session):
    """Create a test user."""
    user = User(
        email="testuser@example.com",
        google_id="test_user_123",
        full_name="Test User",
        is_admin=False,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_product(db_session: Session):
    """Create a test product."""
    brand = Brand(name="Test Brand", slug="test-brand", is_active=True)
    category = Category(name="Test Category", slug="test-category", display_order=1, is_active=True)
    db_session.add(brand)
    db_session.add(category)
    db_session.commit()

    product = Product(
        title="Test Product",
        slug="test-product",
        description="Test description",
        brand_id=brand.id,
        category_id=category.id,
        base_price=50.00,
        inventory_count=100,
        is_active=True,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


@pytest.fixture
def test_order_with_product(db_session: Session, test_user, test_product):
    """Create a completed order with the test product."""
    from decimal import Decimal

    order = Order(
        order_number="ORD-TEST-REV-001",
        user_id=test_user.id,
        subtotal=Decimal("50.00"),
        total_amount=Decimal("50.00"),
        status="delivered",  # Use "delivered" for verified purchases
        payment_confirmed=True,
    )
    db_session.add(order)
    db_session.commit()

    order_item = OrderItem(
        order_id=order.id,
        product_id=test_product.id,
        product_title=test_product.title,
        quantity=1,
        unit_price=Decimal("50.00"),
        total_price=Decimal("50.00"),
    )
    db_session.add(order_item)
    db_session.commit()
    return order


def test_create_review_success(client: TestClient, db_session: Session, test_user, test_product, test_order_with_product, auth_headers):
    """Test creating a review successfully."""
    response = client.post(
        f"/api/products/{test_product.id}/reviews",
        json={"rating": 5, "reviewText": "Great product! Highly recommend."},
        headers=auth_headers(test_user),
    )

    assert response.status_code == 201
    data = response.json()
    assert data["rating"] == 5
    assert data["reviewText"] == "Great product! Highly recommend."
    assert data["isVerifiedPurchase"] is True  # User has purchased the product
    assert data["isApproved"] is False  # Pending admin approval


def test_create_review_duplicate(client: TestClient, db_session: Session, test_user, test_product, auth_headers):
    """Test that user cannot review the same product twice."""
    # Create first review
    client.post(
        f"/api/products/{test_product.id}/reviews",
        json={"rating": 5, "reviewText": "First review"},
        headers=auth_headers(test_user),
    )

    # Attempt second review
    response = client.post(
        f"/api/products/{test_product.id}/reviews",
        json={"rating": 4, "reviewText": "Second review"},
        headers=auth_headers(test_user),
    )

    assert response.status_code == 400
    assert "already reviewed" in response.json()["detail"].lower()


def test_create_review_without_auth(client: TestClient, test_product):
    """Test that creating a review requires authentication."""
    response = client.post(
        f"/api/products/{test_product.id}/reviews",
        json={"rating": 5, "reviewText": "Great product!"},
    )

    assert response.status_code == 401


def test_create_review_without_purchase(client: TestClient, db_session: Session, test_user, test_product, auth_headers):
    """Test creating review without purchasing (not verified)."""
    response = client.post(
        f"/api/products/{test_product.id}/reviews",
        json={"rating": 4, "reviewText": "Good product"},
        headers=auth_headers(test_user),
    )

    assert response.status_code == 201
    data = response.json()
    assert data["isVerifiedPurchase"] is False  # User hasn't purchased


def test_list_product_reviews_approved_only(client: TestClient, db_session: Session, test_product):
    """Test that only approved reviews are returned."""
    # Create approved and unapproved reviews
    user1 = User(email="user1@test.com", google_id="user1_123", full_name="User 1", is_active=True)
    user2 = User(email="user2@test.com", google_id="user2_123", full_name="User 2", is_active=True)
    db_session.add_all([user1, user2])
    db_session.commit()

    review1 = Review(product_id=test_product.id, user_id=user1.id, rating=5, is_approved=True)
    review2 = Review(product_id=test_product.id, user_id=user2.id, rating=4, is_approved=False)
    db_session.add_all([review1, review2])
    db_session.commit()

    response = client.get(f"/api/products/{test_product.id}/reviews")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1  # Only approved review
    assert len(data["reviews"]) == 1


def test_get_my_review(client: TestClient, db_session: Session, test_user, test_product, auth_headers):
    """Test getting user's own review."""
    # Create review
    review = Review(product_id=test_product.id, user_id=test_user.id, rating=5, review_text="My review")
    db_session.add(review)
    db_session.commit()

    response = client.get(
        f"/api/products/{test_product.id}/reviews/my-review",
        headers=auth_headers(test_user),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["rating"] == 5
    assert data["reviewText"] == "My review"


def test_get_my_review_not_found(client: TestClient, test_user, test_product, auth_headers):
    """Test getting my review when none exists."""
    response = client.get(
        f"/api/products/{test_product.id}/reviews/my-review",
        headers=auth_headers(test_user),
    )

    assert response.status_code == 404


def test_mark_review_helpful(client: TestClient, db_session: Session, test_product):
    """Test marking a review as helpful."""
    user = User(email="user@test.com", google_id="user_123", full_name="User", is_active=True)
    db_session.add(user)
    db_session.commit()

    review = Review(product_id=test_product.id, user_id=user.id, rating=5, helpful_count=0)
    db_session.add(review)
    db_session.commit()

    response = client.post(f"/api/reviews/{review.id}/helpful")

    assert response.status_code == 200
    data = response.json()
    assert data["helpfulCount"] == 1
