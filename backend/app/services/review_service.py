"""Review service for business logic."""
from datetime import datetime, timezone
from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.models.content import Review
from app.models.order import Order, OrderItem


def get_review_by_id(db: Session, review_id: UUID) -> Optional[Review]:
    """Get a review by ID with user details."""
    return db.query(Review).options(joinedload(Review.user)).filter(Review.id == review_id).first()


def get_user_review_for_product(
    db: Session, user_id: UUID, product_id: UUID
) -> Optional[Review]:
    """Get a user's review for a specific product."""
    return (
        db.query(Review)
        .filter(and_(Review.user_id == user_id, Review.product_id == product_id))
        .first()
    )


def check_verified_purchase(db: Session, user_id: UUID, product_id: UUID) -> Tuple[bool, Optional[UUID]]:
    """
    Check if user has purchased the product.

    Args:
        db: Database session
        user_id: User ID
        product_id: Product ID

    Returns:
        Tuple of (is_verified, order_id)
    """
    # Find an order where the user purchased this product
    order_item = (
        db.query(OrderItem)
        .join(Order)
        .filter(
            and_(
                Order.user_id == user_id,
                OrderItem.product_id == product_id,
                Order.status.in_(["completed", "delivered"]),  # Only completed/delivered orders
            )
        )
        .first()
    )

    if order_item:
        return True, order_item.order_id
    return False, None


def create_review(
    db: Session,
    product_id: UUID,
    user_id: UUID,
    rating: int,
    review_text: Optional[str] = None,
) -> Tuple[bool, str, Optional[Review]]:
    """
    Create a new review.

    Args:
        db: Database session
        product_id: Product ID
        user_id: User ID
        rating: Rating (1-5)
        review_text: Review text (optional)

    Returns:
        Tuple of (success, message, review)
    """
    from app.models.product import Product

    # Check if product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return False, "Product not found", None

    # Check if user already reviewed this product
    existing = get_user_review_for_product(db, user_id, product_id)
    if existing:
        return False, "You have already reviewed this product", None

    # Check for verified purchase
    is_verified, order_id = check_verified_purchase(db, user_id, product_id)

    # Create review (not approved by default, requires admin approval)
    review = Review(
        product_id=product_id,
        user_id=user_id,
        order_id=order_id,
        rating=rating,
        review_text=review_text,
        is_verified_purchase=is_verified,
        is_approved=False,  # Requires admin approval
        helpful_count=0,
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    return True, "Review created successfully", review


def get_product_reviews(
    db: Session,
    product_id: UUID,
    skip: int = 0,
    limit: int = 20,
    approved_only: bool = True,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> Tuple[list[Review], int]:
    """
    Get reviews for a product with pagination.

    Args:
        db: Database session
        product_id: Product ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        approved_only: Only return approved reviews (default: True for public)
        sort_by: Sort field (created_at, rating, helpful_count)
        sort_order: Sort order (asc or desc)

    Returns:
        Tuple of (reviews list, total count)
    """
    query = db.query(Review).options(joinedload(Review.user)).filter(Review.product_id == product_id)

    # Filter by approval status
    if approved_only:
        query = query.filter(Review.is_approved == True)

    # Get total count
    total = query.count()

    # Determine sort field
    sort_field = getattr(Review, sort_by, Review.created_at)

    # Apply sorting
    if sort_order == "asc":
        query = query.order_by(sort_field.asc())
    else:
        query = query.order_by(sort_field.desc())

    # Apply pagination
    reviews = query.offset(skip).limit(limit).all()

    return reviews, total


def update_review(
    db: Session,
    review_id: UUID,
    user_id: UUID,
    rating: Optional[int] = None,
    review_text: Optional[str] = None,
) -> Tuple[bool, str, Optional[Review]]:
    """
    Update a review (user can only update their own review).

    Args:
        db: Database session
        review_id: Review ID
        user_id: User ID (must match review user_id)
        rating: Optional new rating
        review_text: Optional new review text

    Returns:
        Tuple of (success, message, review)
    """
    review = db.query(Review).filter(Review.id == review_id).first()

    if not review:
        return False, "Review not found", None

    if review.user_id != user_id:
        return False, "You can only update your own reviews", None

    # Update fields
    if rating is not None:
        review.rating = rating

    if review_text is not None:
        review.review_text = review_text

    # Reset approval status if content changed (needs re-review by admin)
    if rating is not None or review_text is not None:
        review.is_approved = False

    db.commit()
    db.refresh(review)

    return True, "Review updated successfully", review


def update_review_approval(
    db: Session, review_id: UUID, is_approved: bool, admin_reply: Optional[str] = None
) -> Optional[Review]:
    """
    Update review approval status and optionally add admin reply.

    Args:
        db: Database session
        review_id: Review ID
        is_approved: Approval status
        admin_reply: Optional admin reply

    Returns:
        Updated review or None if not found
    """
    review = db.query(Review).filter(Review.id == review_id).first()

    if not review:
        return None

    review.is_approved = is_approved

    if admin_reply is not None:
        review.admin_reply = admin_reply
        review.admin_reply_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(review)

    return review


def delete_review(db: Session, review_id: UUID, user_id: UUID) -> Tuple[bool, str]:
    """
    Delete a review (user can only delete their own review).

    Args:
        db: Database session
        review_id: Review ID
        user_id: User ID (must match review user_id)

    Returns:
        Tuple of (success, message)
    """
    review = db.query(Review).filter(Review.id == review_id).first()

    if not review:
        return False, "Review not found"

    if review.user_id != user_id:
        return False, "You can only delete your own reviews"

    db.delete(review)
    db.commit()

    return True, "Review deleted successfully"


def admin_update_review(
    db: Session,
    review_id: UUID,
    is_approved: Optional[bool] = None,
    admin_reply: Optional[str] = None,
) -> Tuple[bool, str, Optional[Review]]:
    """
    Admin update review approval status and add reply.

    Args:
        db: Database session
        review_id: Review ID
        is_approved: Optional approval status
        admin_reply: Optional admin reply

    Returns:
        Tuple of (success, message, review)
    """
    review = db.query(Review).filter(Review.id == review_id).first()

    if not review:
        return False, "Review not found", None

    if is_approved is not None:
        review.is_approved = is_approved

    if admin_reply is not None:
        review.admin_reply = admin_reply
        review.admin_reply_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(review)

    return True, "Review updated successfully", review


def increment_helpful_count(db: Session, review_id: UUID) -> Tuple[bool, str]:
    """
    Increment helpful count for a review.

    Args:
        db: Database session
        review_id: Review ID

    Returns:
        Tuple of (success, message)
    """
    review = db.query(Review).filter(Review.id == review_id).first()

    if not review:
        return False, "Review not found"

    review.helpful_count += 1
    db.commit()

    return True, "Review marked as helpful"


def mark_review_helpful(db: Session, review_id: UUID) -> Optional[Review]:
    """
    Increment helpful count for a review (deprecated - use increment_helpful_count).

    Args:
        db: Database session
        review_id: Review ID

    Returns:
        Updated review or None if not found
    """
    review = db.query(Review).filter(Review.id == review_id).first()

    if not review:
        return None

    review.helpful_count += 1
    db.commit()
    db.refresh(review)

    return review


def get_product_rating_summary(db: Session, product_id: UUID) -> dict:
    """
    Get rating summary for a product.

    Args:
        db: Database session
        product_id: Product ID

    Returns:
        Dictionary with total_reviews, average_rating, rating_distribution
    """
    # Get all approved reviews for the product
    reviews = (
        db.query(Review)
        .filter(Review.product_id == product_id, Review.is_approved == True)
        .all()
    )

    total_reviews = len(reviews)

    if total_reviews == 0:
        return {
            "total_reviews": 0,
            "average_rating": 0.0,
            "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
        }

    # Calculate average rating
    total_rating = sum(review.rating for review in reviews)
    average_rating = total_rating / total_reviews

    # Calculate rating distribution
    rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for review in reviews:
        rating_distribution[review.rating] += 1

    return {
        "total_reviews": total_reviews,
        "average_rating": round(average_rating, 1),
        "rating_distribution": rating_distribution,
    }
