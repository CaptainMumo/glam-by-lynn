"""Public review API routes."""
import math
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewResponse, ReviewListResponse
from app.services import review_service

router = APIRouter(tags=["Product Reviews"])


@router.post("/products/{product_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_product_review(
    product_id: UUID,
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a review for a product (authenticated users only).

    **Requirements:**
    - User must be authenticated
    - One review per user per product (cannot review same product twice)
    - Verified purchase flag set automatically if user purchased the product
    - Reviews require admin approval before being publicly visible

    **Request:**
    - rating: Integer from 1 to 5 stars
    - review_text: Optional review text (min 10 chars if provided)

    **Response:**
    - Created review with is_approved=False (pending admin approval)
    - is_verified_purchase=True if user has purchased the product
    """
    success, message, review = review_service.create_review(
        db=db,
        user_id=current_user.id,
        product_id=product_id,
        rating=review_data.rating,
        review_text=review_data.review_text,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )

    return review


@router.get("/products/{product_id}/reviews", response_model=ReviewListResponse)
async def list_product_reviews(
    product_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=50, alias="pageSize", description="Items per page"),
    db: Session = Depends(get_db),
):
    """
    Get paginated list of approved reviews for a product (public).

    **Returns only approved reviews** (is_approved=True)

    Query parameters:
    - **page**: Page number (default: 1)
    - **pageSize**: Items per page (default: 10, max: 50)

    **Response includes:**
    - Review rating and text
    - User information
    - Verified purchase badge
    - Admin replies
    - Helpful count
    - Timestamps
    """
    reviews, total, total_pages = review_service.get_product_reviews(
        db=db,
        product_id=product_id,
        page=page,
        page_size=page_size,
        only_approved=True,  # Only show approved reviews to public
    )

    # Calculate average rating
    average_rating = None
    if reviews:
        average_rating = sum(review.rating for review in reviews) / len(reviews)

    return ReviewListResponse(
        reviews=reviews,
        total=total,
        page=page,
        pageSize=page_size,
        totalPages=total_pages,
        averageRating=average_rating,
    )


@router.get("/products/{product_id}/reviews/my-review", response_model=ReviewResponse)
async def get_my_review_for_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get current user's review for a product (authenticated).

    Returns the authenticated user's review for the specified product,
    regardless of approval status. Used to check if user has already
    reviewed the product and to show pending review.

    Returns 404 if user hasn't reviewed this product yet.
    """
    review = review_service.get_user_review_for_product(db, current_user.id, product_id)

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You have not reviewed this product yet",
        )

    return review


@router.post("/reviews/{review_id}/helpful", response_model=ReviewResponse)
async def mark_review_helpful(
    review_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Mark a review as helpful (public).

    Increments the helpful_count for a review. No authentication required.
    In a production system, you might want to track which users marked
    which reviews as helpful to prevent duplicate votes.
    """
    success, message = review_service.increment_helpful_count(db, review_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message,
        )

    # Fetch and return the updated review
    review = review_service.get_review_by_id(db, review_id)
    return review
