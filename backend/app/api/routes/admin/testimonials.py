"""Admin testimonial management routes."""
import math
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_admin_user
from app.models.user import User
from app.schemas.testimonial import (
    ApprovalUpdate,
    TestimonialCreate,
    TestimonialListResponse,
    TestimonialResponse,
    TestimonialUpdate,
)
from app.services import testimonial_service

router = APIRouter(tags=["Admin Testimonials"])


@router.get(
    "/admin/testimonials",
    response_model=TestimonialListResponse,
    summary="List all testimonials (admin only)",
)
def list_all_testimonials(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    is_approved: Optional[bool] = Query(None, alias="isApproved", description="Filter by approval status"),
    is_featured: Optional[bool] = Query(None, alias="isFeatured", description="Filter by featured status"),
    related_service_id: Optional[UUID] = Query(
        None, alias="relatedServiceId", description="Filter by service package ID"
    ),
    related_product_id: Optional[UUID] = Query(
        None, alias="relatedProductId", description="Filter by product ID"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Get all testimonials (including unapproved).

    Admin only. Supports pagination and filtering by approval status, featured status,
    and related service/product.
    """
    testimonials, total = testimonial_service.admin_get_all_testimonials(
        db=db,
        skip=skip,
        limit=limit,
        is_approved=is_approved,
        is_featured=is_featured,
        related_service_id=related_service_id,
        related_product_id=related_product_id,
    )

    return TestimonialListResponse(
        items=[TestimonialResponse.model_validate(t) for t in testimonials],
        total=total,
    )


@router.get(
    "/admin/testimonials/{testimonial_id}",
    response_model=TestimonialResponse,
    summary="Get testimonial by ID (admin only)",
)
def get_testimonial(
    testimonial_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Get a single testimonial by ID (includes unapproved).

    Admin only.
    """
    testimonial = testimonial_service.admin_get_testimonial_by_id(db=db, testimonial_id=testimonial_id)
    if not testimonial:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Testimonial with ID {testimonial_id} not found",
        )

    return TestimonialResponse.model_validate(testimonial)


@router.post(
    "/admin/testimonials",
    response_model=TestimonialResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create testimonial (admin only)",
)
def create_testimonial(
    testimonial_data: TestimonialCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Create a new testimonial.

    Admin only. Requires customer name, testimonial text, and rating (1-5).
    Other fields are optional.
    """
    testimonial = testimonial_service.create_testimonial(
        db=db,
        customer_name=testimonial_data.customer_name,
        customer_photo_url=testimonial_data.customer_photo_url,
        location=testimonial_data.location,
        rating=testimonial_data.rating,
        testimonial_text=testimonial_data.testimonial_text,
        related_service_id=testimonial_data.related_service_id,
        related_product_id=testimonial_data.related_product_id,
        is_featured=testimonial_data.is_featured,
        is_approved=testimonial_data.is_approved,
        display_order=testimonial_data.display_order,
    )

    return TestimonialResponse.model_validate(testimonial)


@router.put(
    "/admin/testimonials/{testimonial_id}",
    response_model=TestimonialResponse,
    summary="Update testimonial (admin only)",
)
def update_testimonial(
    testimonial_id: UUID,
    testimonial_data: TestimonialUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Update a testimonial.

    Admin only. All fields are optional for partial updates.
    """
    testimonial = testimonial_service.update_testimonial(
        db=db,
        testimonial_id=testimonial_id,
        customer_name=testimonial_data.customer_name,
        customer_photo_url=testimonial_data.customer_photo_url,
        location=testimonial_data.location,
        rating=testimonial_data.rating,
        testimonial_text=testimonial_data.testimonial_text,
        related_service_id=testimonial_data.related_service_id,
        related_product_id=testimonial_data.related_product_id,
        is_featured=testimonial_data.is_featured,
        is_approved=testimonial_data.is_approved,
        display_order=testimonial_data.display_order,
    )

    if not testimonial:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Testimonial with ID {testimonial_id} not found",
        )

    return TestimonialResponse.model_validate(testimonial)


@router.put(
    "/admin/testimonials/{testimonial_id}/approve",
    response_model=TestimonialResponse,
    summary="Approve/reject testimonial (admin only)",
)
def approve_testimonial(
    testimonial_id: UUID,
    approval_data: ApprovalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Approve or reject a testimonial.

    Admin only. Updates the is_approved status of a testimonial.
    """
    testimonial = testimonial_service.update_testimonial(
        db=db,
        testimonial_id=testimonial_id,
        is_approved=approval_data.is_approved,
    )

    if not testimonial:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Testimonial with ID {testimonial_id} not found",
        )

    return TestimonialResponse.model_validate(testimonial)


@router.delete(
    "/admin/testimonials/{testimonial_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete testimonial (admin only)",
)
def delete_testimonial(
    testimonial_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Delete a testimonial.

    Admin only.
    """
    success = testimonial_service.delete_testimonial(db=db, testimonial_id=testimonial_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Testimonial with ID {testimonial_id} not found",
        )

    return None
