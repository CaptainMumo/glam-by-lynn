"""Testimonial service for business logic."""
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.content import Testimonial


def get_approved_testimonials(
    db: Session,
    featured_only: bool = False,
    related_service_id: Optional[UUID] = None,
    related_product_id: Optional[UUID] = None,
) -> List[Testimonial]:
    """
    Get approved testimonials with optional filters.

    Args:
        db: Database session
        featured_only: Return only featured testimonials
        related_service_id: Filter by service package ID
        related_product_id: Filter by product ID

    Returns:
        List of approved testimonials
    """
    # Build base query - only approved testimonials
    query = db.query(Testimonial).filter(Testimonial.is_approved == True)

    # Apply filters
    if featured_only:
        query = query.filter(Testimonial.is_featured == True)

    if related_service_id:
        query = query.filter(Testimonial.related_service_id == related_service_id)

    if related_product_id:
        query = query.filter(Testimonial.related_product_id == related_product_id)

    # Order by featured status, display order, and creation date
    query = query.order_by(
        Testimonial.is_featured.desc(),
        Testimonial.display_order.asc(),
        Testimonial.created_at.desc(),
    )

    return query.all()


def get_testimonial_by_id(db: Session, testimonial_id: UUID) -> Optional[Testimonial]:
    """Get a single approved testimonial by ID."""
    return (
        db.query(Testimonial)
        .filter(
            Testimonial.id == testimonial_id,
            Testimonial.is_approved == True,
        )
        .first()
    )
