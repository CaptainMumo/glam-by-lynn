"""Testimonials API endpoints."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.testimonial import TestimonialListResponse, TestimonialResponse
from app.services.testimonial_service import get_approved_testimonials

router = APIRouter(prefix="/testimonials", tags=["testimonials"])


@router.get("", response_model=TestimonialListResponse, status_code=status.HTTP_200_OK)
def list_testimonials(
    related_service_id: Optional[UUID] = Query(
        None, description="Filter by service package ID"
    ),
    related_product_id: Optional[UUID] = Query(
        None, description="Filter by product ID"
    ),
    db: Session = Depends(get_db),
):
    """
    Get list of approved testimonials.

    - **related_service_id**: Filter testimonials for a specific service
    - **related_product_id**: Filter testimonials for a specific product

    Returns approved testimonials ordered by featured status, display order, and creation date.
    """
    testimonials = get_approved_testimonials(
        db=db,
        featured_only=False,
        related_service_id=related_service_id,
        related_product_id=related_product_id,
    )

    return TestimonialListResponse(
        items=[TestimonialResponse.model_validate(t) for t in testimonials],
        total=len(testimonials),
    )


@router.get(
    "/featured",
    response_model=TestimonialListResponse,
    status_code=status.HTTP_200_OK,
)
def list_featured_testimonials(
    db: Session = Depends(get_db),
):
    """
    Get list of featured testimonials only.

    Returns only approved testimonials marked as featured,
    ordered by display order and creation date.
    """
    testimonials = get_approved_testimonials(
        db=db,
        featured_only=True,
    )

    return TestimonialListResponse(
        items=[TestimonialResponse.model_validate(t) for t in testimonials],
        total=len(testimonials),
    )
