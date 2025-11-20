"""Tests for product review API."""
from decimal import Decimal

import pytest
from fastapi import status

from app.models.content import Review
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
def admin_token(admin_user):
    """Create JWT token for admin user."""
    from app.core.security import create_access_token

    return create_access_token(data={"sub": str(admin_user.id), "email": admin_user.email})


@pytest.fixture
def sample_product(db_session):
    """Create a sample product."""
    product = Product(
        title="Test Lipstick",
        slug="test-lipstick",
        description="Test product description",
        base_price=Decimal("1500.00"),
        inventory_count=100,
        is_active=True,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


@pytest.fixture
def delivered_order(db_session, regular_user, sample_product):
    """Create a delivered order for verified purchase testing."""
    order = Order(
        order_number="ORD-20250119-TEST1",
        user_id=regular_user.id,
        delivery_county="Nairobi",
        delivery_town="Nairobi",
        delivery_address="123 Test Street",
        subtotal=Decimal("1500.00"),
        discount_amount=Decimal("0.00"),
        delivery_fee=Decimal("200.00"),
        total_amount=Decimal("1700.00"),
        payment_method="mpesa",
        payment_confirmed=True,
        status="delivered",
    )
    db_session.add(order)
    db_session.flush()

    order_item = OrderItem(
        order_id=order.id,
        product_id=sample_product.id,
        product_title=sample_product.title,
        product_sku="TEST-SKU",
        quantity=1,
        unit_price=Decimal("1500.00"),
        discount=Decimal("0.00"),
        total_price=Decimal("1500.00"),
    )
    db_session.add(order_item)
    db_session.commit()
    db_session.refresh(order)
    return order


def test_create_review_success(client, user_token, sample_product):
    """Test creating a review successfully."""
    review_data = {
        "rating": 5,
        "reviewText": "Excellent product! Really love it and would highly recommend to everyone.",
    }

    response = client.post(
        f"/api/products/{sample_product.id}/reviews",
        json=review_data,
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert data["rating"] == 5
    assert data["reviewText"] == review_data["reviewText"]
    assert data["isApproved"] is False  # Requires admin approval
    assert data["isVerifiedPurchase"] is False  # No delivered order yet


def test_create_review_verified_purchase(client, user_token, sample_product, delivered_order):
    """Test creating a review with verified purchase."""
    review_data = {
        "rating": 5,
        "reviewText": "Great product! I purchased it and absolutely love the quality.",
    }

    response = client.post(
        f"/api/products/{sample_product.id}/reviews",
        json=review_data,
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert data["rating"] == 5
    assert data["isVerifiedPurchase"] is True  # User has delivered order


def test_create_review_duplicate(client, user_token, sample_product):
    """Test that users cannot create duplicate reviews."""
    review_data = {
        "rating": 5,
        "reviewText": "First review that is long enough to pass validation rules.",
    }

    # Create first review
    response = client.post(
        f"/api/products/{sample_product.id}/reviews",
        json=review_data,
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == status.HTTP_201_CREATED

    # Try to create second review
    response = client.post(
        f"/api/products/{sample_product.id}/reviews",
        json=review_data,
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already reviewed" in response.json()["detail"].lower()


def test_create_review_unauthenticated(client, sample_product):
    """Test that unauthenticated users cannot create reviews."""
    review_data = {
        "rating": 5,
        "reviewText": "Great product and I really enjoyed using it every single day!",
    }

    response = client.post(
        f"/api/products/{sample_product.id}/reviews",
        json=review_data,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_review_invalid_product(client, user_token):
    """Test creating review for non-existent product."""
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    review_data = {
        "rating": 5,
        "reviewText": "This review is for a product that does not exist in database.",
    }

    response = client.post(
        f"/api/products/{fake_uuid}/reviews",
        json=review_data,
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_product_reviews(client, db_session, sample_product, regular_user):
    """Test getting reviews for a product."""
    # Create approved reviews
    for i in range(3):
        review = Review(
            product_id=sample_product.id,
            user_id=regular_user.id if i == 0 else None,
            rating=5 - i,
            review_text=f"Review {i+1} with enough text to pass validation requirements.",
            is_approved=True,
        )
        if i > 0:
            # Create temp user for other reviews
            temp_user = User(
                email=f"user{i}@example.com",
                google_id=f"user{i}123",
                full_name=f"User {i}",
                is_admin=False,
                is_active=True,
            )
            db_session.add(temp_user)
            db_session.flush()
            review.user_id = temp_user.id
        db_session.add(review)

    db_session.commit()

    response = client.get(f"/api/products/{sample_product.id}/reviews")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "reviews" in data
    assert "total" in data
    assert data["total"] == 3
    assert len(data["reviews"]) == 3


def test_get_product_reviews_only_approved(client, db_session, sample_product, regular_user):
    """Test that only approved reviews are returned to public."""
    # Create one approved and one unapproved review
    approved_review = Review(
        product_id=sample_product.id,
        user_id=regular_user.id,
        rating=5,
        review_text="This is an approved review with sufficient text content.",
        is_approved=True,
    )
    db_session.add(approved_review)

    other_user = User(
        email="temp@example.com",
        google_id="temp123",
        full_name="Temp User",
        is_admin=False,
        is_active=True,
    )
    db_session.add(other_user)
    db_session.flush()

    unapproved_review = Review(
        product_id=sample_product.id,
        user_id=other_user.id,
        rating=3,
        review_text="This is an unapproved review that should not be visible.",
        is_approved=False,
    )
    db_session.add(unapproved_review)
    db_session.commit()

    response = client.get(f"/api/products/{sample_product.id}/reviews")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["total"] == 1  # Only approved review


def test_get_product_rating_summary(client, db_session, sample_product, regular_user):
    """Test getting product rating summary."""
    # Create reviews with different ratings
    ratings = [5, 5, 4, 4, 3]
    for i, rating in enumerate(ratings):
        user = User(
            email=f"user{i}@example.com",
            google_id=f"user{i}123",
            full_name=f"User {i}",
            is_admin=False,
            is_active=True,
        )
        db_session.add(user)
        db_session.flush()

        review = Review(
            product_id=sample_product.id,
            user_id=user.id,
            rating=rating,
            review_text=f"Review with rating {rating} and sufficient text length.",
            is_approved=True,
        )
        db_session.add(review)

    db_session.commit()

    response = client.get(f"/api/products/{sample_product.id}/reviews/summary")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["totalReviews"] == 5
    assert data["averageRating"] == 4.2
    assert data["ratingDistribution"]["5"] == 2
    assert data["ratingDistribution"]["4"] == 2
    assert data["ratingDistribution"]["3"] == 1


def test_update_review_success(client, db_session, user_token, sample_product, regular_user):
    """Test updating own review."""
    # Create initial review
    review = Review(
        product_id=sample_product.id,
        user_id=regular_user.id,
        rating=3,
        review_text="Initial review text with enough characters to pass validation.",
        is_approved=True,
    )
    db_session.add(review)
    db_session.commit()
    db_session.refresh(review)

    # Update review
    update_data = {
        "rating": 5,
        "reviewText": "Updated review text after using product more extensively.",
    }

    response = client.put(
        f"/api/reviews/{review.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["rating"] == 5
    assert data["reviewText"] == update_data["reviewText"]
    assert data["isApproved"] is False  # Requires re-approval


def test_update_review_forbidden(client, db_session, other_token, sample_product, regular_user):
    """Test that users cannot update other users' reviews."""
    # Create review by regular_user
    review = Review(
        product_id=sample_product.id,
        user_id=regular_user.id,
        rating=5,
        review_text="Original review by the first user with sufficient length.",
        is_approved=True,
    )
    db_session.add(review)
    db_session.commit()
    db_session.refresh(review)

    # Try to update with other_user token
    update_data = {
        "rating": 1,
        "reviewText": "Trying to modify someone else's review maliciously.",
    }

    response = client.put(
        f"/api/reviews/{review.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {other_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_review_success(client, db_session, user_token, sample_product, regular_user):
    """Test deleting own review."""
    # Create review
    review = Review(
        product_id=sample_product.id,
        user_id=regular_user.id,
        rating=5,
        review_text="Review to be deleted with enough text for validation.",
        is_approved=True,
    )
    db_session.add(review)
    db_session.commit()
    db_session.refresh(review)

    response = client.delete(
        f"/api/reviews/{review.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify review is deleted
    deleted_review = db_session.query(Review).filter(Review.id == review.id).first()
    assert deleted_review is None


def test_admin_approve_review(client, db_session, admin_token, sample_product, regular_user):
    """Test admin approving a review."""
    # Create unapproved review
    review = Review(
        product_id=sample_product.id,
        user_id=regular_user.id,
        rating=5,
        review_text="Pending review awaiting approval from administrators.",
        is_approved=False,
    )
    db_session.add(review)
    db_session.commit()
    db_session.refresh(review)

    # Admin approves review
    update_data = {
        "isApproved": True,
        "adminReply": "Thank you for your positive feedback!",
    }

    response = client.patch(
        f"/api/admin/reviews/{review.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["isApproved"] is True
    assert data["adminReply"] == "Thank you for your positive feedback!"
    assert data["adminReplyAt"] is not None


def test_admin_update_review_unauthorized(client, db_session, user_token, sample_product, regular_user):
    """Test that non-admin users cannot use admin endpoints."""
    review = Review(
        product_id=sample_product.id,
        user_id=regular_user.id,
        rating=5,
        review_text="Review that regular user tries to approve themselves.",
        is_approved=False,
    )
    db_session.add(review)
    db_session.commit()
    db_session.refresh(review)

    update_data = {"isApproved": True}

    response = client.patch(
        f"/api/admin/reviews/{review.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_mark_review_helpful(client, db_session, sample_product, regular_user):
    """Test marking a review as helpful."""
    review = Review(
        product_id=sample_product.id,
        user_id=regular_user.id,
        rating=5,
        review_text="Helpful review that other customers find useful and informative.",
        is_approved=True,
        helpful_count=0,
    )
    db_session.add(review)
    db_session.commit()
    db_session.refresh(review)

    response = client.post(f"/api/reviews/{review.id}/helpful")

    assert response.status_code == status.HTTP_200_OK

    # Verify helpful count incremented
    db_session.refresh(review)
    assert review.helpful_count == 1
