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
        product_id=product_id,
        user_id=current_user.id,
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
    sort_by: str = Query("created_at", alias="sortBy", description="Sort field (created_at, rating, helpful_count)"),
    sort_order: str = Query("desc", alias="sortOrder", pattern="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db),
):
    """
    Get paginated list of approved reviews for a product (public).

    **Returns only approved reviews** (is_approved=True)

    Query parameters:
    - **page**: Page number (default: 1)
    - **pageSize**: Items per page (default: 10, max: 50)
    - **sortBy**: Sort field - created_at, rating, or helpful_count (default: created_at)
    - **sortOrder**: Sort order - asc or desc (default: desc)

    **Response includes:**
    - Review rating and text
    - User information
    - Verified purchase badge
    - Admin replies
    - Helpful count
    - Timestamps
    """
    skip = (page - 1) * page_size

    reviews, total = review_service.get_product_reviews(
        db=db,
        product_id=product_id,
        skip=skip,
        limit=page_size,
        approved_only=True,  # Only show approved reviews to public
        sort_by=sort_by,
        sort_order=sort_order,
    )

    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return ReviewListResponse(
        reviews=reviews,
        total=total,
        page=page,
        pageSize=page_size,
        totalPages=total_pages,
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
    review = review_service.mark_review_helpful(db, review_id)

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review with ID {review_id} not found",
        )

    return review
