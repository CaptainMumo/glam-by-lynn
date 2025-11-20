"""Review service for business logic."""
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.models.content import Review
from app.models.order import Order, OrderItem


def get_review_by_id(db: Session, review_id: UUID) -> Optional[Review]:
    """Get a review by ID."""
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
) -> Review:
    """
    Create a new review.

    Args:
        db: Database session
        product_id: Product ID
        user_id: User ID
        rating: Rating (1-5)
        review_text: Review text (optional)

    Returns:
        Created review

    Raises:
        ValueError: If user already reviewed this product
    """
    # Check if user already reviewed this product
    existing = get_user_review_for_product(db, user_id, product_id)
    if existing:
        raise ValueError("You have already reviewed this product")

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

    return review


def get_product_reviews(
    db: Session,
    product_id: UUID,
    skip: int = 0,
    limit: int = 20,
    approved_only: bool = True,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> Tuple[List[Review], int]:
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
    from datetime import datetime, timezone

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


def delete_review(db: Session, review_id: UUID) -> bool:
    """
    Delete a review.

    Args:
        db: Database session
        review_id: Review ID

    Returns:
        True if deleted, False if not found
    """
    review = db.query(Review).filter(Review.id == review_id).first()

    if not review:
        return False

    db.delete(review)
    db.commit()

    return True


def mark_review_helpful(db: Session, review_id: UUID) -> Optional[Review]:
    """
    Increment helpful count for a review.

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
